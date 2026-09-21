#!/usr/bin/env python3
"""Generate the Carter-Okafor household's money — the dataset Mind My Money reads.

    python3 generate/gen_household.py --seed 42

Writes `fixtures/mindmymoney/`: thirteen months of three banks' exports, the
source data the portal sites serve, and `PLANTED.md`.

**One ledger, many views.** The statement, the grocer's order history, the
mailbox, the BNPL bank's purchase list and the answer key are all written from
the same list of transactions in the same run, so they cannot disagree about a
cent. Rebuilding with the same seed reproduces every file byte for byte.

It refuses rather than writing a fixture that contradicts its own answer key:
`build.check()` recomputes each planted finding and raises if one has drifted.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from household import build as B      # noqa: E402
from household import emit as E       # noqa: E402

DEFAULT_OUT = Path(__file__).resolve().parent.parent / "fixtures/mindmymoney"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--identity", default="carter-okafor-household",
                    help="recorded in the output; there is only one household")
    args = ap.parse_args()

    result = B.build(args.seed)
    txns, ev, checks = result["txns"], result["evidence"], result["checks"]

    args.out.mkdir(parents=True, exist_ok=True)
    made = E.write_statements(args.out, txns)
    made += E.write_evidence(args.out, ev, txns)
    made.append(E.write_receipt_spec(args.out, ev["photos"]))
    made.append(E.write_planted(args.out, checks, txns))
    E.write_manifest(args.out, made)

    print(f"{args.identity}, seed {args.seed}")
    print(f"  {len(txns)} transactions, {B.M.WINDOW_START} to {B.M.WINDOW_END}")
    for slug, closing in result["closing"].items():
        rows = sum(1 for t in txns if t.account == slug)
        print(f"  {slug:<20} {rows:>5} rows   closing {closing:>10,.2f} EUR")
    h = checks["hidden-rows"]
    print(f"  {h['hidden']} rows the bank text cannot name — one in {h['one_in']}"
          f" ({h['with_nothing']} of them resolvable by nothing at all)")
    print(f"  evidence: {len(ev['mail'])} emails, {len(ev['grocer'])} grocery orders, "
          f"{len(ev['marketplace'])} marketplace orders, {len(ev['bnpl'])} BNPL purchases, "
          f"{len(ev['photos'])} till receipts to photograph")
    print(f"  wrote {len(made) + 1} files to {args.out}")


if __name__ == "__main__":
    main()
