# Clerk.AI period-close fixture — two sets of books, six periods, one per run state

Alex Carter keeps **two sets of books**: the design company they run, and a
climbing club they volunteer as treasurer for. Six closes between them cover
every state the run lifecycle can be in, so every screen the app can show is
reachable from synthetic data and none of it has to come from a real vault.
Demo epoch is **2026-08-03**: July is the run that is going on right now, June
is the one parked on questions, and the rest is history.

| Set of books | Period | `status` | `phase` | What it shows |
|---|---|---|---|---|
| Carter Studio UG | **2026-07** | `running` | `receipts` | **The run that is happening now** — a thin letter with three files in it, twelve lines, three open sign-ins. The one period whose header is about the minute you are looking at it |
| Carter Studio UG | **2026-06** | `paused` | `match` | Parked on questions — a **thin letter, mostly grey**, three files staged. Plus the **allocation view**: 31 rows, the instrument settles 26, five left to decide. 20 candidates awaiting Keep/Drop, 6 open question cards |
| Carter Studio UG | **2026-05** | `review` | `draft` | **Nothing grey left** — every row a staged file, and the send block showing |
| Carter Studio UG | **2026-04** | `sent` | `draft` | Emailed, **and they came back** — the reply thread, and *Is April finished?* not yet pressed |
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
  carter-studio/{2026-03..07}/
  kletterfreunde-kreuzberg/2025/
      run.md                      # run header: phase, status, step tracker
      items/*.md                  # one file per ledger line / deliverable row
      receipts/*.png, *.pdf       # the documents items' receipt_path point at
      statements/*.csv            # the statement for the period
      index.md                    # the assembled packet
      accountant-email-draft.md   # the deliverable email
      attachments-to-send/        # what the period holds for the accountant,
                                  #   under the same filenames receipts/ uses
      attachments-sent-<date>/    # what one day's email actually carried
                                  #   (carter-studio 2026-04: 4 and 6 May)
      accountant-correspondence.md # what went out and came back
                                  #   (carter-studio 2026-03 and 2026-04)
Registry/alex-carter/questions/
  q-*.md                      # the nine open cards — SEVEN of them logins
```

## What the files are called, and why the two names have to be one name

**A document is stored under the name the accountant receives it by.**
`receipts/2026-05-13-buerobedarf-kern-beleg.png` is byte-for-byte the same
filename as the copy in `attachments-to-send/`, and the statement follows the
same shape: `2026-05-meridian-business-kontoauszug.csv`.

| | |
|---|---|
| a receipt | `YYYY-MM-DD-<vendor>-beleg.png` |
| a supplier invoice | `YYYY-MM-DD-<vendor>-rechnung.pdf` |
| a statement | `YYYY-MM-<bank>-kontoauszug.csv` (a year: `YYYY-<bank>-…`) |

This is not tidiness. The app pairs a staged file with the ledger row it belongs
to **by leaf filename**, and that is what puts *your photos* / *your mail* /
*from your bank* beside each attachment in the letter. Two spellings of one
document — `20260513-bürobedarf-kern.png` against
`2026-05-13-buerobedarf-kern-beleg.png` — is a pairing that never matches, and
because the column is allowed to be blank when nothing honest can be said, it
fails silently and looks like a feature nobody built.

Two rules that go with it:

- **ASCII, always.** `ü` can be composed or decomposed; the two are different
  bytes for the same picture, and a name spelled one way here and the other way
  there is a bug you cannot see. German transliteration (`ue`, `oe`, `ae`, `ss`)
  is the ordinary convention for a file that has to survive a mail client, a zip
  and somebody's Windows desktop. Check the bytes, not the glyphs.
- **The document's `source:` says where the DOCUMENT came from**, not where the
  charge came from. A photographed till receipt is `your photos` even though the
  transaction is on the bank statement. Every filed month used to say
  `Meridian Business statement` on all six attachments, which would have read
  *from your bank* under five receipts that came off a phone.

## Two sends, and what went in each

A period that has been sent keeps a folder per send —
`attachments-sent-YYYY-MM-DD/` — holding exactly what went out that day.
**2026-04 is the period that has been sent twice**: the letter and six
attachments on 4 May, then Fischer's question about Vellum & Co, then a
follow-up on the 6th carrying one more document, Vellum's own order with the
VAT number on it. Both sends are entries in `accountant-correspondence.md`
(`## Sent · …`), so the thread reads: sent, they replied, you answered, sent
again — which is the loop the product exists for, and no other period reaches
it.

`attachments-to-send/` still holds all seven afterwards. It is what the period
holds; the sent folders are what a particular day's email carried.

The club's year stands alone — its own bank (Bürgerbank Kreuzberg), its own
card, its own opening balance — because it is different money. Balances chain
*within* a set of books, never across two.

Money/vendor facts (amounts, dates, vendor names) follow PERSONA.md's cast and
business shape. June's receipts come from the sampled
`fixtures/clerkai/receipts/`; March/April's and the club's are rendered to exact
totals from `generate/receipt-specs/` (see "Regenerating").

## What each state shows

**2026-07 — `running`, and it is running NOW.** The one period whose header is
about the minute you are looking at it: a run started on the morning of 3 August,
twelve lines in from the statement, two documents found and staged beside it, and
three sign-ins waiting. Its letter is a thin one — recipient, subject, greeting,
sign-off — so the letter reads *Attached — 3 so far* over a page that is mostly
still to come.

Its ledger is the compact version of June's and shows the same five row states in
its first five rows. **The one thing a fixture cannot supply is liveness**: a run
reads as working because a session is running, and no file makes that true.

**2026-06 — `paused`, parked on questions, and the mid-collection letter.**
- **A thin `accountant-email-draft.md`**, written at the start of the run rather
  than the end, with two files staged in `attachments-to-send/` — the statement,
  and the one receipt already settled to this set of books. Everything else is
  still grey. The RailLink receipt is deliberately NOT staged here: it is
  allocated to the club, and a letter belongs to exactly one set of books.
- **Checklist rows** (`kind: deliverable`): bank statement done, client
  invoice matched, receipts still collecting, supplier invoices not started.
- **Matched ledger lines** (`status: matched`): coworking rent, hosting, the
  Fontrack Pro subscription (matched to an actual receipt image), the
  Northlight income line.
- **Candidate receipts** (`status: candidate`): two OCR-found receipts
  (Kaffebaren Söder, K-Kulma Kioski) awaiting Keep/Drop in the curation panel —
  each carries a `why` explaining the match, and a `photo_uuid` so the
  thumbnail resolves.
- **Blocked-on-you lines** (`status: ask`): seven transactions pointing at open
  question cards via `question_slug` — four supplier sign-ins (Nimbus, two from
  Bürobedarf Kern, two RailLink fares), a new-vendor check (Hallo Mobilfunk
  GmbH) and a personal-vs-business call (Supermercado Listo groceries).
- **The five row states, in the first five rows.** June's ledger opens with the
  desk rent (*none issued*), a sign-in (*asking you*), a photographed café bill
  (*receipt ↗*), a subscription invoice that arrived as a PDF (*invoice ↗*) and
  a sign-in again — then *still looking* for the rest. That is deliberate: a
  screenful that shows one state four hundred times cannot demonstrate a design
  with five in it. The PDF is the only way the word *invoice* can occur at all
  — the app decides invoice-or-receipt from the file, and a fixture of nothing
  but `.png` could never produce it.

## The question cards

Nine open cards, and **seven of them are `kind: login`** — which is the fact the
one-line rows exist to make visible. The Mac puts a phrase on the right of each
row (*needs your Mac*, *a judgement call*, *something to find*) derived from
`kind` and from nothing else, so a card without one gets no phrase and a list of
mostly-blank rows reads as a rendering fault rather than as an absence.

`question:` is **one short sentence** and the detail lives in `context:`, which
is a paragraph and is rendered under the question on the card itself. The row
shows the question and nothing else, so a paragraph there arrives as a fragment
ending mid-amount. *"Five Supermercado Listo charges in June — whose books?"*,
not *"Supermercado Listo (grocery, Berlin) has five charges on the Carter
Studio card this month — €33,52, €24,37…"*.

Six belong to June and three to July, every one stamped with its `period:` and
its `books:`, and each carries `suggested_actions` so the buttons on a card are
the agent's own suggestion rather than the view's guess.

**2026-05 — `review`, and nothing left grey.** All four checklist rows `done`,
7 matched transactions, 1 excluded as personal (Stadtwerke), and every one of
the six files the letter lists really present in `attachments-to-send/` under
exactly the name the letter gives it. That last part is what makes it the
send-state period: the send block appears only once nothing above it is grey, so
a single missing file makes this period unshootable and nothing says so.

**2026-04 — `sent`, and the reply is in.** The email went out on 4 May;
M. Fischer wrote back on the 6th asking whether Vellum & Co — a new payer, and
the studio's first client outside Germany — was domestic or EU, because an EU
business customer means the tax liability transfers and he needs the VAT number
for the quarterly listing. Alex answered in their own words (*"Vellum sitzt in
Wien"*), Clerk found the VAT number on Vellum's order, wrote back, and recorded
that Vellum is an EU client so it never has to ask again.

**This period used to be deliberately reply-LESS**, on the grounds that an empty
paste-reply field is what makes the field read as an affordance. Both halves of
that reasoning have gone: there is no dedicated reply field any more (one box at
the foot of the period does *paste their reply* and *tell me something* alike,
always in the same place), and a `sent` run WITH a reply is exactly what the app
produces the moment somebody pastes one. It is the state the finished-period
screen is drawn from — sent, answered, and not yet filed — and nothing else in
the fixture reaches it.

**2026-03 — `done`.** The full loop, and the only period where the accountant
actually answered: Fischer asked for the Bewirtungs-Anlass on the 12 March
Brew & Bean lunch (§ 4 Abs. 5 Nr. 2 EStG needs occasion + participants), Clerk
recovered it from Alex's own voice memo of that day, the Anlass went into the
ledger row and the assembled list, and Fischer confirmed. That exchange is
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

## The two states the marketing shoot needs

Two frames of the how-it-works story could not be shot from synthetic data, and
both are fixture states rather than screens:

| Frame | Wants | Period |
|---|---|---|
| the send state | a period with **nothing grey** — every row a real staged file, and the send block revealed | **carter-studio/2026-05** |
| the finished period | **sent, and they replied** — the thread, and *Is April finished?* unpressed | **carter-studio/2026-04** |

The rest of the fixture exists to make those two legible: March is what filing
looks like afterwards, June is what the same screen looks like while it is still
mostly grey, and the club is the second tab.

**The letter is the period, so it is written FIRST and mostly empty.** June
used to be the proof of the old order: mid-run, and with no draft file at all,
because the workflow wrote the letter at `review`. It now ships a **thin** one —
recipient, subject, greeting, sign-off, and a plain sentence saying what is still
being collected — and it stages files as it gets them rather than in a batch at
the end, so `attachments-to-send/` holds the statement and the one receipt that
is already settled. That is what makes June the mid-collection frame: two solid
rows and the rest grey.

**Solid rows come from the STAGED FOLDER, not from the letter's own numbered
list.** The app lists what is really in `attachments-to-send/` and ghosts the
checklist rows that have nothing there yet. So a filename typed into the draft
with no file behind it does not produce a row — it produces a discrepancy
between the letter the user reads and the folder they send.

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

`--spec` mode writes the **packet** filename — `YYYY-MM-DD-<vendor>-beleg.png`,
ASCII — because those images are the ones that go out attached to a letter. The
sampled mode keeps its own `YYYYMMDD-slug.png`; it feeds the photo library,
where nothing is staged and nothing is paired.

**Supplier invoices are PDFs, and they are generated too**: `gen_invoice_pdf.py`
writes each one into its period's `receipts/` folder. Copies under
`attachments-to-send/` and `attachments-sent-*/` are made by hand, because which
of them went out on which day is a fact about the sending rather than about the
document.

A spec entry may declare `"total"`; the renderer sums the line items and
**aborts** if they disagree, so a typo can't reach a packet. Merchants must
already exist in `MERCHANTS` (city, language and VAT rate come from there, so a
spec can't invent an inconsistent merchant).

## Invariants worth re-checking after any edit

**Five of them are now a script, not a memory:**

```bash
python3 generate/check_bookkeeping_fixture.py
```

It asserts the letter/staged-folder agreement, the no-paths and no-our-words
rules over everything a person reads, that every `receipt_path` resolves, and
that each closed month has exactly one nameable document-less movement. Run it
after editing any fixture file; the rest of this list is still yours to check.


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
- **A document has ONE filename**, in `receipts/` or `statements/` and in
  `attachments-to-send/` alike, byte-for-byte — see the naming section above.
  Different spellings of one document silently empty the letter's origin
  column.
- **Every filename in a letter is a file that exists**, in that period's
  `attachments-to-send/`, spelled identically. The app makes an openable link
  out of each one, so a name with no file behind it is the single lie the letter
  can tell — and it looks exactly like a correct row until somebody clicks it.
- **Nothing a person reads carries a path or an internal filename.** Not a
  deliverable `label` or `detail`, not `current_activity`, not a question, and
  not the letter — the recipient of that email has no `Notes/bookkeeping/`.
- **No word that is ours rather than theirs** in those same places: not
  *packet*, *deliverables*, *round*, *set of books* or *reconcile*, and never one
  of our own bank names. The company's own name, the period's own name, and the
  files' own names are what belong there.
- **Exactly one movement per closed month has no document at all** (the
  Werkraum desk, which issues no monthly invoice, and Alex said so). That is
  what the finished period leads with, so it has to be nameable and singular —
  the income lines point at the statement and say in `why` where the real
  invoice lives, rather than looking like three more gaps.
