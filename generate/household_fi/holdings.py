"""What the Heikkilä-Brooks household owns: delivery B.

Three portals' records, built from the same ledger as everything else so the
monthly transfers in the rows and the subscriptions at the broker cannot
disagree about a cent:

| record | portal | what Mind My Money 0.2.0 reads from it |
|---|---|---|
| `broker.json` | Kanerva Invest | holdings in four funds; two overlap; a yearly costs and charges report for three of them and none for the fourth |
| `loan.json` | Kuusikko Pankki's loan page | balance, margin, reference rate, the next reset date, and each instalment split into interest and principal |
| `pension.json` | Peruskivi Eläkevakuutus | Daniel's earnings-related pension record: accrued monthly pension, an estimate at retirement age, the date it was read. **No balance** |

**Every company here is invented**, the funds' holdings included: a global
index fund's top ten are the most screenshotted names in finance, so they are
replaced by companies that do not exist. Every ISIN carries a valid check digit
and belongs to no fund.

Each one is found **from the rows**, as the bills plan says a source is: the
monthly `KANERVA INVEST OY` transfers (Noora's reference ends `…1`, Daniel's
`…2`), the `LAINAN LYHENNYS` rows from the joint account, and Daniel's YEL
payments to Peruskivi.

The prices use their own random stream (`seed + 7`), so building delivery B
leaves every row of delivery A byte for byte as it was.
"""

from __future__ import annotations

import random
from datetime import date, timedelta

from . import model as M


# --------------------------------------------------------------- identifiers


def isin(country: str, nsin: str) -> str:
    """An ISIN with a valid check digit (ISO 6166: letters to numbers, Luhn)."""
    body = country + nsin
    digits = "".join(str(int(c, 36)) for c in body)
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 0:
            n *= 2
            n = n - 9 if n > 9 else n
        total += n
    return body + str((10 - total % 10) % 10)


def isin_ok(code: str) -> bool:
    digits = "".join(str(int(c, 36)) for c in code)
    total = 0
    for i, ch in enumerate(reversed(digits)):
        n = int(ch)
        if i % 2 == 1:
            n *= 2
            n = n - 9 if n > 9 else n
        total += n
    return total % 10 == 0


# ------------------------------------------------------------------- the funds

FUNDS = {
    "maailma": {
        "name": "Kanerva Maailma Indeksi A",
        "manager": "Kanerva Rahastoyhtiö Oy",
        "isin": isin("FI", "400071325"),
        "kind": "Osakerahasto, globaali indeksi",
        "risk": 4,
        "ongoing": 0.25, "transaction": 0.02, "entry_fee": 0.0,
        "drift": 0.006, "vol": 0.035, "start_nav": 11.8204,
        "regions": [("Pohjois-Amerikka", 64.2), ("Eurooppa", 17.8), ("Japani", 6.1),
                    ("Muu Aasia ja Tyynimeri", 7.4), ("Muut", 4.5)],
        "top": [("Arkanen Systems Inc.", "Yhdysvallat", 4.8),
                ("Pelton Semiconductor Corp.", "Yhdysvallat", 4.1),
                ("Northway Software Inc.", "Yhdysvallat", 3.9),
                ("Harrowgate Retail Co.", "Yhdysvallat", 2.6),
                ("Corvel Health Group", "Yhdysvallat", 2.2),
                ("Teshima Motor Co.", "Japani", 1.4),
                ("Valmont Pharma AG", "Sveitsi", 1.3),
                ("Brightwater Energy Corp.", "Yhdysvallat", 1.2),
                ("Kestrel Bancorp", "Yhdysvallat", 1.1),
                ("Lindqvist Industri AB", "Ruotsi", 0.9)],
        "report": True,
    },
    "amerikka": {
        "name": "Kanerva Pohjois-Amerikka Osake A",
        "manager": "Kanerva Rahastoyhtiö Oy",
        "isin": isin("FI", "400071341"),
        "kind": "Osakerahasto, Pohjois-Amerikka",
        "risk": 5,
        "ongoing": 0.45, "transaction": 0.03, "entry_fee": 0.0,
        "drift": 0.0075, "vol": 0.042, "start_nav": 19.4517,
        "regions": [("Yhdysvallat", 96.1), ("Kanada", 3.9)],
        "top": [("Arkanen Systems Inc.", "Yhdysvallat", 7.9),
                ("Pelton Semiconductor Corp.", "Yhdysvallat", 6.8),
                ("Northway Software Inc.", "Yhdysvallat", 6.5),
                ("Harrowgate Retail Co.", "Yhdysvallat", 4.3),
                ("Corvel Health Group", "Yhdysvallat", 3.6),
                ("Brightwater Energy Corp.", "Yhdysvallat", 2.0),
                ("Kestrel Bancorp", "Yhdysvallat", 1.9),
                ("Ridgeford Insurance Holdings", "Yhdysvallat", 1.7),
                ("Calder Rail Corp.", "Kanada", 1.5),
                ("Mesa Foods Inc.", "Yhdysvallat", 1.4)],
        "report": True,
    },
    "korko": {
        "name": "Kanerva Lyhyt Korko A",
        "manager": "Kanerva Rahastoyhtiö Oy",
        "isin": isin("FI", "400071358"),
        "kind": "Lyhyen koron rahasto",
        "risk": 2,
        "ongoing": 0.15, "transaction": 0.04, "entry_fee": 0.0,
        "drift": 0.0025, "vol": 0.004, "start_nav": 98.7710,
        "regions": [("Valtiot", 38.0), ("Yrityslainat", 41.0), ("Pankit", 21.0)],
        "top": [("Rautaranta Asuntorahoitus Oyj 2027", "Suomi", 4.4),
                ("Ahvenkoski Energia Oyj 2027", "Suomi", 3.8),
                ("Nordvind Kredit AB 2028", "Ruotsi", 3.5),
                ("Hallberg Bank ASA 2027", "Norja", 3.1),
                ("Kuusikko Pankki Oyj 2028", "Suomi", 2.9)],
        "report": True,
    },
    "pohjola": {
        "name": "Lumme Pohjola Pienyhtiöt B",
        "manager": "Lumme Rahastoyhtiö Oy",
        "isin": isin("FI", "400052719"),
        "kind": "Osakerahasto, Pohjoismaiden pienyhtiöt",
        "risk": 6,
        "ongoing": 1.45, "transaction": 0.0, "entry_fee": 1.0,
        "drift": 0.003, "vol": 0.05, "start_nav": 3.9871,
        "regions": [("Ruotsi", 44.0), ("Suomi", 31.0), ("Norja", 15.0), ("Tanska", 10.0)],
        "top": [("Sjöberg Verktyg AB", "Ruotsi", 3.6), ("Halla Laboratoriot Oyj", "Suomi", 3.2),
                ("Fjellvik Marine ASA", "Norja", 2.9), ("Kaarto Rakennus Oyj", "Suomi", 2.7),
                ("Brandt & Holm A/S", "Tanska", 2.5)],
        "report": False,
        "no_report_why": "Kulu- ja palkkioraporttia ei ole saatavilla tälle rahastolle: "
                         "rahaston hallinnoi toinen rahastoyhtiö, eikä se ole toimittanut "
                         "kulutietoja Kanerva Investille. Juoksevat kulut ovat rahaston "
                         "avaintietoesitteestä.",
    },
}

PORTFOLIOS = {
    "noora": {"owner": "Noora Heikkilä", "account": "kuusikko-noora", "ref_suffix": "1",
              "since": (2023, 1), "monthly": {"maailma": 500.0, "korko": 250.0,
                                               "amerikka": 150.0}},
    "daniel": {"owner": "Daniel Brooks", "account": "saarni-daniel", "ref_suffix": "2",
               "since": (2024, 3), "monthly": {"amerikka": 300.0},
               "lump": {"fund": "pohjola", "date": "2022-05-12", "amount": 4000.0}},
}

REPORT_YEAR = 2025
REPORT_PUBLISHED = "2026-02-16"


# ------------------------------------------------------------------ the prices


def _month_iter(y, m, end):
    while (y, m) <= end:
        yield y, m
        m += 1
        if m == 13:
            y, m = y + 1, 1


def _prices(seed: int) -> dict[str, dict[str, float]]:
    """A NAV on the 5th of every month from 2022-05 to 2026-10, plus the day
    before the epoch. One stream per fund, all from `seed + 7`."""
    rng = random.Random(seed + 7)
    out = {}
    for slug, f in FUNDS.items():
        nav = f["start_nav"]
        series = {}
        for y, m in _month_iter(2022, 5, (2026, 10)):
            series[date(y, m, 5).isoformat()] = round(nav, 4)
            nav *= 1 + rng.gauss(f["drift"], f["vol"])
        series["2022-05-12"] = series["2022-05-05"]
        last = date.fromisoformat(M.EPOCH) - timedelta(days=1)
        series[last.isoformat()] = round(series["2026-10-05"] * (1 + rng.gauss(0.002, f["vol"] / 3)), 4)
        out[slug] = series
    return out


# ------------------------------------------------------------------- the broker


def broker(txns, seed: int) -> dict:
    prices = _prices(seed)
    value_date = (date.fromisoformat(M.EPOCH) - timedelta(days=1)).isoformat()
    window = (M.WINDOW_START, M.WINDOW_END)
    transfers = {p: [t for t in txns if t.counterparty == M.BROKER["name"].upper()
                     and t.account == pf["account"]] for p, pf in PORTFOLIOS.items()}

    portfolios = {}
    for who, pf in PORTFOLIOS.items():
        trades = []
        if "lump" in pf:
            lump = pf["lump"]
            fee = round(lump["amount"] * FUNDS[lump["fund"]]["entry_fee"] / 100, 2)
            nav = prices[lump["fund"]][lump["date"]]
            trades.append({"date": lump["date"], "fund": lump["fund"], "kind": "Merkintä",
                           "amount": lump["amount"], "fee": fee, "nav": nav,
                           "units": round((lump["amount"] - fee) / nav, 4), "transfer": ""})
        rows = {t.date[:7]: t for t in transfers[who]}
        for y, m in _month_iter(*pf["since"], (2026, 10)):
            pay_day = date(y, m, 3).isoformat()
            if pay_day > M.EPOCH:
                break
            trade_day = date(y, m, 5).isoformat()
            in_window = window[0] <= pay_day <= window[1]
            row = rows.get(pay_day[:7])
            if in_window:
                assert row is not None and round(-row.amount, 2) == sum(pf["monthly"].values()), \
                    (who, pay_day)
            for fund, amt in pf["monthly"].items():
                nav = prices[fund][trade_day]
                trades.append({"date": trade_day, "fund": fund, "kind": "Merkintä",
                               "amount": amt, "fee": 0.0, "nav": nav,
                               "units": round(amt / nav, 4),
                               "transfer": row.id if (in_window and row) else ""})
        trades.sort(key=lambda t: (t["date"], t["fund"]))

        holdings = []
        for fund in sorted({t["fund"] for t in trades}, key=list(FUNDS).index):
            mine = [t for t in trades if t["fund"] == fund]
            units = round(sum(t["units"] for t in mine), 4)
            cost = round(sum(t["amount"] for t in mine), 2)
            nav = prices[fund][value_date]
            value = round(units * nav, 2)
            holdings.append({"fund": fund, "units": units, "nav": nav, "nav_date": value_date,
                             "value": value, "cost": cost,
                             "gain": round(value - cost, 2)})

        reports = []
        for h in holdings:
            f = FUNDS[h["fund"]]
            if not f["report"]:
                continue
            vals = []
            for mo in range(1, 13):
                d = date(REPORT_YEAR, mo, 5).isoformat()
                u = sum(t["units"] for t in trades if t["fund"] == h["fund"] and t["date"] <= d)
                vals.append(u * prices[h["fund"]][d])
            avg = round(sum(vals) / 12, 2)
            ongoing = round(avg * f["ongoing"] / 100, 2)
            transaction = round(avg * f["transaction"] / 100, 2)
            entry = round(sum(t["fee"] for t in trades if t["fund"] == h["fund"]
                              and t["date"].startswith(str(REPORT_YEAR))), 2)
            total = round(ongoing + transaction + entry, 2)
            reports.append({
                "id": f"KR-{REPORT_YEAR}-{who}-{h['fund']}", "year": REPORT_YEAR,
                "published": REPORT_PUBLISHED, "fund": h["fund"],
                "average_value": avg,
                "lines": [
                    {"label": "Rahaston juoksevat kulut", "pct": f["ongoing"], "eur": ongoing},
                    {"label": "Rahaston kaupankäyntikulut", "pct": f["transaction"], "eur": transaction},
                    {"label": "Merkintä- ja lunastuspalkkiot", "pct": None, "eur": entry},
                    {"label": "Kanerva Investin palvelumaksut", "pct": None, "eur": 0.0},
                    {"label": "Kolmansien osapuolten kannustimet", "pct": None, "eur": 0.0},
                ],
                "total_eur": total,
                "total_pct": round(total / avg * 100, 2) if avg else 0.0,
            })
        portfolios[who] = {"owner": pf["owner"],
                           "reference": M.ref_fi(M.BROKER["ref_base"] + pf["ref_suffix"]),
                           "paid_from": M.ACCOUNTS[pf["account"]]["iban"],
                           "monthly": pf["monthly"], "trades": trades,
                           "holdings": holdings, "reports": reports,
                           "value": round(sum(h["value"] for h in holdings), 2)}

    funds = {k: {kk: v for kk, v in f.items() if kk not in ("drift", "vol", "start_nav")}
             for k, f in FUNDS.items()}
    return {"name": M.BROKER["name"], "iban": M.BROKER["iban"], "value_date": value_date,
            "login_holder": "Noora Heikkilä",
            "note": "Daniel has given Noora view access to his portfolio "
                    "(katseluoikeus), so one sign-in shows both.",
            "funds": funds, "portfolios": portfolios,
            "nav_history": {k: dict(sorted(v.items())) for k, v in prices.items()}}


# --------------------------------------------------------------------- the loan

LOAN_TERMS = {
    "number": "7731",
    "label": M.LOAN["label"],
    "kind": "Asuntolaina, tasaerä",
    "drawn": "2021-11-20",
    "original": 200000.00,
    "margin": 0.55,
    "reference": "12 kk euribor",
    "reset_day": (11, 20),
    "rates": [("2021-11-20", 0.000), ("2022-11-20", 2.832), ("2023-11-20", 4.016),
              ("2024-11-20", 2.506), ("2025-11-20", 2.180)],
    "floor_note": "Negatiivinen viitekorko lasketaan nollana.",
    "collateral": "As Oy Kotikallio, osakkeet 1 201–1 268 (B 14)",
}


def loan(txns) -> dict:
    T = LOAN_TERMS
    payment = M.LOAN["monthly"]
    rows = {t.date: t for t in txns if t.kind == "LAINAN LYHENNYS"}
    bal = T["original"]
    sched = []

    def rate_on(day: str) -> tuple[float, float]:
        ref = [r for d, r in T["rates"] if d <= day][-1]
        return ref, round(ref + T["margin"], 3)

    y, m = 2021, 12
    while True:
        day = date(y, m, M.LOAN["day"]).isoformat()
        if day > M.EPOCH:
            break
        # Interest for the month that ended today, at the rate that ran over it.
        ref, total = rate_on((date.fromisoformat(day) - timedelta(days=28)).isoformat())
        interest = round(bal * total / 100 / 12, 2)
        principal = round(payment - interest, 2)
        assert principal > 0, day
        bal = round(bal - principal, 2)
        row = rows.get(day)
        if M.WINDOW_START <= day <= M.WINDOW_END:
            assert row is not None and round(-row.amount, 2) == payment, day
        sched.append({"date": day, "payment": payment, "interest": interest,
                      "principal": principal, "balance_after": bal, "rate": total,
                      "row": row.id if row else ""})
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)

    ref_now, total_now = rate_on(M.EPOCH)
    resets = [d for d, _ in T["rates"]]
    next_reset = date(int(resets[-1][:4]) + 1, *T["reset_day"]).isoformat()
    assert next_reset > M.EPOCH

    # When the loan ends at today's rate, the payment staying the same.
    b, n, yy, mm = bal, 0, *((int(sched[-1]["date"][:4]), int(sched[-1]["date"][5:7])))
    while b > 0:
        n += 1
        mm += 1
        if mm == 13:
            yy, mm = yy + 1, 1
        b = round(b - (payment - b * total_now / 100 / 12), 2)
    last = date(yy, mm, M.LOAN["day"]).isoformat()

    return {
        "number": T["number"], "label": T["label"], "kind": T["kind"],
        "lender": M.LOAN["lender"], "account": "kuusikko-joint",
        "holders": "Noora Heikkilä / Daniel Brooks",
        "drawn": T["drawn"], "original": T["original"],
        "balance": bal, "balance_date": sched[-1]["date"],
        "payment": payment, "payment_day": M.LOAN["day"],
        "reference_rate": T["reference"], "reference_value": ref_now,
        "margin": T["margin"], "rate": total_now,
        "last_reset": resets[-1], "next_reset": next_reset,
        "reset_note": "Uusi korko määräytyy koronmuutospäivän 12 kk euriborin mukaan. "
                      "Tasaerälainassa maksuerä pysyy samana ja laina-aika muuttuu.",
        "rate_history": [{"from": d, "reference": r, "rate": round(r + T["margin"], 3)}
                         for d, r in T["rates"]],
        "estimated_last_payment": last, "remaining_payments": n,
        "collateral": T["collateral"], "floor_note": T["floor_note"],
        "schedule": sched,
    }


# ------------------------------------------------------------------ the pension

PENSION_EARNINGS = [
    # (year, law, insurer, earnings)  TyEL = employee, YEL = self-employed
    (2014, "TyEL", "Työnantajan eläkevakuutus", 21450),
    (2015, "TyEL", "Työnantajan eläkevakuutus", 37820),
    (2016, "TyEL", "Työnantajan eläkevakuutus", 39140),
    (2017, "TyEL", "Työnantajan eläkevakuutus", 18900),
    (2017, "YEL", "Peruskivi Eläkevakuutus Oy", 3600),
    (2018, "YEL", "Peruskivi Eläkevakuutus Oy", 7750),
    (2019, "YEL", "Peruskivi Eläkevakuutus Oy", 7750),
    (2020, "YEL", "Peruskivi Eläkevakuutus Oy", 7900),
    (2021, "YEL", "Peruskivi Eläkevakuutus Oy", 7900),
    (2022, "YEL", "Peruskivi Eläkevakuutus Oy", 8066),
    (2023, "YEL", "Peruskivi Eläkevakuutus Oy", 8066),
    (2024, "YEL", "Peruskivi Eläkevakuutus Oy", 8066),
    (2025, "YEL", "Peruskivi Eläkevakuutus Oy", 8066),
]
ACCRUAL = 1.5  # % a year of earnings


def pension() -> dict:
    rows = [{"year": y, "law": law, "insurer": who, "earnings": e,
             "accrued_yearly": round(e * ACCRUAL / 100, 2)} for y, law, who, e in PENSION_EARNINGS]
    accrued = round(sum(r["accrued_yearly"] for r in rows) / 12, 2)
    yel_now = 8350
    years_left = 2055 - 2026
    estimate = round(accrued + years_left * yel_now * ACCRUAL / 100 / 12, 2)
    read = (date.fromisoformat(M.EPOCH) - timedelta(days=1)).isoformat()
    return {
        "provider": "Peruskivi Eläkevakuutus Oy",
        "person": "Daniel Brooks", "born": "1988-03-14",
        "kind": "Työeläkeote",
        "accrued_to": "2025-12-31",
        "accrued_monthly": accrued,
        "retirement_age": "67 vuotta 2 kuukautta",
        "retirement_from": "2055-06-01",
        "estimate_monthly": estimate,
        "estimate_basis": f"Arvio olettaa, että nykyinen YEL-työtulo {yel_now:,} € vuodessa ".replace(",", "\u00a0") +
                          "jatkuu eläkeikään asti. Arvio ei sisällä kansaneläkettä, "
                          "takuueläkettä eikä ulkomailta kertyneitä eläkkeitä.",
        "current_yel_income": yel_now,
        "read": read,
        "earnings": rows,
        "note": "The record has no balance. Finnish earnings-related pension is not a "
                "pot: it is an accrued monthly amount.",
    }


# ------------------------------------------------------------------ the checks


def build(txns, seed: int) -> dict:
    b, l, p = broker(txns, seed), loan(txns), pension()
    return {"broker": b, "loan": l, "pension": p, "checks": check(b, l, p, txns)}


def check(b, l, p, txns) -> dict:
    out = {}
    for f in b["funds"].values():
        assert isin_ok(f["isin"]), f["isin"]
    top = {k: {n for n, _, _ in f["top"]} for k, f in b["funds"].items()}
    shared = sorted(top["maailma"] & top["amerikka"])
    assert len(shared) >= 5
    weight = {k: {n: w for n, _, w in f["top"]} for k, f in b["funds"].items()}
    out["overlap"] = {
        "funds": ["maailma", "amerikka"], "shared": shared,
        "in_maailma_pct": round(sum(weight["maailma"][n] for n in shared), 1),
        "in_amerikka_pct": round(sum(weight["amerikka"][n] for n in shared), 1),
        "north_america_in_maailma_pct": dict(b["funds"]["maailma"]["regions"])["Pohjois-Amerikka"],
    }
    held = {h["fund"] for pf in b["portfolios"].values() for h in pf["holdings"]}
    assert held == set(b["funds"]), held
    no_report = [k for k in held if not b["funds"][k]["report"]]
    assert len(no_report) == 1
    reported = {r["fund"] for pf in b["portfolios"].values() for r in pf["reports"]}
    assert reported == held - set(no_report)
    out["no_report"] = no_report[0]

    for who, pf in b["portfolios"].items():
        rows = [t for t in txns if t.counterparty == M.BROKER["name"].upper()
                and t.account == PORTFOLIOS[who]["account"]]
        linked = {t["transfer"] for t in pf["trades"] if t["transfer"]}
        assert linked == {t.id for t in rows}, who
        for r in rows:
            assert r.reference == pf["reference"], who
    out["portfolios"] = {who: {"owner": pf["owner"], "value": pf["value"],
                               "holdings": [(h["fund"], h["units"], h["value"])
                                            for h in pf["holdings"]],
                               "reports": [(r["fund"], r["total_eur"], r["total_pct"])
                                           for r in pf["reports"]]}
                         for who, pf in b["portfolios"].items()}
    est = [(h["value"], b["funds"][h["fund"]]["ongoing"])
           for pf in b["portfolios"].values() for h in pf["holdings"]
           if h["fund"] == no_report[0]]
    out["estimate_basis"] = {"value": est[0][0], "ongoing_pct": est[0][1],
                             "yearly_eur": round(est[0][0] * est[0][1] / 100, 2)}

    prev = l["original"]
    for s in l["schedule"]:
        assert round(prev - s["principal"], 2) == s["balance_after"]
        assert round(s["interest"] + s["principal"], 2) == s["payment"]
        prev = s["balance_after"]
    loan_rows = {t.id for t in txns if t.kind == "LAINAN LYHENNYS"}
    assert loan_rows == {s["row"] for s in l["schedule"] if s["row"]}
    days = (date.fromisoformat(l["next_reset"]) - date.fromisoformat(M.EPOCH)).days
    assert 0 < days <= 60
    out["loan"] = {"balance": l["balance"], "rate": l["rate"], "margin": l["margin"],
                   "reference": f"{l['reference_rate']} {str(l['reference_value']).replace('.', ',')} %",
                   "next_reset": l["next_reset"], "next_reset_days": days,
                   "estimated_last_payment": l["estimated_last_payment"]}

    flat = repr(p).lower()
    assert "balance" not in [k.lower() for k in p] and "saldo" not in flat
    assert round(sum(r["accrued_yearly"] for r in p["earnings"]) / 12, 2) == p["accrued_monthly"]
    out["pension"] = {"accrued_monthly": p["accrued_monthly"],
                      "estimate_monthly": p["estimate_monthly"],
                      "retirement_age": p["retirement_age"]}
    return out
