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

One voice per speaker (see `generate/voice-scripts/README.md` and PERSONA.md):

| Speaker | Voice | Locale | Scripts | Kind |
|---|---|---|---|---|
| Alex Carter | Daniel | en_GB | `en-northlight-debrief`, `en-expense-context-lunch`, `en-climbing-trip` | dictated note |
| Herr Fischer (tax advisor) | Reed | de_DE | `de-steuerberater-termin` | meeting Alex recorded |
| Sam Okafor (partner) | Anna | de_DE | `de-mira-schulausflug` | dictated note |

**Two kinds of memo, and the kind decides the language.** Alex *dictating* a
note to self is always English — Alex is British, and a note-to-self doesn't
change language with the departure gate. Alex *recording a meeting* held in
German is German, because that's what was said in the room; you record it
precisely so you can transcribe and review it later. Alex has lived in Berlin
since 2016, so German meetings are routine; Sam lives and teaches there.

Note the deliberate split on the tax-advisor file: **German audio, English
title** ("Tax advisor meeting — Herr Fischer"). Alex named the recording;
Herr Fischer supplied the content. That combination is realistic and it
exercises title-vs-content language independence in the apps.

**What this set deliberately does NOT do:** an earlier version had Alex
dictating notes-to-self in Swedish, Finnish and Spanish purely because a
business trip went there, and a later revision had foreign clients leaving
Alex voicemail in languages Alex can't understand. Both were incoherent.
**Multilingual OCR is showcased instead by the receipts** (`fixtures/clerkai/
receipts/` — Finnish, Swedish, Spanish and German merchants print in their own
language, which is exactly what a traveller's receipt pile looks like).
Broader multi-language ASR should come from a second identity whose speakers
genuinely use those languages — not from making Alex a polyglot.

## Files

Each script produces a pair:
- `<slug>.m4a` — the rendered audio.
- `<slug>.expected.txt` — the exact text that was spoken (the script's body,
  minus its H1 title — the title is metadata for title-sync, not spoken).
  Use this as the ground truth when checking transcription accuracy; a good
  transcriber should land close to this modulo punctuation/number formatting.

Import via the app's drop folder or `transcriber transcribe <file>` (CLI) to
produce indexed fixtures inside a vault.
