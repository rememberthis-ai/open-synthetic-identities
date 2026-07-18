# Open Synthetic Identities

Fictional, fully synthetic example data for [Remember This](https://rememberthis.ai),
[My Transcriber](https://mytranscriber.app), and [Clerk.AI](https://clerkai.eu).

Every person, merchant, bank, company, and event in this dataset is **invented**. No
real personal data, no real brands, no real financials. That makes it safe to use for:

- **Screenshots, screencasts, and demos** — see the apps working on a realistic life
  without exposing anyone's actual one.
- **Bug reports** — reproduce an issue against a demo identity instead of your own
  vault, and share the repro publicly ("fails on `alex-carter` after seeding").
- **Trying the apps** — seed a demo identity and explore with data already in place.
- **Benchmarks** — the [local-ai-benchmarks](https://github.com/rememberthis-ai/local-ai-benchmarks)
  harness is moving to these identities as its standard corpus, so published numbers
  are reproducible against public data.

## Layout

```
open-synthetic-identities/
  identities/
    alex-carter/          # the primary demo identity (see PERSONA.md)
      PERSONA.md          # the persona bible: who they are, cast, timeline, business
  generate/               # scripts that produce fixtures (regeneratable)
    gen_receipts.py       # renders synthetic receipt images (thermal-paper style)
    gen_statement_csv.py  # generates bank-statement CSVs matching the receipts
    voice-scripts/        # fictional voice-memo scripts (English + multilingual set)
  fixtures/
    clerkai/              # receipts (PNG), statements (CSV), period-close run state
    transcriber/          # audio fixtures + expected transcripts
    rememberthis/         # photo-set manifest, memo fixtures, Life Book states
  shots/                  # per-brand screenshot shot-list manifests (capture rig)
```

## Principles

1. **Fictional everything.** Merchants like "Brew & Bean" and "Nimbus Cloud Hosting"
   exist only here. The persona's bank is a fictional pan-EU fintech. Faces in photos
   (when the photo set lands) are AI-generated characters that do not exist.
2. **English-first, multilingual by design.** The persona operates in English; a
   dedicated fixture subset is in Swedish, Finnish, German, and Spanish to exercise
   (and demonstrate) multi-language transcription and receipt OCR.
3. **Regeneratable.** Fixtures are committed for stability, but every fixture family
   has a generator under `generate/`. Want a second demo identity? Copy
   `identities/alex-carter/PERSONA.md`, change the facts, re-run the generators with
   `--identity your-new-persona`.
4. **Deterministic.** Generators take a `--seed`; the committed fixtures use seed 42.
   Dates are anchored to the demo epoch (**2026-06-30**) so period pickers, timelines,
   and relative dates stay coherent with the apps' `DEMO_MODE` pinned clock.

## Generating more data

```bash
cd generate
python3 gen_receipts.py --identity alex-carter --month 2026-06 --seed 42 \
  --out ../fixtures/clerkai/receipts
python3 gen_statement_csv.py --identity alex-carter --month 2026-06 --seed 42 \
  --out ../fixtures/clerkai/statements
```

Voice fixtures: scripts in `generate/voice-scripts/` are read by TTS (any engine) or a
human voice actor; drop the audio into the app via its drop folder or CLI
(`transcriber transcribe <file>`) to produce indexed fixtures.

## Adding a demo identity

1. Write a `PERSONA.md` (copy alex-carter's as a template): identity, cast of
   recurring people, era timeline, business shape, banks/merchants.
2. Add the persona's merchant/transaction tables to the generators (one dict each).
3. Regenerate with your identity flag. Keep everything fictional — that's the deal
   that lets this dataset stay public.
