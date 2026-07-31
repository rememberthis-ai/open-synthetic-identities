# Cast sheets

Generated reference portraits — the identity-consistency anchor every scene
generation conditions on via `flux-kontext-pro`. See `../PLAN.md` ("Cast
sheets" section) for the mechanism and `../CHARACTERS.md` for the appearance
descriptions/era-styling notes behind each prompt. Regenerate with
`../gen_cast.py` (idempotent — skips files that already exist unless
`--force`).

## Status

| Character | Files | Notes |
|---|---|---|
| **alex** | `canonical.png` (age ~36 reference) + `age-{26,29,32,35,38}.png` | one variant per era |
| **sam** | `canonical.png` (= `age-38`, current-day) + `age-{29,32,35}.png` | Sam only appears from 2017 on, so "now" is the anchor; variants kontext backward |
| **mira** | `age-{0,2,4,7}.png` (no separate canonical — `age-7` is the base) | chained newest→oldest (7→4→2→0); a school-age face carries more identity signal than a newborn's, and each step conditions on the previous, not all on age-7 |
| jonas, priya, rosa | not yet generated | after alex/sam/mira, per PLAN.md sequencing |

14 images total (3 base `flux-1.1-pro` calls + 11 `flux-kontext-pro` age
variants), 1024×1024 PNG.

## Regenerating

```bash
export REPLICATE_API_TOKEN=...   # house key, service `augmentedmind-genai`
                                   # in the keychain — see genai-game-assets skill
python3 gen_cast.py                        # all three characters
python3 gen_cast.py --character alex        # one character
python3 gen_cast.py --character mira --force  # force regen even if files exist
```

Cast sheets are the consistency anchor — treat as frozen once scenes start
referencing them (per PLAN.md). Regenerate only when a character's look
must change, and expect every scene depending on that character to need
regeneration too.
