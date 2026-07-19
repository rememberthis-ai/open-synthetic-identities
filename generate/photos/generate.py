#!/usr/bin/env python3
"""Generate scene photos from a manifest (step 2 of PLAN.md's pipeline).

Reads generate/photos/manifests/<identity>.yaml, calls Replicate
flux-1.1-pro (no cast) or flux-kontext-pro (with cast, conditioned on the
era-appropriate cast-sheet file(s) in generate/photos/cast/), writes raw
PNGs to generate/photos/raw/<identity>/ (gitignored scratch, per PLAN.md's
pipeline diagram — stamp_exif.py turns these into the committed library/).

Cast handling (v1 limitation — flux-kontext-pro takes ONE input_image):
single-cast scenes kontext off that character's cast-sheet file directly.
Multi-cast scenes kontext off the FIRST-listed character (pixel-identity
locked) and describe any other characters in the prompt text only (not
pixel-identity locked). Good enough to verify the pipeline mechanism on the
10-photo pilot; revisit (e.g. a second kontext pass, or an inpainting step)
if multi-person identity fidelity matters once full eras are generated.

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
    "manchester": {"alex": "age-26.png"},
    "berlin-move": {"alex": "age-29.png", "sam": "age-29.png"},
    "mira-arrives": {"alex": "age-32.png", "sam": "age-32.png", "mira": "age-2.png"},
    "carter-studio": {"alex": "age-35.png", "sam": "age-35.png", "mira": "age-4.png"},
    "balance": {
        "alex": "age-38.png",
        "sam": "age-38.png",
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
            other_descriptions = []
            for name in cast[1:]:
                spec = CAST_SPECS.get(name)
                desc = spec["base_prompt"].replace(PORTRAIT_SUFFIX, "").strip(" ,.") if spec else name
                other_descriptions.append(f"{name} ({desc})")
            others_text = "; ".join(other_descriptions)
            edit_prompt = (
                "This reference photo shows one specific person — call them "
                "the reference person. Generate a new candid photo with "
                f"EXACTLY {headcount} people in the frame, no more, no "
                "bystanders, no duplicates: (1) the reference person, same "
                f"face, same identity; and (2) {others_text}. "
                f"Scene: {prompt}"
            )
        print(f"[{entry['file']}] generating (flux-kontext-pro, cast={cast}, ref={primary})...")
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

    for i, entry in enumerate(entries):
        generate_entry(entry, args.identity, args.force)
        if i < len(entries) - 1:
            time.sleep(3)

    print(f"Done. {len(entries)} entries -> {RAW_ROOT / args.identity}")


if __name__ == "__main__":
    main()
