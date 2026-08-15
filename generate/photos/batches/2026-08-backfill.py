"""Backfill batch: thin years, travel history, and a 2026 that has a life in it.

Three problems this fixes, none of them "the dataset is out of date":

1. **3–7 photos a year does not render a life.** The Life Book, the Places map
   and Groups all need density; the hero slice deliberately went wide and thin.
2. **2026 was 26 photos of which 20 were receipts** — so the era the apps
   pre-select as most recent had six actual life photos in it.
3. **Trips existed only as receipts.** June's fixtures assert Helsinki,
   Stockholm, Madrid, Leipzig and Amsterdam; the photo library had essentially
   no evidence of any of them, so the Places map showed cities Alex apparently
   visited without taking a picture. These entries corroborate the receipts —
   same days, same cities.

(date, city-key, cast joined by +, scene, sequence-suffix)
"""

SPEC = [
    # ---------------- 2014 — Manchester, university tail + first agency job
    ("2014-02-15", "manchester", "alex+jonas", "two friends in winter coats on a canal towpath in Manchester, red brick mills behind, grey afternoon light", "01"),
    ("2014-05-04", "peak", "alex+jonas", "two climbers coiling a rope at the base of a gritstone edge, moorland behind, spring light", "01"),
    ("2014-09-21", "manchester", "alex", "a cluttered student desk with a laptop, sketchbook and cold tea, evening lamp light", "01"),
    ("2014-11-08", "manchester", "alex+rosa", "a mother and her adult child at a kitchen table with mugs, terraced house interior, warm lamp light", "01"),
    ("2014-12-24", "manchester", "alex+rosa", "a small decorated Christmas tree in a narrow front room, tinsel and a gas fire, evening", "01"),

    # ---------------- 2015 — agency work, climbing
    ("2015-03-14", "peak", "alex+jonas", "a climber halfway up a gritstone crack, belayer looking up from below, overcast", "01"),
    ("2015-04-26", "manchester", "alex", "a young designer at a shared agency desk with two monitors and printed layouts pinned above", "01"),
    ("2015-06-13", "manchester", "alex+jonas", "friends outside a red brick pub with pints on a wooden bench, summer evening", "01"),
    ("2015-08-30", "peak", "alex", "a lone walker on a moorland path at golden hour, heather and gritstone boulders", "01"),
    ("2015-10-17", "manchester", "alex+rosa", "an older woman and her adult child walking through a park in autumn, leaves underfoot", "01"),
    ("2015-12-05", "manchester", "alex", "a rain-streaked bus window looking out at Manchester city lights at night", "01"),

    # ---------------- 2016 — the move to Berlin (era changes mid-year)
    ("2016-02-20", "manchester", "alex+jonas", "two friends at a climbing wall indoors, chalk dust and bright holds, evening session", "01"),
    ("2016-05-08", "manchester", "alex+rosa", "a farewell dinner at a small kitchen table, plates cleared, warm light", "01"),
    ("2016-07-16", "berlin", "alex", "a young man surrounded by unopened cardboard boxes in an empty Berlin flat, bare bulb, afternoon sun", "01"),
    ("2016-08-27", "berlin", "alex", "cycling along a canal in Kreuzberg, plane trees and graffiti walls, summer", "01"),
    ("2016-10-09", "berlin-mitte", "alex", "a first day at a co-working desk, laptop and a new notebook, tall windows", "01"),
    ("2016-12-18", "berlin", "alex", "a Christmas market stall with mulled wine cups, string lights, cold night", "01"),

    # ---------------- 2017 — Sam appears mid-year
    ("2017-03-11", "berlin", "alex", "a flat white and a laptop on a marble cafe table, Berlin cafe interior, morning", "01"),
    ("2017-05-20", "berlin-park", "alex", "kite flyers and cyclists on a vast open former airfield, big sky, spring", "01"),
    ("2017-07-08", "berlin", "alex+sam", "two people laughing over shared plates at a busy outdoor restaurant table, summer evening", "01"),
    ("2017-08-19", "hamburg", "alex+sam", "a couple on a harbour promenade with cranes and water behind, bright windy day", "01"),
    ("2017-10-01", "berlin", "alex+sam", "a couple cooking together in a small kitchen, steam and open cookbook, evening", "01"),
    ("2017-11-25", "berlin", "alex+sam", "two people under an umbrella on a wet Berlin street at night, shop lights reflected", "01"),

    # ---------------- 2018 — settled in Berlin, first conference trip
    ("2018-01-13", "berlin", "alex+sam", "a couple walking a snowy park path, bare trees, low winter sun", "01"),
    ("2018-04-07", "amsterdam", "alex", "a designer with a lanyard outside a conference venue, canal and bicycles behind, spring", "01"),
    ("2018-04-08", "amsterdam", "alex", "a packed conference hall from the back row, slide glow on faces", "01"),
    ("2018-06-16", "berlin", "alex+sam+jonas", "three friends around a picnic blanket in a park, bottles and bread, summer afternoon", "01"),
    ("2018-08-04", "bavaria", "alex+jonas", "two hikers on an alpine ridge with limestone peaks behind, clear summer day", "01"),
    ("2018-09-22", "berlin", "alex+sam", "a couple painting a room together, roller and dust sheets, afternoon light", "01"),
    ("2018-12-31", "berlin", "alex+sam", "fireworks over a Berlin rooftop, silhouetted figures on a balcony, night", "01"),

    # ---------------- 2019 — Mira arrives
    ("2019-05-02", "berlin", "alex+sam", "an expectant couple in a bright flat, hand on bump, soft morning light", "01"),
    ("2019-09-14", "berlin", "alex+mira", "a new parent holding a newborn by a window, exhausted and delighted, soft daylight", "01"),
    ("2019-10-27", "berlin", "sam+mira", "a parent asleep on a sofa with a baby on their chest, blanket, afternoon light", "01"),
    ("2019-12-20", "berlin", "alex+sam+mira", "a family of three by a small Christmas tree, baby in arms, warm lamps", "01"),

    # ---------------- 2020 — the year at home
    ("2020-02-08", "berlin", "alex+mira", "a parent pushing a pram along a canal path in winter, bare trees", "01"),
    ("2020-03-29", "berlin", "alex", "a improvised home desk at the end of a dining table, video call on screen, daylight", "01"),
    ("2020-04-18", "berlin", "alex+sam+mira", "a family in a small courtyard garden, baby on a rug, spring sun", "01"),
    ("2020-05-30", "berlin", "mira", "a baby pulling herself up on a low bookshelf, blurred living room behind", "01"),
    ("2020-07-11", "berlin-park", "alex+mira", "a toddler taking first steps on a wide grassy field, parent crouched ahead", "01"),
    ("2020-09-05", "berlin", "alex+sam", "two people eating takeaway on a sofa surrounded by toys, evening lamp light", "01"),
    ("2020-10-24", "berlin", "alex+mira", "a toddler in a puddle in wellies, autumn leaves, laughing", "01"),
    ("2020-12-12", "berlin", "sam+mira", "a parent and toddler decorating a small tree together, warm indoor light", "01"),

    # ---------------- 2021 — family era, first trips again
    ("2021-02-27", "berlin", "alex+mira", "a toddler and parent building a snowman in a courtyard, thick winter coats", "01"),
    ("2021-04-10", "berlin", "alex", "a home office corner at night, two monitors, city window behind", "01"),
    ("2021-06-19", "berlin-park", "alex+sam+mira", "a family picnic on a huge open field, bikes laid on the grass, summer", "01"),
    ("2021-07-24", "bavaria", "alex+sam+mira", "a family by an alpine lake with a toddler at the water edge, mountains behind", "01"),
    ("2021-09-11", "berlin", "mira", "a small child in a nursery doorway with a rucksack almost as big as her", "01"),
    ("2021-10-30", "berlin", "alex+jonas", "two friends at an indoor climbing gym, chalk and bright holds, evening", "01"),
    ("2021-12-05", "berlin", "alex+sam+mira", "a family at a Christmas market, child on shoulders, string lights, cold night", "01"),

    # ---------------- 2022 — going solo, Carter Studio
    ("2022-03-08", "berlin", "alex", "a person signing paperwork at a cafe table with a laptop, morning light", "01"),
    ("2022-04-21", "berlin", "alex+priya", "two professionals in a design review over printed boards, studio wall behind", "01"),
    ("2022-06-30", "lisbon", "alex", "a designer on a tiled Lisbon terrace with a laptop, pastel buildings and river behind", "01"),
    ("2022-07-01", "lisbon", "alex", "a steep Lisbon street with a yellow tram, bright summer light", "01"),
    ("2022-09-17", "berlin", "alex+sam+mira", "a family cycling together on a quiet Berlin street, child seat, autumn", "01"),
    ("2022-11-19", "berlin", "alex", "a co-working studio at dusk, empty desks, one lamp still on", "01"),

    # ---------------- 2023 — the studio finds its feet
    ("2023-01-28", "berlin", "alex+jonas", "two friends bouldering, one spotting the other, gym chalk haze", "01"),
    ("2023-03-25", "amsterdam", "alex+priya", "two colleagues walking beside an Amsterdam canal with coffee, spring morning", "01"),
    ("2023-05-13", "berlin", "alex+mira", "a parent and small child painting at a kitchen table covered in newspaper", "01"),
    ("2023-06-24", "copenhagen", "alex+sam+mira", "a family on a harbour swimming platform, colourful townhouses behind, summer", "01"),
    ("2023-08-12", "berlin-park", "alex+sam", "a couple watching a sunset over a wide open field, bikes beside them", "01"),
    ("2023-10-07", "berlin", "alex+priya", "a client workshop with sticky notes across a glass wall, people mid-discussion", "01"),
    ("2023-12-16", "manchester", "alex+sam+mira+rosa", "three generations at a crowded Christmas table in a small terraced house", "01"),

    # ---------------- 2024 — established studio, climbing returns
    ("2024-02-17", "berlin", "alex", "a designer at a standing desk in a bright studio, plants and pinned work", "01"),
    ("2024-04-06", "dolomites", "alex+jonas", "two climbers on a via ferrata with dramatic limestone towers behind, clear day", "01"),
    ("2024-04-07", "dolomites", "alex+jonas", "a mountain hut terrace with boots and rucksacks, peaks in cloud behind", "01"),
    ("2024-05-25", "berlin", "alex+mira", "a parent teaching a child to ride a bike without stabilisers, park path", "01"),
    ("2024-07-13", "porto", "alex+sam+mira", "a family on a riverside walkway with port barges and a tall bridge behind", "01"),
    ("2024-09-14", "berlin", "alex+priya", "two people presenting to a room, projected slide glow, evening event", "01"),
    ("2024-10-26", "peak", "alex+jonas", "two climbers back at a gritstone edge after years, autumn moorland light", "01"),
    ("2024-12-08", "berlin", "alex+sam+mira", "a family baking together, flour everywhere, kitchen warm light", "01"),

    # ---------------- 2025 — the balance era begins
    ("2025-02-22", "berlin", "alex+sam", "a couple at a small neighbourhood restaurant, candle on the table, winter evening", "01"),
    ("2025-04-19", "berlin", "alex+jonas", "two friends at a climbing gym competition, crowd and bright holds", "01"),
    ("2025-08-09", "bavaria", "alex+sam+mira", "a family on an alpine trail, child leading, wildflowers and peaks", "01"),
    ("2025-11-15", "berlin", "alex+mira", "a parent and child at a kitchen table doing homework together, lamp light", "01"),

    # ---------------- 2026 — the current era needs a life, not just receipts.
    # June corroborates the receipts: Helsinki 3rd, Stockholm 5th, Madrid 15th,
    # Leipzig 7th (the club trip), Amsterdam 21st.
    ("2026-01-17", "berlin", "alex+sam+mira", "a family walking through fresh snow in a Berlin park, bright winter morning", "01"),
    ("2026-02-28", "berlin", "alex+priya", "two people in a studio reviewing a rebrand on a large screen, focused", "01"),
    ("2026-04-11", "berlin", "alex+jonas", "two friends leaving a climbing gym at night with rope bags, city street", "01"),
    ("2026-05-16", "berlin-park", "alex+sam+mira", "a family flying a kite on a vast open field, big spring sky", "01"),
    ("2026-06-03", "helsinki", "alex", "a designer with a coffee outside a Helsinki kiosk, pale northern light, granite buildings", "01"),
    ("2026-06-03", "helsinki", "alex+priya", "two colleagues walking a Helsinki waterfront in bright June light, ferries behind", "02"),
    ("2026-06-05", "stockholm", "alex", "a workshop room in Stockholm with sticky notes on glass, participants mid-discussion", "01"),
    ("2026-06-05", "stockholm", "alex", "a narrow Södermalm street with pastel facades in low evening sun", "02"),
    ("2026-06-07", "leipzig", "alex+jonas", "a youth climbing competition in a sports hall, teenagers on a bright wall, parents watching", "01"),
    ("2026-06-15", "madrid", "alex", "a sunlit Madrid plaza with a cortado on an outdoor cafe table, awnings and terracotta", "01"),
    ("2026-06-21", "amsterdam", "alex+priya", "two colleagues at an Amsterdam canal-side table with laptops closed, late afternoon", "01"),
    ("2026-06-27", "berlin", "alex+sam+mira", "a family at a long table in a courtyard with neighbours, summer evening, strung lights", "01"),
]
