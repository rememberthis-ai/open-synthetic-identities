# Clerk.AI period-close fixture — 2026-06, frozen mid-run

A snapshot of a Clerk.AI period-close run for the `alex-carter` demo identity,
frozen partway through: statement collected, some receipts matched, two
receipts still awaiting curation review, and two transactions blocked on an
open question card (personal-vs-business judgment calls). Demo epoch is
2026-06-30, so this is "yesterday's" in-progress state — exactly what a fresh
screenshot pass wants to show off the live run view, the materials/candidates
panel, and the question-card inbox without waiting for a real browser-driven
collection run.

Matches the real schema documented in the monorepo's
`docs/technical/CLERK-PERIOD-CLOSE.md` and implemented in
`core-lib/src/services/period_close.rs` / `core-lib/src/workers/
questions_watcher.rs` — **markdown is the ground truth**; the app's SQLite
index is a rebuildable projection of these files.

## Layout

```
Notes/bookkeeping/2026-06/
  run.md            # run header: phase=match, status=paused, step tracker
  items/*.md         # one file per ledger line item / deliverable-checklist row
  receipts/*.png      # receipt images referenced by items' receipt_path
                       # (copied from ../../../receipts/, the source fixtures)
  statements/*.csv    # the downloaded bank statement (copied from
                       # ../../../statements/, the source fixture)
Registry/alex-carter/questions/
  q-*.md              # the two open question cards the run's blocked on
```

Money/vendor facts (amounts, dates, vendor names) are drawn from the existing
`fixtures/clerkai/receipts/` + `fixtures/clerkai/statements/` fixtures for
alex-carter's June 2026 — see PERSONA.md for the cast/business shape.

## What state this shows

- **Deliverables checklist** (`kind: deliverable` items): bank statement done,
  client invoice matched, receipts still collecting, vendor invoices not
  started.
- **Matched ledger lines** (`status: matched`): coworking rent, hosting, the
  Fontrack Pro subscription (matched to an actual receipt image), and the
  Northlight income line.
- **Candidate receipts** (`status: candidate`, `kind: receipt`): two OCR-found
  receipts (Kaffebaren Söder, K-Kulma Kioski) awaiting Keep/Drop review in the
  curation panel — each carries a `why` explaining the match.
- **Blocked-on-you lines** (`status: ask`): two transactions each pointing at
  an open question card via `question_slug` — a new-vendor check (Hallo
  Mobilfunk GmbH) and a personal-vs-business call (Supermercado Listo
  groceries).

## Restoring into a vault

Markdown is the ground truth, so restoring is a file copy + reindex — no app
code involved:

```bash
# vault = ~/Clerk.AI (or wherever the target install's vault root is)
cp -R fixtures/clerkai/period-close/Notes/bookkeeping/2026-06 "$vault/Notes/bookkeeping/"
mkdir -p "$vault/Registry/alex-carter/questions"
cp fixtures/clerkai/period-close/Registry/alex-carter/questions/*.md \
   "$vault/Registry/alex-carter/questions/"
```

Then either wait for the daemon's `questions_watcher` (polls every 2s) to
pick up the new files, or trigger `POST /index/rebuild` on the daemon
(port 21438) for an immediate full reindex. The active identity must be
`alex-carter` (or whichever identity id the target vault uses — rename the
`Registry/<identity>/` folder to match) for the question cards to surface;
the bookkeeping tables aren't identity-scoped.

## Regenerating

This fixture is hand-authored, not script-generated (unlike the receipts/
statement CSVs) — it's a deliberately curated *narrative* state (which items
are matched vs. candidate vs. blocked), not a bulk data table. To evolve it
(e.g. a July close, or a further-along phase), edit the files directly
following the frontmatter schema in `core-lib/src/services/period_close.rs`
(`RunUpdate` / `MaterialUpdate`) and `build_question_markdown` in
`core-lib/src/mcp/server.rs` for question cards.
