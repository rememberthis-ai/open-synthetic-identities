#!/usr/bin/env python3
"""Contact sheet of every cast sheet, one row per character.

# Why this is a standing check and not a one-off

The cast sheets are the only thing holding a persona's face together: every
generated photo is conditioned on one, so a sheet that drifts silently rewrites
who a character IS for a whole era. There is no way to notice from the manifest,
the generator's output, or the EXIF — all of which will look perfect.

Found 2026-08, after ~40 photos had been generated from them:

- `alex/age-32.png` was **a woman**. That is the `mira-arrives` era, 2019–2021.
- `alex/age-35.png` was **a different man** — fair-skinned, cropped hair. That is
  `carter-studio`, 2022–2024.

Both were produced by prompts that said *"Same person, same face, same
identity"*. kontext drifts anyway when the variant prompt asks for a strong
appearance change, and Alex's base prompt says "androgynous", which gave it
latitude on gender. The give-aways were wardrobe cues: a "soft oatmeal cardigan"
took age-32 female, a "confident close-cropped haircut, structured blazer" took
age-35 to a different man. Anchoring each variant on the nearest GOOD sheet
rather than on the canonical, and dropping the wardrobe cue, fixed both.

The cost of not checking: the protagonist has two faces, so People and Groups
cluster him as two people and Life Book era detection sees a stranger appear.
Every one of those photos looked fine individually — the defect only exists
across images, which is exactly what a contact sheet shows and nothing else does.

**Run this after generating or regenerating any cast sheet, and read it.** The
question it answers is not "did it render" but "is this the same person in every
frame of the row".

Usage:
  python3 check_cast.py [--open]
"""
import argparse
import pathlib

from PIL import Image, ImageDraw

HERE = pathlib.Path(__file__).parent
CAST = HERE / "cast"
THUMB = 300


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/tmp/cast-contact.png")
    ap.add_argument("--open", action="store_true", help="reveal it when done")
    args = ap.parse_args()

    chars = [d for d in sorted(CAST.iterdir()) if d.is_dir() and not d.name.startswith("_")]
    rows = [(d.name, sorted(d.glob("*.png"))) for d in chars]
    rows = [(n, s) for n, s in rows if s]
    if not rows:
        raise SystemExit(f"no cast sheets under {CAST}")

    width = max(len(s) for _, s in rows) * THUMB + 150
    out = Image.new("RGB", (width, len(rows) * (THUMB + 22)), (255, 255, 255))
    draw = ImageDraw.Draw(out)
    for r, (name, sheets) in enumerate(rows):
        y = r * (THUMB + 22)
        draw.text((8, y + THUMB // 2), name, fill=(0, 0, 0))
        for c, sheet in enumerate(sheets):
            im = Image.open(sheet).convert("RGB").resize((THUMB, THUMB))
            out.paste(im, (150 + c * THUMB, y))
            draw.text((154 + c * THUMB, y + THUMB + 4), sheet.stem, fill=(0, 0, 0))
    out.save(args.out)
    print(f"wrote {args.out} — {len(rows)} characters, "
          f"{sum(len(s) for _, s in rows)} sheets")
    print("Look along each row: it must be ONE person at different ages.")
    if args.open:
        import subprocess
        subprocess.run(["open", args.out], check=False)


if __name__ == "__main__":
    main()
