# Photo library — committed, EXIF-stamped output

The final artifact of PLAN.md's pipeline: `generate.py` (scene generation
via Replicate Flux, conditioned on `cast/`) → `stamp_exif.py` (EXIF/GPS/
camera metadata + resize to the camera table's resolution) → here.
`raw/` (pre-stamp PNGs) is gitignored scratch; this directory is the
committed, LFS-tracked artifact.

Layout: `library/<identity>/<era>/<file>.jpg` — era matches the manifest
entry's `era` field (and PERSONA.md's era slugs).

## Status: 10-photo pilot slice (alex-carter)

The pilot manifest (`manifests/alex-carter.yaml`, 10 entries) is fully
generated and stamped — this is step 2 of PLAN.md's sequencing ("10-photo
pilot slice (one era) → verify look, EXIF, import, indexing end-to-end").

**Verified so far (this repo's scope):**
- [x] Every manifest entry produces a stamped JPEG at the correct camera
      resolution (4032×3024 for iphone-15-pro) with correct
      DateTimeOriginal/OffsetTime, GPS, Make/Model, and a deterministic
      ImageUniqueID.
- [x] Cast consistency: single-subject scenes kontext cleanly off the cast
      sheet with no duplicate people. Multi-subject scenes (2 people) hold
      the correct headcount after a prompt fix (see "Known limitations").
- [x] The receipt-photo composite (Clerk.AI subset) reproduces the source
      receipt's printed text/amount faithfully in a photographed context.

**Not verified (needs the demo macOS account, out of scope for this public
repo — see `docs/plans/MARKETING-ASSETS.md` Track 2 item 3 in the private
monorepo):** `osxphotos import` into a Photos library, PhotoKit/app
indexing, era/people-clustering detection. That's an app-side verification
step for whoever runs the demo-account setup next.

## Known limitations (v1, documented in generate.py)

- **flux-kontext-pro takes one `input_image`.** Multi-cast scenes kontext
  off the first-listed character (pixel-identity-locked); any other listed
  characters are described in the prompt text only, pulled from
  `CHARACTERS.md`/`gen_cast.py`'s descriptions — not pixel-identity-locked.
  In practice this reads as "clearly the right person" for the primary and
  "plausible for the role" for others, not perfect likeness. Revisit (e.g. a
  second kontext pass, or inpainting) if full-era generation needs tighter
  multi-person fidelity.
- **Jonas and Priya are pilot-minimal** — one look each (`cast/jonas/age-38.png`,
  `cast/priya/age-36.png`), not a full era-spanning age progression. Fine for
  this slice (both only appear in "balance"-era entries); generate their
  full progressions before any era batch that needs them at a different age.
- No era color-grade/grain LUT applied yet (PLAN.md calls this optional
  polish, not required for the pilot).

## Regenerating

```bash
export REPLICATE_API_TOKEN=...
python3 generate.py --manifest manifests/alex-carter.yaml     # -> raw/ (scratch)
python3 stamp_exif.py --manifest manifests/alex-carter.yaml   # -> library/ (committed)
```

Both scripts are resumable (skip existing output unless `--force`) and
support `--only file-stem-1,file-stem-2` for targeted regeneration.
