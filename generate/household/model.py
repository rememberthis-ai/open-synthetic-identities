"""The world the Carter-Okafor household spends in.

**Every company, bank, rail and levy named here is invented.** That is not a
stylistic preference: these files are published, they get screenshotted, and a
statement row is exactly the kind of artefact that reads as real. The German
ones are invented compound nouns in the same family as the rest of this
repository (`Werkraum Kollektiv`, `Hallo Mobilfunk`), and the statutory-looking
ones are invented too — there is no `Rundfunkbeitrag` here, because that is a
real levy with a real amount and a real collector.

## The three instruments, and why their exports differ

| slug | what | export |
|---|---|---|
| `meridian-everyday` | Alex's own card | Meridian's English CSV — the same shape as the studio's business export |
| `havelbank-joint` | the household Girokonto | German semicolon CSV, comma decimals, `Buchungstag`/`Verwendungszweck`, **UTF-8 with a BOM** |
| `nordufer-sam` | Sam's card at a second bank | German semicolon CSV, quoted fields, **Soll/Haben in two columns**, **cp1252** |

The agent is the parser, so the dialects are the point. The BOM and the cp1252
are not cruelty — they are what German bank exports actually are, and a run that
only ever meets one well-behaved UTF-8 CSV has not met a bank.

## The rails

A payment rail is a company that stands between the household and the shop, so
the bank sees the rail. The nine here are fictional stand-ins for the nine
shapes a Berlin statement actually carries; `RAILS` records which real shape
each one imitates, because that is the fact a reader needs and the invented name
is the fact a reader must not mistake for real.
"""

from __future__ import annotations

from dataclasses import dataclass, field

# --------------------------------------------------------------------- window

WINDOW_START = "2025-06-01"
WINDOW_END = "2026-06-30"
"""Thirteen months to the demo epoch, so June 2026 has June 2025 beside it and
the report's shadow columns have numbers."""

ACCOUNTS = {
    "meridian-everyday": {
        "label": "Meridian Everyday",
        "bank": "Meridian",
        "holder": "Alex Carter",
        "iban": "DE21 5001 0517 0044 1928 33",
        "dialect": "meridian",
        "opening": 1842.10,
    },
    "havelbank-joint": {
        "label": "Havelbank Girokonto (gemeinsam)",
        "bank": "Havelbank Berlin",
        "holder": "A. Carter / S. Okafor",
        "iban": "DE68 1002 0500 0071 4488 02",
        "dialect": "havelbank",
        "opening": 3180.44,
    },
    "nordufer-sam": {
        "label": "Nordufer Bank Karte",
        "bank": "Nordufer Bank",
        "holder": "Sam Okafor",
        "iban": "DE44 1007 7777 0284 6610 51",
        "dialect": "nordufer",
        "opening": 612.85,
    },
}

# ---------------------------------------------------------------- the categories
#
# The labels the answer key grades against. They are the person's words, not a
# taxonomy: the agent writes its own in `axes.md`, and these exist so a run can
# be marked. Kept close to the vocabulary in the design samples so a grader is
# comparing like with like.

CATEGORIES = [
    "Housing",
    "Food and drink",
    "Children",
    "Transport",
    "Health",
    "Subscriptions and memberships",
    "Clothing",
    "Home and things",
    "Going out",
    "Insurance and money",
    "Holidays",
    "Money in",
]

# --------------------------------------------------------------------- rails


@dataclass(frozen=True)
class Rail:
    slug: str
    name: str
    imitates: str
    """The real-world shape this stands in for. Documentation, never rendered."""
    names_the_shop: str
    """`always` | `sometimes` | `never` — what the bank row gives you."""
    evidence: str
    """Where the thing that names it lives, when it exists at all."""


RAILS = {
    "pagolink": Rail(
        "pagolink", "Pagolink Europe S.a r.l. et Cie, S.C.A.",
        "PayPal — about 35% of German e-commerce, arriving as a SEPA-Lastschrift",
        "sometimes", "mail",
    ),
    "ratenwerk": Rail(
        "ratenwerk", "Ratenwerk Bank AB",
        "Klarna — Rechnungskauf and instalments, which absorbed SOFORT in 2025",
        "never", "bnpl",
    ),
    "warenlager": Rail(
        "warenlager", "Warenlager Payments Europe",
        "an Amazon-style marketplace: the marketplace is named, the item is not",
        "never", "marketplace",
    ),
    "rechnungsbruecke": Rail(
        "rechnungsbruecke", "Rechnungsbrücke GmbH",
        "Ratepay / Riverty — Rechnungskauf for German webshops",
        "never", "mail",
    ),
    "kassenband": Rail(
        "kassenband", "Kassenband",
        "Stripe — the shop inside a 22-character descriptor, so it is truncated",
        "sometimes", "mail",
    ),
    "zahlnetz": Rail(
        "zahlnetz", "Zahlnetz Payments",
        "Mollie — the processor's name and an order reference",
        "never", "mail",
    ),
    "nordpfad": Rail(
        "nordpfad", "Nordpfad Payments",
        "Adyen — meant to carry the shop, sometimes carries the chain",
        "sometimes", "mail",
    ),
    "kartenkopf": Rail(
        "kartenkopf", "Kartenkopf",
        "SumUp / Zettle — a market stall's terminal, sometimes a bare merchant code",
        "sometimes", "photo",
    ),
    "tellerflink": Rail(
        "tellerflink", "Tellerflink Lieferservice",
        "a Lieferando-style platform: the platform, never the restaurant",
        "never", "mail",
    ),
}

# ----------------------------------------------------------------- merchants
#
# `(name, category, rail-or-None, low, high, times-per-month)` for the everyday
# card spend. A rail of None means the shop's own terminal or Lastschrift, so
# the bank names it and the row is `named` from the bank text alone.

@dataclass(frozen=True)
class Shop:
    name: str
    category: str
    lo: float
    hi: float
    per_month: float
    """Expected appearances per month; fractional means "some months"."""
    rail: str | None = None
    terminal: str = ""
    """How a girocard terminal registers it, if that differs from the name."""
    basket: str = ""
    """Which basket generator fills the line items, if any."""
    bare_code: float = 0.25
    """For a card-terminal rail: how often the terminal prints a merchant code
    instead of the shop. A market stall's hired terminal usually does; a cafe
    that has had the same one for years usually does not."""


HOUSEHOLD_SHOPS = [
    # --- the joint account's girocard and Lastschrift spending ------------
    Shop("Kaufhalle Nord", "Food and drink", 22.0, 96.0, 5.2,
         terminal="KAUFHALLE NORD 4471 BERLIN"),
    Shop("Drogerie Flink", "Home and things", 6.4, 38.0, 2.8,
         terminal="DROGERIE FLINK FIL 212"),
    Shop("Bäckerei Sonnenschein", "Food and drink", 2.8, 11.4, 4.1,
         terminal="BAECKEREI SONNENSCHE"),
    Shop("Apotheke am Kottbusser Tor", "Health", 7.2, 44.0, 0.8,
         terminal="APO KOTTBUSSER TOR"),
    Shop("Späti Mond", "Food and drink", 3.1, 14.0, 2.3,
         terminal="SPAETI MOND BERLIN"),
    Shop("Baumarkt Schraube & Co", "Home and things", 9.0, 128.0, 0.6,
         terminal="BAUMARKT SCHRAUBE CO"),
    Shop("Spielwerk Spielzeug", "Children", 8.0, 46.0, 0.5,
         terminal="SPIELWERK SPIELZEUG"),
    Shop("Marktstand Grünwinkel", "Food and drink", 6.0, 29.0, 1.6,
         rail="kartenkopf", bare_code=0.65),
    Shop("Hofladen Havelgrün", "Food and drink", 11.0, 41.0, 0.4,
         rail="kartenkopf", bare_code=0.6),

    # --- Alex's card -------------------------------------------------------
    Shop("Brew & Bean", "Going out", 3.4, 18.5, 4.6,
         terminal="BREW AND BEAN BERLIN"),
    Shop("Supermercado Listo", "Food and drink", 9.4, 44.0, 3.1,
         terminal="SUPERMERCADO LISTO"),
    Shop("Vertikal Sport Berlin", "Home and things", 14.0, 142.0, 0.5,
         terminal="VERTIKAL SPORT BLN"),
    Shop("RailLink DE", "Transport", 22.0, 184.0, 0.9,
         terminal="RAILLINK DE"),
    Shop("Kino Lichtblick", "Going out", 9.0, 27.0, 0.6,
         rail="kassenband"),
    Shop("Radwerk Kreuzberg", "Transport", 8.0, 96.0, 0.35,
         terminal="RADWERK KREUZBERG"),
    Shop("Bar Nachtkarte", "Going out", 11.0, 48.0, 0.5,
         rail="kartenkopf", bare_code=0.3),

    # --- Sam's card --------------------------------------------------------
    Shop("Buchhandlung Silbenfisch", "Home and things", 7.9, 38.0, 1.5,
         terminal="BUCHH SILBENFISCH"),
    Shop("Kleiderwerk Berlin", "Clothing", 18.0, 94.0, 0.6,
         terminal="KLEIDERWERK BERLIN"),
    Shop("Schuhhaus Trittfest", "Clothing", 24.0, 118.0, 0.25,
         terminal="SCHUHHAUS TRITTFEST"),
    Shop("Café Zeitlupe", "Going out", 3.6, 16.4, 3.3,
         rail="kartenkopf", bare_code=0.2),
    Shop("Optiker Klarsicht", "Health", 18.0, 210.0, 0.12,
         terminal="OPTIKER KLARSICHT"),
]

SHOPS_BY_ACCOUNT = {
    "havelbank-joint": [
        "Kaufhalle Nord", "Drogerie Flink", "Bäckerei Sonnenschein",
        "Apotheke am Kottbusser Tor", "Späti Mond", "Baumarkt Schraube & Co",
        "Spielwerk Spielzeug", "Marktstand Grünwinkel", "Hofladen Havelgrün",
    ],
    "meridian-everyday": [
        "Brew & Bean", "Supermercado Listo", "Vertikal Sport Berlin",
        "RailLink DE", "Kino Lichtblick", "Radwerk Kreuzberg", "Bar Nachtkarte",
        "Bäckerei Sonnenschein",
    ],
    "nordufer-sam": [
        "Buchhandlung Silbenfisch", "Kleiderwerk Berlin", "Schuhhaus Trittfest",
        "Café Zeitlupe", "Optiker Klarsicht", "Drogerie Flink",
    ],
}

# ------------------------------------------------------- online-only merchants
#
# These never have a terminal: they are reached through a rail, so the bank row
# is the rail's and the shop's name lives in the evidence.

@dataclass(frozen=True)
class OnlineShop:
    name: str
    category: str
    lo: float
    hi: float
    weight: float
    goods: list[str] = field(default_factory=list)
    handle: str = ""
    """What the wallet shows instead of the shop, when it shows a handle."""


ONLINE_SHOPS = [
    OnlineShop("Stoffkreis", "Clothing", 24.0, 148.0, 3.0,
               ["Winterjacke Kind", "Turnschuhe 34", "Regenhose", "Pullover",
                "Zwei Paar Jeans", "Schal und Mütze"], "sk-versandhandel"),
    OnlineShop("Spielwerk Spielzeug", "Children", 12.0, 68.0, 1.6,
               ["Bausteine-Set", "Puzzle 200 Teile", "Brettspiel",
                "Malkasten groß"], "spw-handel-berlin"),
    OnlineShop("Buchhandlung Silbenfisch", "Home and things", 9.0, 52.0, 1.8,
               ["Zwei Taschenbücher", "Bilderbuch", "Kochbuch",
                "Hörbuch (CD)"], "silbenfisch"),
    OnlineShop("Gartenmarkt Blattgrün", "Home and things", 14.0, 86.0, 0.9,
               ["Blumenerde 40l", "Balkonkasten x3", "Kräuterset",
                "Gießkanne"], "bg-gartenversand"),
    OnlineShop("Möbelhaus Eichblatt", "Home and things", 38.0, 340.0, 0.5,
               ["Schreibtischstuhl", "Regal Kiefer 80cm", "Bettwäsche-Set",
                "Lampe Wohnzimmer"], ""),
    OnlineShop("Vertikal Sport Berlin", "Home and things", 22.0, 165.0, 0.7,
               ["Kletterschuhe", "Chalkbag und Bürste", "Sicherungsgerät",
                "Kletterseil 60m"], "vertikal-sport"),
    OnlineShop("Pizzeria Vulkano", "Going out", 18.0, 46.0, 1.5,
               ["Familienbestellung"], ""),
    OnlineShop("Thai Küche Lotus", "Going out", 21.0, 52.0, 1.0,
               ["Abendessen zu dritt"], ""),
    OnlineShop("Döner Palast Kottbusser", "Going out", 12.0, 31.0, 1.1,
               ["Abendessen"], ""),
    OnlineShop("Schwimmschule Delphin", "Children", 58.0, 96.0, 0.25,
               ["Kursgebühr Halbjahr"], "schwimmschule-delphin"),
    OnlineShop("Fotolabor Silberkorn", "Home and things", 11.0, 38.0, 0.4,
               ["Abzüge 13x18", "Fotobuch klein"], "silberkorn-foto"),
    OnlineShop("Zoohandlung Fellnest", "Home and things", 14.0, 44.0, 0.6,
               ["Katzenfutter Vorrat", "Streu 20l"], "zh-fn-vertrieb"),
]

# The delivery platform only ever orders from restaurants.
DELIVERY_RESTAURANTS = [
    "Pizzeria Vulkano", "Thai Küche Lotus", "Döner Palast Kottbusser",
    "Sushi Blauwal", "Curry Ecke Oranien",
]

# Which rail an online order goes through, and how often. Roughly the German
# share: the wallet dominates, BNPL is about a fifth, the rest share the tail.
RAIL_MIX = [
    ("pagolink", 0.34),
    ("warenlager", 0.20),
    ("ratenwerk", 0.15),
    ("tellerflink", 0.10),
    ("kassenband", 0.07),
    ("rechnungsbruecke", 0.05),
    ("zahlnetz", 0.04),
    ("nordpfad", 0.04),
    ("kartenkopf", 0.02),
]

# --------------------------------------------------------- standing charges
#
# `(day, counterparty, purpose, booking_text, amount, category, first, last)`
# `first`/`last` are inclusive `YYYY-MM` bounds; None means the whole window.

@dataclass(frozen=True)
class Standing:
    account: str
    day: int
    counterparty: str
    purpose: str
    booking: str
    amount: float
    category: str
    merchant: str
    first: str | None = None
    last: str | None = None
    months: tuple[int, ...] | None = None
    """Restrict to these calendar months (for quarterly charges)."""
    slug: str = ""
    """Links the charge to a recurring commitment in PLANTED.md."""


STANDING = [
    # --- the joint Girokonto ----------------------------------------------
    Standing("havelbank-joint", 1, "HAUSVERWALTUNG LINDENHOF GMBH",
             "MIETE WHG 3 OG RE OBJ 4471", "DAUERAUFTRAG",
             -1480.00, "Housing", "Hausverwaltung Lindenhof", slug="miete"),
    Standing("havelbank-joint", 3, "HAUSVERWALTUNG LINDENHOF GMBH",
             "NEBENKOSTEN VORAUSZAHLUNG OBJ 4471", "LASTSCHRIFT",
             -240.00, "Housing", "Hausverwaltung Lindenhof", slug="nebenkosten"),
    # The utility Abschlag that falls after a contract change: 118,00 through
    # 2025, 94,00 from January. `what changed` has a true sentence because of
    # this row and the letter in the mailbox that announces it.
    Standing("havelbank-joint", 5, "SPREELICHT ENERGIE GMBH",
             "ABSCHLAG STROM KD 88-114-203", "LASTSCHRIFT",
             -118.00, "Housing", "Spreelicht Energie",
             last="2025-12", slug="strom"),
    Standing("havelbank-joint", 5, "SPREELICHT ENERGIE GMBH",
             "ABSCHLAG STROM KD 88-114-203 NEUER TARIF", "LASTSCHRIFT",
             -94.00, "Housing", "Spreelicht Energie",
             first="2026-01", slug="strom"),
    Standing("havelbank-joint", 2, "KITA SONNENBLUME E.V.",
             "ELTERNBEITRAG MIRA CARTER-OKAFOR", "LASTSCHRIFT",
             -95.00, "Children", "Kita Sonnenblume", slug="kita"),
    # Hausrat, switched in January and debited by BOTH insurers in February and
    # March. The old mandate was supposed to end on 31 December.
    Standing("havelbank-joint", 8, "NORDSTERN VERSICHERUNG AG",
             "HAUSRAT MANDAT NV-2019-4471 GLG DE44ZZZ00000441702", "LASTSCHRIFT",
             -18.40, "Insurance and money", "Nordstern Versicherung",
             last="2026-03", slug="hausrat-alt"),
    Standing("havelbank-joint", 10, "BLAUSCHILD VERSICHERUNG AG",
             "HAUSRAT MANDAT BS-2026-8812 GLG DE09ZZZ00000881204", "LASTSCHRIFT",
             -21.90, "Insurance and money", "Blauschild Versicherung",
             first="2026-01", slug="hausrat-neu"),
    Standing("havelbank-joint", 10, "BLAUSCHILD VERSICHERUNG AG",
             "PRIVATHAFTPFLICHT MANDAT BS-2021-3310", "LASTSCHRIFT",
             -7.60, "Insurance and money", "Blauschild Versicherung",
             slug="haftpflicht"),
    Standing("havelbank-joint", 15, "KIEZNETZ BERLIN GMBH",
             "DSL 100 KD 2214-99 RECHNUNG", "LASTSCHRIFT",
             -39.99, "Housing", "Kieznetz Berlin", slug="internet"),
    Standing("havelbank-joint", 16, "MEDIENABGABE ZENTRALSTELLE",
             "MEDIENABGABE BEITRAGSNR 41 992 114", "LASTSCHRIFT",
             -57.60, "Housing", "Medienabgabe Zentralstelle",
             months=(2, 5, 8, 11), slug="medienabgabe"),
    Standing("havelbank-joint", 20, "STADTLINIE BERLIN VERKEHR",
             "MONATSKARTE ABO NR 71-448821", "LASTSCHRIFT",
             -59.00, "Transport", "Stadtlinie Berlin", slug="monatskarte"),
    # The duplicate membership. Sam took it out on 14 October 2025 not knowing
    # Alex had had one on the Meridian card since before the window opened.
    Standing("havelbank-joint", 14, "BILDSTROM MEDIA GMBH",
             "MITGLIEDSCHAFT KD 5512-887", "LASTSCHRIFT",
             -12.99, "Subscriptions and memberships", "Bildstrom",
             first="2025-10", last="2026-01", slug="bildstrom-joint"),
    Standing("havelbank-joint", 14, "BILDSTROM MEDIA GMBH",
             "MITGLIEDSCHAFT KD 5512-887", "LASTSCHRIFT",
             -14.99, "Subscriptions and memberships", "Bildstrom",
             first="2026-02", slug="bildstrom-joint"),
    Standing("havelbank-joint", 28, "LANDESSCHULAMT SUEDOST BEZUEGE",
             "BEZUEGE OKAFOR S PERS-NR 884112", "GUTSCHRIFT",
             +2480.00, "Money in", "Landesschulamt Suedost", slug="gehalt-sam"),
    Standing("havelbank-joint", 30, "A CARTER", "HAUSHALT MONATLICH",
             "GUTSCHRIFT", +1400.00, "Money in", "Alex Carter", slug="haushaltsgeld"),
    Standing("havelbank-joint", 28, "S OKAFOR", "TASCHENGELD",
             "UEBERWEISUNG", -430.00, "Insurance and money", "Sam Okafor",
             slug="uebertrag-sam"),

    # --- Alex's Meridian Everyday -----------------------------------------
    Standing("meridian-everyday", 1, "KRAFTKAMMER KREUZBERG",
             "MITGLIEDSBEITRAG", "LASTSCHRIFT",
             -34.90, "Subscriptions and memberships", "Kraftkammer Kreuzberg",
             slug="kraftkammer"),
    Standing("meridian-everyday", 6, "BILDSTROM MEDIA GMBH",
             "MITGLIEDSCHAFT KD 1140-229", "LASTSCHRIFT",
             -12.99, "Subscriptions and memberships", "Bildstrom",
             last="2026-01", slug="bildstrom-alex"),
    Standing("meridian-everyday", 6, "BILDSTROM MEDIA GMBH",
             "MITGLIEDSCHAFT KD 1140-229", "LASTSCHRIFT",
             -14.99, "Subscriptions and memberships", "Bildstrom",
             first="2026-02", slug="bildstrom-alex"),
    Standing("meridian-everyday", 11, "TONSPUR MUSIK", "ABO FAMILIE",
             "LASTSCHRIFT", -10.99, "Subscriptions and memberships", "Tonspur Musik",
             slug="tonspur"),
    Standing("meridian-everyday", 23, "WOLKENFACH SPEICHER", "200 GB PLAN",
             "LASTSCHRIFT", -2.99, "Subscriptions and memberships", "Wolkenfach",
             slug="wolkenfach"),
    Standing("meridian-everyday", 20, "HALLO MOBILFUNK GMBH",
             "MOBILFUNK PRIVAT VERTRAG 8841-2", "LASTSCHRIFT",
             -24.99, "Subscriptions and memberships", "Hallo Mobilfunk",
             slug="mobil-alex"),
    # The paid trial nobody cancelled: free for thirty days from 3 November,
    # first charged on 3 December, and the descriptor never says what it is.
    Standing("meridian-everyday", 3, "WARENLAGER DIGITAL DE",
             "ABO", "LASTSCHRIFT",
             -4.99, "Subscriptions and memberships", "Warenlager Plus",
             first="2025-12", slug="warenlager-plus"),
    Standing("meridian-everyday", 15, "KLETTERFREUNDE KREUZBERG E.V.",
             "JAHRESBEITRAG 2026", "LASTSCHRIFT",
             -120.00, "Subscriptions and memberships", "Kletterfreunde Kreuzberg e.V.",
             first="2026-01", last="2026-01", slug="kletterfreunde"),
    Standing("meridian-everyday", 29, "HAUSHALT HAVELBANK", "HAUSHALT MONATLICH",
             "UEBERWEISUNG", -1400.00, "Insurance and money", "Havelbank joint",
             slug="haushaltsgeld"),
    Standing("meridian-everyday", 27, "CARTER STUDIO UG", "ENTNAHME MONATLICH",
             "GUTSCHRIFT", +2240.00, "Money in", "Carter Studio UG",
             slug="entnahme"),

    # --- Sam's Nordufer card ----------------------------------------------
    Standing("nordufer-sam", 18, "HALLO MOBILFUNK GMBH",
             "MOBILFUNK PRIVAT VERTRAG 8841-3", "LASTSCHRIFT",
             -14.99, "Subscriptions and memberships", "Hallo Mobilfunk",
             slug="mobil-sam"),
    Standing("nordufer-sam", 7, "BLATTWERK LESEN", "LESEFLAT MONATLICH",
             "LASTSCHRIFT", -9.99, "Subscriptions and memberships", "Blattwerk Lesen",
             slug="blattwerk"),
    Standing("nordufer-sam", 12, "PULSBAHN APP", "PREMIUM", "LASTSCHRIFT",
             -7.99, "Subscriptions and memberships", "Pulsbahn",
             slug="pulsbahn"),
    Standing("nordufer-sam", 28, "A CARTER S OKAFOR", "TASCHENGELD",
             "GUTSCHRIFT", +430.00, "Money in", "Havelbank joint",
             slug="uebertrag-sam"),
]

# Quarterly account charge, both German banks.
QUARTERLY_FEES = [
    ("havelbank-joint", "RECHNUNGSABSCHLUSS", "ENTGELTABSCHLUSS",
     "KONTOFUEHRUNG QUARTAL", -14.70),
    ("nordufer-sam", "RECHNUNGSABSCHLUSS", "ENTGELTABSCHLUSS",
     "KARTENENTGELT QUARTAL", -5.85),
]

# ------------------------------------------------------- the grocer's baskets
#
# `(label, sub, low, high)` — `sub` is the grading sub-category. The weights
# below are what makes "sweets and ice cream cost more than fish and meat" true
# across the year, and `build.py` ASSERTS it rather than hoping: a fixture that
# quietly stopped satisfying its own answer key would be worse than no fixture.

GROCERY_ITEMS = [
    # sweets and ice cream — small, frequent, and nobody notices them
    ("Schokolade Tafel x3", "sweets", 2.85, 4.20),
    ("Eiscreme 900ml", "sweets", 3.49, 5.29),
    ("Gummibärchen Großpackung", "sweets", 1.99, 3.49),
    ("Kekse Sortiment", "sweets", 2.19, 3.99),
    ("Schokoriegel 10er", "sweets", 3.29, 4.99),
    ("Eis am Stiel 8er", "sweets", 2.99, 4.49),
    ("Kinderschokolade Packung", "sweets", 2.49, 3.89),
    # fish and meat
    ("Hähnchenbrust 600g", "meatfish", 6.49, 9.20),
    ("Hackfleisch gemischt 500g", "meatfish", 4.79, 6.80),
    ("Lachsfilet 2 Stueck", "meatfish", 8.49, 12.40),
    ("Aufschnitt Schinken", "meatfish", 2.79, 4.60),
    ("Bratwurst 4er", "meatfish", 3.49, 5.20),
    # produce, dairy, bakery, staples, drinks
    ("Äpfel 1kg", "produce", 2.19, 3.40),
    ("Bananen 1kg", "produce", 1.59, 2.60),
    ("Tomaten 500g", "produce", 1.89, 3.10),
    ("Salat und Gurke", "produce", 2.20, 3.80),
    ("Kartoffeln 2kg", "produce", 2.49, 3.60),
    ("Milch 1l x6", "dairy", 5.34, 7.14),
    ("Joghurt 4er", "dairy", 1.99, 3.20),
    ("Käse Stück", "dairy", 3.29, 6.40),
    ("Butter 250g", "dairy", 2.09, 3.29),
    ("Brot Vollkorn", "bakery", 2.49, 3.80),
    ("Brötchen 6er", "bakery", 1.80, 2.70),
    ("Nudeln 500g x2", "staples", 1.98, 3.20),
    ("Reis 1kg", "staples", 2.29, 3.60),
    ("Passierte Tomaten x3", "staples", 1.77, 2.85),
    ("Mineralwasser Kasten", "drinks", 4.99, 6.90),
    ("Apfelsaft 1l x2", "drinks", 2.58, 4.20),
    ("Kaffeebohnen 1kg", "coffee", 12.90, 18.40),
    ("Kaffeepads 36er", "coffee", 4.29, 6.80),
    # under "groceries" and not food at all
    ("Spülmittel und Schwämme", "household", 3.49, 5.60),
    ("Waschmittel 20WL", "household", 4.99, 8.40),
    ("Toilettenpapier 10er", "household", 4.29, 6.80),
    ("Windeln Gr 5", "household", 8.99, 13.40),
    ("Zahnpasta x2", "household", 3.18, 4.80),
    ("Müllbeutel", "household", 1.99, 3.20),
]

# How many lines of each sub-category a basket tends to carry. The first number
# is the chance the sub-category appears at all; the second is how many lines.
BASKET_SHAPE = [
    ("sweets", 0.90, (2, 4)),
    ("meatfish", 0.62, (1, 2)),
    ("produce", 0.95, (3, 5)),
    ("dairy", 0.92, (2, 4)),
    ("bakery", 0.80, (1, 3)),
    ("staples", 0.66, (1, 3)),
    ("drinks", 0.58, (1, 2)),
    ("coffee", 0.34, (1, 1)),
    ("household", 0.70, (1, 3)),
]

NOT_FOOD = {"household"}

# ----------------------------------------------------------- planted findings
#
# The answer key, declared here and rendered into PLANTED.md with the figures
# `build.py` measures. A finding whose figure is written by hand is a figure
# that drifts the first time a weight changes.

PLANTED = [
    {
        "slug": "bildstrom-duplicate",
        "title": "Two memberships of the same streaming service",
        "what": "Alex has paid Bildstrom from the Meridian Everyday card since "
                "before the window opened. Sam took out a second membership on "
                "the joint Girokonto on 14 October 2025, not knowing about the "
                "first. Both are full-price family plans; nobody watches the "
                "second one.",
        "where": "havelbank-joint (the duplicate) and meridian-everyday (the original)",
        "evidence": "Bildstrom's own account page lists the membership, when it "
                    "started and when it was last watched (never). The cancel "
                    "flow ends on a confirmation page naming the end date.",
        "verdict": "Cancel the joint-account one.",
        "measure": "bildstrom-joint",
    },
    {
        "slug": "bildstrom-price-rise",
        "title": "The streaming plan went up mid-year",
        "what": "12,99 a month until January 2026, 14,99 from February, on both "
                "memberships. Two amounts across the months, announced by an "
                "email in the household mailbox.",
        "where": "both Bildstrom rows",
        "evidence": "The mailbox holds the price-change notice dated 2026-01-12.",
        "verdict": "Nothing to act on; it belongs in *what changed*.",
        "measure": "bildstrom-rise",
    },
    {
        "slug": "kraftkammer-unused",
        "title": "A gym charged every month, unvisited since March",
        "what": "34,90 a month on Alex's card for the whole window. The last "
                "check-in was 7 March 2026 — after which Alex went back to "
                "climbing with Jonas at the club.",
        "where": "meridian-everyday",
        "evidence": "The gym's members' area lists every check-in, newest first.",
        "verdict": "Ask whether to cancel. The person decides; the rows only "
                   "prove it has not been used.",
        "measure": "kraftkammer",
    },
    {
        "slug": "warenlager-plus-trial",
        "title": "A paid trial nobody cancelled",
        "what": "Warenlager Plus, free for thirty days from 3 November 2025, "
                "first charged on 3 December and every month since. The bank "
                "row says WARENLAGER DIGITAL DE and nothing else, so it reads "
                "as a purchase rather than a subscription.",
        "where": "meridian-everyday",
        "evidence": "The marketplace's Memberships page gives the trial start, "
                    "the first payment and the renewal date.",
        "verdict": "Cancel, or keep deliberately. Small, and the point is that "
                   "small is what survives unnoticed.",
        "measure": "warenlager-plus",
    },
    {
        "slug": "hausrat-doppelt",
        "title": "Household insurance paid twice for a quarter",
        "what": "The Hausratversicherung moved from Nordstern to Blauschild "
                "with effect from 1 January 2026. Blauschild began collecting "
                "in January; Nordstern's mandate was never stopped and went on "
                "collecting through the whole first quarter as well, so the "
                "household paid two household-contents policies for three "
                "months.",
        "where": "havelbank-joint",
        "evidence": "The mailbox holds Nordstern's cancellation confirmation "
                    "naming 31 December 2025 as the end date, and Blauschild's "
                    "new policy starting 1 January.",
        "verdict": "Claim the two collections back. This is money owed, not "
                   "money to stop spending.",
        "measure": "hausrat-doppelt",
    },
    {
        "slug": "sweets-over-meat",
        "title": "Sweets and ice cream cost more than all the fish and meat",
        "what": "Across thirteen months at the grocer, the sweets and ice cream "
                "lines outspend every line of fish and meat. Neither figure is "
                "visible from the bank, which only ever says KAUFHALLE NORD.",
        "where": "the grocer's order history, line by line",
        "evidence": "Every online order at Kaufhalle Nord has its items, and "
                    "each order reconciles to a statement row to the cent.",
        "verdict": "Analysis, not advice. Name the two figures and stop.",
        "measure": "sweets-vs-meat",
    },
    {
        "slug": "strom-runter",
        "title": "The electricity Abschlag fell after a contract change",
        "what": "118,00 a month through 2025, 94,00 from January 2026 after the "
                "tariff changed. The saving is already made; it belongs in "
                "*what changed*, not in *what to do*.",
        "where": "havelbank-joint",
        "evidence": "The mailbox holds Spreelicht's letter of 2025-12-09 "
                    "announcing the new Abschlag from January.",
        "verdict": "Nothing to act on. A round that only ever reports losses "
                   "is a round the person stops opening.",
        "measure": "strom-runter",
    },
]


# ------------------------------------------------------------- dated events
#
# A year of a family's money is not a flat rate. These are the lumps: a summer
# on the Baltic, Christmas, a spring trip, the washing machine that broke, the
# glasses. They are what makes a month report have something to say about the
# month, and what stops every account simply filling up with an unspent surplus.

@dataclass(frozen=True)
class Event:
    when: str
    account: str
    counterparty: str
    purpose: str
    booking: str
    amount: float
    category: str
    merchant: str
    rail: str | None = None
    slug: str = ""
    goods: str = ""
    ref: str = ""
    """A fixed rail reference, where several rows are one purchase — the three
    instalments on the washing machine share one Vorgang number, because that is
    what the BNPL bank's own purchase list shows."""


EVENTS = [
    # --- summer 2025: two weeks on Usedom ---------------------------------
    Event("2025-07-12", "havelbank-joint", "FERIENHAUS SEEBLICK USEDOM",
          "BUCHUNG 2025-8841 ANZAHLUNG", "UEBERWEISUNG",
          -620.00, "Holidays", "Ferienhaus Seeblick", slug="sommer-2025"),
    Event("2025-08-01", "havelbank-joint", "FERIENHAUS SEEBLICK USEDOM",
          "BUCHUNG 2025-8841 RESTZAHLUNG", "UEBERWEISUNG",
          -620.00, "Holidays", "Ferienhaus Seeblick", slug="sommer-2025"),
    Event("2025-08-02", "meridian-everyday", "RAILLINK DE",
          "RAILLINK DE//BERLIN/DE FAMILIENTICKET", "KARTENZAHLUNG",
          -248.60, "Transport", "RailLink DE", slug="sommer-2025"),
    Event("2025-08-04", "havelbank-joint", "STRANDKORBVERMIETUNG DUENE",
          "STRANDKORB WOCHE 32", "KARTENZAHLUNG",
          -84.00, "Holidays", "Strandkorbvermietung Duene", slug="sommer-2025"),
    Event("2025-08-07", "meridian-everyday", "FISCHRAEUCHEREI HAFFBLICK",
          "FISCHRAEUCHEREI HAFFBLICK//USEDOM/DE", "KARTENZAHLUNG",
          -46.80, "Food and drink", "Fischraeucherei Haffblick", slug="sommer-2025"),
    Event("2025-08-09", "nordufer-sam", "BERNSTEINMUSEUM USEDOM",
          "EINTRITT FAMILIE", "KARTENZAHLUNG",
          -28.00, "Holidays", "Bernsteinmuseum Usedom", slug="sommer-2025"),
    Event("2025-08-16", "meridian-everyday", "RAILLINK DE",
          "RAILLINK DE//BERLIN/DE FAMILIENTICKET RUECK", "KARTENZAHLUNG",
          -248.60, "Transport", "RailLink DE", slug="sommer-2025"),

    # --- a bike, a school trip, the autumn ---------------------------------
    Event("2025-09-04", "havelbank-joint", "KITA SONNENBLUME E.V.",
          "AUSFLUG WALDTAG MIRA", "LASTSCHRIFT",
          -45.00, "Children", "Kita Sonnenblume"),
    Event("2025-09-12", "meridian-everyday", "RADWERK KREUZBERG",
          "RADWERK KREUZBERG//BERLIN/DE", "KARTENZAHLUNG",
          -420.00, "Transport", "Radwerk Kreuzberg", slug="fahrrad"),
    Event("2025-10-21", "nordufer-sam", "ZAHNARZTPRAXIS AM MARKT",
          "RECHNUNG 2025-4412", "UEBERWEISUNG",
          -186.00, "Health", "Zahnarztpraxis am Markt"),

    # --- Christmas 2025: gifts, mostly bought through rails ----------------
    Event("2025-12-06", "meridian-everyday", None, None, "LASTSCHRIFT",
          -148.90, "Children", "Spielwerk Spielzeug",
          rail="pagolink", goods="Holzeisenbahn-Set", slug="weihnachten-2025"),
    Event("2025-12-09", "havelbank-joint", None, None, "LASTSCHRIFT",
          -212.40, "Clothing", "Stoffkreis",
          rail="ratenwerk", goods="Winterjacken x2", slug="weihnachten-2025"),
    Event("2025-12-11", "nordufer-sam", None, None, "LASTSCHRIFT",
          -87.60, "Home and things", "Buchhandlung Silbenfisch",
          rail="warenlager", goods="Buecher, vier Titel", slug="weihnachten-2025"),
    Event("2025-12-14", "meridian-everyday", None, None, "LASTSCHRIFT",
          -64.00, "Home and things", "Fotolabor Silberkorn",
          rail="kassenband", goods="Fotobuch gross", slug="weihnachten-2025"),
    Event("2025-12-20", "havelbank-joint", "KAUFHALLE NORD 4471 BERLIN",
          "KAUFHALLE NORD 4471 BERLIN//BERLIN/DE 20.12.2025 17.42 UHR KARTE 1",
          "KARTENZAHLUNG",
          -164.20, "Food and drink", "Kaufhalle Nord", slug="weihnachten-2025"),
    Event("2025-12-23", "havelbank-joint", "GASTHAUS ALTE WAND",
          "GASTHAUS ALTE WAND//BERLIN/DE", "KARTENZAHLUNG",
          -96.50, "Going out", "Gasthaus Alte Wand", slug="weihnachten-2025"),

    # --- the washing machine, bought on instalments -------------------------
    # Three equal payments through the BNPL bank, and the bank row says only
    # `Ratenwerk` and a Vorgang number. Nothing in the statement says what was
    # bought or where; the BNPL bank's own purchase list does.
    Event("2026-04-11", "havelbank-joint", None, None, "LASTSCHRIFT",
          -163.00, "Home and things", "Elektro Hausgeraete Nordlicht",
          rail="ratenwerk", goods="Waschmaschine 8kg (Rate 1 von 3)",
          slug="waschmaschine", ref="40117"),
    Event("2026-05-11", "havelbank-joint", None, None, "LASTSCHRIFT",
          -163.00, "Home and things", "Elektro Hausgeraete Nordlicht",
          rail="ratenwerk", goods="Waschmaschine 8kg (Rate 2 von 3)",
          slug="waschmaschine", ref="40117"),
    Event("2026-06-11", "havelbank-joint", None, None, "LASTSCHRIFT",
          -163.00, "Home and things", "Elektro Hausgeraete Nordlicht",
          rail="ratenwerk", goods="Waschmaschine 8kg (Rate 3 von 3)",
          slug="waschmaschine", ref="40117"),

    # --- spring 2026 ---------------------------------------------------------
    Event("2026-02-17", "meridian-everyday", "ZAHNARZTPRAXIS AM MARKT",
          "RECHNUNG 2026-0221", "UEBERWEISUNG",
          -280.00, "Health", "Zahnarztpraxis am Markt"),
    Event("2026-04-02", "havelbank-joint", "RAILLINK DE",
          "RAILLINK DE//BERLIN/DE OSTERREISE AMSTERDAM", "KARTENZAHLUNG",
          -312.00, "Transport", "RailLink DE", slug="ostern-2026"),
    Event("2026-04-03", "havelbank-joint", None, None, "LASTSCHRIFT",
          -498.00, "Holidays", "Hotel Grachtenblick",
          rail="nordpfad", goods="Drei Naechte, Familienzimmer",
          slug="ostern-2026"),
    Event("2026-04-05", "meridian-everyday", "RIJKSMUSEUMSHOP AMSTERDAM",
          "RIJKS MUSEUMSHOP//AMSTERDAM/NL", "KARTENZAHLUNG",
          -38.40, "Holidays", "Museumsshop Amsterdam", slug="ostern-2026"),
    Event("2026-05-20", "nordufer-sam", "OPTIKER KLARSICHT",
          "OPTIKER KLARSICHT//BERLIN/DE", "KARTENZAHLUNG",
          -295.00, "Health", "Optiker Klarsicht", slug="brille"),
    Event("2026-06-13", "havelbank-joint", "SCHWIMMSCHULE DELPHIN",
          "KURSGEBUEHR SOMMER MIRA C-O", "LASTSCHRIFT",
          -88.00, "Children", "Schwimmschule Delphin"),
]


# --------------------------------------------- what a till receipt actually says
#
# The stall and cafe rows whose terminal prints only a merchant code are the ones
# a photographed slip has to explain, so their amounts are **built from a basket**
# rather than sampled and then reverse-engineered into one.
#
# The first version did it the other way round — sample the amount, then pad the
# last item with whatever was left over — and produced a 22,61 EUR bottle of
# rapeseed oil and a 55-cent Milchkaffee. Every total was right and every receipt
# was absurd, which is worse than a wrong total: a person reads the slip, and an
# agent asked to break one down would write the nonsense down as a line item.
#
# `weighed` is what makes an exact odd total honest: a market stall really does
# sell apples by the kilo, so a line priced at 3,84 is what a scale produces.
# Its two numbers are a PRICE PER KILO, and the line's amount is the weight
# times that — the first version drew the weight and the price independently and
# printed a dish of the day at "1,059 kg". A cafe has no weighed goods at all
# and so has none here; its totals are plain sums of menu prices, which is what
# a cafe bill is.

RECEIPT_BASKETS = {
    "Café Zeitlupe": {
        "fixed": [("Milchkaffee", 3.60), ("Cappuccino", 3.20),
                  ("Filterkaffee", 2.80), ("Apfelkuchen", 3.90),
                  ("Käsekuchen", 4.20), ("Belegtes Brot", 5.40),
                  ("Mineralwasser 0,3l", 2.60), ("Tagesgericht", 8.90)],
        "weighed": [],
        "open": (9, 17),
    },
    "Marktstand Grünwinkel": {
        "fixed": [("Feldsalat 150g", 2.80), ("Eier 10er", 4.20),
                  ("Ziegenkäse 200g", 6.80), ("Honig 500g", 7.50),
                  ("Möhren Bund", 2.20)],
        "weighed": [("Äpfel", 2.80, 4.40), ("Kartoffeln", 1.60, 2.40),
                    ("Tomaten", 3.60, 6.80)],           # EUR per kilo
        "open": (9, 13),
    },
    "Hofladen Havelgrün": {
        "fixed": [("Rohmilch 1l", 2.30), ("Bauernbrot 1kg", 4.80),
                  ("Rapsöl 500ml", 7.90), ("Marmelade 340g", 4.60)],
        "weighed": [("Hofkäse", 22.00, 32.00), ("Kirschen", 7.40, 11.80)],
        "open": (10, 16),
    },
    "Bar Nachtkarte": {
        "fixed": [("Bier 0,5l", 4.50), ("Weinschorle", 5.20),
                  ("Limonade", 3.80), ("Nuesse", 2.40), ("Aperitif", 7.50)],
        "weighed": [],
        "open": (18, 23),
    },
}
