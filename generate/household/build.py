"""Build the household's ledger — one list of transactions, from one seed.

Everything else in this package is a *view* over what this file returns: the
three bank exports, the mailbox, the grocer's order history, the marketplace's,
the BNPL bank's purchase list, and the answer key. That is deliberate. A fixture
whose statement and whose order history are generated independently will
disagree about a cent sooner or later, and the disagreement will be read as the
agent getting it wrong.

**The planted findings are asserted, not hoped for.** `check()` recomputes each
one from the finished ledger and raises if a figure has drifted — so a change to
a weight cannot quietly leave `PLANTED.md` describing a dataset that no longer
exists.
"""

from __future__ import annotations

import calendar
import hashlib
import random
from dataclasses import dataclass, field
from datetime import date, timedelta

from . import model as M


@dataclass
class Txn:
    """One row, with both what the bank shows and what is actually true."""

    date: date
    account: str
    amount: float

    # what a parser sees
    booking: str = ""
    """German `Buchungstext`. Empty for Meridian, which has a `Type` instead."""
    counterparty: str = ""
    purpose: str = ""
    descriptor: str = ""
    """Meridian's single `Description` column."""

    # ground truth, for the answer key — never rendered into a bank export
    merchant: str = ""
    category: str = ""
    rail: str | None = None
    evidence: str = "bank text"
    """`bank text` | `mail:<id>` | `grocer:<order>` | `marketplace:<order>`
    | `bnpl:<id>` | `photo:<file>` | `none`"""
    items: list = field(default_factory=list)
    """`(label, sub, amount)` where a basket is known."""
    slug: str = ""
    note: str = ""

    # filled in by `finish()`
    txn_id: str = ""
    balance: float = 0.0


# ------------------------------------------------------------------ helpers


def months_in_window() -> list[tuple[int, int]]:
    """Every month the window touches, derived from `WINDOW_START`/`WINDOW_END`.

    ⭐ **Moving the window is meant to be editing those two strings and nothing
    else.** A synthetic life that stops eight weeks ago reads as abandoned, and
    a money round cannot be told to pretend it is June — it reads the live date.
    So the dataset has to be rolled forward, and the only version of that which
    survives being done every month is a mechanical one.
    """
    ys, ms = (int(x) for x in M.WINDOW_START.split("-")[:2])
    ye, me = (int(x) for x in M.WINDOW_END.split("-")[:2])
    out = []
    y, m = ys, ms
    while (y, m) <= (ye, me):
        out.append((y, m))
        m += 1
        if m == 13:
            y, m = y + 1, 1
    return out


def window_tag() -> str:
    """How a whole-window export names itself: `2025-06--2026-06`."""
    first, last = months_in_window()[0], months_in_window()[-1]
    return f"{first[0]:04d}-{first[1]:02d}--{last[0]:04d}-{last[1]:02d}"


def _biller_code(prefix: str, slug: str, ym: str) -> str:
    """A reference a biller rotates every month, derived from the month alone.

    Not drawn from the shared random stream: that stream feeds every row
    after it, so a new standing charge that consumed it would move every
    basket and every hidden row in the year."""
    h = hashlib.sha256(f"{slug}:{ym}".encode()).hexdigest().upper()
    if prefix == "PR":  # a card descriptor's short code
        digits = "".join(c for c in h if c.isalnum())
        return "PR" + digits[:7]
    n = int(h[:12], 16)
    return f"{prefix}-{n % 10_000_000:07d}-{(n // 10_000_000) % 10_000_000:07d}"


def _clamp_day(y: int, m: int, day: int) -> date:
    return date(y, m, min(day, calendar.monthrange(y, m)[1]))


def _in_range(ym: str, first: str | None, last: str | None) -> bool:
    if first and ym < first:
        return False
    if last and ym > last:
        return False
    return True


def _money(rng, lo, hi) -> float:
    return round(rng.uniform(lo, hi), 2)


def _weighted(rng, pairs):
    total = sum(w for _, w in pairs)
    x = rng.uniform(0, total)
    for item, w in pairs:
        x -= w
        if x <= 0:
            return item
    return pairs[-1][0]


def _ascii_upper(s: str) -> str:
    """What a terminal or a German bank field does to a name: no lower case, no
    umlauts, no punctuation it cannot print."""
    table = {"ä": "AE", "ö": "OE", "ü": "UE", "ß": "SS",
             "Ä": "AE", "Ö": "OE", "Ü": "UE", "&": "U", "é": "E"}
    out = "".join(table.get(c, c) for c in s)
    return out.upper()


# ------------------------------------------------------------ the rail masks
#
# Each returns `(counterparty, purpose, descriptor)`. The descriptor is what
# Meridian's one-column English export shows; the other two are the German
# banks' two fields. **The whole point is what they leave out.**


def mask(rng, rail: str, shop: str, handle: str, ref: str, bare_code: float = 0.25):
    up = _ascii_upper(shop)
    if rail == "pagolink":
        # The three shapes a wallet row actually takes, and the English export
        # has to show the SAME one — deriving Meridian's column from the shop
        # rather than from the variant handed the shop back for free, which is
        # exactly the information this rail is supposed to be hiding.
        roll = rng.random()
        if roll < 0.45:                       # names the shop outright
            shown = up
            pu = f"PP.{ref}.PP . {up}, Ihr Einkauf bei {shop}"
        elif roll < 0.75:                     # only the seller's trading handle
            shown = _ascii_upper(handle or shop)
            pu = f"PP.{ref}.PP . {handle or up}"
        else:                                 # truncated to nothing useful
            shown = up[:11]
            pu = f"PP.{ref}.PP . {up[:11]}"
        return f"PAGOLINK . {shown}", pu, f"PAGOLINK {shown}"
    if rail == "ratenwerk":
        return ("RATENWERK BANK AB",
                f"Kauf auf Rechnung, Vorgang {ref}",
                f"RATENWERK BANK AB {ref}")
    if rail == "warenlager":
        return ("WARENLAGER PAYMENTS EUROPE",
                f"WRNLGR MKTP DE {ref}",
                f"WRNLGR MKTP DE*{ref}")
    if rail == "rechnungsbruecke":
        return ("RECHNUNGSBRUECKE GMBH",
                f"Rechnung RB-{ref} Kd 44-11820",
                f"RECHNUNGSBRUECKE RB-{ref}")
    if rail == "kassenband":
        # Stripe's 22-character cap, applied to the whole descriptor.
        return (f"KASSENBAND * {up[:9]}",
                f"KB {ref}",
                f"KB* {up}"[:22])
    if rail == "zahlnetz":
        return ("ZAHLNETZ PAYMENTS",
                f"Bestellung {ref}",
                f"ZAHLNETZ PAYMENTS {ref}")
    if rail == "nordpfad":
        if rng.random() < 0.6:                # carries the shop, as intended
            return (f"NORDPFAD*{up[:16]}", f"Zahlung {ref}", f"NORDPFAD*{up[:16]}")
        return ("NORDPFAD*HANDELSGRUPPE OST",  # carries the chain instead
                f"Zahlung {ref}", "NORDPFAD*HANDELSGRUPPE OST")
    if rail == "kartenkopf":
        if rng.random() >= bare_code:
            return (f"KARTENKOPF *{shop}", f"Kartenzahlung {ref}",
                    f"KARTENKOPF *{shop}")
        return (f"KARTENKOPF MERCH {ref}", f"Kartenzahlung {ref}",
                f"KARTENKOPF MERCH {ref}")
    if rail == "tellerflink":
        return ("TELLERFLINK LIEFERSERVICE",
                f"Bestellung {ref}",
                f"TELLERFLINK BESTELLUNG {ref}")
    raise SystemExit(f"unknown rail {rail!r}")


# ------------------------------------------------------------- basket filling


def fill_basket(rng) -> list:
    by_sub = {}
    for label, sub, lo, hi in M.GROCERY_ITEMS:
        by_sub.setdefault(sub, []).append((label, lo, hi))
    lines = []
    for sub, chance, (n_lo, n_hi) in M.BASKET_SHAPE:
        if rng.random() > chance:
            continue
        pool = by_sub[sub]
        for _ in range(rng.randint(n_lo, n_hi)):
            label, lo, hi = pool[rng.randrange(len(pool))]
            lines.append((label, sub, _money(rng, lo, hi)))
    return lines


def till_basket(rng, merchant: str, lo: float, hi: float) -> list:
    """One visit's worth of what a shop sells, priced the way it prices it.

    Returns `(label, sub, amount)` lines summing to somewhere inside the shop's
    usual range — or an empty list for a shop whose goods are not written down,
    in which case the caller keeps its sampled amount and the row simply has no
    slip behind it.
    """
    spec = M.RECEIPT_BASKETS.get(merchant)
    if not spec:
        return []
    fixed, weighed = list(spec["fixed"]), list(spec["weighed"])
    rng.shuffle(fixed)
    lines, running = [], 0.0
    for label, price in fixed:
        if running + price > hi:
            continue
        lines.append((label, "till", price))
        running = round(running + price, 2)
        if len(lines) >= rng.randint(1, 3):
            break
    if weighed and running < hi - 2.0:
        # The price follows the weight at the shop's own rate, so the implied
        # EUR/kg is always one somebody would recognise. Drawing the two
        # independently gave cherries at 2,60 a kilo on one slip and 14,00 on
        # the next.
        label, rate_lo, rate_hi = weighed[rng.randrange(len(weighed))]
        rate = round(rng.uniform(rate_lo, rate_hi), 2)
        max_kilos = min(1.8, (hi - running) / rate)
        if max_kilos >= 0.3:
            kilos = round(rng.uniform(0.3, max_kilos), 3)
            price = round(kilos * rate, 2)
            lines.append((f"{label} {kilos:.3f} kg".replace(".", ",")
                          + f" x {rate:.2f}".replace(".", ","), "till", price))
            running = round(running + price, 2)
    if not lines or running < lo * 0.5:
        label, price = fixed[0]
        return [(label, "till", price)]
    return lines


# ----------------------------------------------------------------- the build


def build(seed: int = 42):
    rng = random.Random(seed)
    txns: list[Txn] = []
    refs = {"pagolink": 4410000, "ratenwerk": 880000, "warenlager": 302000,
            "rechnungsbruecke": 55100, "kassenband": 71200, "zahlnetz": 90400,
            "nordpfad": 66300, "kartenkopf": 21100, "tellerflink": 730000}

    def next_ref(rail: str) -> str:
        refs[rail] += rng.randint(3, 97)
        return str(refs[rail])

    shops = {s.name: s for s in M.HOUSEHOLD_SHOPS}
    online = {o.name: o for o in M.ONLINE_SHOPS}

    for (y, m) in months_in_window():
        ym = f"{y:04d}-{m:02d}"
        last_month = (y, m) == months_in_window()[-1]

        # --- standing charges ------------------------------------------
        for st in M.STANDING:
            if not _in_range(ym, st.first, st.last):
                continue
            if st.months and m not in st.months:
                continue
            amount, cp, purpose = st.amount, st.counterparty, st.purpose
            if st.code:
                code = _biller_code(st.code, st.slug, ym)
                cp, purpose = cp.replace("{code}", code), purpose.replace("{code}", code)
            if st.fx:
                currency, foreign = st.fx
                rate = M.FX_RATES[currency][ym]
                amount = -round(foreign * rate, 2)
                purpose = f"{purpose} {currency} {foreign:.2f} @ {rate:.4f}"
            txns.append(Txn(
                date=_clamp_day(y, m, st.day), account=st.account,
                amount=amount, booking=st.booking,
                counterparty=cp, purpose=purpose,
                descriptor=f"{cp} {purpose}"[:64],
                merchant=st.merchant, category=st.category, slug=st.slug,
            ))

        # --- the quarterly account charge ------------------------------
        if m in (3, 6, 9, 12):
            for acct, cp, booking, purpose, amount in M.QUARTERLY_FEES:
                txns.append(Txn(
                    date=_clamp_day(y, m, calendar.monthrange(y, m)[1]),
                    account=acct, amount=amount, booking=booking,
                    counterparty=cp, purpose=purpose,
                    descriptor=f"{cp} {purpose}",
                    merchant=cp.title(), category="Insurance and money",
                    slug="kontofuehrung",
                ))

        # --- the shops with their own terminals ------------------------
        for account, names in M.SHOPS_BY_ACCOUNT.items():
            for name in names:
                s = shops[name]
                times = int(s.per_month) + (1 if rng.random() < s.per_month % 1 else 0)
                for _ in range(times):
                    d = _clamp_day(y, m, rng.randint(1, 28))
                    amount = -_money(rng, s.lo, s.hi)
                    if s.rail:
                        ref = next_ref(s.rail)
                        cp, pu, desc = mask(rng, s.rail, s.name, "", ref,
                                            bare_code=s.bare_code)
                        # A card-terminal row is one paper slip, so where we know
                        # what the shop sells the AMOUNT COMES FROM THE BASKET.
                        # Sampling it and reconstructing a basket afterwards is
                        # what produced the 22,61 EUR bottle of oil.
                        basket = till_basket(rng, s.name, s.lo, s.hi)
                        if basket:
                            amount = -round(sum(a for _, _, a in basket), 2)
                        txns.append(Txn(
                            date=d, account=account, amount=amount,
                            booking="KARTENZAHLUNG", counterparty=cp, purpose=pu,
                            descriptor=desc, merchant=s.name, category=s.category,
                            rail=s.rail, evidence="none", items=basket,
                        ))
                    else:
                        term = s.terminal or _ascii_upper(s.name)
                        stamp = f"{d.strftime('%d.%m.')}{y} {rng.randint(8,20):02d}.{rng.randint(0,59):02d} UHR"
                        txns.append(Txn(
                            date=d, account=account, amount=amount,
                            booking="KARTENZAHLUNG", counterparty=term,
                            purpose=f"{term}//BERLIN/DE {stamp} KARTE 1",
                            descriptor=term, merchant=s.name,
                            category=s.category,
                        ))

        # --- the online grocer: a Lastschrift, and a basket behind it ---
        for _ in range(4 if rng.random() < 0.6 else 3):
            d = _clamp_day(y, m, rng.randint(2, 27))
            lines = fill_basket(rng)
            total = round(sum(a for _, _, a in lines), 2)
            order = f"KN-{y%100:02d}{m:02d}-{rng.randint(1000, 9999)}"
            txns.append(Txn(
                date=d, account="havelbank-joint", amount=-total,
                booking="LASTSCHRIFT", counterparty="KAUFHALLE NORD LIEFERDIENST",
                purpose=f"BESTELLUNG {order} MANDAT KN-2022-8841",
                descriptor=f"KAUFHALLE NORD LIEFERDIENST {order}",
                merchant="Kaufhalle Nord", category="Food and drink",
                evidence=f"grocer:{order}", items=lines, slug="kaufhalle-online",
            ))

        # --- everything bought through a rail --------------------------
        # Roughly one row in twelve, with a few more in the last month so the
        # round has work to show on the month the person opens first.
        n_rail = rng.randint(6, 9) + (4 if last_month else 0)
        for _ in range(n_rail):
            rail = _weighted(rng, M.RAIL_MIX)
            account = _weighted(rng, [
                ("havelbank-joint", 0.45), ("meridian-everyday", 0.35),
                ("nordufer-sam", 0.20)])
            if rail == "tellerflink":
                shop_name = M.DELIVERY_RESTAURANTS[
                    rng.randrange(len(M.DELIVERY_RESTAURANTS))]
                cat, lo, hi, goods, handle = "Going out", 14.0, 48.0, ["Abendessen"], ""
            else:
                o = _weighted(rng, [(x.name, x.weight) for x in M.ONLINE_SHOPS])
                sh = online[o]
                shop_name, cat, lo, hi = sh.name, sh.category, sh.lo, sh.hi
                goods, handle = sh.goods, sh.handle
            ref = next_ref(rail)
            cp, pu, desc = mask(rng, rail, shop_name, handle, ref)
            amount = -_money(rng, lo, hi)
            good = goods[rng.randrange(len(goods))] if goods else "Bestellung"
            d = _clamp_day(y, m, rng.randint(1, 28))
            txns.append(Txn(
                date=d, account=account, amount=amount, booking="LASTSCHRIFT",
                counterparty=cp, purpose=pu, descriptor=desc,
                merchant=shop_name, category=cat, rail=rail,
                evidence="pending", items=[(good, "order", -amount)],
                note=ref,
            ))

    # --- the year's lumps: holidays, Christmas, the washing machine -------
    for ev in M.EVENTS:
        d = date.fromisoformat(ev.when)
        if ev.rail:
            ref = ev.ref or next_ref(ev.rail)
            cp, pu, desc = mask(rng, ev.rail, ev.merchant, "", ref)
            txns.append(Txn(
                date=d, account=ev.account, amount=ev.amount, booking=ev.booking,
                counterparty=cp, purpose=pu, descriptor=desc,
                merchant=ev.merchant, category=ev.category, rail=ev.rail,
                evidence="pending", items=[(ev.goods or "Bestellung", "order",
                                            round(-ev.amount, 2))],
                slug=ev.slug, note=ref,
            ))
        else:
            txns.append(Txn(
                date=d, account=ev.account, amount=ev.amount, booking=ev.booking,
                counterparty=ev.counterparty, purpose=ev.purpose,
                descriptor=f"{ev.counterparty}",
                merchant=ev.merchant, category=ev.category, slug=ev.slug,
            ))

    return finish(txns, rng)


# ------------------------------------------------------- ids, order, evidence


def finish(txns: list[Txn], rng) -> dict:
    txns.sort(key=lambda t: (t.date, t.account))

    seq: dict[tuple, int] = {}
    for t in txns:
        key = (t.date, t.account)
        seq[key] = seq.get(key, 0) + 1
        t.txn_id = f"{t.date.isoformat()}-{t.account}-{seq[key]:02d}"

    balances = {k: v["opening"] for k, v in M.ACCOUNTS.items()}
    for t in txns:
        balances[t.account] = round(balances[t.account] + t.amount, 2)
        t.balance = balances[t.account]

    evidence = assign_evidence(txns, rng)
    evidence["photos"] = assign_photo_evidence(txns)
    return {"txns": txns, "evidence": evidence,
            "closing": balances, "checks": check(txns, evidence)}


# How often a rail's row has the thing that names it. The gaps are the point:
# `unnamed` is a real state in the contract, and a run that names everything
# proves nothing.
COVERAGE = {
    "pagolink": 0.72, "warenlager": 0.92, "ratenwerk": 1.00,
    "rechnungsbruecke": 0.62, "kassenband": 0.50, "zahlnetz": 0.55,
    "nordpfad": 0.50, "kartenkopf": 0.0, "tellerflink": 0.70,
}


def assign_evidence(txns: list[Txn], rng) -> dict:
    """Decide, per rail row, whether the thing that names it exists — and if it
    does, put it where a person would actually go and find it."""
    mail, grocer, marketplace, bnpl = [], [], [], []

    for t in txns:
        if t.evidence.startswith("grocer:"):
            grocer.append({
                "order": t.evidence.split(":", 1)[1],
                "date": t.date.isoformat(),
                "total": round(-t.amount, 2),
                "account": t.account,
                "txn_id": t.txn_id,
                "lines": [{"label": lbl, "sub": sub, "amount": round(a, 2)}
                          for lbl, sub, a in t.items],
            })
            continue
        if t.evidence != "pending":
            continue

        ref = t.note
        has = rng.random() < COVERAGE.get(t.rail, 0.5)
        item = t.items[0][0] if t.items else "Bestellung"
        amount = round(-t.amount, 2)

        if not has:
            t.evidence = "none"
        elif t.rail == "warenlager":
            t.evidence = f"marketplace:{ref}"
            marketplace.append({
                "order": ref, "date": t.date.isoformat(), "total": amount,
                "shop": t.merchant, "txn_id": t.txn_id,
                "lines": [{"label": item, "amount": amount}],
            })
        elif t.rail == "ratenwerk":
            t.evidence = f"bnpl:{ref}"
            bnpl.append({
                "purchase": ref, "date": t.date.isoformat(), "total": amount,
                "shop": t.merchant, "txn_id": t.txn_id, "kind": "Rechnungskauf",
                "lines": [{"label": item, "amount": amount}],
            })
        else:
            t.evidence = f"mail:{ref}"
            mail.append({
                "id": ref, "date": t.date.isoformat(),
                "from": f"{t.merchant}",
                "subject": f"Ihre Bestellung bei {t.merchant}",
                "total": amount, "txn_id": t.txn_id, "rail": t.rail,
                "lines": [{"label": item, "amount": amount}],
            })
        t.note = ""

    for bucket in (mail, grocer, marketplace, bnpl):
        bucket.sort(key=lambda r: r["date"])
    return {"mail": mail, "grocer": grocer,
            "marketplace": marketplace, "bnpl": bnpl}


def assign_photo_evidence(txns: list[Txn], wanted: int = 6) -> list:
    """A handful of rows whose only witness is a photograph of the till receipt.

    These are the market-stall and bar rows where the terminal printed a bare
    merchant code: no email, no order history, nothing online at all. What a
    person actually has is the slip, photographed on a kitchen table — so *Find
    out for sure* has a source to ask for, and asking for it is the one moment
    the round looks at the photo library at all.

    Chosen from the second half of the window and spread across months, because
    six receipts in one week is a person who has just been told to photograph
    receipts, not a person who happens to have some.
    """
    # ⛔ `evidence == "none"` is NOT the filter. A `KARTENKOPF *Marktstand
    # Gruenwinkel` row has no email and needs none: the bank already named the
    # shop. A photograph is only worth having where the terminal printed a bare
    # merchant code, so the pool is the HIDDEN rows.
    pool = [t for t in txns
            if t.rail == "kartenkopf" and t.evidence == "none"
            and not names_the_shop(t)
            and (t.date.year, t.date.month) >= months_in_window()[3]]

    # Spread across BOTH merchants and months. Taking the pool in date order
    # gives six slips from the same cafe, because the cafe is the most frequent
    # stall-terminal shop; taking the newest of each merchant gives six slips
    # from one fortnight, which is a person who has just been told to photograph
    # receipts rather than a person who happens to have some.
    by_merchant: dict[str, list[Txn]] = {}
    for t in pool:
        by_merchant.setdefault(t.merchant, []).append(t)
    for rows in by_merchant.values():
        rows.sort(key=lambda t: t.date)

    per = -(-wanted // max(1, len(by_merchant)))       # ceiling division
    picked: list[Txn] = []
    for merchant in sorted(by_merchant):
        rows = by_merchant[merchant]
        take = min(per, len(rows))
        for k in range(take):
            # evenly along that merchant's own run of rows
            picked.append(rows[round(k * (len(rows) - 1) / max(1, take - 1))
                               if take > 1 else len(rows) // 2])
    seen, unique = set(), []
    for t in picked:
        if t.txn_id not in seen:
            seen.add(t.txn_id)
            unique.append(t)
    picked = sorted(unique, key=lambda t: t.date)[:wanted]

    out = []
    for t in picked:
        slug = "".join(c if c.isalnum() else "-" for c in t.merchant.lower())
        slug = "-".join(x for x in slug.split("-") if x)
        stem = f"{t.date.strftime('%Y%m%d')}-{slug}"
        t.evidence = f"photo:{stem}"
        out.append({
            "stem": stem, "date": t.date.isoformat(), "merchant": t.merchant,
            "total": round(-t.amount, 2), "txn_id": t.txn_id,
            "account": t.account, "bank_text": t.counterparty,
            "items": [(label, round(amount, 2)) for label, _, amount in t.items],
        })
    return out


# ------------------------------------------------------- the invariant checks


def names_the_shop(t: Txn) -> bool:
    """Does the bank's own text give the shop away?

    The question the brief's *one row in twelve* is about, and it has to be
    asked of the rendered row rather than of the rail: `KARTENKOPF *Bar
    Nachtkarte` names the shop and `KARTENKOPF MERCH 21118` does not, and they
    are the same rail on the same day.
    """
    haystack = f"{t.counterparty} {t.purpose} {t.descriptor}".upper()
    # Any substantial word will do — the FIRST word is not enough, and taking it
    # called `KARTENKOPF *Bar Nachtkarte` a hidden row because `Bar` is three
    # letters. A person reading that line knows exactly which bar it was.
    words = [w for w in _ascii_upper(t.merchant).split() if len(w) >= 4]
    return any(w in haystack for w in words)


def check(txns: list[Txn], evidence: dict) -> dict:
    """Recompute every planted finding from the finished ledger.

    A figure written by hand into `PLANTED.md` drifts the first time a weight
    changes, and nothing says so. These are measured, and anything that has
    stopped being true raises rather than shipping a fixture that contradicts
    its own answer key.
    """
    out: dict = {}

    def total(pred) -> float:
        return round(sum(-t.amount for t in txns if pred(t)), 2)

    out["bildstrom-joint"] = {
        "charges": sum(1 for t in txns if t.slug == "bildstrom-joint"),
        "paid_so_far": total(lambda t: t.slug == "bildstrom-joint"),
        "annual_if_left": round(12 * 14.99, 2),
        "first": min(t.date.isoformat() for t in txns if t.slug == "bildstrom-joint"),
    }
    uk = sorted((t for t in txns if t.slug == "prime-uk"), key=lambda t: t.date)
    de = sorted((t for t in txns if t.slug == "prime-de"), key=lambda t: t.date)
    de_months = {(t.date.year, t.date.month) for t in de}
    overlap_uk = [t for t in uk if (t.date.year, t.date.month) in de_months]
    out["prime-doppelt"] = {
        "uk_charges": len(uk), "uk_paid_in_window_eur": total(lambda t: t.slug == "prime-uk"),
        "uk_gbp_each": 8.99,
        "de_charges": len(de), "de_paid_in_window_eur": total(lambda t: t.slug == "prime-de"),
        "de_first": de[0].date.isoformat() if de else "",
        "months_billed_twice": len(overlap_uk),
        "uk_paid_during_overlap_eur": round(sum(-t.amount for t in overlap_uk), 2),
        "annual_uk_eur": round(12 * -uk[-1].amount, 2) if uk else 0.0,
    }
    out["bildstrom-rise"] = {
        "before": 12.99, "after": 14.99, "from": "2026-02",
        "extra_a_year": round(12 * (14.99 - 12.99), 2),
    }
    out["kraftkammer"] = {
        "charges": sum(1 for t in txns if t.slug == "kraftkammer"),
        "paid_in_window": total(lambda t: t.slug == "kraftkammer"),
        "annual": round(12 * 34.90, 2),
        "last_visit": "2026-03-07",
        "paid_since_last_visit": total(
            lambda t: t.slug == "kraftkammer" and t.date > date(2026, 3, 7)),
    }
    out["warenlager-plus"] = {
        "charges": sum(1 for t in txns if t.slug == "warenlager-plus"),
        "paid_so_far": total(lambda t: t.slug == "warenlager-plus"),
        "annual": round(12 * 4.99, 2),
        "trial_started": "2025-11-03", "first_charge": "2025-12-03",
    }
    doubled = [t for t in txns if t.slug == "hausrat-alt"
               and t.date >= date(2026, 1, 1)]
    out["hausrat-doppelt"] = {
        "collections_after_the_switch": len(doubled),
        "claimable": round(sum(-t.amount for t in doubled), 2),
        "dates": [t.date.isoformat() for t in doubled],
    }
    out["strom-runter"] = {
        "before": 118.00, "after": 94.00, "from": "2026-01",
        "saved_a_year": round(12 * (118.00 - 94.00), 2),
    }

    # How many rows the bank text cannot name — the figure the brief sets at
    # roughly one in twelve. Measured rather than assumed: a rail that happens
    # to print the shop is not a hidden row, whatever rail it is.
    hidden = [t for t in txns if t.rail and not names_the_shop(t)]
    out["hidden-rows"] = {
        "hidden": len(hidden),
        "rows": len(txns),
        "one_in": round(len(txns) / len(hidden), 1) if hidden else 0,
        "with_evidence": sum(1 for t in hidden if t.evidence != "none"),
        "with_nothing": sum(1 for t in hidden if t.evidence == "none"),
        "in_the_last_month": sum(
            1 for t in hidden
            if (t.date.year, t.date.month) == months_in_window()[-1]),
        "by_rail": {r: sum(1 for t in hidden if t.rail == r)
                    for r in sorted({t.rail for t in hidden})},
    }

    sweets = meat = notfood = grocery = 0.0
    for order in evidence["grocer"]:
        for line in order["lines"]:
            grocery += line["amount"]
            if line["sub"] == "sweets":
                sweets += line["amount"]
            elif line["sub"] == "meatfish":
                meat += line["amount"]
            if line["sub"] in M.NOT_FOOD:
                notfood += line["amount"]
    out["sweets-vs-meat"] = {
        "sweets_and_ice_cream": round(sweets, 2),
        "fish_and_meat": round(meat, 2),
        "grocer_total": round(grocery, 2),
        "not_food": round(notfood, 2),
        "not_food_share": round(100 * notfood / grocery, 1) if grocery else 0.0,
        "orders": len(evidence["grocer"]),
    }

    # ⛔ The asserts below are the reason this function exists. Reintroduce a
    # weight that breaks one and the generator refuses to write anything.
    if sweets <= meat:
        raise SystemExit(
            "PLANTED.md claims sweets and ice cream outspend fish and meat, and "
            f"this ledger has sweets {sweets:.2f} against meat {meat:.2f}. "
            "Fix BASKET_SHAPE in model.py or drop the finding — do not ship a "
            "fixture that contradicts its own answer key.")
    if out["hausrat-doppelt"]["collections_after_the_switch"] != 3:
        raise SystemExit(
            "the insurance finding wants the old insurer collecting through the "
            "whole of the first quarter (three collections) and this ledger has "
            f"{out['hausrat-doppelt']['collections_after_the_switch']}. Either "
            "the mandate's `last` moved or the switch date did.")
    if out["bildstrom-joint"]["charges"] < 8:
        raise SystemExit("the duplicate membership is too short to be findable: "
                         f"{out['bildstrom-joint']['charges']} charges.")
    if out["prime-doppelt"]["months_billed_twice"] < 6:
        raise SystemExit("the doubled Prime is too short to be found by a "
                         "recurring-charge read: billed twice in "
                         f"{out['prime-doppelt']['months_billed_twice']} months.")
    if len({t.amount for t in uk}) < 3:
        raise SystemExit("the UK Prime should move with the exchange rate; "
                         "its EUR amounts are all but identical.")
    if out["kraftkammer"]["charges"] != 13:
        raise SystemExit("the gym should be charged in every month of the window; "
                         f"it is charged {out['kraftkammer']['charges']} times.")
    return out
