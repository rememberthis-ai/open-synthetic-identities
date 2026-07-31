#!/usr/bin/env python3
"""Write the file list the app downloads the Clerk bookkeeping fixture from.

Photos and audio each have a manifest the app reads before fetching; the
bookkeeping tree had none, so nothing could enumerate it — and nothing could
PRUNE it either, which matters more. A downloader without a manifest can only
add: on an update it leaves retired periods on disk forever and the demo
quietly shows a mix of current and stale books. The manifest is what makes
"reconcile" possible, so it is not optional scaffolding.

Paths are repo-relative, one per line, sorted. The app turns each into a URL:
binaries (`.png`) through `media.githubusercontent.com`, which resolves Git LFS
pointers to real bytes; text through `raw.githubusercontent.com`.

Usage:
  python3 gen_bookkeeping_manifest.py     # rewrites the manifest in place
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "fixtures/clerkai/period-close"
MANIFEST = FIXTURE / "MANIFEST.txt"

# The manifest lists itself into existence, so exclude it; README is developer
# documentation the app has no use for.
SKIP = {"MANIFEST.txt", "README.md"}


def main():
    paths = sorted(
        p.relative_to(REPO).as_posix()
        for p in FIXTURE.rglob("*")
        if p.is_file() and p.name not in SKIP and not p.name.startswith(".")
    )
    if not paths:
        raise SystemExit(f"no files under {FIXTURE} — refusing to write an empty manifest")
    MANIFEST.write_text("\n".join(paths) + "\n")
    kinds = {}
    for p in paths:
        kinds[Path(p).suffix or "(none)"] = kinds.get(Path(p).suffix or "(none)", 0) + 1
    print(f"wrote {MANIFEST.relative_to(REPO)} — {len(paths)} files")
    for suffix, n in sorted(kinds.items()):
        print(f"  {suffix:8} {n}")


if __name__ == "__main__":
    main()
