# PLANTED — what is in the Carter-Okafor household's money, and what it costs

**This is an answer key. It is not seeded into any vault and must never be.**
A run is graded against what was planted, not against what the agent happened
to say — otherwise a confident wrong answer and a correct one read the same.

Every figure below is **measured from the generated ledger** by
`generate/household/build.py::check`, which raises rather than writing a
fixture that contradicts this file. Regenerate both together:

```sh
python3 generate/gen_household.py --seed 42
```

## The shape of the year

- **1060 transactions**, 2025-06-01 to 2026-06-30, across three instruments.
- **96 of them** — one in 11.0 — are behind a payment rail whose text does not name the shop.
  65 of those can be resolved from evidence that exists; **31 cannot be resolved at all** and `unnamed` is the right answer for them.
  7 fall in June 2026, the month the person opens first.

| rail | hidden rows |
|---|---|
| Warenlager Payments Europe | 26 |
| Kartenkopf | 25 |
| Ratenwerk Bank AB | 16 |
| Tellerflink Lieferservice | 11 |
| Pagolink Europe S.a r.l. et Cie, S.C.A. | 9 |
| Zahlnetz Payments | 5 |
| Rechnungsbrücke GmbH | 4 |

## The findings

### Two memberships of the same streaming service

- **What.** Alex has paid Bildstrom from the Meridian Everyday card since before the window opened. Sam took out a second membership on the joint Girokonto on 14 October 2025, not knowing about the first. Both are full-price family plans; nobody watches the second one.
- **Where.** havelbank-joint (the duplicate) and meridian-everyday (the original)
- **The evidence.** Bildstrom's own account page lists the membership, when it started and when it was last watched (never). The cancel flow ends on a confirmation page naming the end date.
- **The verdict.** Cancel the joint-account one.
- **Measured:**

  - `charges`: 9
  - `paid_so_far`: 126.91
  - `annual_if_left`: 179.88
  - `first`: 2025-10-14

### The same Amazon Prime membership, billed from two countries

- **What.** Alex kept Prime on the UK account after moving to Berlin, paid in pounds on the Meridian Everyday card, and signed up again on amazon.de in September 2025, paid by Lastschrift from the joint Girokonto. Two Prime memberships for one person: one in GBP, one in EUR, from September on. The UK one changes by a few cents every month with the exchange rate, so it does not look like a fixed subscription.
- **Where.** meridian-everyday (amazon.co.uk, GBP) and havelbank-joint (amazon.de, EUR)
- **The evidence.** The statement text names both. The household mailbox holds amazon.de's welcome mail of September 2025 and amazon.co.uk's renewal reminder of May 2026, both addressed to Alex.
- **The verdict.** Cancel one; the person decides which. The UK one is the older, in a currency the household no longer lives in.
- **Measured:**

  - `uk_charges`: 13
  - `uk_paid_in_window_eur`: 137.81
  - `uk_gbp_each`: 8.99
  - `de_charges`: 10
  - `de_paid_in_window_eur`: 89.9
  - `de_first`: 2025-09-02
  - `months_billed_twice`: 10
  - `uk_paid_during_overlap_eur`: 105.95
  - `annual_uk_eur`: 127.8

### The streaming plan went up mid-year

- **What.** 12,99 a month until January 2026, 14,99 from February, on both memberships. Two amounts across the months, announced by an email in the household mailbox.
- **Where.** both Bildstrom rows
- **The evidence.** The mailbox holds the price-change notice dated 2026-01-12.
- **The verdict.** Nothing to act on; it belongs in *what changed*.
- **Measured:**

  - `before`: 12.99
  - `after`: 14.99
  - `from`: 2026-02
  - `extra_a_year`: 24.0

### A gym charged every month, unvisited since March

- **What.** 34,90 a month on Alex's card for the whole window. The last check-in was 7 March 2026 — after which Alex went back to climbing with Jonas at the club.
- **Where.** meridian-everyday
- **The evidence.** The gym's members' area lists every check-in, newest first.
- **The verdict.** Ask whether to cancel. The person decides; the rows only prove it has not been used.
- **Measured:**

  - `charges`: 13
  - `paid_in_window`: 453.7
  - `annual`: 418.8
  - `last_visit`: 2026-03-07
  - `paid_since_last_visit`: 104.7

### A paid trial nobody cancelled

- **What.** Warenlager Plus, free for thirty days from 3 November 2025, first charged on 3 December and every month since. The bank row says WARENLAGER DIGITAL DE and nothing else, so it reads as a purchase rather than a subscription.
- **Where.** meridian-everyday
- **The evidence.** The marketplace's Memberships page gives the trial start, the first payment and the renewal date.
- **The verdict.** Cancel, or keep deliberately. Small, and the point is that small is what survives unnoticed.
- **Measured:**

  - `charges`: 7
  - `paid_so_far`: 34.93
  - `annual`: 59.88
  - `trial_started`: 2025-11-03
  - `first_charge`: 2025-12-03

### Household insurance paid twice for a quarter

- **What.** The Hausratversicherung moved from Nordstern to Blauschild with effect from 1 January 2026. Blauschild began collecting in January; Nordstern's mandate was never stopped and went on collecting through the whole first quarter as well, so the household paid two household-contents policies for three months.
- **Where.** havelbank-joint
- **The evidence.** The mailbox holds Nordstern's cancellation confirmation naming 31 December 2025 as the end date, and Blauschild's new policy starting 1 January.
- **The verdict.** Claim the two collections back. This is money owed, not money to stop spending.
- **Measured:**

  - `collections_after_the_switch`: 3
  - `claimable`: 55.2
  - `dates`: 2026-01-08, 2026-02-08, 2026-03-08

### Sweets and ice cream cost more than all the fish and meat

- **What.** Across thirteen months at the grocer, the sweets and ice cream lines outspend every line of fish and meat. Neither figure is visible from the bank, which only ever says KAUFHALLE NORD.
- **Where.** the grocer's order history, line by line
- **The evidence.** Every online order at Kaufhalle Nord has its items, and each order reconciles to a statement row to the cent.
- **The verdict.** Analysis, not advice. Name the two figures and stop.
- **Measured:**

  - `sweets_and_ice_cream`: 499.91
  - `fish_and_meat`: 320.25
  - `grocer_total`: 3037.21
  - `not_food`: 388.48
  - `not_food_share`: 12.8
  - `orders`: 48

### The electricity Abschlag fell after a contract change

- **What.** 118,00 a month through 2025, 94,00 from January 2026 after the tariff changed. The saving is already made; it belongs in *what changed*, not in *what to do*.
- **Where.** havelbank-joint
- **The evidence.** The mailbox holds Spreelicht's letter of 2025-12-09 announcing the new Abschlag from January.
- **The verdict.** Nothing to act on. A round that only ever reports losses is a round the person stops opening.
- **Measured:**

  - `before`: 118.0
  - `after`: 94.0
  - `from`: 2026-01
  - `saved_a_year`: 288.0

## The totals a graded run should arrive at

| | a year | already paid in the window |
|---|---|---|
| Duplicate streaming membership | 179.88 EUR | 126.91 EUR |
| Amazon Prime billed twice (UK, in GBP) | 127.80 EUR | 105.95 EUR during the overlap |
| Gym, unvisited since March | 418.80 EUR | 104.70 EUR since the last visit |
| Marketplace membership from an uncancelled trial | 59.88 EUR | 34.93 EUR |
| **Recoverable by cancelling, a year** | **786.36 EUR** | |
| Insurance collected twice — claimable, not saved | — | 55.20 EUR |

Two more that are **not** savings and must not be counted as any:

- the streaming price rise costs **24.00 EUR a year** more than it did;
- the electricity tariff change already saves **288.00 EUR a year**, and belongs in *what changed*.

## Where the food went

Across 48 online grocery orders totalling **3037.21 EUR**:

- sweets and ice cream: **499.91 EUR**
- all fish and meat: **320.25 EUR**
- not food at all (cleaning, nappies, toiletries): **388.48 EUR**, 12.8% of the grocery bill

None of this is visible from a bank statement, which only ever says
`KAUFHALLE NORD LIEFERDIENST` and a number. It is visible from the order
history, one basket at a time, and that is the point of the scene.

⛔ **Analysis, never advice.** The finding is the two figures. What a
household eats is not ours to have an opinion about.
