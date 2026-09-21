#!/usr/bin/env python3
"""Reconcile the household fixture — against the files, not against the builder.

    python3 generate/check_household_fixture.py

`build.py` already asserts the planted findings while it is generating. This is
the other half and the one that matters: it reads what was actually **written**,
in the encodings and dialects the portals and the agent will meet, and proves
the pieces still agree with each other.

That distinction is the whole reason this file exists separately. A check that
imports the builder and re-derives the answer is asking the generator whether it
agrees with itself; only reading the CSV back through a cp1252 decoder proves
the cp1252 encoder did something a reader can undo.

Every check is **counted**, and a check that matched nothing fails. An audit
that silently examines an empty set reports the good news.
"""

from __future__ import annotations

import csv
import io
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIX = ROOT / "fixtures/mindmymoney"

OPENING = {"meridian-everyday": 1842.10, "havelbank-joint": 3180.44,
           "nordufer-sam": 612.85}


def window_files(slug: str):
    """The whole-window export and the monthly ones, found rather than named.

    The window moves — the dataset is rolled forward as time passes — so a
    hardcoded `2025-06--2026-06` here would start reporting a missing file the
    first month somebody advances it, which reads as a broken fixture rather
    than as a stale checker.
    """
    stmts = FIX / "statements"
    months = sorted(stmts.glob(f"{slug}-20??-??.csv"))
    whole = [p for p in stmts.glob(f"{slug}-*--*.csv")]
    return (whole[0] if len(whole) == 1 else None), months

EXPECTED_MONTHS = 13
"""Thirteen months, so the last month has the same month a year earlier beside
it. Move this when the window moves."""

problems: list[str] = []
counted: dict[str, int] = {}


def note(key: str, n: int = 1) -> None:
    counted[key] = counted.get(key, 0) + n


def fail(msg: str) -> None:
    problems.append(msg)


def _num_de(s: str) -> float:
    s = s.strip()
    if not s:
        return 0.0
    return float(s.replace(".", "").replace(",", "."))


def read_statement(path: Path) -> list[dict]:
    """Decode and parse one export in its own dialect. A wrong guess here is
    supposed to raise, not to silently produce rows nobody can reconcile."""
    raw = path.read_bytes()
    name = path.name

    if name.startswith("meridian-everyday"):
        text = raw.decode("utf-8")
        rows = list(csv.DictReader(io.StringIO(text)))
        return [{"date": r["Date"], "amount": float(r["Amount (EUR)"]),
                 "balance": float(r["Balance (EUR)"]),
                 "text": r["Description"]} for r in rows]

    if name.startswith("havelbank-joint"):
        if not raw.startswith(b"\xef\xbb\xbf"):
            fail(f"{name}: the Havelbank export is supposed to carry a BOM and does not")
        text = raw.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text), delimiter=";"))
        return [{"date": r["Buchungstag"], "amount": _num_de(r["Betrag"]),
                 "balance": _num_de(r["Saldo"]),
                 "text": f"{r['Beguenstigter/Zahlungspflichtiger']} {r['Verwendungszweck']}"}
                for r in rows]

    if name.startswith("nordufer-sam"):
        try:
            text = raw.decode("cp1252")
        except UnicodeDecodeError as exc:
            fail(f"{name}: does not decode as cp1252 ({exc})")
            return []
        if raw.decode("cp1252").encode("cp1252") != raw:
            fail(f"{name}: does not round-trip through cp1252")
        rows = list(csv.DictReader(io.StringIO(text), delimiter=";"))
        out = []
        for r in rows:
            soll, haben = _num_de(r["Soll"]), _num_de(r["Haben"])
            if soll and haben:
                fail(f"{name}: a row carries both Soll and Haben")
            out.append({"date": r["Buchung"], "amount": haben - soll,
                        "balance": _num_de(r["Saldo"]),
                        "text": f"{r['Auftraggeber/Empfaenger']} {r['Verwendungszweck']}"})
        return out

    fail(f"{name}: no dialect knows how to read this")
    return []


def check_statements() -> dict[str, list[dict]]:
    """Balances chain from the opening figure to the last row, and the per-month
    files say exactly what the whole-window file says."""
    whole: dict[str, list[dict]] = {}
    for slug, opening in OPENING.items():
        full, months = window_files(slug)
        if full is None:
            fail(f"{slug}: expected exactly one whole-window export in "
                 f"{(FIX / 'statements').relative_to(ROOT)}")
            continue
        rows = read_statement(full)
        if not rows:
            fail(f"{slug}: the whole-window export is empty")
            continue
        whole[slug] = rows

        balance = opening
        for i, r in enumerate(rows):
            balance = round(balance + r["amount"], 2)
            if abs(balance - r["balance"]) > 0.005:
                fail(f"{slug} row {i + 1} ({r['date']}): balance says "
                     f"{r['balance']:.2f}, the chain says {balance:.2f}")
                break
            note("balance steps")

        if len(months) != EXPECTED_MONTHS:
            fail(f"{slug}: {len(months)} monthly exports, expected "
                 f"{EXPECTED_MONTHS}")
        rebuilt = [r for p in months for r in read_statement(p)]
        if rebuilt != rows:
            fail(f"{slug}: the monthly exports do not add up to the whole-window one "
                 f"({len(rebuilt)} rows against {len(rows)})")
        else:
            note("months reconciled", len(months))
    return whole


def index(whole: dict[str, list[dict]]) -> dict:
    """Every row, addressable the way the evidence files address one."""
    out: dict[tuple, list[dict]] = {}
    for slug, rows in whole.items():
        seq: dict[tuple, int] = {}
        for r in rows:
            d = r["date"]
            if "." in d:                       # TT.MM.JJJJ
                dd, mm, yy = d.split(".")
                d = f"{yy}-{mm}-{dd}"
            key = (d, slug)
            seq[key] = seq.get(key, 0) + 1
            out[f"{d}-{slug}-{seq[key]:02d}"] = r
    return out


def load(name: str):
    p = FIX / "evidence" / name
    if not p.exists():
        fail(f"missing {p.relative_to(ROOT)}")
        return None
    return json.loads(p.read_text())


def check_evidence(rows_by_id: dict) -> None:
    """Every piece of evidence points at a row that exists and agrees with it.

    This is the property the whole dataset rests on: an order history that
    reconciles to the statement is a thing the agent can prove a name from, and
    one that does not is a thing that makes a correct agent look wrong.
    """
    def agrees(kind: str, txn_id: str, total: float, label: str) -> None:
        if not txn_id:
            return
        row = rows_by_id.get(txn_id)
        if row is None:
            fail(f"{kind} {label}: names row {txn_id}, which is in no statement")
            return
        if abs(abs(row["amount"]) - total) > 0.005:
            fail(f"{kind} {label}: says {total:.2f}, row {txn_id} is "
                 f"{abs(row['amount']):.2f}")
            return
        note(f"{kind} reconciled")

    grocer = load("grocer-orders.json")
    if grocer:
        for o in grocer["orders"]:
            lines = round(sum(l["amount"] for l in o["lines"]), 2)
            if abs(lines - o["total"]) > 0.005:
                fail(f"grocery order {o['order']}: items sum to {lines:.2f}, "
                     f"the order says {o['total']:.2f}")
                continue
            agrees("grocery order", o["txn_id"], o["total"], o["order"])

    mkt = load("marketplace-orders.json")
    if mkt:
        for o in mkt["orders"]:
            agrees("marketplace order", o["txn_id"], o["total"], o["order"])

    bnpl = load("bnpl-purchases.json")
    if bnpl:
        for p in bnpl["purchases"]:
            agrees("BNPL purchase", p["txn_id"], p["total"], p["purchase"])

    mail = load("mail.json")
    if mail:
        for msg in mail["messages"]:
            agrees("email", msg.get("txn_id", ""), msg["total"], msg["id"])

    for name, key in (("streaming-account.json", "memberships"),
                      ("gym-account.json", None)):
        data = load(name)
        if not data:
            continue
        holders = data[key] if key else [data]
        for h in holders:
            for c in h.get("charges", []):
                agrees(name.split("-")[0], c["txn_id"], c["amount"],
                       h.get("id") or h.get("member_no", "?"))

    photos = load("photo-evidence.json")
    if photos:
        for r in photos["rows"]:
            agrees("till receipt", r["txn_id"], r["total"], r["stem"])


def check_planted() -> None:
    """The answer key names figures a reader will check. If it has drifted from
    the statements, it is worse than no answer key."""
    p = FIX / "PLANTED.md"
    if not p.exists():
        fail("missing PLANTED.md")
        return
    text = p.read_text()
    for phrase in ("PLANTED", "answer key", "sweets and ice cream",
                   "fish and meat", "unnamed"):
        if phrase not in text:
            fail(f"PLANTED.md no longer mentions {phrase!r}")
        else:
            note("answer-key phrases")

    grocer = load("grocer-orders.json")
    if not grocer:
        return
    sweets = sum(l["amount"] for o in grocer["orders"] for l in o["lines"]
                 if l["sub"] == "sweets")
    meat = sum(l["amount"] for o in grocer["orders"] for l in o["lines"]
               if l["sub"] == "meatfish")
    if sweets <= meat:
        fail(f"the sweets-over-meat finding is false in the shipped files: "
             f"{sweets:.2f} against {meat:.2f}")
    for figure in (f"{sweets:.2f}", f"{meat:.2f}"):
        if figure not in text:
            fail(f"PLANTED.md does not quote {figure}, which the orders add up to")
        else:
            note("answer-key figures")


def check_photos() -> None:
    """The photo half drifts silently and expensively, so it is checked here too.

    The rows whose only witness is a paper slip are CHOSEN BY THE LEDGER, so
    they move whenever the ledger is regenerated — and a composite that cost
    real money to generate then photographs a transaction that no longer
    exists. Nothing else in the pipeline can see one: the manifest still parses,
    the library still has a JPEG, and OCR still reads a perfectly good receipt.
    """
    script = ROOT / "generate/gen_household_photos.py"
    if not script.exists():
        fail("generate/gen_household_photos.py is gone; nothing reconciles the "
             "till receipts with the ledger any more")
        return
    r = subprocess.run([sys.executable, str(script), "--check"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        for line in r.stdout.strip().splitlines():
            fail(f"photos: {line.strip()}")
    else:
        note("photo chain in step")


def main() -> int:
    if not FIX.exists():
        print(f"no fixture at {FIX} — run generate/gen_household.py first")
        return 2
    whole = check_statements()
    rows_by_id = index(whole)
    check_evidence(rows_by_id)
    check_planted()
    check_photos()

    # ⛔ The floor. A checker that matched nothing prints the good news, and this
    # one reads files whose names it builds from patterns — one renamed
    # directory and every loop above iterates over an empty list.
    for key in ("balance steps", "months reconciled", "grocery order reconciled",
                "marketplace order reconciled", "BNPL purchase reconciled",
                "email reconciled", "till receipt reconciled",
                "answer-key phrases", "answer-key figures", "photo chain in step"):
        if not counted.get(key):
            fail(f"nothing was checked for {key!r} — the check read an empty set")

    for key in sorted(counted):
        print(f"  {counted[key]:>5}  {key}")
    if problems:
        print(f"\n{len(problems)} problem(s):")
        for p in problems:
            print(f"  - {p}")
        return 1
    print("\nthe household fixture reconciles.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
