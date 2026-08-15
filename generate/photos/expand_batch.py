#!/usr/bin/env python3
"""Expand a compact life-event spec into full manifest entries.

# Why this exists

The dataset has to be **rolled forward regularly** — a synthetic life that stops
eight weeks ago reads as abandoned, and a pinned clock cannot fix it for the
paths that matter most: Clerk's period close runs a real agent session, which
reads the live system date, the real file mtimes and its own context. You can
tell it to pretend and it will drift straight back out. So the fiction has to be
maintained rather than frozen, and the only way that survives being done monthly
is if adding a month is mechanical.

Hand-writing manifest entries is the part that does not survive: eight lines
each, of which six are derivable. This takes the two that are not — when, and
what is happening — and fills in the rest:

- **era** from the date (the era timeline in PERSONA.md)
- **camera** from the era (Alex's phone upgrades are part of the story; the
  Cameras screen is built out of exactly this)
- **GPS + place name + UTC offset** from a city key
- **`cast`** passed through, because who is in a photo is a fact about the story
  and cannot be derived

Usage:
  python3 expand_batch.py --spec batches/2026-backfill.py --identity alex-carter
      >> manifests/alex-carter.yaml

The spec is a Python list of tuples so it stays readable in a diff:
  ("2026-02-14", "berlin", "sam", "Alex and Sam at the kitchen table ...", "01")
"""
import argparse
import importlib.util
from pathlib import Path

# Alex's phone history. A photo's camera is not decoration — the Cameras screen
# is built from EXIF Make/Model, so an era with the wrong phone shows up as a
# device Alex never owned.
ERAS = [
    ("manchester",    "2014-01-01", "2016-06-30", "iphone-5s"),
    ("berlin-move",   "2016-07-01", "2018-12-31", "iphone-7"),
    ("mira-arrives",  "2019-01-01", "2021-12-31", "iphone-xs"),
    ("carter-studio", "2022-01-01", "2024-12-31", "iphone-13-pro"),
    ("balance",       "2025-01-01", "2099-12-31", "iphone-15-pro"),
]

# City → (display name, lat, lon, UTC offset). Offsets are summer values where a
# city is only visited in summer; the stamp step writes them verbatim.
CITIES = {
    "berlin":      ("Kreuzberg, Berlin", 52.4990, 13.4180, "+02:00"),
    "berlin-mitte":("Mitte, Berlin", 52.5250, 13.4020, "+02:00"),
    "berlin-park": ("Tempelhofer Feld, Berlin", 52.4730, 13.4030, "+02:00"),
    "manchester":  ("Manchester", 53.4808, -2.2426, "+01:00"),
    "peak":        ("Peak District", 53.3500, -1.8200, "+01:00"),
    "amsterdam":   ("Amsterdam", 52.3676, 4.9041, "+02:00"),
    "lisbon":      ("Lisbon", 38.7223, -9.1393, "+01:00"),
    "helsinki":    ("Punavuori, Helsinki", 60.1610, 24.9400, "+03:00"),
    "stockholm":   ("Södermalm, Stockholm", 59.3140, 18.0720, "+02:00"),
    "madrid":      ("Madrid", 40.4168, -3.7038, "+02:00"),
    "bavaria":     ("Berchtesgaden, Bavaria", 47.6300, 13.0000, "+02:00"),
    "copenhagen":  ("Nørrebro, Copenhagen", 55.6900, 12.5500, "+02:00"),
    "hamburg":     ("Hamburg", 53.5511, 9.9937, "+02:00"),
    "dolomites":   ("Cortina d'Ampezzo, Dolomites", 46.5400, 12.1400, "+02:00"),
    "porto":       ("Porto", 41.1579, -8.6291, "+01:00"),
    "leipzig":     ("Leipzig", 51.3397, 12.3731, "+02:00"),
}


def era_for(date: str):
    for name, start, end, camera in ERAS:
        if start <= date <= end:
            return name, camera
    raise SystemExit(f"no era covers {date}")


def expand(spec, identity):
    out = []
    for date, city, cast, scene, seq in spec:
        if city not in CITIES:
            raise SystemExit(f"unknown city key {city!r} — add it to CITIES")
        name, lat, lon, offset = CITIES[city]
        era, camera = era_for(date)
        cast_list = [c for c in cast.split("+") if c] if cast else []
        slug = "-".join(scene.lower().split()[:4])
        slug = "".join(ch for ch in slug if ch.isalnum() or ch == "-")
        # Time of day, spread deterministically across the date AND the
        # sequence. Deriving it from `seq` alone gave every photo tagged `01`
        # the same 12:17 — a whole year of pictures sharing a clock time, which
        # is both implausible in an EXIF dump and misleading to anything that
        # clusters on time of day.
        h = int(date[5:7]) * 3 + int(date[8:10]) + int(seq) * 5
        m = (int(date[8:10]) * 7 + int(seq) * 23) % 60
        hhmm = f"{8 + h % 12:02d}:{m:02d}:00"
        out.append(f"""
- file: {date}-{slug}-{seq}
  era: {era}
  datetime: {date}T{hhmm}{offset}
  location: {{ name: "{name}", lat: {lat}, lon: {lon} }}
  camera: {camera}
  cast: [{", ".join(cast_list)}]
  scene: "{scene}\"""")
    return "".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True)
    ap.add_argument("--identity", default="alex-carter")
    args = ap.parse_args()
    path = Path(args.spec)
    sp = importlib.util.spec_from_file_location("spec", path)
    mod = importlib.util.module_from_spec(sp)
    sp.loader.exec_module(mod)
    print(expand(mod.SPEC, args.identity))


if __name__ == "__main__":
    main()
