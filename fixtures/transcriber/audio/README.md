# Transcriber audio fixtures

Synthetic voice memos for the `alex-carter` demo identity, TTS-rendered from
the scripts in `generate/voice-scripts/`. Regenerate with
`generate/tts_voice_scripts.sh` (macOS only — uses the built-in `say` command).

Every file is a fictional voice memo: the words are spoken by a synthetic
voice, but the *content* (people, dates, amounts, places) is entirely
invented, per the dataset's fictional-everything rule.

## Engine

macOS `say`, System Voices (no Siri/Premium voice download required), `-r 175`
(words per minute), rendered directly to AAC-in-M4A
(`--file-format=m4af --data-format=aac`) — the same container Apple Voice
Memos and the app's own recordings use. This is a v1 placeholder tier; nothing
stops a future pass from swapping in ElevenLabs/Kokoro or a human read using
the same file names.

## Voice-per-speaker mapping

Two recurring "voices" across the set, matching who the script's memo is
attributed to (see `generate/voice-scripts/README.md` and PERSONA.md):

| Speaker | Voice | Locale | Scripts |
|---|---|---|---|
| Alex Carter | Daniel | en_GB | `en-northlight-debrief`, `en-expense-context-lunch`, `en-climbing-trip` |
| Alex Carter | Alva | sv_SE | `sv-kvitto-stockholm` |
| Alex Carter | Satu | fi_FI | `fi-helsinki-muistiinpano` |
| Alex Carter | Mónica | es_ES | `es-idea-viaje` |
| Sam Okafor | Anna | de_DE | `de-mira-schulausflug` |

Alex's English memos use a single consistent voice (Daniel, en_GB — matches
Alex's Manchester origin per the era timeline). The sv/fi/es business-trip
notes are also Alex's, but macOS TTS voices are per-locale, so the "same
character, different language" story is necessarily told with a different
voice per language rather than one voice speaking four languages. The German
memo is explicitly Sam's dictation (per PERSONA.md), so it gets its own voice
throughout, not just for this file.

## Files

Each script produces a pair:
- `<slug>.m4a` — the rendered audio.
- `<slug>.expected.txt` — the exact text that was spoken (the script's body,
  minus its H1 title — the title is metadata for title-sync, not spoken).
  Use this as the ground truth when checking transcription accuracy; a good
  transcriber should land close to this modulo punctuation/number formatting.

Import via the app's drop folder or `transcriber transcribe <file>` (CLI) to
produce indexed fixtures inside a vault.
