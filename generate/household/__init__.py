"""The Carter-Okafor household's money — the dataset Mind My Money reads.

`model.py` is the world (banks, merchants, payment rails, standing charges, the
planted findings). `build.py` turns it into one ledger. `emit.py` writes that
ledger out as bank exports, portal source data and an answer key.

Everything is generated from one ledger so the statement, the order history, the
mailbox and `PLANTED.md` cannot disagree with each other. Regenerate with:

    python3 generate/gen_household.py --seed 42
"""
