"""Write the ledger out — as three banks' exports, as the portals' source data,
and as the answer key.

Nothing here invents a figure. Every number is read off the ledger `build.py`
produced, which is what lets the grocer's order history reconcile to a statement
row to the cent and `PLANTED.md` quote a total somebody can check.

## The three dialects, and what is deliberate about each

| file | separator | decimals | dates | encoding |
|---|---|---|---|---|
| `meridian-everyday-*.csv` | `,` | `1234.56` | `YYYY-MM-DD` | UTF-8 |
| `havelbank-joint-*.csv` | `;` | `1.234,56` | `TT.MM.JJJJ` | **UTF-8 with a BOM** |
| `nordufer-sam-*.csv` | `;`, every field quoted | `1234,56` | `TT.MM.JJJJ` | **cp1252** |

The BOM and the cp1252 are not decoration. A German bank export really does
arrive as one or the other, the BOM really does turn the first header into
`\\ufeffBuchungstag` for anything that reads the file naively, and Nordufer
really does split the amount across `Soll` and `Haben` so the sign lives in
which column it is in rather than in the number. The agent is the parser; a run
that only ever meets one well-behaved UTF-8 CSV has not met a bank.
"""

from __future__ import annotations

import csv
import io
import json
from datetime import timedelta
from pathlib import Path

from . import model as M
from .build import Txn, months_in_window, window_tag


def _de(amount: float, thousands: bool) -> str:
    s = f"{abs(amount):,.2f}" if thousands else f"{abs(amount):.2f}"
    s = s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return ("-" if amount < 0 else "") + s


def _dm(d) -> str:
    return d.strftime("%d.%m.%Y")


def _valuta(t: Txn):
    """Wertstellung. A card payment settles the same day; a Lastschrift or a
    standing order is commonly value-dated a day later."""
    return t.date if t.booking in ("KARTENZAHLUNG", "") else t.date + timedelta(days=1)


# --------------------------------------------------------------- the dialects


def meridian_csv(rows: list[Txn]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(["Date", "Description", "Amount (EUR)", "Balance (EUR)", "Type"])
    for t in rows:
        kind = ("CREDIT" if t.amount > 0
                else "CARD" if t.booking == "KARTENZAHLUNG" else "DEBIT")
        w.writerow([t.date.isoformat(), t.descriptor,
                    f"{t.amount:.2f}", f"{t.balance:.2f}", kind])
    return buf.getvalue().encode("utf-8")


def havelbank_csv(rows: list[Txn]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\r\n")
    w.writerow(["Buchungstag", "Wertstellung", "Buchungstext",
                "Beguenstigter/Zahlungspflichtiger", "Verwendungszweck",
                "Betrag", "Waehrung", "Saldo"])
    for t in rows:
        w.writerow([_dm(t.date), _dm(_valuta(t)), t.booking, t.counterparty,
                    t.purpose, _de(t.amount, True), "EUR", _de(t.balance, True)])
    # The BOM is the point: it is what a German bank's export carries, and it is
    # the thing that turns the first column header into a name no parser expects.
    return b"\xef\xbb\xbf" + buf.getvalue().encode("utf-8")


def nordufer_csv(rows: list[Txn]) -> bytes:
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", quoting=csv.QUOTE_ALL, lineterminator="\r\n")
    w.writerow(["Buchung", "Valuta", "Auftraggeber/Empfaenger", "Buchungstext",
                "Verwendungszweck", "Soll", "Haben", "Saldo", "Waehrung"])
    for t in rows:
        soll = _de(-t.amount, False) if t.amount < 0 else ""
        haben = _de(t.amount, False) if t.amount > 0 else ""
        w.writerow([_dm(t.date), _dm(_valuta(t)), t.counterparty, t.booking,
                    t.purpose, soll, haben, _de(t.balance, False), "EUR"])
    # cp1252, with `errors="replace"` deliberately ABSENT: a character this
    # encoding cannot carry is a fact about the fixture worth failing on, not a
    # question mark to ship.
    return buf.getvalue().encode("cp1252")


WRITERS = {"meridian": meridian_csv, "havelbank": havelbank_csv,
           "nordufer": nordufer_csv}


# ------------------------------------------------------------------- statements


def write_statements(out: Path, txns: list[Txn]) -> list[Path]:
    made = []
    stmts = out / "statements"
    stmts.mkdir(parents=True, exist_ok=True)
    for slug, acct in M.ACCOUNTS.items():
        writer = WRITERS[acct["dialect"]]
        mine = [t for t in txns if t.account == slug]
        for (y, m) in months_in_window():
            rows = [t for t in mine if (t.date.year, t.date.month) == (y, m)]
            path = stmts / f"{slug}-{y:04d}-{m:02d}.csv"
            path.write_bytes(writer(rows))
            made.append(path)
        # The whole window in one file, because that is what a person who knows
        # their bank's date picker actually downloads. Generated in the same run
        # from the same rows, so the two cannot disagree.
        path = stmts / f"{slug}-{window_tag()}.csv"
        path.write_bytes(writer(mine))
        made.append(path)
    return made


# -------------------------------------------------------------------- evidence


def write_evidence(out: Path, ev: dict, txns: list[Txn]) -> list[Path]:
    """The portals' source data — read and served by the end-to-end harness,
    which holds no second copy of any figure in here."""
    made = []
    d = out / "evidence"
    d.mkdir(parents=True, exist_ok=True)

    def dump(name, obj):
        p = d / name
        p.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n")
        made.append(p)

    dump("mail.json", {
        "mailbox": "carter.okafor@haushalt.example",
        "note": "Receipt and order-confirmation emails. Every one names a shop "
                "and an amount that a statement row does not.",
        "messages": ev["mail"] + standing_mail(txns),
    })
    dump("grocer-orders.json", {
        "shop": "Kaufhalle Nord Lieferdienst",
        "account": "carter.okafor@haushalt.example",
        "note": "Each order reconciles to one KAUFHALLE NORD LIEFERDIENST row "
                "to the cent. The line items are the only place the household's "
                "food is broken down at all.",
        "orders": ev["grocer"],
    })
    dump("marketplace-orders.json", {
        "shop": "Warenlager",
        "note": "Order history and memberships. The bank row names the "
                "marketplace and never the item.",
        "orders": ev["marketplace"],
        "memberships": [{
            "name": "Warenlager Plus",
            "started": "2025-11-03",
            "trial_days": 30,
            "first_payment": "2025-12-03",
            "price_eur": 4.99,
            "renews": "monthly",
            "next_renewal": "2026-07-03",
            "status": "active",
            "note": "Trial started 3 November 2025, first payment 3 December 2025.",
        }],
    })
    dump("bnpl-purchases.json", {
        "bank": "Ratenwerk Bank AB",
        "note": "Rechnungskauf and Ratenkauf. The statement shows only "
                "RATENWERK BANK AB and a Vorgang number; this is where the shop "
                "is written down.",
        "purchases": ev["bnpl"],
    })
    dump("streaming-account.json", streaming_account(txns))
    dump("gym-account.json", gym_account(txns))
    dump("photo-evidence.json", {
        "note": "Rows whose only witness is a photograph of the till receipt. "
                "The scans are rendered into receipt-photo-sources/ and "
                "composited into the photo library by generate/photos/.",
        "rows": ev["photos"],
    })
    return made


def standing_mail(txns: list[Txn]) -> list:
    """The letters that explain the standing charges.

    These are the ones a planted finding leans on — a price rise, a tariff
    change, a cancellation confirmation — and they are written here rather than
    generated from a row because each one is a document a company sent, not a
    payment that happened.
    """
    def first(slug):
        rows = sorted((t for t in txns if t.slug == slug), key=lambda t: t.date)
        return rows[0] if rows else None

    prime_de = first("prime-de")
    # ⚠️ The only real brand in the mailbox (see STANDING in model.py). Plain
    # mail text naming the membership and the account it is billed to: enough
    # for an agent to name both rows, and nothing that imitates Amazon's site.
    prime = [
        {"id": "amazon-de-prime-start", "date": prime_de.date.isoformat(),
         "from": "Amazon.de",
         "subject": "Willkommen bei Amazon Prime",
         "total": 8.99, "txn_id": prime_de.txn_id, "rail": None,
         "lines": [{"label": "Mitglied: Alex Carter", "amount": 0.0},
                   {"label": "Prime-Mitgliedschaft, monatlich", "amount": 8.99},
                   {"label": "Zahlungsart: Lastschrift, Havelbank Girokonto …88 02",
                    "amount": 0.0}]},
        {"id": "amazon-uk-prime-renewal", "date": "2026-05-26",
         "from": "Amazon.co.uk", "currency": "GBP",
         "subject": "Your Amazon Prime membership renews on 9 June",
         "total": 8.99, "txn_id": "", "rail": None,
         "lines": [{"label": "Member: Alex Carter", "amount": 0.0},
                   {"label": "Prime monthly membership (GBP)", "amount": 8.99},
                   {"label": "Payment card: Meridian Everyday", "amount": 0.0},
                   {"label": "Member since 14 March 2019", "amount": 0.0}]},
    ] if prime_de else []
    return prime + [
        {"id": "bildstrom-preis", "date": "2026-01-12",
         "from": "Bildstrom Media GmbH",
         "subject": "Änderung Ihres Mitgliedsbeitrags ab Februar",
         "total": 14.99, "txn_id": "", "rail": None,
         "lines": [{"label": "Bisher 12,99 EUR monatlich", "amount": 12.99},
                   {"label": "Ab 01.02.2026 14,99 EUR monatlich", "amount": 14.99}]},
        {"id": "spreelicht-abschlag", "date": "2025-12-09",
         "from": "Spreelicht Energie GmbH",
         "subject": "Ihre neue Abschlagshöhe ab Januar 2026",
         "total": 94.00, "txn_id": "", "rail": None,
         "lines": [{"label": "Abschlag bisher (monatlich)", "amount": 118.00},
                   {"label": "Abschlag ab 01.01.2026 (monatlich)", "amount": 94.00},
                   {"label": "Kundennummer 88-114-203", "amount": 0.0}]},
        {"id": "nordstern-kuendigung", "date": "2025-11-24",
         "from": "Nordstern Versicherung AG",
         "subject": "Bestätigung Ihrer Kündigung — Hausratversicherung",
         "total": 0.0, "txn_id": "", "rail": None,
         "lines": [{"label": "Vertrag NV-2019-4471 endet am 31.12.2025", "amount": 0.0},
                   {"label": "Letzter Beitragseinzug Dezember 2025", "amount": 18.40}]},
        {"id": "blauschild-police", "date": "2025-12-18",
         "from": "Blauschild Versicherung AG",
         "subject": "Ihre neue Hausratversicherung — Police BS-2026-8812",
         "total": 21.90, "txn_id": "", "rail": None,
         "lines": [{"label": "Versicherungsbeginn 01.01.2026", "amount": 0.0},
                   {"label": "Monatsbeitrag", "amount": 21.90}]},
        {"id": "warenlager-plus-trial", "date": "2025-11-03",
         "from": "Warenlager", "subject": "Ihre Warenlager-Plus-Testphase hat begonnen",
         "total": 0.0, "txn_id": "", "rail": None,
         "lines": [{"label": "Kostenlos bis 03.12.2025", "amount": 0.0},
                   {"label": "Danach 4,99 EUR monatlich", "amount": 4.99}]},
    ]


def streaming_account(txns: list[Txn]) -> dict:
    """Bildstrom's own account page: two memberships on one household, what each
    costs, and — the whole reason this portal exists — when each was last
    watched. The cancel flow ends on a page naming the end date, because a
    clicked button is not a cancellation."""
    def charges(slug):
        return [{"date": t.date.isoformat(), "amount": round(-t.amount, 2),
                 "txn_id": t.txn_id} for t in txns if t.slug == slug]

    return {
        "service": "Bildstrom",
        "note": "Two memberships, one household. Nobody watches the second.",
        "memberships": [
            {"id": "1140-229", "label": "Bildstrom Familie",
             "holder": "Alex Carter", "paid_from": "Meridian Everyday",
             "started": "2024-03-06", "status": "active",
             "price_now": 14.99, "price_before": 12.99, "price_changed": "2026-02-01",
             "last_watched": "2026-06-24",
             "recent_activity": [
                 {"when": "2026-06-24", "what": "Die Lange Nacht, Folge 4"},
                 {"when": "2026-06-18", "what": "Nordwand (Film)"},
                 {"when": "2026-06-09", "what": "Die Lange Nacht, Folge 3"},
                 {"when": "2026-05-30", "what": "Kinderstunde, Folge 12"}],
             "charges": charges("bildstrom-alex")},
            {"id": "5512-887", "label": "Bildstrom Familie",
             "holder": "Sam Okafor", "paid_from": "Havelbank Girokonto (gemeinsam)",
             "started": "2025-10-14", "status": "active",
             "price_now": 14.99, "price_before": 12.99, "price_changed": "2026-02-01",
             "last_watched": None,
             "recent_activity": [],
             "charges": charges("bildstrom-joint")},
        ],
        "cancel": {
            "cancellable": ["5512-887", "1140-229"],
            "ends_on": "2026-07-14",
            "confirmation": "Ihre Mitgliedschaft {id} endet am 14.07.2026. "
                            "Bis dahin können Sie Bildstrom weiter nutzen.",
        },
    }


def gym_account(txns: list[Txn]) -> dict:
    """Kraftkammer's members' area. The check-in list is the evidence, and it
    stops in March — which is a fact the rows cannot show and the person may
    well not remember."""
    visits = [
        "2026-03-07", "2026-03-01", "2026-02-24", "2026-02-19", "2026-02-11",
        "2026-02-03", "2026-01-28", "2026-01-21", "2026-01-14", "2026-01-07",
        "2025-12-17", "2025-12-09", "2025-11-26", "2025-11-18", "2025-11-11",
        "2025-10-29", "2025-10-21", "2025-10-14", "2025-10-02", "2025-09-24",
        "2025-09-16", "2025-09-08", "2025-08-26", "2025-07-30", "2025-07-22",
        "2025-07-15", "2025-07-08", "2025-06-24", "2025-06-17", "2025-06-10",
    ]
    return {
        "gym": "Kraftkammer Kreuzberg",
        "member": "Alex Carter",
        "member_no": "KK-4471",
        "plan": "Mitgliedschaft Standard",
        "price": 34.90,
        "since": "2023-09-01",
        "status": "active",
        "last_check_in": visits[0],
        "check_ins": visits,
        "note": "Check-ins, newest first. Nothing since 7 March 2026.",
        "charges": [{"date": t.date.isoformat(), "amount": round(-t.amount, 2),
                     "txn_id": t.txn_id}
                    for t in txns if t.slug == "kraftkammer"],
        "cancel": {"notice_months": 1, "ends_on": "2026-07-31",
                   "confirmation": "Ihre Mitgliedschaft KK-4471 endet am 31.07.2026."},
    }


# ------------------------------------------------------------------ answer key


def write_planted(out: Path, checks: dict, txns: list[Txn]) -> Path:
    c = checks
    lines = [
        "# PLANTED — what is in the Carter-Okafor household's money, and what it costs",
        "",
        "**This is an answer key. It is not seeded into any vault and must never be.**",
        "A run is graded against what was planted, not against what the agent happened",
        "to say — otherwise a confident wrong answer and a correct one read the same.",
        "",
        "Every figure below is **measured from the generated ledger** by",
        "`generate/household/build.py::check`, which raises rather than writing a",
        "fixture that contradicts this file. Regenerate both together:",
        "",
        "```sh",
        "python3 generate/gen_household.py --seed 42",
        "```",
        "",
        "## The shape of the year",
        "",
        f"- **{len(txns)} transactions**, {M.WINDOW_START} to {M.WINDOW_END}, across three instruments.",
        f"- **{c['hidden-rows']['hidden']} of them** — one in {c['hidden-rows']['one_in']} —"
        " are behind a payment rail whose text does not name the shop.",
        f"  {c['hidden-rows']['with_evidence']} of those can be resolved from evidence that exists;"
        f" **{c['hidden-rows']['with_nothing']} cannot be resolved at all** and `unnamed` is the right answer for them.",
        f"  {c['hidden-rows']['in_the_last_month']} fall in June 2026, the month the person opens first.",
        "",
        "| rail | hidden rows |",
        "|---|---|",
    ]
    for rail, n in sorted(c["hidden-rows"]["by_rail"].items(),
                          key=lambda kv: -kv[1]):
        lines.append(f"| {M.RAILS[rail].name} | {n} |")
    lines += ["",
              "## The findings", ""]

    for f in M.PLANTED:
        m = c[f["measure"]]
        lines += [f"### {f['title']}", "",
                  f"- **What.** {f['what']}",
                  f"- **Where.** {f['where']}",
                  f"- **The evidence.** {f['evidence']}",
                  f"- **The verdict.** {f['verdict']}",
                  "- **Measured:**", ""]
        for k, v in m.items():
            if isinstance(v, list):
                v = ", ".join(str(x) for x in v)
            lines.append(f"  - `{k}`: {v}")
        lines.append("")

    recoverable = (c["bildstrom-joint"]["annual_if_left"]
                   + c["prime-doppelt"]["annual_uk_eur"]
                   + c["kraftkammer"]["annual"]
                   + c["warenlager-plus"]["annual"])
    lines += [
        "## The totals a graded run should arrive at", "",
        "| | a year | already paid in the window |",
        "|---|---|---|",
        f"| Duplicate streaming membership | {c['bildstrom-joint']['annual_if_left']:.2f} EUR"
        f" | {c['bildstrom-joint']['paid_so_far']:.2f} EUR |",
        f"| Amazon Prime billed twice (UK, in GBP) | {c['prime-doppelt']['annual_uk_eur']:.2f} EUR"
        f" | {c['prime-doppelt']['uk_paid_during_overlap_eur']:.2f} EUR during the overlap |",
        f"| Gym, unvisited since March | {c['kraftkammer']['annual']:.2f} EUR"
        f" | {c['kraftkammer']['paid_since_last_visit']:.2f} EUR since the last visit |",
        f"| Marketplace membership from an uncancelled trial | {c['warenlager-plus']['annual']:.2f} EUR"
        f" | {c['warenlager-plus']['paid_so_far']:.2f} EUR |",
        f"| **Recoverable by cancelling, a year** | **{recoverable:.2f} EUR** | |",
        f"| Insurance collected twice — claimable, not saved | — | {c['hausrat-doppelt']['claimable']:.2f} EUR |",
        "",
        "Two more that are **not** savings and must not be counted as any:",
        "",
        f"- the streaming price rise costs **{c['bildstrom-rise']['extra_a_year']:.2f} EUR a year** more than it did;",
        f"- the electricity tariff change already saves **{c['strom-runter']['saved_a_year']:.2f} EUR a year**,"
        " and belongs in *what changed*.",
        "",
        "## Where the food went", "",
        f"Across {c['sweets-vs-meat']['orders']} online grocery orders totalling"
        f" **{c['sweets-vs-meat']['grocer_total']:.2f} EUR**:",
        "",
        f"- sweets and ice cream: **{c['sweets-vs-meat']['sweets_and_ice_cream']:.2f} EUR**",
        f"- all fish and meat: **{c['sweets-vs-meat']['fish_and_meat']:.2f} EUR**",
        f"- not food at all (cleaning, nappies, toiletries): **{c['sweets-vs-meat']['not_food']:.2f} EUR**,"
        f" {c['sweets-vs-meat']['not_food_share']}% of the grocery bill",
        "",
        "None of this is visible from a bank statement, which only ever says",
        "`KAUFHALLE NORD LIEFERDIENST` and a number. It is visible from the order",
        "history, one basket at a time, and that is the point of the scene.",
        "",
        "⛔ **Analysis, never advice.** The finding is the two figures. What a",
        "household eats is not ours to have an opinion about.",
        "",
    ]
    p = out / "PLANTED.md"
    p.write_text("\n".join(lines))
    return p


# -------------------------------------------------------------------- manifest


def write_manifest(out: Path, paths: list[Path]) -> Path:
    rel = sorted(str(p.relative_to(out)) for p in paths)
    p = out / "MANIFEST.txt"
    p.write_text("\n".join(rel) + "\n")
    return p


# ------------------------------------------------- the receipts to photograph


def write_receipt_spec(out: Path, photos: list) -> Path:
    """The spec `gen_receipts.py --spec` renders into scans.

    The items are the ones the LEDGER already built the amount from
    (`build.till_basket`), so the slip and the bank row agree to the cent by
    construction rather than by adjustment — and `--spec` refuses a spec whose
    items do not sum to its stated total, which is the check this relies on
    rather than duplicates.
    """
    spec = []
    for i, row in enumerate(photos):
        if not row.get("items"):
            raise SystemExit(
                f"{row['stem']}: no basket. A till receipt has to list "
                "something; add the shop to RECEIPT_BASKETS in model.py.")
        lo, hi = M.RECEIPT_BASKETS[row["merchant"]]["open"]
        hour = lo + (i * 3) % max(1, hi - lo)
        spec.append({
            "merchant": row["merchant"],
            "when": f"{row['date']}T{hour:02d}:{(11 + i * 7) % 60:02d}",
            "total": row["total"],
            "items": [[label, amount] for label, amount in row["items"]],
            "_row": row["txn_id"],
        })
    p = out / "receipt-spec.json"
    p.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n")
    return p
