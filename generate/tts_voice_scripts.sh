#!/usr/bin/env bash
# Render generate/voice-scripts/*.md into fixtures/transcriber/audio/ via macOS `say`.
#
# Each script's body (everything after the H1 title line) is the spoken text.
# The H1 stays a title-only field (exercises the app's title-sync, not spoken).
# One fixed voice per speaker — same character should sound the same across
# eras/languages where the language allows it; macOS voices are per-locale, so
# a speaker's language-showcase memos necessarily use that language's voice.
#
# Usage: ./generate/tts_voice_scripts.sh [--rate WPM]
set -euo pipefail

cd "$(dirname "$0")/.."

RATE="175"
if [[ "${1:-}" == "--rate" ]]; then
  RATE="$2"
fi

SRC_DIR="generate/voice-scripts"
OUT_DIR="fixtures/transcriber/audio"
mkdir -p "$OUT_DIR"

# file-slug -> "voice|speaker" (bash 3.2 compatible — no associative arrays,
# since macOS ships bash 3.2 as /bin/bash and this script targets `say`).
voice_for() {
  case "$1" in
    # Two different KINDS of memo, which is what decides the language:
    #   1. Alex DICTATING a note to self  -> always English, wherever Alex is.
    #      A note-to-self is not in Finnish because the trip was to Helsinki.
    #   2. Alex RECORDING a meeting/conversation held in another language, to
    #      transcribe and process afterwards -> that language, spoken by the
    #      other party. This is the real reason a recording app's library is
    #      multilingual, and it's the product's actual use case.
    # Alex has lived in Berlin since 2016, so German meetings are routine.
    # Sam lives and teaches in Berlin. See voice-scripts/README.md.
    en-northlight-debrief)       echo "Daniel|alex" ;;
    en-expense-context-lunch)    echo "Daniel|alex" ;;
    en-climbing-trip)            echo "Daniel|alex" ;;
    de-steuerberater-termin)     echo "Reed|fischer" ;;
    de-mira-schulausflug)        echo "Anna|sam" ;;
    *) echo "" ;;
  esac
}

for md in "$SRC_DIR"/*.md; do
  slug="$(basename "$md" .md)"
  [[ "$slug" == "README" ]] && continue
  entry="$(voice_for "$slug")"
  if [[ -z "$entry" ]]; then
    echo "no voice mapping for $slug — skipping" >&2
    continue
  fi
  voice="${entry%%|*}"
  speaker="${entry##*|}"

  # Body = everything after the H1 line and the blank line(s) following it.
  body="$(awk 'NR==1{next} started==0 && NF==0{next} {started=1; print}' "$md")"

  audio_out="$OUT_DIR/${slug}.m4a"
  transcript_out="$OUT_DIR/${slug}.expected.txt"

  echo "== $slug  (speaker=$speaker voice=$voice) =="
  say -v "$voice" -r "$RATE" -o "$audio_out" --file-format=m4af --data-format=aac "$body"
  printf '%s\n' "$body" > "$transcript_out"
done

echo "Done. Audio + expected-transcript sidecars in $OUT_DIR/"
