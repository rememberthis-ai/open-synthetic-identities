#!/usr/bin/env python3
"""Stamp EXIF/GPS/camera metadata onto raw generated images (step 3 of
PLAN.md's pipeline) and resize to the camera-per-era table's resolution.

For each manifest entry: resize the raw PNG (from generate.py's output in
raw/) to its camera's native resolution, write DateTimeOriginal/
DateTimeDigitized (+ OffsetTimeOriginal/Digitized parsed straight from the
manifest's ISO datetime), GPSLatitude/Longitude, Make/Model, and a
deterministic ImageUniqueID derived from the manifest stem (idempotent
re-runs — same stem always produces the same ID). EXIF needs a format that
carries it, so output is JPEG (PNG doesn't) — written to
library/<identity>/<era>/<file>.jpg (the committed artifact; LFS).

Usage:
  python3 stamp_exif.py --manifest manifests/alex-carter.yaml
"""
import argparse
import hashlib
from datetime import datetime
from pathlib import Path

import piexif
import yaml
from PIL import Image

HERE = Path(__file__).parent
RAW_ROOT = HERE / "raw"
LIBRARY_ROOT = HERE / "library"

# camera slug (manifest) -> (Make, Model, width, height), per PLAN.md's
# "Camera-per-era table".
CAMERA_TABLE = {
    "iphone-5s": ("Apple", "iPhone 5s", 3264, 2448),
    "iphone-7": ("Apple", "iPhone 7", 4032, 3024),
    "iphone-xs": ("Apple", "iPhone XS", 4032, 3024),
    "iphone-13-pro": ("Apple", "iPhone 13 Pro", 4032, 3024),
    "iphone-15-pro": ("Apple", "iPhone 15 Pro", 4032, 3024),
}


def load_manifest(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)


def to_deg_rational(value: float):
    """Decimal degrees -> EXIF (deg, min, sec) rational triple.

    Rounds once to integer hundredths-of-an-arcsecond up front, then does
    the deg/min/sec split with integer division — avoids the classic
    float-cascade bug where e.g. 11.35 degrees comes out as "20min 60.00sec"
    instead of carrying to "21min 0sec" (60 is out of range for a seconds
    field even though the value is mathematically equal).
    """
    total_hundredths = round(abs(value) * 3600 * 100)
    degrees, rem = divmod(total_hundredths, 3600 * 100)
    minutes, sec_hundredths = divmod(rem, 60 * 100)
    return [(degrees, 1), (minutes, 1), (sec_hundredths, 100)]


def format_offset(offset) -> str:
    total_minutes = int(offset.total_seconds() // 60)
    sign = "+" if total_minutes >= 0 else "-"
    total_minutes = abs(total_minutes)
    return f"{sign}{total_minutes // 60:02d}:{total_minutes % 60:02d}"


def unique_id(stem: str) -> str:
    """Deterministic 32-hex-char ImageUniqueID so re-running is idempotent."""
    return hashlib.sha1(stem.encode()).hexdigest()[:32]


def stamp_entry(entry: dict, identity: str, force: bool):
    raw_path = RAW_ROOT / identity / f"{entry['file']}.png"
    if not raw_path.exists():
        print(f"[{entry['file']}] no raw image (run generate.py first), skipping")
        return None

    out_dir = LIBRARY_ROOT / identity / entry["era"]
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{entry['file']}.jpg"
    if out_path.exists() and not force:
        print(f"[{entry['file']}] already stamped, skipping")
        return out_path

    make, model, width, height = CAMERA_TABLE[entry["camera"]]

    img = Image.open(raw_path).convert("RGB")
    img = img.resize((width, height), Image.LANCZOS)

    # PyYAML auto-parses ISO-8601-looking scalars into (usually
    # timezone-aware) datetime objects; fall back to fromisoformat in case a
    # future manifest quotes the value as a plain string.
    dt = entry["datetime"]
    if isinstance(dt, str):
        dt = datetime.fromisoformat(dt)
    offset = dt.utcoffset()
    offset_str = "+00:00" if offset is None else format_offset(offset)
    dt_str = dt.strftime("%Y:%m:%d %H:%M:%S")

    lat = entry["location"]["lat"]
    lon = entry["location"]["lon"]

    zeroth_ifd = {
        piexif.ImageIFD.Make: make,
        piexif.ImageIFD.Model: model,
    }
    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: dt_str,
        piexif.ExifIFD.DateTimeDigitized: dt_str,
        piexif.ExifIFD.OffsetTimeOriginal: offset_str,
        piexif.ExifIFD.OffsetTimeDigitized: offset_str,
        piexif.ExifIFD.ImageUniqueID: unique_id(entry["file"]),
    }
    gps_ifd = {
        piexif.GPSIFD.GPSVersionID: (2, 3, 0, 0),
        piexif.GPSIFD.GPSLatitudeRef: "N" if lat >= 0 else "S",
        piexif.GPSIFD.GPSLatitude: to_deg_rational(lat),
        piexif.GPSIFD.GPSLongitudeRef: "E" if lon >= 0 else "W",
        piexif.GPSIFD.GPSLongitude: to_deg_rational(lon),
    }
    exif_bytes = piexif.dump({"0th": zeroth_ifd, "Exif": exif_ifd, "GPS": gps_ifd, "1st": {}})

    img.save(out_path, "jpeg", quality=92, exif=exif_bytes)
    return out_path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--identity", default="alex-carter")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    entries = load_manifest(args.manifest)
    stamped = 0
    for entry in entries:
        if stamp_entry(entry, args.identity, args.force):
            stamped += 1
    print(f"Done. {stamped}/{len(entries)} stamped -> {LIBRARY_ROOT / args.identity}")


if __name__ == "__main__":
    main()
