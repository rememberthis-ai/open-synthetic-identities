# The Heikkilä-Brooks household's bills

A year of one Espoo household's money, **2025-10-01 to 2026-10-15**, built for
Mind My Money 0.2.0's bills work: finding bills before they are due, telling a
real bill from a trap, and paying with one OK each. Everything is fictional and
generated from one seed:

```sh
python3 generate/gen_household_fi.py --seed 42     # the ledger and every view of it
python3 generate/check_household_fi_fixture.py     # reads it all back
```

Noora Heikkilä (Finnish, salaried), Daniel Brooks (British, a freelance
illustrator who pays his own pension insurance) and their daughter Aino, four.
**They write to the app in English; every bank, biller and mailbox writes to
them in Finnish**, so a run in English has to read Finnish bills. The Berlin
household (`../mindmymoney/`) stays for regression and for a German
household's bills.

The request it answers is `docs/ongoing/MMM-0.2.0-HOUSEHOLD-REQUEST-2026-10-06.md`
in the monorepo. **Delivery A** is the bills; **delivery B** is what the
household owns (`evidence/broker.json`, `loan.json`, `pension.json`, built by
`generate/household_fi/holdings.py`); C (paying) adds to it.

## ⛔ What may be seeded into a vault, and what must never be

| | |
|---|---|
| `statements/` | **input.** What the household downloads from its two banks. |
| `evidence/` | **the portals' records**: the e-invoice list, the scheduled payments, the digital mailbox, the mail, and the ledger the bank portals serve exports from. Reached only by signing in. |
| `PLANTED.md` | **the answer key.** Every planted bill, fee and trap. |

## The dates move, the files do not

Every date here is at the **epoch, 2026-10-15** (`evidence/clock.json`). The
portals shift every date by (today − epoch) when they serve it, statements
included, so the household always ends on the day of the run and *due in nine
days* means nine days after the run starts. `E2E_TODAY=YYYY-MM-DD` (or
`portal.sh start --today YYYY-MM-DD`) fixes today, so a failed run can be
replayed on the same dates.

## The three accounts

| file prefix | whose | dialect |
|---|---|---|
| `kuusikko-joint` | the joint account the bills are paid from; it receives the e-invoices | Kuusikko Pankki: Finnish headers, `;`, `dd.mm.yyyy`, `-412,00`, UTF-8, the counterparty's IBAN and the reference in their own columns |
| `kuusikko-noora` | Noora's own account, same bank | the same |
| `saarni-daniel` | Daniel's account at a second bank | Saarni Pankki, set to English: English headers, `d.m.yyyy`, `-1 350,00`, **Latin-1**, CRLF, a running balance |

Every IBAN and every reference number carries valid check digits (Finnish
national references with the 7-3-1 rule; RF creditor references for the
insurer and the first-time sender), so an agent that validates them finds them
valid. The account numbers belong to nobody.

## Every company is invented

Kuusikko Pankki, Saarni Pankki, Viestisilta (the digital mailbox), Kumpu Mail,
Päiväkoti Pikkutikka, Virtaväylä Energia, Kuitulinja, Aallokko Mobile,
Turvaranta Vakuutus, Peruskivi Eläkevakuutus, As Oy Kotikallio, Musiikkikoulu
Sävelpolku, Siivouspalvelu Kirkas, Kanerva Invest, Yritysluettelo Nordic and the
shops. None imitates a real Finnish bank, OmaPosti, Suomi.fi, an insurer, a
pension company or a fund.

## What they own

- **Kanerva Invest**, a fund platform: Noora saves 900 € a month into three
  funds, Daniel 300 € into one and holds a fourth from 2022. Two funds overlap
  (a global index fund and a North America fund share seven of their top ten).
  Three funds have a yearly **costs and charges report**; the fourth, managed
  by another company, has none, so its cost can only be estimated from its
  ongoing charge. Found from the monthly `KANERVA INVEST OY` transfers.
- **The mortgage**, on Kuusikko Pankki's loan page: balance, 12-month euribor
  plus margin, the next reset date (epoch +36 days) and each instalment split
  into interest and principal, one for each `LAINAN LYHENNYS` row.
- **Daniel's pension record** at Peruskivi Eläkevakuutus: the accrued monthly
  pension and an estimate at retirement age. No balance, by design.

Every fund, holding and ISIN is invented (the ISINs carry valid check digits).

## What is planted

`PLANTED.md` lists each one with its reference and its due date in days from
the epoch: bills due within 14 days, one bill found twice (an e-invoice and a
mailbox letter with the same reference), one that pays itself, one already
scheduled, one only in the mailbox, a familiar payee asking for a new account
number, a bill more than twice its payee's usual range, a first-time sender by
email only, a known sender's PDF by email, and two reminder fees and a late fee
in last year's rows with the bills behind them.
