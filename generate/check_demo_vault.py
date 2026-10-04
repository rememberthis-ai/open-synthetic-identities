#!/usr/bin/env python3
"""Read Mind My Money's finished demo vault back, and refuse what would break it.

    python3 generate/check_demo_vault.py

`fixtures/mindmymoney/demo-vault` is what a finished money round wrote on the
Carter-Okafor household, copied off the test rig and cleaned. Nothing
regenerates it, so this is what stands between a hand edit and a demo that
draws nothing. It checks:

- the file contracts the app reads (`money-act.md` in the monorepo): every
  `rows/` table has `currency:` and the exact columns, the ledger has its total
  line and exact header, every status starts with a known keyword, every
  commitment links an item that exists;
- the open cards: at least two, each routed back to a round
  (`asked_by: dreamer:money-round`), at most three answers;
- that the vault says it is made up, in the two files a person opens;
- that nothing from a real machine survived the copy (rig paths, the test
  portal's address, a user name, an email address);
- that `MANIFEST.txt` lists exactly the files present, so the app's fetch and
  its prune agree with the tree.

Every check counts what it examined; a check that examined nothing fails.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VAULT = REPO / "fixtures/mindmymoney/demo-vault"
MONEY = VAULT / "Notes/money"
CARDS = VAULT / "Registry/alex-carter/questions"

ROW_HEADER = "| id | date | account | bank text | amount | name | certainty | category | verbs | evidence | named_at |"
LEDGER_HEADER = "| commitment | €/year | cadence | last seen | status | recoverable |"
KEYWORDS = {"verified", "cancelled", "kept", "ended", "yours", "found", "asked", "unknown"}
FORBIDDEN = [
    (re.compile(r"localhost|127\.0\.0\.1|:8420"), "the test portal's address"),
    (re.compile(r"/Users/|/private/|/tmp/|~/"), "a machine path"),
    (re.compile(r"\bmotin\b|alexcarter|mbp1[0-9]|mbp2[0-9]", re.I), "a real user or machine name"),
    (re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "an email address"),
    (re.compile(r"\btest-(reshape|fetch)\b|catch-up test", re.I), "a rig test's leftovers"),
]

problems: list[str] = []


def fail(msg: str) -> None:
    problems.append(msg)


def frontmatter(text: str) -> dict[str, str]:
    if not text.startswith("---\n"):
        return {}
    end = text.index("\n---", 4)
    out = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith(" "):
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip().strip('"')
    return out


def main() -> int:
    rows = sorted((MONEY / "rows").glob("*.md"))
    if len(rows) < 12:
        fail(f"rows/: {len(rows)} month tables, expected at least 12")
    for p in rows:
        t = p.read_text()
        if frontmatter(t).get("currency") != "EUR":
            fail(f"{p.name}: no `currency: EUR` in frontmatter")
        if ROW_HEADER not in t:
            fail(f"{p.name}: the rows table header is not the contract's")

    ledger = (MONEY / "ledger.md").read_text()
    if not re.search(r"^Running total of verified savings: \*\*€[\d.,]+ a year\*\* \(", ledger, re.M):
        fail("ledger.md: no running-total line in the form the app reads")
    if LEDGER_HEADER not in ledger:
        fail("ledger.md: the table header is not the contract's")
    lines = [l for l in ledger.splitlines() if l.startswith("| [")]
    if not lines:
        fail("ledger.md: no commitments")
    for l in lines:
        cells = [c.strip() for c in l.strip("|").split("|")]
        link = re.match(r"\[.+\]\((items/[^)]+)\)", cells[0])
        if not link or not (MONEY / link.group(1)).is_file():
            fail(f"ledger.md: commitment does not link an item that exists: {cells[0]}")
        if cells[4].split(":", 1)[0].strip() not in KEYWORDS:
            fail(f"ledger.md: status {cells[4]!r} does not start with a known keyword")

    reports = sorted((MONEY / "reports").glob("*.md"))
    if not any(p.name.startswith("12m-") for p in reports):
        fail("reports/: no rolling 12m- report")
    accepted = re.findall(r"^- (\d{4}-\d{2}) ", (MONEY / "accepted.md").read_text(), re.M)
    for month in accepted:
        if not (MONEY / "reports" / f"{month}.md").is_file():
            fail(f"accepted.md names {month}, which has no report")

    cards = sorted(CARDS.glob("*.md"))
    open_cards = []
    for p in cards:
        fm = frontmatter(p.read_text())
        if fm.get("status") == "open":
            open_cards.append(p.name)
            if fm.get("asked_by") != "dreamer:money-round":
                fail(f"{p.name}: open card not routed to a round (asked_by)")
            if len([a for a in fm.get("suggested_actions", "").split("|") if a.strip()]) > 3:
                fail(f"{p.name}: more than three answers")
            if len(fm.get("question", "")) > 100:
                fail(f"{p.name}: question longer than 100 characters")
    if len(open_cards) < 2:
        fail(f"questions/: {len(open_cards)} open cards, the demo needs at least two")
    round_fm = frontmatter((MONEY / "round.md").read_text())
    if open_cards and round_fm.get("status") != "waiting-on-you":
        fail("round.md: cards are open but status is not waiting-on-you")

    for name in ("README.md", "round.md"):
        if "made-up household" not in (MONEY / name).read_text():
            fail(f"Notes/money/{name}: does not say this is a made-up household")

    files = sorted(p for p in VAULT.rglob("*") if p.is_file())
    scanned = 0
    for p in files:
        if p.parent == VAULT:
            continue
        # nordufer-sam.csv is cp1252, as a German bank export is; latin-1 reads any byte.
        raw = p.read_bytes()
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("latin-1")
        scanned += 1
        for rx, what in FORBIDDEN:
            m = rx.search(text)
            if m:
                fail(f"{p.relative_to(VAULT)}: {what} survived: {m.group(0)!r}")
    if scanned < 100:
        fail(f"scanned only {scanned} files for leftovers")

    listed = [l for l in (VAULT / "MANIFEST.txt").read_text().splitlines() if l.strip()]
    present = sorted(
        p.relative_to(REPO).as_posix()
        for p in files
        if not (p.parent == VAULT and p.name in {"MANIFEST.txt", "README.md"})
    )
    if listed != present:
        fail("MANIFEST.txt is out of date: run generate/gen_bookkeeping_manifest.py")

    print(f"rows {len(rows)} · reports {len(reports)} · commitments {len(lines)} · "
          f"cards {len(cards)} ({len(open_cards)} open) · files scanned {scanned}")
    for msg in problems:
        print("  ✗", msg)
    print("OK" if not problems else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
