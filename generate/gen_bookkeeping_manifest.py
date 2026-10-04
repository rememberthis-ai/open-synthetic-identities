#!/usr/bin/env python3
"""Write the file lists the app downloads its finished demo vaults from.

Two fixtures, one shape: Clerk's bookkeeping (`fixtures/clerkai/period-close`)
and Mind My Money's finished household (`fixtures/mindmymoney/demo-vault`).

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
  python3 gen_bookkeeping_manifest.py     # rewrites both manifests in place
"""
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURES = [
    REPO / "fixtures/clerkai/period-close",
    REPO / "fixtures/mindmymoney/demo-vault",
]

# The manifest lists itself into existence, so exclude it; the README at the
# fixture's ROOT is developer documentation the app has no use for. Only at the
# root: `Notes/money/README.md` is part of the vault, and skipping every file
# named README.md would drop it.
SKIP_AT_ROOT = {"MANIFEST.txt", "README.md"}


def main():
    for fixture in FIXTURES:
        write_one(fixture)


def write_one(fixture: Path):
    manifest = fixture / "MANIFEST.txt"
    paths = sorted(
        p.relative_to(REPO).as_posix()
        for p in fixture.rglob("*")
        if p.is_file()
        and not (p.parent == fixture and p.name in SKIP_AT_ROOT)
        and not p.name.startswith(".")
    )
    if not paths:
        raise SystemExit(f"no files under {fixture} — refusing to write an empty manifest")
    manifest.write_text("\n".join(paths) + "\n")
    kinds = {}
    for p in paths:
        kinds[Path(p).suffix or "(none)"] = kinds.get(Path(p).suffix or "(none)", 0) + 1
    print(f"wrote {manifest.relative_to(REPO)} — {len(paths)} files")
    for suffix, n in sorted(kinds.items()):
        print(f"  {suffix:8} {n}")


if __name__ == "__main__":
    main()
