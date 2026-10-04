# Mind My Money demo vault — a finished round on the Carter-Okafor household

What a **finished** money round leaves in a vault, for somebody who wants to try
Mind My Money without their own bank data: a tester, an App Review reviewer, a
screenshot. The household is the made-up one in `../` (Alex Carter, Sam Okafor
and their daughter Mira in Berlin, three accounts, June 2025 to June 2026).

The tree is laid out as a vault root: copy `Notes/` and `Registry/` into a vault
and it is the state a round left behind.

| Path | What it is |
|---|---|
| `Notes/money/round.md` | the round: what was read (3 accounts, 1,060 payments), what was named, what was acted on. `status: waiting-on-you` |
| `Notes/money/rows/{YYYY-MM}.md` | 13 month tables, every payment named, guessed or not yet named |
| `Notes/money/reports/` | 20 reports: every month, the quarters 2025-Q3 to 2026-Q2, the two part years, and `12m-2026-06` |
| `Notes/money/ledger.md`, `items/` | 25 recurring commitments, the running total (**€179.88 a year**, one verified cancellation) |
| `Notes/money/actions.md`, `accepted.md` | the approval log, and June 2026 accounted for |
| `Notes/money/evidence/`, `axes.md`, `vendors.md`, `views/` | what proved a name, the categories, the merchant memo, one picture asked for |
| `Notes/money/raw/2026-10-01/` | the three exports the round read, byte for byte the ones in `../statements/` |
| `Registry/alex-carter/questions/` | the setup answer, 8 answered round cards, and **2 open cards**: the gym (is it still used?) and one Ratenwerk purchase (what was it?) |

## Where it came from

A real round on the end-to-end rig, 1–2 October 2026, against the household's
portals (`scripts/e2e/` in the monorepo). Copied off the rig and cleaned:

- dropped what the app writes for itself (`phone/`, `asks/`), the after-close
  favour ledger and its two cards, the catch-up test's leftovers (a second
  export, a section of `round.md`, a line in the June report), and the two
  cards whose answers were the rig's portal addresses;
- the remaining portal addresses became `<name>.example`;
- the two open cards are new. They ask what the round itself left open (the
  ledger said `found` and `unknown` for them), and `ledger.md` and `items/` now
  say `asked` to match;
- `round.md` and `Notes/money/README.md` say it is a made-up household.

Nothing regenerates this tree. Edit it by hand, then:

```sh
python3 generate/gen_bookkeeping_manifest.py   # rewrites MANIFEST.txt here and Clerk's
python3 generate/check_demo_vault.py           # the contracts, the open cards, no leftovers
```

## How the app fetches it

Same as Clerk's `fixtures/clerkai/period-close` (`core-lib/src/services/demo_dataset.rs`
in the monorepo): `MANIFEST.txt` lists every file as a **repo-relative path**, one
per line; each is fetched from `raw.githubusercontent.com` (everything here is
text, so nothing goes through the LFS host); anything the manifest no longer
lists is pruned. This README and the manifest itself are not in the manifest.

⛔ **The app's version stamp must be bumped in the same change as any edit here**,
or an install that has fetched the demo before never fetches the edit.

⚠️ **The cards are filed under `alex-carter`.** The app reads cards from
`Registry/<the vault's active identity>/questions/`, so the seed copies them
into whatever identity the vault has, as Clerk's does.

⛔ **Never seed this into a vault the end-to-end rig runs a round on.** It is
the finished round, i.e. the answer key, the same as `../PLANTED.md`. A round
that starts from it has nothing left to find.
