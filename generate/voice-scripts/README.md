# Voice-memo scripts

Fictional scripts for the alex-carter demo identity. Read them with any TTS engine or
a human voice; import the audio via the app's drop folder or
`transcriber transcribe <file>`. File naming: `<lang>-<slug>.md`, one memo per file,
the H1 is the memo's custom title (exercises title sync).

## Who speaks what

There are **two kinds of memo**, and the kind decides the language:

1. **Alex dictating a note to self → always English.** Alex is British; a
   note-to-self is in English wherever it was recorded. It is *not* in Finnish
   because the trip happened to be to Helsinki.
2. **Alex recording a meeting/conversation held in another language → that
   language, spoken by the other party.** You record it precisely *because* you
   want to transcribe and process it afterwards — which is the product's actual use
   case, and the honest reason a real recording library ends up multilingual. The
   title stays in Alex's own words (English), because Alex is the one naming the
   recording.

So: three English notes-to-self, Sam's German note about Mira's Berlin school, and a
recording of the German tax-advisor meeting (Herr Fischer talking, English title).

**Never put a memo in a language its speaker doesn't speak.** Earlier versions had
Alex dictating to themselves in Swedish/Finnish/Spanish because a trip went there,
then foreign clients leaving Alex voicemail Alex couldn't understand — both read as
bugs. Multilingual OCR is showcased by the receipts instead
(`fixtures/clerkai/receipts/`, five languages, entirely natural). More ASR languages
should come from recordings of meetings genuinely held in them, or a second identity.

Speaker → voice mapping lives in `../tts_voice_scripts.sh` and
`fixtures/transcriber/audio/README.md`; keep the three in sync when adding a memo.
