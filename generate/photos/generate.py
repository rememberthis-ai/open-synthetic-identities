#!/usr/bin/env python3
"""Generate scene photos from a manifest (step 2 of PLAN.md's pipeline).

Reads generate/photos/manifests/<identity>.yaml, calls Replicate
flux-1.1-pro (no cast) or flux-kontext-pro (with cast, conditioned on the
era-appropriate cast-sheet file(s) in generate/photos/cast/), writes raw
PNGs to generate/photos/raw/<identity>/ (gitignored scratch, per PLAN.md's
pipeline diagram — stamp_exif.py turns these into the committed library/).

Cast handling: flux-kontext-pro takes ONE input_image, so a multi-cast scene
composites every member's era-appropriate sheet into a single side-by-side
strip (`ensemble_ref_path`) and names them by position in the prompt. EVERY
face in the photo is therefore pixel-identity locked.

It used to lock only the first person and describe the rest in words. That does
not work — kontext is an image-editing model, the input image dominates, and
text about a face absent from it is weakly weighted. Measured 2026-08: Jonas,
Alex's university friend and the same age, came back as a man in his sixties in
61 of 86 photos, and stayed that way after the prompt was given his explicit
age and build. The strip fixed it on the first try.

Receipt composites (`style: receipt`, `scene: "COMPOSITE: <path>"`) kontext
the referenced receipt PNG itself into a photographed context, per PLAN.md's
"Receipt-photos subset" section.

Resumable: skips manifest entries whose raw output already exists unless
--force. Standard 429/retry_after backoff via replicate_client.

Usage:
  export REPLICATE_API_TOKEN=...
  python3 generate.py --manifest manifests/alex-carter.yaml
"""
import argparse
import time
from pathlib import Path

import yaml
from PIL import Image

from gen_cast import CHARACTERS as CAST_SPECS
from gen_cast import PORTRAIT_SUFFIX
from replicate_client import FLUX_CREATE, FLUX_KONTEXT, image_data_uri, replicate_predict

HERE = Path(__file__).parent
CAST_DIR = HERE / "cast"
RAW_ROOT = HERE / "raw"
REPO_ROOT = HERE.parent.parent  # open-synthetic-identities/

# era -> {character: cast-sheet filename}. A character/era combination not
# listed here (or missing on disk) falls back to that character's only/most
# recently generated file — covers the pilot-minimal Jonas/Priya entries,
# which only have one look each.
ERA_AGE = {
    "manchester": {"alex": "age-26.png", "jonas": "age-26.png", "rosa": "age-50.png"},
    "berlin-move": {"alex": "age-29.png", "sam": "age-29.png"},
    "mira-arrives": {"alex": "age-32.png", "sam": "age-32.png", "mira": "age-2.png", "rosa": "age-55.png"},
    "carter-studio": {
        "alex": "age-35.png", "sam": "age-35.png", "mira": "age-4.png",
        "priya": "age-36.png", "jonas": "age-35.png",
    },
    "balance": {
        "alex": "age-38.png",
        "sam": "canonical.png",  # Sam's canonical IS the 2026/age-38 look
        "mira": "age-7.png",
        "jonas": "age-38.png",
        "priya": "age-36.png",
    },
    "receipts": {},
}

STYLE_SUFFIX = {
    "candid-phone": (
        "candid smartphone photo, natural handheld framing, slightly "
        "imperfect composition, realistic phone-camera color and dynamic "
        "range, no visible UI overlay, no text, no watermark"
    ),
    "posed": (
        "posed smartphone photo, deliberate composition but still shot on a "
        "phone camera (not a professional camera), natural lighting, no "
        "text, no watermark"
    ),
    "landscape": (
        "wide smartphone landscape photo, natural phone-camera color and "
        "dynamic range, tourist snapshot framing, no text, no watermark"
    ),
    "receipt": (
        "photographed with a smartphone camera, realistic table/surface and "
        "soft shadow, slight perspective distortion typical of a handheld "
        "phone shot, natural indoor lighting, no watermark"
    ),
}


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def cast_ref_path(character: str, era: str) -> Path:
    char_dir = CAST_DIR / character
    filename = ERA_AGE.get(era, {}).get(character)
    if filename and (char_dir / filename).exists():
        return char_dir / filename
    candidates = sorted(char_dir.glob("*.png"))
    if not candidates:
        raise RuntimeError(f"no cast-sheet files found for '{character}' in {char_dir}")
    return candidates[0]


# Appearance + birth year for everyone in the cast, condensed from
# CHARACTERS.md. **This exists because only the FIRST cast member is
# pixel-identity locked** — kontext takes one input image, so everybody else in
# a photo is whatever the model invents from the prompt.
#
# Until 2026-08 the prompt said nothing about them at all, despite the module
# docstring claiming they were "described in the prompt text". A scene reading
# "two climbers coiling a rope" produced Alex at 26 beside a stranger in his
# SIXTIES — cast as his university friend, the same age. That breaks the thing
# the photos exist for: People, Groups and Network cluster on faces, and a
# friend who is 60 in one photo and 38 in another is two people.
#
# The prompt cannot lock identity, but it can hold age and build steady, which
# is most of what clustering needs.
CAST_DESC = {
    "alex":  (1988, "warm olive complexion, dark wavy hair, slim build"),
    "sam":   (1988, "Black British, warm dark brown skin, close-cropped black hair, broad friendly build"),
    "mira":  (2019, "a child with light brown skin and dark curly hair"),
    "jonas": (1988, "tanned sun-weathered skin, short practical dark-blonde hair, athletic wiry build"),
    "priya": (1987, "deep-brown skin, sleek dark hair in a low bun, tailored business-casual clothes"),
    "rosa":  (1960, "fair British complexion with laugh-lines, softly waved silver-grey shoulder-length hair"),
}


def positions_for(n: int) -> list:
    """Plain-English position words for a strip of n portraits.

    A fixed ladder ("far left", "second from left", …) reads wrongly for the
    commonest case: in a TWO-portrait strip, "second from left" is an odd way
    to say "on the right", and an ambiguous instruction is how you get the same
    person rendered twice — observed once in a two-cast photo that came back
    with two identical Alexes flanking the child.
    """
    if n == 1:
        return ["in the reference image"]
    if n == 2:
        return ["on the left", "on the right"]
    middles = ["in the middle"] if n == 3 else [
        f"{i}{'nd' if i == 2 else 'rd' if i == 3 else 'th'} from the left"
        for i in range(2, n)]
    return ["on the far left"] + middles + ["on the far right"]


def ensemble_ref_path(cast: list, era: str) -> Path:
    """One reference image holding every cast member's era-appropriate face.

    kontext accepts a single `input_image`, which is why only the first person
    was ever identity-locked. Compositing the sheets side by side turns that
    one slot into as many faces as the photo needs.

    Cached under `cast/_ensembles/` and keyed by cast + era, so a repeat run or
    a `--force` regeneration does not rebuild it.
    """
    key = "-".join(cast) + "-" + era
    out = CAST_DIR / "_ensembles" / f"{key}.png"
    if out.exists():
        return out
    out.parent.mkdir(parents=True, exist_ok=True)
    sheets = [Image.open(cast_ref_path(name, era)).convert("RGB") for name in cast]
    h = max(s.height for s in sheets)
    scaled = [s.resize((int(s.width * h / s.height), h)) for s in sheets]
    strip = Image.new("RGB", (sum(s.width for s in scaled), h), (255, 255, 255))
    x = 0
    for s in scaled:
        strip.paste(s, (x, 0))
        x += s.width
    strip.save(out)
    return out


def cast_note(entry: dict) -> str:
    """Describe the cast the input image cannot lock — everyone after the first.

    Age is computed from the photo's own date rather than stated once, because
    the library spans twelve years and a fixed description would put a
    seven-year-old in a 2014 photo taken before she was born.
    """
    cast = entry.get("cast") or []
    if len(cast) < 2:
        return ""
    year = int(str(entry["datetime"])[:4])
    parts = []
    for name in cast[1:]:
        spec = CAST_DESC.get(name)
        if not spec:
            continue
        born, look = spec
        age = year - born
        who = f"a {age}-year-old" if age >= 13 else f"a child of {age}"
        parts.append(f"{name.title()} is {who}, {look}")
    if not parts:
        return ""
    return " Also in the photo: " + "; ".join(parts) + "."


def build_prompt(entry: dict) -> str:
    style = entry.get("style", "candid-phone")
    suffix = STYLE_SUFFIX.get(style, STYLE_SUFFIX["candid-phone"])
    return f"{entry['scene']}. {suffix}"


def generate_entry(entry: dict, identity: str, force: bool) -> Path:
    out_dir = RAW_ROOT / identity
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{entry['file']}.png"
    if out_path.exists() and not force:
        print(f"[{entry['file']}] exists, skipping")
        return out_path

    cast = entry.get("cast") or []
    scene_text = entry["scene"]
    prompt = build_prompt(entry)

    if scene_text.startswith("COMPOSITE:"):
        rest = scene_text[len("COMPOSITE:") :].strip()
        receipt_rel, _, scene_desc = rest.partition(" ")
        receipt_path = REPO_ROOT / receipt_rel
        if not receipt_path.exists():
            raise RuntimeError(f"[{entry['file']}] receipt not found: {receipt_path}")
        style_suffix = STYLE_SUFFIX.get(entry.get("style", "receipt"), STYLE_SUFFIX["receipt"])
        edit_prompt = (
            "Photograph this exact receipt (keep all printed text, layout, "
            f"and thermal-paper texture identical) as if placed in a real "
            f"scene: {scene_desc.strip()}. {style_suffix}"
        )
        print(f"[{entry['file']}] generating (flux-kontext-pro, receipt composite)...")
        img = replicate_predict(
            FLUX_KONTEXT,
            {
                "prompt": edit_prompt,
                "input_image": image_data_uri(receipt_path),
                "aspect_ratio": "4:3",
                "output_format": "png",
                "safety_tolerance": 2,
            },
        )
    elif not cast:
        print(f"[{entry['file']}] generating (flux-1.1-pro, no cast)...")
        img = replicate_predict(
            FLUX_CREATE,
            {
                "prompt": prompt,
                "aspect_ratio": "4:3",
                "output_format": "png",
                "output_quality": 90,
                "safety_tolerance": 2,
            },
        )
    else:
        primary = cast[0]
        ref_path = cast_ref_path(primary, entry["era"])
        headcount = len(cast)
        if headcount == 1:
            edit_prompt = (
                "This reference photo shows one specific person. Generate a "
                "new candid photo of that exact same person (same face, "
                "same identity) in a different scene. Exactly ONE person in "
                "the frame — no duplicate or second copy of them, no other "
                f"bystanders. Scene: {prompt}"
            )
        else:
            # EVERY cast member goes into the ONE reference image, side by
            # side, and the prompt names them by position.
            #
            # **Describing them in words does not work.** This branch used to
            # pass only the first person's cast sheet and describe the rest
            # from `CAST_SPECS`; a 2026-08 batch then rendered Jonas — Alex's
            # university friend, the same age — as a man in his SIXTIES, in
            # 61 of 86 photos. Adding an explicit "Jonas is a 26-year-old,
            # athletic wiry build" to the prompt changed nothing: kontext is
            # an image-EDITING model, so the input image dominates and text
            # about someone absent from it is weakly weighted. You cannot talk
            # it into a face.
            #
            # Putting both faces in the reference does work (verified before
            # this was written, not after): the same scene came back with both
            # men in their mid-twenties and Jonas matching his sheet.
            #
            # This matters more than it looks: People, Groups and Network all
            # cluster on faces, so a friend who is 60 in one photo and 38 in
            # the next is two different people, and the social graph fragments.
            ref_path = ensemble_ref_path(cast, entry["era"])
            year = int(str(entry["datetime"])[:4])
            places = positions_for(headcount)
            roster = []
            for i, name in enumerate(cast):
                born = CAST_DESC.get(name, (None, ""))[0]
                age = f", aged {year - born}" if born else ""
                roster.append(f"({i + 1}) the person {places[i]}{age}")
            edit_prompt = (
                f"The reference image is a strip of {headcount} separate "
                "portraits, side by side. Put those exact people — same faces, "
                "same identities — together into ONE new candid photograph: "
                + "; ".join(roster) + ". "
                f"EXACTLY {headcount} people in the frame — each of them appears "
                "ONCE, never twice, and there are no bystanders. "
                f"Scene: {prompt}"
            )
        print(f"[{entry['file']}] generating (flux-kontext-pro, cast={cast}, ref={'+'.join(cast) if headcount > 1 else primary})...")
        img = replicate_predict(
            FLUX_KONTEXT,
            {
                "prompt": edit_prompt,
                "input_image": image_data_uri(ref_path),
                "aspect_ratio": "4:3",
                "output_format": "png",
                "safety_tolerance": 2,
            },
        )

    out_path.write_bytes(img)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", default="alex-carter")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--limit", type=int, help="only generate the first N entries (debugging)")
    parser.add_argument("--only", help="comma-separated list of manifest 'file' stems to (re)generate")
    args = parser.parse_args()

    entries = load_manifest(args.manifest)
    if args.only:
        wanted = set(args.only.split(","))
        entries = [e for e in entries if e["file"] in wanted]
    if args.limit:
        entries = entries[: args.limit]

    # **One bad entry must not cost the batch.** A single failed prediction
    # used to raise straight out of the loop: a 95-photo regeneration stopped
    # at 34 because the 35th was refused, and the remaining 60 were never
    # attempted. A generation run costs money and an hour, and the failures are
    # per-entry (a moderation refusal on one scene says nothing about the next
    # one), so collect them and report at the end.
    failed = []
    for i, entry in enumerate(entries):
        try:
            generate_entry(entry, args.identity, args.force)
        except Exception as exc:  # noqa: BLE001 — per-entry isolation is the point
            failed.append((entry["file"], f"{type(exc).__name__}: {exc}"))
            print(f"[{entry['file']}] FAILED — {exc}")
        if i < len(entries) - 1:
            time.sleep(3)

    print(f"Done. {len(entries) - len(failed)}/{len(entries)} entries -> "
          f"{RAW_ROOT / args.identity}")
    if failed:
        # Named, not counted. "3 failed" sends you to the log; the names send
        # you to the cause, and these cluster (every refusal so far has been a
        # scene with the child in it).
        print(f"\n{len(failed)} FAILED — rerun with --only <names> once fixed:")
        for name, why in failed:
            print(f"  {name}: {why}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
