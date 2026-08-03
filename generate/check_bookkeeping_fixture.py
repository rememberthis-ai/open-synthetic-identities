#!/usr/bin/env python3
"""Assert the invariants the Clerk bookkeeping fixture's README states in prose.

The README has always listed these, and nothing checked them — so the way they
were kept was by remembering. Each of the checks below corresponds to a way the
fixture has actually gone wrong, or to a way it silently would:

1. **A filename in a letter is a file that exists**, and a finished period's
   folder holds nothing the letter did not list. The app makes an openable
   link out of every staged file, and lists the staged folder rather than the
   letter's own numbering — so a name typed into the draft with no file behind
   it is a discrepancy between what the user reads and what they send, and it
   looks exactly like a correct row.
2. **Nothing a person reads carries a path or an internal filename.** The
   recipient of that email has no `Notes/bookkeeping/`.
3. **No word that is ours rather than theirs** in those same places — not
   *packet*, *deliverables*, *reconcile*. (`Vocabulary.swift` enforces the same
   list against the app's own sources; this is the data half.)
4. **Every `receipt_path` resolves**, or a ledger row points at nothing.
5. **Exactly one movement per closed month has no document at all.** The
   finished period leads with that exception by name, so it has to be singular:
   the income lines point at the statement and say in `why` where the real
   invoice lives, rather than looking like three more gaps.

Usage:
  python3 check_bookkeeping_fixture.py      # exits non-zero on any failure
"""
import glob
import os
import re
import sys
from pathlib import Path

import yaml

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures/clerkai/period-close"
BOOKS = FIXTURE / "Notes/bookkeeping"

# Paths and internal filenames. A person reads none of these.
BAD_PATH = re.compile(r"Notes/bookkeeping|\brun\.md\b|\bindex\.md\b|accountant\.md")
# Words that are ours rather than the reader's (App Simple §1). `collect` as a
# VERB is deliberately absent — "collecting your statements" is a sentence
# somebody would say out loud.
OURS = re.compile(r"\bpackets?\b|\bdeliverables?\b|\breconcile[ds]?\b", re.I)

# Periods that are finished collecting, and therefore expected to be complete.
CLOSED_MONTHS = ["carter-studio/2026-03", "carter-studio/2026-04", "carter-studio/2026-05"]

fail: list[str] = []


def frontmatter(path: str) -> dict:
    text = Path(path).read_text()
    if not text.startswith("---"):
        return {}
    return yaml.safe_load(text.split("---", 2)[1]) or {}


def rel(path: str) -> str:
    return os.path.relpath(path, FIXTURE)


def run_status(period_dir: str) -> str:
    run = os.path.join(period_dir, "run.md")
    if not os.path.exists(run):
        return ""
    return str(frontmatter(run).get("status") or "")


# A period whose run is finished: the letter is written and the folder settled.
# **A live run is deliberately NOT held to the second half of check 1.** The
# letter is written first and mostly empty, and files are staged as they arrive
# — so a period still collecting legitimately holds documents its letter has
# not listed yet. Requiring the two to agree there would force the fixture to
# choose between an honest mid-collection state and a green check.
SETTLED = {"review", "sent", "done"}

# 1. Letters name only files that exist, and — once the run is finished —
#    stage only files they name.
for draft in glob.glob(f"{BOOKS}/*/*/accountant-email-draft.md"):
    period = os.path.dirname(draft)
    folder = os.path.join(period, "attachments-to-send")
    staged = set(os.listdir(folder)) if os.path.isdir(folder) else set()
    named = re.findall(r"^\s*\d+\.\s+(\S+)$", Path(draft).read_text(), re.M)
    for name in named:
        if name not in staged:
            fail.append(f"{rel(draft)}: the letter names {name!r}, which is not staged")
    if run_status(period) in SETTLED:
        for name in staged:
            if name not in named:
                fail.append(f"{rel(draft)}: {name!r} is staged but the letter never names it")

# 1b. What went out is kept. A period that records a send has a folder of what
#     it sent that day, and every file in it is a file the period holds — a
#     sent folder naming something the letter never listed is a claim about
#     what an accountant received that nothing else in the vault supports.
for sent_dir in sorted(glob.glob(f"{BOOKS}/*/*/attachments-sent-*")):
    period = os.path.dirname(sent_dir)
    staged = set(os.listdir(os.path.join(period, "attachments-to-send")))
    for name in sorted(os.listdir(sent_dir)):
        if name not in staged:
            fail.append(f"{rel(sent_dir)}: sent {name!r}, which the period does not hold")

# 2 + 3. What a person reads: the letter, the thread, `current_activity`, the
# step details, and a checklist row's label/detail/why.
for path in glob.glob(f"{BOOKS}/**/*.md", recursive=True):
    name = os.path.basename(path)
    text = Path(path).read_text()
    if name in ("accountant-email-draft.md", "accountant-correspondence.md"):
        read_by_a_person = [text]
    elif name == "run.md":
        read_by_a_person = re.findall(r"^(?:current_activity|steps): (.*)$", text, re.M)
    elif "/items/" in path:
        fm = frontmatter(path)
        read_by_a_person = [str(fm.get(k) or "") for k in ("label", "detail", "why")]
    else:
        continue
    for value in read_by_a_person:
        # Quote the OFFENDING span with a little context, not the head of the
        # value — for a whole letter the head is always the To: line, which
        # says nothing about what is wrong.
        for rule, label in ((BAD_PATH, "a path or internal filename"),
                            (OURS, "our word rather than theirs")):
            hit = rule.search(value)
            if hit:
                start, end = max(0, hit.start() - 24), hit.end() + 24
                context = value[start:end].replace("\n", " ").strip()
                fail.append(f"{rel(path)}: {label} — {hit.group(0)!r} in …{context}…")

# 4. Every receipt_path resolves.
for path in glob.glob(f"{BOOKS}/**/items/*.md", recursive=True):
    receipt = frontmatter(path).get("receipt_path")
    if receipt and not (FIXTURE / receipt).exists():
        fail.append(f"{rel(path)}: receipt_path does not resolve — {receipt}")

# 5. One nameable exception per closed month, not a scattering of gaps.
for period in CLOSED_MONTHS:
    undocumented = []
    for path in glob.glob(f"{BOOKS}/{period}/items/*.md"):
        fm = frontmatter(path)
        if fm.get("kind") != "transaction" or fm.get("status") == "excluded":
            continue
        if not fm.get("receipt_path") and not fm.get("photo_uuid"):
            undocumented.append(fm.get("vendor"))
    if len(undocumented) != 1:
        fail.append(
            f"{period}: {len(undocumented)} movements with no document "
            f"({', '.join(str(v) for v in undocumented) or 'none'}) — want exactly one"
        )

if fail:
    print("\n".join(f"  FAIL {line}" for line in fail))
    print(f"\n{len(fail)} failure(s).")
    sys.exit(1)
print("all bookkeeping-fixture invariants hold")
