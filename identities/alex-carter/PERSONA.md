# Alex Carter — primary demo identity

Fictional. Any resemblance to real persons or companies is coincidental.

## Identity

- **Name:** Alex Carter (they/them in all copy — keeps assets universally relatable)
- **Age:** 38. **Born:** **1987-08-11**. **Base:** Berlin, Germany
  (English-speaking expat — EU story for Clerk.AI, English assets for everyone
  else)
  - The date is pinned because "age 38" alone is ambiguous — it only says
    *somewhere between 1987-07-01 and 1988-06-30* relative to the demo epoch
    below, so anything needing a real date (a form, an ID document, an
    age-gated signup) would invent its own and the fixtures would quietly
    disagree with each other. It is 11 August 1987, the day **HyperCard**
    shipped: Apple's "programming for the rest of us", which is close enough to
    what these products are for to be worth the wink.
  - **Note it does NOT track the demo epoch.** Alex turns 39 in August 2026, so
    if the epoch ever moves past 2026-08-11 the age above becomes 39 and this
    file is the place to fix it.
- **Work:** independent product designer + front-end consultant, solo company
  **Carter Studio UG** (fictional German UG), clients across DE/UK/NL
- **Demo epoch ("today"):** **2026-06-30** — end of a month, end of a quarter:
  perfect for a period-close demo, recent enough for fresh timeline items.

## Cast (recurring people — must stay consistent across all fixtures & photos)

| Person | Role | Appears in |
|---|---|---|
| Alex Carter | protagonist | everything |
| Sam Okafor | partner, secondary-school teacher | photos across all eras, voice memos |
| Mira Carter-Okafor | daughter, b. 2019 | photos 2019→, school-logistics memos |
| Jonas Weber | best friend since university, climbing partner | photos (climbing trips), memos |
| Priya Sharma | Carter Studio's biggest client (fictional agency "Northlight") | work memos, invoices |
| Rosa Carter | Alex's mother, in Manchester | visit-era photos, calls |

## Era timeline (drives RT's Life Book era detection)

1. **2014–2016 — Manchester:** university tail + first agency job. Photos: city, uni
   friends, early climbing with Jonas.
2. **2016–2018 — the move to Berlin:** new city, Sam appears mid-2017.
3. **2019–2021 — Mira arrives:** family era, fewer trips, home photos.
4. **2022–2024 — Carter Studio:** going solo; workspace, client work, conference trips
   (Amsterdam, Lisbon).
5. **2025–2026 — now:** balance era — family + studio + climbing returns; the era the
   apps' "most recent era" pre-selects.

## Money shape (drives Clerk.AI fixtures)

- **Bank:** "Meridian Business" (fictional pan-EU fintech; CSV export) + a personal
  card "Meridian Everyday". Currency: EUR.
- **Recurring costs:** Nimbus Cloud Hosting (infra), Fontrack Pro (design SaaS),
  RailLink (travel), Brew & Bean (client coffees), Bürobedarf Kern (office supplies,
  German receipts), studio co-working rent "Werkraum Kollektiv".
- **Income:** monthly invoice to Northlight Agency + 1-2 smaller clients.
- **Accountant:** "M. Fischer Steuerberatung" (fictional) — the period-close packet
  recipient.

## Second set of books — Kletterfreunde Kreuzberg e.V.

Alex keeps a **second set of books** that is not a second business: they are the
volunteer **Kassenwart** (treasurer) of a small Berlin climbing club, about
ninety members, elected 2024. They came to it through Jonas Weber, who is
already the cast's climbing partner — so it adds a set of books without adding
a person.

- **Its own instruments.** A club account at **Bürgerbank Kreuzberg** (a local
  Genossenschaftsbank — clubs bank locally, not with a business fintech) *and* a
  **Vereinskarte** the treasurer holds. Two instruments, one set of books.
- **Its own cadence.** Financial year = calendar year; the **Kassenbericht** is
  due for the **Mitgliederversammlung in May**. So the 2025 books closed in May
  2026 and the next is not due till May 2027 — the opposite rhythm to Carter
  Studio's monthly close.
- **Its own recipient.** A club's books do not go to a Steuerberater. They go to
  the two elected **Kassenprüfer**, who report to the members' meeting. No VAT
  return, no EÜR, no Fischer.

**Why a club rather than a second company.** Two companies filing to the same
accountant would be the same story twice. A club is a set of books kept by
someone who owns no second business, files to no accountant, and reports to a
room of members — which is the shape a bookkeeping product is least likely to
have been designed around, and therefore the one worth having in the dataset.

**What it makes demonstrable.** Three instruments settle almost everything by
themselves:

| Instrument | Belongs to |
|---|---|
| Meridian Business account / card | Carter Studio UG |
| Bürgerbank account / Vereinskarte | Kletterfreunde Kreuzberg e.V. |
| **Meridian Everyday (Alex's own card)** | **nothing — only Alex knows** |

The third is the interesting one. Alex buys club things on their own card — a
rope, a competition entry, a round of coffees after a session — and claims them
back at the next committee meeting; and buys studio things on it too. Those are
the handful of purchases a month that a person has to sort out themselves.

Club shape: membership dues in over January and February, a quarterly hall
block-booking, annual liability insurance, a DAV section levy, competition entry
fees in spring, a minibus for the youth trip, gear.

## Multilingual showcase subset

Fixtures deliberately not in English, to demonstrate multi-language handling:

- **Receipts:** Bäckerei Sonnenschein (German), K-Kulma Kioski (Finnish), Kaffebaren
  Söder (Swedish), Café del Sol (Spanish).
- **Voice memos:** English + German only — see "Languages" below. The multilingual
  *OCR* showcase is carried by the receipts above, which is where it belongs: a
  traveller's receipt pile is naturally in the merchants' languages.

## Languages (governs every voice fixture)

| Person | Speaks | Why |
|---|---|---|
| Alex Carter | English (native), German (learned) | British; Berlin resident since 2016 |
| Sam Okafor | English, German | lives + teaches in Berlin |
| Mira | English, German | Berlin school |

**Rule: never put a fixture in a language its speaker doesn't speak.** Alex does not
dictate notes-to-self in Finnish because a trip went to Helsinki, and foreign clients
do not leave Alex voicemail in languages Alex can't understand — earlier versions of
this dataset did both and they read as bugs.

**The legitimate route to another language is a RECORDED MEETING** held in it, where
the other party speaks and Alex recorded it to transcribe afterwards (that's the
product's actual use case). The German tax-advisor recording works exactly this way:
German audio, English title, because Alex named the file. Any future language should
arrive the same way — or via a second identity whose cast genuinely speaks it.

## Voice-memo topics (English bulk — scripts in `generate/voice-scripts/`)

Client-call debriefs (Northlight rebrand), expense context notes ("client lunch with
Priya, the rebrand kickoff, expense not personal"), Mira logistics, climbing-trip
planning with Jonas, studio ideas, a call-mum reminder. Fictional throughout.
