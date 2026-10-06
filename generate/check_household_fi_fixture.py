#!/usr/bin/env python3
"""Reconcile the Heikkilä-Brooks fixture — against the files, not the builder.

    python3 generate/check_household_fi_fixture.py

`household_fi/build.py` asserts the planted traps while it generates. This is
the other half: it reads what was WRITTEN, the two banks' CSVs in their own
encodings and the portals' JSON records, and proves they agree with each other
and that every trap the answer key names is really there. It imports nothing
from the builder; the IBAN and reference checks are written out again here so a
bug in the builder's validator cannot pass its own output.

Every check is counted, and a check that examined nothing fails.
"""

from __future__ import annotations

import csv
import io
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
import os  # noqa: E402
FIX = Path(os.environ.get("FI_FIXTURE") or ROOT / "fixtures/mindmymoney-fi")

problems: list[str] = []
counted: dict[str, int] = {}


def note(key: str, n: int = 1) -> None:
    counted[key] = counted.get(key, 0) + n


def fail(msg: str) -> None:
    problems.append(msg)


def iban_ok(iban: str) -> bool:
    s = iban.replace(" ", "")
    moved = s[4:] + s[:4]
    return int("".join(str(int(c, 36)) for c in moved)) % 97 == 1


def ref_ok(ref: str) -> bool:
    s = ref.replace(" ", "")
    if s.startswith("RF"):
        moved = s[4:] + s[:4]
        return int("".join(str(int(c, 36)) for c in moved)) % 97 == 1
    total = sum(int(d) * (7, 3, 1)[i % 3] for i, d in enumerate(reversed(s[:-1])))
    return (10 - total % 10) % 10 == int(s[-1])


def iso(d: str) -> str:
    a, b, c = d.split(".")
    return f"{c}-{int(b):02d}-{int(a):02d}"


def read_csv(path: Path) -> list[dict]:
    raw = path.read_bytes()
    if path.name.startswith("saarni"):
        text = raw.decode("latin-1")
        rows = list(csv.DictReader(io.StringIO(text), delimiter=";"))
        out = []
        for r in rows:
            out.append({"date": iso(r["Date"]),
                        "amount": float(r["Amount"].replace(" ", "").replace(",", ".")),
                        "counterparty": r["Payee/Payer"], "iban": r["Account"],
                        "reference": r["Reference"], "message": r["Message"],
                        "balance": float(r["Balance"].replace(" ", "").replace(",", "."))})
        return out
    text = raw.decode("utf-8")
    rows = list(csv.DictReader(io.StringIO(text), delimiter=";"))
    return [{"date": iso(r["Kirjauspäivä"]),
             "amount": float(r["Määrä EUROA"].replace(",", ".")),
             "counterparty": r["Saaja/Maksaja"], "iban": r["Saajan tilinumero"],
             "reference": r["Viite"], "message": r["Viesti"],
             "archive": r["Arkistointitunnus"]} for r in rows]


def isin_ok(code: str) -> bool:
    digits = "".join(str(int(c, 36)) for c in code)
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n = n * 2 - 9 if n * 2 > 9 else n * 2
        total += n
    return total % 10 == 0


def check_owned(ev: Path, ledger: list, epoch: str, planted: str) -> None:
    """Delivery B: the broker, the loan, the pension statement."""
    from datetime import date
    b = json.loads((ev / "broker.json").read_text())
    loan = json.loads((ev / "loan.json").read_text())
    pen = json.loads((ev / "pension.json").read_text())

    for k, f in b["funds"].items():
        if not isin_ok(f["isin"]):
            fail(f"fund {k}: invalid ISIN {f['isin']}")
        note("funds")
    top = {k: {t[0] for t in f["top"]} for k, f in b["funds"].items()}
    if len(top["maailma"] & top["amerikka"]) < 5:
        fail("the global and the North America fund do not overlap")
    note("overlap checked")

    held, reported = set(), set()
    for who, pf in b["portfolios"].items():
        rows = [t for t in ledger if t["counterparty"] == b["name"].upper()
                and t["iban"].replace(" ", "") == b["iban"].replace(" ", "")
                and t["reference"] == pf["reference"]]
        if not rows:
            fail(f"{who}: no transfers to the broker in the rows")
        for r in rows:
            trades = [t for t in pf["trades"] if t["transfer"] == r["id"]]
            if round(sum(t["amount"] for t in trades), 2) != round(-r["amount"], 2):
                fail(f"{who}: transfer {r['id']} is not the sum of its subscriptions")
            note("broker transfers matched")
        for h in pf["holdings"]:
            units = round(sum(t["units"] for t in pf["trades"] if t["fund"] == h["fund"]), 4)
            if abs(units - h["units"]) > 0.00005:
                fail(f"{who}/{h['fund']}: units {h['units']} but trades add to {units}")
            if abs(round(h["units"] * h["nav"], 2) - h["value"]) > 0.011:
                fail(f"{who}/{h['fund']}: value is not units times price")
            held.add(h["fund"])
            note("holdings")
        for r in pf["reports"]:
            if round(sum(l["eur"] for l in r["lines"]), 2) != r["total_eur"]:
                fail(f"{r['id']}: lines do not add to the total")
            if abs(r["total_eur"] / r["average_value"] * 100 - r["total_pct"]) > 0.006:
                fail(f"{r['id']}: total % is not total over average value")
            reported.add(r["fund"])
            note("costs reports")
    no_report = held - reported
    if len(no_report) != 1:
        fail(f"expected one held fund without a costs report, found {sorted(no_report)}")
    else:
        f = b["funds"][no_report.pop()]
        if not f["ongoing"] or f["name"] not in planted:
            fail("the fund without a report has no ongoing charge, or PLANTED.md does not name it")
    note("trap: no costs report")

    prev = loan["original"]
    for s_ in loan["schedule"]:
        if round(prev - s_["principal"], 2) != s_["balance_after"] or \
                round(s_["interest"] + s_["principal"], 2) != s_["payment"]:
            fail(f"loan: instalment {s_['date']} does not add up")
            break
        prev = s_["balance_after"]
    if prev != loan["balance"]:
        fail("loan: balance is not the last instalment's balance")
    loan_rows = {t["id"] for t in ledger if t["kind"] == "LAINAN LYHENNYS"}
    linked = {s_["row"] for s_ in loan["schedule"] if s_["row"]}
    if loan_rows != linked or not loan_rows:
        fail("loan: the rows and the schedule do not match one to one")
    note("loan rows matched", len(linked))
    if round(loan["reference_value"] + loan["margin"], 3) != loan["rate"]:
        fail("loan: rate is not reference plus margin")
    if not loan["next_reset"] > epoch or loan["next_reset"] not in planted:
        fail("loan: next reset not after the epoch, or not in PLANTED.md")

    if any(k.lower() in ("balance", "saldo", "value") for k in pen):
        fail("pension: the record carries a balance")
    if round(sum(r["accrued_yearly"] for r in pen["earnings"]) / 12, 2) != pen["accrued_monthly"]:
        fail("pension: accrued monthly is not the sum of the years")
    note("pension checked")


def main() -> int:
    if not FIX.exists():
        print(f"no fixture at {FIX}: python3 generate/gen_household_fi.py")
        return 1
    ev = FIX / "evidence"
    clock = json.loads((ev / "clock.json").read_text())
    ledger = json.loads((ev / "ledger.json").read_text())
    bills = {b["id"]: b for b in json.loads((ev / "bills.json").read_text())}
    einv = json.loads((ev / "einvoices.json").read_text())
    mailbox = json.loads((ev / "mailbox.json").read_text())
    mail = json.loads((ev / "mail.json").read_text())
    sched = json.loads((ev / "scheduled.json").read_text())
    epoch = clock["epoch"]
    w0, w1 = clock["window"]

    # ------------------------------------------------ the exports agree
    all_rows: list[dict] = []
    for acct, meta in clock["accounts"].items():
        whole = FIX / "statements" / f"{acct}-{w0}--{w1}.csv"
        if not whole.exists():
            fail(f"{acct}: no whole-window export {whole.name}")
            continue
        rows = read_csv(whole)
        months = sorted((FIX / "statements").glob(f"{acct}-20??-??.csv"))
        if len(months) != 13:
            fail(f"{acct}: {len(months)} monthly exports, expected 13")
        joined = [r for m in months for r in read_csv(m)]
        strip = lambda rs: [{k: v for k, v in r.items() if k != "balance"} for r in rs]
        if strip(joined) != strip(rows):
            fail(f"{acct}: the monthly exports do not add up to the whole-window one")
        mine = [t for t in ledger if t["account"] == acct]
        if len(mine) != len(rows):
            fail(f"{acct}: ledger has {len(mine)} rows, export {len(rows)}")
        for t, r in zip(mine, rows):
            if (t["date"], round(t["amount"], 2), t["iban"], t["reference"]) != \
                    (r["date"], round(r["amount"], 2), r["iban"], r["reference"]):
                fail(f"{acct}: row {t['id']} differs from its export line")
                break
        note("rows", len(rows))
        if acct.startswith("saarni"):
            bal = meta["opening"]
            for r in rows:
                bal = round(bal + r["amount"], 2)
                if abs(bal - r["balance"]) > 0.005:
                    fail(f"{acct}: running balance wrong on {r['date']}")
                    break
            note("balances checked", len(rows))
        for r in rows:
            if r["iban"] and not iban_ok(r["iban"]):
                fail(f"{acct}: invalid IBAN {r['iban']} on {r['date']}")
            if r["reference"] and not ref_ok(r["reference"]):
                fail(f"{acct}: invalid reference {r['reference']} on {r['date']}")
            if not (w0 <= r["date"] <= w1):
                fail(f"{acct}: row outside the window on {r['date']}")
        all_rows += rows

    by_row = {t["id"]: t for t in ledger}

    # ------------------------------------------- every paid bill has its row
    for b in bills.values():
        note("bills")
        if not iban_ok(b["iban"]) or not ref_ok(b["reference"]):
            fail(f"{b['id']}: invalid IBAN or reference")
        if b["paid_txn"]:
            t = by_row.get(b["paid_txn"])
            if not t or t["reference"] != b["reference"] or t["iban"] != b["iban"]:
                fail(f"{b['id']}: its paying row does not carry its reference and IBAN")
            note("paid bills matched to rows")

    # -------------------------------------------------- the portals' records
    for bid in einv["invoices"]:
        if bid not in bills or "einvoice" not in bills[bid]["channels"]:
            fail(f"e-invoice list names {bid}, which is not an e-invoice")
        note("e-invoices")
    for l in mailbox["letters"]:
        if l["bill"] and l["bill"] not in bills:
            fail(f"mailbox letter {l['id']} names a bill that does not exist")
        note("letters")
    for m in mail["messages"]:
        for a in m["attachments"]:
            if a["bill"] not in bills:
                fail(f"mail {m['id']} attaches a bill that does not exist")
            note("mail attachments")

    open_ = [b for b in bills.values() if b["status"] in ("open", "automatic", "scheduled")]
    from datetime import date
    days = lambda b: (date.fromisoformat(b["due"]) - date.fromisoformat(epoch)).days

    # --------------------------------------------------------------- the traps
    soon = [b for b in open_ if b["status"] == "open" and 0 <= days(b) <= 14]
    if not soon:
        fail("no open bill due within 14 days of the epoch")
    note("trap: due soon", len(soon))

    letters_bills = {l["bill"] for l in mailbox["letters"] if l["bill"]}
    twice = [b for b in open_ if b["id"] in einv["invoices"] and b["id"] in letters_bills]
    if len(twice) != 1:
        fail(f"expected one open bill both in the e-invoices and the mailbox, found {len(twice)}")
    note("trap: found twice", len(twice))

    auto = [b for b in open_ if b["status"] == "automatic"]
    sched_bills = {s.get("bill") for s in sched}
    if len(auto) != 1 or auto[0]["id"] not in sched_bills:
        fail("the automatic bill is missing, or missing from the scheduled list")
    note("trap: automatic", len(auto))

    for b in open_:
        if b["status"] == "scheduled" and b["id"] not in sched_bills:
            fail(f"{b['id']} is scheduled but not in the scheduled list")

    paid_ibans: dict[str, set] = {}
    for r in all_rows:
        paid_ibans.setdefault(r["counterparty"], set()).add(r["iban"])
    changed = [b for b in open_ if b["payee"].upper() in paid_ibans
               and b["iban"] not in paid_ibans[b["payee"].upper()]]
    if len(changed) != 1:
        fail(f"expected one familiar payee with a new IBAN, found {len(changed)}")
    note("trap: changed IBAN", len(changed))

    out_of_range = []
    for b in open_:
        past = [x["amount"] for x in bills.values()
                if x["biller"] == b["biller"] and x["kind"] == "bill" and x["paid_txn"]]
        if past and b["amount"] > 2 * max(past):
            out_of_range.append(b)
    if len(out_of_range) != 1:
        fail(f"expected one bill above twice its payee's usual range, found {len(out_of_range)}")
    note("trap: out of range", len(out_of_range))

    first = [b for b in open_ if not any(r["iban"] == b["iban"] for r in all_rows)
             and b["payee"].upper() not in paid_ibans]
    firsts_by_mail = [b for b in first if b["channels"] == ["email"]]
    if len(firsts_by_mail) != 1:
        fail(f"expected one first-time sender by email, found {len(firsts_by_mail)}")
    note("trap: first-time sender", len(firsts_by_mail))

    mbox_only = [b for b in open_ if b["channels"] == ["mailbox"]
                 and b["id"] not in einv["invoices"]]
    if len(mbox_only) != 1:
        fail(f"expected one bill only in the mailbox, found {len(mbox_only)}")
    note("trap: mailbox only", len(mbox_only))

    fee_rows = [r for r in all_rows if any(w in r["message"].lower()
                                           for w in ("muistutusmaksu", "viivästyskorko"))]
    if len(fee_rows) != 3:
        fail(f"expected three fee rows in last year's rows, found {len(fee_rows)}")
    behind = [b for b in bills.values() if b["kind"] in ("reminder", "late_fee")]
    if len(behind) != 3:
        fail(f"expected three reminder/late-fee bills behind the fee rows, found {len(behind)}")
    note("trap: fees", len(fee_rows))

    planted = (FIX / "PLANTED.md").read_text()
    for b in soon + twice + auto + changed + out_of_range + firsts_by_mail + mbox_only:
        if b["reference"] not in planted:
            fail(f"PLANTED.md does not name {b['id']}")
    note("answer key entries", 1)

    check_owned(ev, ledger, epoch, planted)

    manifest = set((FIX / "MANIFEST.txt").read_text().split())
    for p in FIX.rglob("*"):
        if p.is_file() and p.name not in ("MANIFEST.txt", "README.md"):
            if str(p.relative_to(FIX)) not in manifest:
                fail(f"{p.relative_to(FIX)} is not in MANIFEST.txt")

    for k, n in sorted(counted.items()):
        print(f"  {k:<32} {n}")
    for key in ("rows", "bills", "e-invoices", "letters", "mail attachments", "funds",
                "holdings", "costs reports", "broker transfers matched", "loan rows matched"):
        if not counted.get(key):
            fail(f"examined no {key}")
    for p in problems:
        print("  ✗", p)
    print("the Finnish household fixture reconciles." if not problems
          else f"{len(problems)} problem(s)")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
