#!/usr/bin/env python3
"""Generate the Heikkilä-Brooks household — the Finnish fixture Mind My Money
0.2.0's bills work is tested on.

    python3 generate/gen_household_fi.py --seed 42

Writes `fixtures/mindmymoney-fi/`: a year of three accounts' exports, the
records the portal sites serve (e-invoices, scheduled payments, the digital
mailbox, the mail), and `PLANTED.md`. Same rules as the Berlin household
(`gen_household.py`): one ledger, one seed, and a build that refuses to write a
fixture its own answer key contradicts. Rebuilding with the same seed
reproduces every file byte for byte.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from household_fi import build as B   # noqa: E402
from household_fi import emit as E    # noqa: E402
from household_fi import holdings as H  # noqa: E402

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "fixtures/mindmymoney-fi"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    args = ap.parse_args()

    r = B.build(args.seed)
    owned = H.build(r["txns"], args.seed)
    args.out.mkdir(parents=True, exist_ok=True)
    made = E.write_statements(args.out, r["txns"])
    made += E.write_evidence(args.out, r["evidence"])
    made += E.write_owned(args.out, owned)
    made.append(E.write_paying(args.out, r["bills"]))
    made.append(E.write_planted(args.out, r["checks"], r["bills"], owned["checks"]))
    E.write_manifest(args.out, made)

    c = r["checks"]
    print(f"Heikkilä-Brooks, seed {args.seed}, epoch {B.M.EPOCH}")
    print(f"  {c['rows']} rows, {B.M.WINDOW_START} to {B.M.WINDOW_END}; {c['bills']} bills")
    for slug, (closing, low) in r["closing"].items():
        n = sum(1 for t in r["txns"] if t.account == slug)
        print(f"  {slug:<16} {n:>5} rows   closing {closing:>10,.2f}   lowest {low:>10,.2f}")
    print(f"  open on the epoch: {len(c['open'])}; due within 14 days: "
          f"{', '.join(c['due_within_14_days'])}")
    print(f"  fees in the rows: {c['fees']['fee_total']:.2f} EUR")
    o = owned["checks"]
    for who, pf in o["portfolios"].items():
        print(f"  broker, {pf['owner']}: {pf['value']:,.2f} EUR in "
              f"{', '.join(h[0] for h in pf['holdings'])}")
    print(f"  loan {o['loan']['balance']:,.2f} EUR at {o['loan']['rate']} %, "
          f"reset {o['loan']['next_reset']}; pension {o['pension']['accrued_monthly']} EUR/kk accrued")
    print(f"  wrote {len(made) + 1} files to {args.out}")


if __name__ == "__main__":
    main()
