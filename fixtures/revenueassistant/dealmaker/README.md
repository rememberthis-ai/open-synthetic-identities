# Lindgate Advisory: a deal maker's sources

For The Revenue Assistant (https://therevenueassistant.com), which keeps a map of who is around a business:
customers, investors and partners, placed by what has actually happened with each of them.

**Everything here is invented**: the firm, the people, the companies, the investors and the deals. Domains
are `.example`, and iMessage handles are email addresses, so no phone number belongs to anyone. Lindgate
Advisory is a two-partner corporate-finance boutique in Helsinki that sells founder-owned Nordic companies,
and it works two kinds of counterpart at once: the companies and the investors who buy them.

"Today" is **2026-10-09**. Mail, calendar and iMessage cover June to that date; older history lives only in
the CRM or the folder, so a reader has to use those to place the long relationships.

| Path | What |
|---|---|
| `shared/` | mail (`.eml`), `calendar.ics`, iMessage threads, a newsletter activity export, a site summary |
| `crm/` | variant A: a Pipedrive-style CSV export (organizations, persons, deals, activities) |
| `folder/` | variant B: a shared folder used as the CRM: `Prospects.xlsx` (and its two sheets as CSV), a OneNote-style export with a page per meeting and a log page per company |
| `truth.json`, `ANSWER-KEY.md` | each of the 20 parties' ring, kind and sector, and why |
| `PERSONA.md`, `rig/respond.py` | Johan Aalto, one of the partners, answering an app's questions about his business |

Use `shared/` plus **one** of `crm/` or `folder/`: they describe the same relationships two ways.

Everything is written by `generate/gen_dealmaker.py` (needs `openpyxl`); edit the story there and rerun it,
never the files here. `ANSWER-KEY.md` lists the traps a correct reading avoids: a CRM stage is not an event,
a "no" to one deal is not a "no" to the person, and a bidder's track is its own deal, part of the sale.
