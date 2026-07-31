#!/usr/bin/env python3
"""Generate a fictional bank-statement CSV ("Meridian Business" format) for a demo
identity, consistent with the receipts produced by gen_receipts.py (same seed).

Usage:
  python3 gen_statement_csv.py --identity alex-carter --month 2026-06 --seed 42 \
      --out ../fixtures/clerkai/statements
"""
import argparse
import csv
import random
from datetime import date, timedelta
from pathlib import Path

RECURRING = {
    "alex-carter": [
        # (day, description, amount € — negative = spend)
        (1, "WERKRAUM KOLLEKTIV FLEX DESK", -240.00),
        (2, "NIMBUS CLOUD HOSTING", -45.00),
        (3, "FONTRACK PRO SUBSCRIPTION", -18.00),
        (15, "NORTHLIGHT AGENCY INV-2026-", +4800.00),
        (22, "HALLO MOBILFUNK GMBH", -29.99),
        (27, "STADTWERKE BERLIN ABSCHLAG", -86.00),
    ]
}

CARD_SPEND = {
    "alex-carter": [
        ("BREW AND BEAN BERLIN", 3.4, 18.5, 6),
        ("BUEROBEDARF KERN BERLIN", 5.9, 32.0, 2),
        ("RAILLINK DE", 74.0, 182.0, 2),
        ("BAECKEREI SONNENSCHEIN", 2.6, 9.8, 3),
        ("SUPERMERCADO LISTO BERLIN", 12.4, 68.0, 5),
        ("K-KULMA KIOSKI HELSINKI", 3.2, 9.9, 1),
        ("KAFFEBAREN SODER STOCKHOLM", 3.4, 11.2, 1),
        ("CAFE DEL SOL MADRID", 2.2, 10.6, 1),
    ]
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", default="alex-carter")
    ap.add_argument("--month", default="2026-06")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", default="../fixtures/clerkai/statements")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    year, month = map(int, args.month.split("-"))
    first = date(year, month, 1)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows = []
    balance = 12408.33
    for day, desc, amount in RECURRING[args.identity]:
        if desc.endswith("INV-2026-"):
            desc += f"{month:02d}"
        rows.append((first + timedelta(days=day - 1), desc, amount))
    for desc, lo, hi, times in CARD_SPEND[args.identity]:
        for _ in range(times):
            d = first + timedelta(days=rng.randint(0, 27))
            rows.append((d, desc, -round(rng.uniform(lo, hi), 2)))
    rows.sort(key=lambda r: r[0])

    fname = out / f"meridian-business-{args.month}.csv"
    with open(fname, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["Date", "Description", "Amount (EUR)", "Balance (EUR)", "Type"])
        for d, desc, amount in rows:
            balance = round(balance + amount, 2)
            w.writerow([d.isoformat(), desc, f"{amount:.2f}", f"{balance:.2f}",
                        "CREDIT" if amount > 0 else "CARD" if abs(amount) < 200 else "DEBIT"])
    print(f"wrote {len(rows)} transactions to {fname}")


if __name__ == "__main__":
    main()
