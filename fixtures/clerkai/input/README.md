# `input/` — the source documents, before anything has been done with them

The sibling `period-close/` tree is a **finished** close: a month's material
already sorted, staged and written up. This is the other end of the same month —
what Alex Carter possesses before any of that work happens.

Useful if you want to exercise a bookkeeping pipeline from a realistic starting
point rather than from its output.

## What is here

| Path | What it is |
|---|---|
| `statements/meridian-business-2026-06.csv` | Carter Studio UG's June 2026 business account statement, 27 lines. The spine of the month: every line either has a document behind it or needs explaining. |

## What is deliberately not here

**No summary, no categorisation, no accountant or business details.** Those are
conclusions, and a fixture that ships them cannot be used to test whether a tool
arrives at them. The statement is the raw material; `period-close/` is one worked
answer to it.

**No photos** — not missing, just elsewhere. Twenty phone photographs of paper
receipts from this same June live in
`generate/photos/library/alex-carter/receipts/`, with EXIF timestamps and GPS at
the merchants' locations; sixteen carry a legible total. Duplicating large images
here would serve nothing.

**No email.** This identity has no mailbox fixture; the correspondence in
`period-close/` is written as markdown rather than as mail files.

## Reconciling the two ends

Every debit in the statement should be traceable to something — a receipt
photograph in the photo library, a rendered scan in `../receipts/`, or a line in
the close under `../period-close/`. That correspondence is the point of shipping
both ends. A few lines are deliberately explainable only from context (bank fees,
an internal transfer), because a real month has those too.
