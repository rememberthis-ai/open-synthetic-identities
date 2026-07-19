#!/usr/bin/env python3
"""Generate cast-sheet reference portraits (step 1 of PLAN.md).

One canonical reference portrait per character (flux-1.1-pro), then
kontext-pro age variants so the same face ages across eras. Outputs are the
consistency anchor every later scene generation conditions on — see PLAN.md
"Cast sheets" and CHARACTERS.md for the appearance descriptions.

Model choices, the 429/retry_after loop, and the offline-bundle-via-git-LFS
approach are the house pattern documented in the `genai-game-assets` skill
(augmentedmind/claude-skills) — this script only adds the prompts, the
per-character age list, and the output path.

Usage:
  export REPLICATE_API_TOKEN=...
  python3 gen_cast.py [--character alex|sam|mira] [--force]
"""
import argparse
import time
from pathlib import Path

from replicate_client import FLUX_CREATE, FLUX_KONTEXT, image_data_uri, replicate_predict

OUT_ROOT = Path(__file__).parent / "cast"

PORTRAIT_SUFFIX = (
    "photorealistic portrait photograph, head-and-shoulders, direct gaze at "
    "camera, neutral studio lighting, plain light-gray seamless background, "
    "natural skin texture, 50mm portrait lens look, high detail, no text, "
    "no watermark, no logo, no jewelry brand marks"
)

# Each character: base (flux-1.1-pro) prompt + ordered list of kontext
# variants. Variants are applied in order; `from_` names an already-generated
# file to condition on (defaults to the character's base file) so a chain
# (e.g. Mira aging backward) can condition each step on the previous one.
CHARACTERS = {
    "alex": {
        "base_file": "canonical.png",
        "base_prompt": (
            "A 36-year-old androgynous adult, light-olive skin tone, short "
            "textured dark-brown hair in a low-maintenance side part, warm "
            "brown eyes, slim-average build, calm friendly expression, "
            "wearing a simple charcoal crew-neck sweater, a thin silver ring "
            "on one hand, no other jewelry. " + PORTRAIT_SUFFIX
        ),
        "variants": [
            {
                "file": "age-26.png",
                "prompt": (
                    "Same person, same face, same identity, same eye color "
                    "and skin tone — change apparent age to about 26 years "
                    "old: slightly longer and messier dark-brown hair, "
                    "wearing a plain gray hoodie, fresh-faced student "
                    "energy. Keep facial structure identical. "
                    + PORTRAIT_SUFFIX
                ),
            },
            {
                "file": "age-29.png",
                "prompt": (
                    "Same person, same face, same identity, same eye color "
                    "and skin tone — change apparent age to about 29 years "
                    "old: short neat dark-brown hair, wearing a plain "
                    "olive-green crewneck, calm new-city minimalism. Keep "
                    "facial structure identical. " + PORTRAIT_SUFFIX
                ),
            },
            {
                "file": "age-32.png",
                "prompt": (
                    "Same person, same face, same identity, same eye color "
                    "and skin tone — change apparent age to about 32 years "
                    "old: practical low-effort hairstyle, wearing a soft "
                    "oatmeal cardigan, a touch of new-parent tiredness "
                    "around the eyes but still warm. Keep facial structure "
                    "identical. " + PORTRAIT_SUFFIX
                ),
            },
            {
                "file": "age-35.png",
                "prompt": (
                    "Same person, same face, same identity, same eye color "
                    "and skin tone — change apparent age to about 35 years "
                    "old: confident close-cropped modern haircut, wearing a "
                    "structured charcoal blazer over a plain tee, "
                    "professional but relaxed. Keep facial structure "
                    "identical. " + PORTRAIT_SUFFIX
                ),
            },
            {
                "file": "age-38.png",
                "prompt": (
                    "Same person, same face, same identity, same eye color "
                    "and skin tone — change apparent age to about 38 years "
                    "old: faint gray fleck at the temples, relaxed but "
                    "polished, wearing a light gray-green weatherproof "
                    "outdoor jacket over a tee. Keep facial structure "
                    "identical. " + PORTRAIT_SUFFIX
                ),
            },
        ],
    },
    "sam": {
        # Sam's canonical IS the current-day (2026, age 38) look — Sam only
        # appears from 2017 onward, so "now" is the natural identity anchor
        # and every variant kontexts backward from it.
        "base_file": "canonical.png",
        "base_prompt": (
            "A 38-year-old adult, warm dark-brown skin tone, natural black "
            "hair worn in short locs, round tortoiseshell glasses, kind "
            "expressive eyes, average-tall build, easy warm smile, wearing "
            "a soft rust-orange knit cardigan over a plain shirt, subtle "
            "gray fleck at the temples. " + PORTRAIT_SUFFIX
        ),
        "variants": [
            {
                "file": "age-35.png",
                "prompt": (
                    "Same person, same face, same identity, same eye color "
                    "and skin tone, same glasses — change apparent age to "
                    "about 35 years old: established short locs, no gray "
                    "yet, wearing a smart-casual olive cardigan, confident "
                    "classroom-ready look. Keep facial structure identical. "
                    + PORTRAIT_SUFFIX
                ),
            },
            {
                "file": "age-32.png",
                "prompt": (
                    "Same person, same face, same identity, same eye color "
                    "and skin tone, same glasses — change apparent age to "
                    "about 32 years old: locs just starting to grow in "
                    "(shorter than the reference), tired-happy new-parent "
                    "expression, wearing a plain gray sweater. Keep facial "
                    "structure identical. " + PORTRAIT_SUFFIX
                ),
            },
            {
                "file": "age-29.png",
                "prompt": (
                    "Same person, same face, same identity, same eye color "
                    "and skin tone — change apparent age to about 29 years "
                    "old: simple short natural hair (no locs yet), plain "
                    "round glasses, casual teacher-in-training look, "
                    "wearing a plain cotton shirt. Keep facial structure "
                    "identical. " + PORTRAIT_SUFFIX
                ),
            },
        ],
    },
    "mira": {
        # Mira ages fast and a school-age face carries more identity signal
        # than a newborn's, so generate the current (2026, age 7) look
        # directly and chain the kontext de-aging backward: 7 -> 4 -> 2 -> 0,
        # each step conditioned on the previous (not all from age-7) so the
        # progression stays plausible.
        "base_file": "age-7.png",
        "base_prompt": (
            "A 7-year-old child, light-brown skin tone, dark curly hair in "
            "twin puffs, bright dark eyes, warm expressive face blending "
            "mixed-heritage features, easy confident smile with a gap where "
            "a baby tooth is missing, wearing a simple striped t-shirt. "
            + PORTRAIT_SUFFIX
        ),
        "variants": [
            {
                "file": "age-4.png",
                "from_": "age-7.png",
                "prompt": (
                    "Same child, same face, same identity, same skin tone "
                    "and hair texture — change apparent age to about 4 "
                    "years old: rounder toddler-to-child face, "
                    "shoulder-length curls in twin puffs, playful "
                    "preschooler expression, full set of baby teeth "
                    "showing in the smile. " + PORTRAIT_SUFFIX
                ),
            },
            {
                "file": "age-2.png",
                "from_": "age-4.png",
                "prompt": (
                    "Same child, same face, same identity, same skin tone "
                    "and hair texture — change apparent age to about 2 "
                    "years old: chubby-cheeked toddler, small dark curl "
                    "puffs, curious wide-eyed expression, simple onesie. "
                    + PORTRAIT_SUFFIX
                ),
            },
            {
                "file": "age-0.png",
                "from_": "age-2.png",
                "prompt": (
                    "Same child, same identity, same skin tone and hair "
                    "texture — change apparent age to a newborn, a few "
                    "weeks old: swaddled in a plain white blanket, wisps of "
                    "dark curly hair, soft sleepy newborn-portrait "
                    "expression, minimal facial definition as is natural "
                    "for a newborn. " + PORTRAIT_SUFFIX
                ),
            },
        ],
    },
    # Minimal single-look entries — only the "balance" era (2025-2026)
    # portrait each pilot-slice manifest entry needs. Full age progressions
    # (matching their real appearance spans) are deferred to the post-pilot
    # cast-sheet pass per PLAN.md sequencing; see CHARACTERS.md.
    "jonas": {
        "base_file": "age-38.png",
        "base_prompt": (
            "A 38-year-old adult, tanned sun-weathered skin from outdoor "
            "climbing, short practical dark-blonde hair, athletic wiry "
            "build, easygoing warm expression, light stubble, wearing a "
            "faded green outdoor softshell jacket. " + PORTRAIT_SUFFIX
        ),
        "variants": [],
    },
    "priya": {
        "base_file": "age-36.png",
        "base_prompt": (
            "A 36-year-old adult, deep-brown skin tone, sleek dark hair in "
            "a low bun, sharp confident professional expression, wearing a "
            "tailored charcoal blazer over a cream blouse, small gold stud "
            "earrings. " + PORTRAIT_SUFFIX
        ),
        "variants": [],
    },
}


def generate_character(name: str, spec: dict, force: bool) -> None:
    out_dir = OUT_ROOT / name
    out_dir.mkdir(parents=True, exist_ok=True)

    base_path = out_dir / spec["base_file"]
    if base_path.exists() and not force:
        print(f"[{name}] {base_path.name} exists, skipping")
    else:
        print(f"[{name}] generating base {base_path.name} (flux-1.1-pro)...")
        img = replicate_predict(
            FLUX_CREATE,
            {
                "prompt": spec["base_prompt"],
                "aspect_ratio": "1:1",
                "output_format": "png",
                "output_quality": 90,
                "safety_tolerance": 2,
            },
        )
        base_path.write_bytes(img)
        time.sleep(3)

    for variant in spec["variants"]:
        out_path = out_dir / variant["file"]
        if out_path.exists() and not force:
            print(f"[{name}] {out_path.name} exists, skipping")
            continue
        ref_name = variant.get("from_", spec["base_file"])
        ref_path = out_dir / ref_name
        if not ref_path.exists():
            raise RuntimeError(
                f"[{name}] {variant['file']} needs reference {ref_name}, "
                "which hasn't been generated yet (run without --force first, "
                "or fix the variant order)"
            )
        print(f"[{name}] generating {out_path.name} (flux-kontext-pro, from {ref_name})...")
        img = replicate_predict(
            FLUX_KONTEXT,
            {
                "prompt": variant["prompt"],
                "input_image": image_data_uri(ref_path),
                "output_format": "png",
                "safety_tolerance": 2,
            },
        )
        out_path.write_bytes(img)
        time.sleep(3)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--character", choices=list(CHARACTERS.keys()), help="generate only this character")
    parser.add_argument("--force", action="store_true", help="regenerate even if the output file exists")
    args = parser.parse_args()

    names = [args.character] if args.character else list(CHARACTERS.keys())
    for name in names:
        generate_character(name, CHARACTERS[name], args.force)

    print("Done. Cast sheets in", OUT_ROOT)


if __name__ == "__main__":
    main()
