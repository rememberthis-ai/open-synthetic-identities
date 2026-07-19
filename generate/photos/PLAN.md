# Photo & metadata generation plan

Full pipeline for generating each identity's photo library — images, EXIF timestamps,
GPS coordinates, and per-era camera metadata — so the apps' timeline, era detection,
people clustering, places, and receipt-OCR features all work on fully synthetic data,
and every marketing asset can be produced from it.

Generation stack: Replicate Flux — `flux-1.1-pro` (create), `flux-kontext-pro`
(identity-preserving variations — the mechanism for keeping recurring characters
consistent across years), `background-remover` (alpha when compositing). Build-time
generation, outputs committed via git LFS, API keys stay in env (never committed).

## Identity roster

| Identity | Role | Photo volume | Status |
|---|---|---|---|
| **alex-carter** | primary/hero — all three apps, all marketing assets | ~450 photos, 2014–2026 | planned below |
| **sam-okafor** | secondary household member — multi-identity features, shared-folder/team stories | ~60 photos (overlapping events shot "from Sam's phone") | after alex |
| **test-minimal** | tiny smoke identity for bug repros & CI | ~12 photos, 1 era | after alex |

## Cast sheets (step 1 — everything depends on these)

One **canonical reference portrait per character** (flux-1.1-pro, neutral lighting,
head-and-shoulders), then **age variants** via flux-kontext-pro so the same face ages
across eras. Committed under `generate/photos/cast/<character>/`:

```
cast/alex/canonical.png        # age ~36 reference
cast/alex/age-26.png ... age-38.png   # kontext age variants, one per era
cast/mira/age-0.png age-2.png age-4.png age-7.png   # child ages fast — one per ~2y
cast/sam/..., cast/jonas/..., cast/priya/..., cast/rosa/...
```

Every scene image that includes a character is generated with kontext against that
character's era-appropriate variant. Cast sheets are regenerated **only** when a
character's look must change — they are the consistency anchor; treat as frozen.

**Status: alex/sam/mira generated** (`generate/photos/gen_cast.py`, appearance
descriptions in `generate/photos/CHARACTERS.md`, status detail in
`generate/photos/cast/README.md`). Jonas/Priya/Rosa not yet generated — next in
sequence once the pilot slice (below) verifies the mechanism end-to-end.

## Scene manifests (step 2 — the dataset spec)

One YAML manifest per identity at `generate/photos/manifests/<identity>.yaml`. Each
entry fully determines one photo — the manifest IS the dataset; images are derived.

```yaml
# schema
- file: 2019-03-12-berlin-mira-newborn-01   # output stem; .heic-era naming applied by stamper
  era: mira-arrives                          # must match PERSONA.md era slugs
  datetime: 2019-03-12T14:22:00+01:00        # local time; stamper writes EXIF DateTimeOriginal
  location: { name: "Charité, Berlin", lat: 52.5236, lon: 13.3782 }   # public place; stamper writes GPS
  camera: iphone-xs                          # resolved via the camera table below
  cast: [alex, sam, mira]                    # characters present → kontext identity refs
  scene: "hospital room, new parents holding newborn, soft window light, candid"
  style: candid-phone                        # candid-phone | posed | landscape | receipt | screenshot-free
```

Per-era targets for **alex-carter** (~450 total):

| Era | Years | Photos | Locations (GPS anchors) | Notes |
|---|---|---|---|---|
| manchester | 2014–2016 | 60 | Manchester city/uni, Peak District climbing | uni friends + Jonas appears |
| berlin-move | 2016–2018 | 70 | Kreuzberg/Mitte, Mauerpark; Sam appears mid-2017 | new-city texture, café/work shots |
| mira-arrives | 2019–2021 | 100 | Berlin home/parks, Manchester visits (Rosa) | family density peak, fewer trips |
| carter-studio | 2022–2024 | 110 | Werkraum co-working, Amsterdam + Lisbon conferences | workspace, client dinners w/ Priya |
| balance | 2025–2026 | 90 | Berlin, Frankenjura climbing, Helsinki + Stockholm + Madrid work trips | ties into receipts/statement cities |
| receipts | 2026-06 | ~20 | the June merchants' cities | see receipt-photos below |

Density matters as much as count: cluster photos into believable bursts (a weekend
trip = 8–12 shots over 2 days, then gaps) — era detection and Journal-style grouping
read gaps as signal.

## Camera-per-era table (EXIF Make/Model + resolution)

The registry indexes `device_make`/`device_model` (schema v18), and real libraries
show phone upgrades — so the demo library has them:

| Years | Model (EXIF) | Resolution | Aspect |
|---|---|---|---|
| 2014–2016 | Apple iPhone 5s | 3264×2448 | 4:3 |
| 2016–2018 | Apple iPhone 7 | 4032×3024 | 4:3 |
| 2019–2021 | Apple iPhone XS | 4032×3024 | 4:3 |
| 2022–2024 | Apple iPhone 13 Pro | 4032×3024 | 4:3 |
| 2025–2026 | Apple iPhone 15 Pro | 4032×3024 (+ some 48MP) | 4:3 |

Generate at model-native aspect (Flux supports arbitrary AR), upscale/downscale to
the table's resolution at stamping time. A light era-grade (subtle color/grain LUT
per era) sells "old photo" without faking damage.

## EXIF/GPS stamping (step 3 — `stamp_exif.py`, to be written)

For each manifest entry: write `DateTimeOriginal`/`CreateDate` (+ correct `OffsetTime`
for the location's timezone), `GPSLatitude/Longitude`, `Make`/`Model`, and a
deterministic `ImageUniqueID` derived from the manifest stem (idempotent re-runs).
Tooling: `exiftool` (preferred) or `piexif`. GPS coordinates are real public places
(parks, streets, venues) — locations aren't personal data, and real coords make
reverse-geocoding and the apps' Places features resolve to believable names.

## Receipt-photos subset (Clerk.AI)

The rendered thermal receipts in `fixtures/clerkai/receipts/` look like scans. For
the photo library (Clerk discovers receipts via OCR over Photos), composite each
June receipt into a **photographed context** via kontext: receipt on a café table /
held in hand / on a car seat, slight perspective and shadow, phone-camera framing.
EXIF datetime = minutes after the receipt's own timestamp, GPS = the merchant's city
anchor. ~20 images. OCR must still read them — verify with the app's OCR pass before
committing the batch.

## Pipeline (end to end)

```
manifest.yaml ──▶ generate.py ──▶ raw/ (per-entry PNG, kontext w/ cast refs)
                         │
                         ▼
                  stamp_exif.py ──▶ library/<identity>/<era>/*.jpg (EXIF+GPS+model, LFS)
                         │
                         ▼ (per demo machine)
                  osxphotos import --exportdb ... ──▶ demo macOS account's Photos library
                         │
                         ▼
                  apps index via PhotoKit ──▶ verify checklist
```

- `generate.py`: reads manifest, calls Replicate (flux-1.1-pro for cast-free scenes,
  kontext with cast refs otherwise), standard 429/`retry_after` backoff, resumable
  (skips entries whose output exists unless `--force`).
- Committed artifacts: `library/` (final JPEGs, LFS) + `cast/` (LFS). `raw/` is
  gitignored scratch.
- Import into Photos on the demo account via `osxphotos import` (keeps EXIF dates/
  GPS). One manual step, documented: naming the People clusters in Photos once
  (Photos does its own face clustering on our consistent cast — that's the goal).

## Verification checklist (per identity, after import + index)

- [ ] Timeline spans 2014→2026 with believable density and gaps
- [ ] Era detection produces ~the 5 planned eras (Life Book picker)
- [ ] Photos People clustering groups each cast member (then name them once)
- [ ] Places resolve to Manchester/Berlin/Amsterdam/Lisbon/Helsinki/… via geocoding
- [ ] device_make/model distribution matches the camera table
- [ ] Clerk OCR finds the ~20 photographed receipts; curation panel thumbnails look right
- [ ] No real person/brand visible in any image (spot-check the full set)

## Cost & effort estimate

~450 scenes + ~40 cast-sheet images + ~20 receipt composites ≈ 510 generations, most
with one kontext pass ⇒ ~800–1000 model calls. At current Replicate Flux pricing
(~$0.04–0.06/image) ≈ **$35–60 per full regeneration** of alex-carter. Wall-clock: an
evening with the resumable generator. Cheap enough to iterate; still — iterate on
10-entry manifest slices before running full eras.

## Sequencing

1. **Done** — Cast sheets (alex + sam + mira, plus pilot-minimal single looks
   for jonas + priya). `generate/photos/cast/`, `CHARACTERS.md`.
2. **Done (this repo's scope)** — 10-photo pilot slice (`generate.py` +
   `stamp_exif.py` → `generate/photos/library/alex-carter/`). Look + EXIF/GPS/
   camera metadata verified; `osxphotos import` + app indexing verification
   still needs the demo macOS account (private monorepo, not yet set up) —
   see `generate/photos/library/README.md` for exactly what's
   verified vs. not.
3. Full alex-carter era batches + receipt subset → verification checklist
4. sam-okafor overlap set, test-minimal
5. Hand off to the marketing-assets capture rig (private monorepo,
   `docs/plans/MARKETING-ASSETS.md`)
