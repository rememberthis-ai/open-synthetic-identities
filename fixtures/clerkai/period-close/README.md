# Clerk.AI period-close fixture — two sets of books, five periods, one per run state

Alex Carter keeps **two sets of books**: the design company they run, and a
climbing club they volunteer as treasurer for. Five closes between them cover
every state the run lifecycle can be in, so every screen the app can show is
reachable from synthetic data and none of it has to come from a real vault.
Demo epoch is 2026-06-30, so June is "yesterday's" in-progress state and the
rest is history.

| Set of books | Period | `status` | `phase` | What it shows |
|---|---|---|---|---|
| Carter Studio UG | **2026-06** | `paused` | `match` | The live run, and the **allocation view**: 31 rows, the instrument settles 26, five left to decide. 2 candidates awaiting Keep/Drop, 2 open question cards |
| Carter Studio UG | **2026-05** | `review` | `draft` | Packet assembled + accountant email **drafted, not yet sent** |
| Carter Studio UG | **2026-04** | `sent` | `draft` | Emailed, **awaiting their reply** — the paste-reply field, empty, plus "Mark books as closed" |
| Carter Studio UG | **2026-03** | `done` | `draft` | **Books closed**, with the reply loop on file in `accountant-correspondence.md` |
| Kletterfreunde Kreuzberg e.V. | **2025** | `done` | `draft` | The club's **annual** Kassenbericht, closed in May 2026 before the members' meeting — and the one period whose recipient is **not an accountant** |

## Two sets of books, and why the club is one of them

`Notes/bookkeeping/books/{slug}.md` defines each set. The bodies are **prose,
not tables** — that prose is the allocation mechanism: the agent reads it to
decide which set of books a receipt belongs to. Do not turn it into a table.

The club earns its place by being the case the product never anticipated. Its
books go to the elected **Kassenprüfer**, not to a Steuerberater — so its books
file carries `recipient: Kassenprüfer` and the app says "awaiting your
Kassenprüfer's reply". Two companies both filing to the same accountant would
only show that the plumbing exists.

**The path is the fact.** A run's set of books is derived from where its file
sits, and a directory under `bookkeeping/` is read as a period or as a set of
books **by its name** (`2026`, `2026-05`, `2026-Q2` are periods; anything else
holds them). There is no `books:`
frontmatter key — a period copied to the wrong depth is silently filed under the
wrong set of books. A vault with only ONE set keeps the original flat layout
(`bookkeeping/{period}/`) and is never migrated; naming a second set is what
moves the first.

## The allocation dataset

Every ledger row in June names its `instrument:` — **rows without one are
dropped from the allocation screen entirely**, because that screen's claim is
that the instrument settles it, and an unlabelled row has not been through that
reasoning. 26 of the 31 also carry `allocation:`; the five that don't are the
point, because **the absence is what makes a row ask**.

| Pile | Rows | Instruments |
|---|---|---|
| Carter Studio UG | 24 | Carter Studio's account, Carter Studio's card, Your own card |
| Kletterfreunde Kreuzberg e.V. | 1 | Your own card |
| Personal | 1 | Carter Studio's card |
| *needs you* | 5 | Carter Studio's card |

Two things that shape are chosen to demonstrate. A settled pile groups by
**destination and names several instruments underneath** — Carter Studio has an
account *and* a card *and* catches a personal-card purchase — which is what
the allocation view groups by. And the five unsettled rows are all Supermercado Listo under
**one** allocation card: answering once settles five rows.

**`done` is the terminal state, not `closed`** — there is no `closed` status.
The two routes there differ: the run view's *"Mark books as closed"* calls
the run view's own status write and leaves `phase`/`steps` alone (that's 2026-03),
while Home's "handled outside Clerk" calls the "handled outside" route, which also
forces `phase: done` and strips every step `detail`.

**Carter Studio's** four periods are one company's continuous year: same accountant
(M. Fischer Steuerberatung), same bank (Meridian Business), recurring vendors,
and **balances that chain exactly** — each period's closing balance is the
next one's opening (1,276.85 → 3,679.25 → 8,212.35 → 12,408.33). Northlight's
invoice grows month over month (2,900 → 4,200 → 4,800 → 4,800), and April
picks up a second client (Vellum & Co), so the history reads as a studio
winning work rather than four copies of one month.

**Hallo Mobilfunk GmbH appears in June and nowhere earlier — on purpose.**
June's open question card asks whether it's a legitimate new vendor; that card
is only honest while the earlier periods genuinely don't contain it. Don't add
it retroactively.

**Markdown is the ground truth** — the app's index is a rebuildable
projection of these files, so restoring a fixture is a file copy plus a
reindex.

## Layout

```
Notes/bookkeeping/
  books/{slug}.md             # one per set of books: name, slug, optional
                              #   recipient, and PROSE naming its accounts,
                              #   cards and portal logins
  round.md                    # the last sweep (the round views)
  carter-studio/{2026-03..06}/
  kletterfreunde-kreuzberg/2025/
      run.md                      # run header: phase, status, step tracker
      items/*.md                  # one file per ledger line / deliverable row
      receipts/*.png              # images referenced by items' receipt_path
      statements/*.csv            # the statement for the period
      index.md                    # the assembled packet
      accountant-email-draft.md   # the deliverable email
      attachments-to-send/        # the packet's files under the names the
                                  #   email lists them by
      accountant-correspondence.md # what went out and came back
                                  #   (carter-studio/2026-03 only)
Registry/alex-carter/questions/
  q-*.md                      # the two open question cards June is blocked on
```

The club's year stands alone — its own bank (Bürgerbank Kreuzberg), its own
card, its own opening balance — because it is different money. Balances chain
*within* a set of books, never across two.

Money/vendor facts (amounts, dates, vendor names) follow PERSONA.md's cast and
business shape. June's receipts come from the sampled
`fixtures/clerkai/receipts/`; March/April's and the club's are rendered to exact
totals from `generate/receipt-specs/` (see "Regenerating").

## What each state shows

**2026-06 — `paused`, the live run.**
- **Deliverables checklist** (`kind: deliverable`): bank statement done, client
  invoice matched, receipts still collecting, vendor invoices not started.
- **Matched ledger lines** (`status: matched`): coworking rent, hosting, the
  Fontrack Pro subscription (matched to an actual receipt image), the
  Northlight income line.
- **Candidate receipts** (`status: candidate`): two OCR-found receipts
  (Kaffebaren Söder, K-Kulma Kioski) awaiting Keep/Drop in the curation panel —
  each carries a `why` explaining the match, and a `photo_uuid` so the
  thumbnail resolves.
- **Blocked-on-you lines** (`status: ask`): two transactions pointing at open
  question cards via `question_slug` — a new-vendor check (Hallo Mobilfunk
  GmbH) and a personal-vs-business call (Supermercado Listo groceries).

**2026-05 — `review`.** All four deliverables done, 7 matched transactions,
1 excluded as personal (Stadtwerke), packet assembled, German email drafted and
awaiting the user's send.

**2026-04 — `sent`.** Same shape, plus: the email went out on 4 May and the run
is parked waiting for M. Fischer. Deliberately has **no**
`accountant-correspondence.md` — marking a run sent doesn't write one (the app
only appends on a pasted reply), so the reply field renders empty, which is the
whole point of this period. Second client (Vellum & Co) shows a resolved
new-payer judgment call in the packet's *Open question* column.

**2026-03 — `done`.** The full loop, and the only period where the accountant
actually answered: Fischer asked for the Bewirtungs-Anlass on the 12 March
Brew & Bean lunch (§ 4 Abs. 5 Nr. 2 EStG needs occasion + participants), Clerk
recovered it from Alex's own voice memo of that day, the Anlass went into the
ledger row and an `index.md` Nachtrag, and Fischer confirmed. That exchange is
`accountant-correspondence.md` — the three entries are exactly the shape the
app appends (`Accountant reply` / `Note` / `Accountant reply`).

**2025 (the club) — `done`, and the reason the club exists.** An annual close:
14 rows on the Bürgerbank account and the Vereinskarte, membership dues booked
as two collective credits rather than ninety, a Kassenbericht in German, and a
covering note to two named Kassenprüfer. Nothing in it mentions Fischer, and the
app calls its recipient a Kassenprüfer because `books/kletterfreunde-kreuzberg.md`
says so — that is the whole not-hardcoded-recipient principle, on screen.

> **This used to be unphotographable and no longer is.** When the March reply
> loop was written, nothing in the app rendered `accountant-correspondence.md` —
> it was write-only from the run view. The app-UX rebuild then built the reader
> (the run view's *"Afterwards"* thread), so the exchange
> now shows as a conversation: the accountant's two messages on their side,
> Clerk's note italic and unadorned between them.

## Restoring into a vault

Markdown is the ground truth, so restoring is a file copy + reindex — no app
code involved:

```bash
# vault = ~/Clerk.AI Demo (or wherever the target install's vault root is)
cp -R fixtures/clerkai/period-close/Notes/bookkeeping/* "$vault/Notes/bookkeeping/"
mkdir -p "$vault/Registry/alex-carter/questions"
cp fixtures/clerkai/period-close/Registry/alex-carter/questions/*.md \
   "$vault/Registry/alex-carter/questions/"
```

Prefer a scripted restore over doing this by hand: replace each period rather
than merging into it (a copy over an existing period dir keeps files the
fixture has since renamed), remove periods the fixture no longer ships, and
resolve the target vault's own daemon port rather than assuming the default —
pointing an admin endpoint at the wrong vault is the mistake worth engineering
out.

The app watches the vault and picks the new files up within a couple of
seconds; a full reindex makes it immediate. The active identity must be
`alex-carter` (or whichever identity id the target vault uses — rename the
`Registry/<identity>/` folder to match) for the question cards to surface;
the bookkeeping side is not identity-scoped.

## Regenerating

The markdown is hand-authored — it's a deliberately curated *narrative* state
(which items are matched vs. candidate vs. blocked), not a bulk data table. To
evolve it (a July close, a further-along phase), edit the files directly,
following the frontmatter shape the existing files already use.

**Receipt images are generated, and must print the ledger's exact amount.** The
receipt is the document the accountant sees, so it — not the markdown — is the
source of truth for the amount; a ledger row that disagrees with its own scan
is the mistake this mode exists to prevent. `gen_receipts.py`'s
sampled mode can't hit a chosen total, so March/April use its `--spec` mode:

```bash
cd generate
python3 gen_receipts.py --spec receipt-specs/alex-carter-2026-04.json --seed 4 \
    --out ../fixtures/clerkai/period-close/Notes/bookkeeping/2026-04/receipts
```

A spec entry may declare `"total"`; the renderer sums the line items and
**aborts** if they disagree, so a typo can't reach a packet. Merchants must
already exist in `MERCHANTS` (city, language and VAT rate come from there, so a
spec can't invent an inconsistent merchant).

## Invariants worth re-checking after any edit

- **Balances chain across periods** — each period's closing balance is the
  next's opening. Break it and a reader comparing two screenshots sees a
  company whose money doesn't add up.
- **Every statement line has exactly one ledger item, and vice versa** —
  `index.md`'s "N transactions" counts business lines only (excluded ones are
  listed separately), matching the statement's line count in *Enclosed*.
- **Every `receipt_path` resolves, its printed total equals `|amount|`, and no
  receipt is an orphan** with no ledger row.
- **`index.md`'s summary arithmetic** — income, expenses, net, opening and
  closing — is recomputed, not carried over. 
- **Hallo Mobilfunk stays June-only**, or June's new-vendor card is a lie.
