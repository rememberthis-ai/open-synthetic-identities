"""July and early-August 2026 — the months the app can actually navigate to.

Requested by the Clerk app-testing session (`docs/ongoing/
SYNTHETIC-PHOTOS-REQUEST-2026-08-15.md` in the monorepo). The reason is a
product constraint, not plausibility: the app can only reach a period that
already has a close, or the most recent ENDED period. That is July. June is
reachable by no control a person has, so **testing on June routes around the
product and testing on July tests it.**

Ordinary life photos, not receipts — the receipts are separate composite
entries. This half is the haystack: discovery's job is finding receipts among
photos that are not receipts, and a library where most images carry text makes
that trivially easy in a way the real world is not.

**No July close ships with this.** A user would already have photos of their
receipts; the close is what Clerk *produces*. Seeding a finished July run would
make any test a picture of something no code made.

(date, city-key, cast joined by +, scene, sequence-suffix)
"""

SPEC = [
    # --- July: high summer in Berlin, the studio ticking over ---
    ("2026-07-02", "berlin", "alex", "a designer at a cafe window seat with a laptop and a flat white, bright summer morning", "01"),
    ("2026-07-05", "berlin-park", "alex+sam+mira", "a family on a picnic blanket on a vast open field, bikes laid on the grass, hot afternoon", "01"),
    ("2026-07-09", "berlin", "alex", "a co-working studio desk with a new notebook and a pack of highlighters still wrapped, flat afternoon light", "01"),
    ("2026-07-13", "berlin", "alex+priya", "two colleagues over a long working lunch, plates pushed aside and a laptop open between them", "01"),
    ("2026-07-15", "hamburg", "alex", "a harbour promenade with cranes and container ships behind, bright windy day", "01"),
    ("2026-07-18", "berlin", "alex+jonas", "two friends at an outdoor climbing wall in a city park, chalk bag and rope, evening sun", "01"),
    ("2026-07-22", "berlin", "alex+priya", "a small meeting room with printed layouts spread across the table, mid-discussion", "01"),
    ("2026-07-26", "berlin", "alex+sam+mira", "a family eating ice cream on a kerb outside a corner shop, hot summer evening", "01"),
    ("2026-07-30", "berlin", "alex+sam", "a couple on a balcony with plants and a bottle of wine, city rooftops, dusk", "01"),

    # --- August: the quiet month, and the trip that RailLink pays for ---
    ("2026-08-02", "berlin-park", "alex+mira", "a parent and child cycling side by side on a wide empty path, early morning", "01"),
    ("2026-08-05", "berlin", "alex", "a bakery counter with a paper bag and a coffee, warm morning light through the window", "01"),
    ("2026-08-08", "berlin", "alex+jonas", "two friends at an indoor climbing gym in summer, fans running, chalk haze", "01"),
    ("2026-08-12", "amsterdam", "alex+priya", "two colleagues walking a canal-side street with bags, arriving for a client visit, morning", "01"),
    ("2026-08-13", "amsterdam", "alex", "a hotel desk with a laptop and notes, canal visible through the window, evening", "01"),
]
