# Character appearance bible

Physical descriptions used to prompt the cast-sheet generator (`gen_cast.py`)
and, later, every scene generation that includes these characters. Keeping
the description here (not just implicit in a prompt string) means any future
script — scene generation, a second identity, a regen after a look tweak —
can quote the same source of truth instead of re-inventing the character.

Fictional throughout; no resemblance to real people intended or claimed.
Alex is written gender-neutral in features (PERSONA.md: "they/them in all
copy — keeps assets universally relatable").

## Alex Carter

Androgynous features, light-olive skin tone, short textured dark-brown hair
(side part, low maintenance), warm brown eyes, slim-average build, calm
friendly expression, minimal jewelry (a thin silver band). Wardrobe leans
smart-casual designer: crew-neck knitwear, simple structured jackets, muted
neutral tones (charcoal, oatmeal, forest green) — a product designer's
restrained palette, not corporate.

Era styling (kontext prompt deltas from the canonical reference):
- **age-26 (Manchester, 2014–2016):** slightly longer/messier hair, plain
  hoodie or graphic tee, fresh-faced student energy.
- **age-29 (Berlin move, 2016–2018):** shorter neater hair, plain crewneck,
  new-city minimalism, slightly more polished than the student look.
- **age-32 (Mira arrives, 2019–2021):** practical low-effort hairstyle, soft
  cardigan, a touch of new-parent tiredness around the eyes.
- **age-35 (Carter Studio, 2022–2024):** confident, close-cropped modern cut,
  structured blazer-casual, professional but not stiff.
- **age-38 (Balance era, 2025–2026 — closest to canonical):** relaxed but
  polished, faint gray fleck at the temples, mix of professional and
  outdoors/climbing texture (light weatherproof jacket).

## Sam Okafor

Warm dark-brown skin tone, natural black hair worn in short locs, round
tortoiseshell glasses, kind expressive eyes, average-tall build, easy warm
smile — reads as approachable secondary-school teacher. Wardrobe: soft
knitwear, corduroy, muted earth tones; comfortable over fashionable.

Era styling:
- **age-29 (2017, first appears in Berlin):** younger, simpler short natural
  hair (pre-locs), plain round glasses, casual teacher-in-training look.
- **age-32 (2020, Mira arrives):** locs just started growing in, tired-happy
  new-parent look, same glasses.
- **age-35 (2023, Carter Studio era):** established locs, smart-casual
  cardigan, confident classroom-ready look.
- **age-38 (2026, Balance era — canonical):** mature, subtle gray at the
  temples, same glasses and locs, warm settled expression.

## Mira Carter-Okafor (b. 2019)

Light-brown skin tone, dark curly hair, bright dark eyes, features blending
both parents — warm expressive face, easy smile. Generated chained
newest→oldest (age-7 as the base reference, then kontext de-aging backward)
since a school-age face carries more identity signal than a newborn's.

Age progression:
- **age-7 (2026, Balance era — base/canonical):** dark curly hair in twin
  puffs or braids, gap where a baby tooth is missing, confident school-age
  proportions and posture.
- **age-4 (2023, Carter Studio era):** shoulder-length curls often in twin
  puffs, playful preschooler expression, rounder toddler-to-child face.
- **age-2 (2021, Mira-arrives era):** chubby-cheeked toddler, small dark
  curl puffs, curious wide-eyed expression.
- **age-0 (2019, newborn):** swaddled infant, wisps of dark curly hair, soft
  sleepy newborn-portrait expression — minimal identity signal by nature,
  kept consistent mainly via skin tone and hair texture.

## Jonas Weber

Tanned, sun-weathered skin from outdoor climbing, short practical
dark-blonde hair, athletic wiry build, easygoing warm expression, light
stubble. Wardrobe: technical outdoor gear (softshell jackets, climbing
harness in relevant scenes).

Era variants (`age-38.png` is the anchor; younger ages kontext back from it):
- **age-26 (Manchester, 2014–2016):** youthful un-weathered skin, slightly
  longer tousled hair, clean-shaven/very light stubble, plain tee.
- **age-35 (Carter Studio, 2022–2024 — the Frankenjura return):** lightly
  sun-weathered, short hair, light stubble.
- **age-38 (Balance, 2025–2026):** the anchor look, most weathered.

## Priya Sharma (pilot-minimal — single look only)

Deep-brown skin tone, sleek dark hair in a low bun, sharp confident
professional expression, tailored business-casual wardrobe (blazers,
neutral tones), small gold stud earrings — reads as a senior agency client.

Generated at a single "balance"-era look (`age-36.png`) only — just enough
for the pilot manifest's one Priya entry (client lunch, 2026-06). Priya only
appears 2022–2026 (Carter Studio era onward), so a shorter age progression
(two variants, not five) will suffice when generated properly post-pilot.

## Rosa Carter (Alex's mother, Manchester)

A woman in her mid-fifties, fair British complexion with gentle laugh-lines,
softly waved silver-grey shoulder-length hair, warm hazel eyes, kind
approachable expression. Wardrobe: soft cardigans and blouses in muted
heathers and navy; reading glasses often pushed up into her hair.

Era variants (`age-55.png` is the anchor — her most-featured years, the
2019–2021 grandmother visits; age-50 kontexts back for the Manchester era):
- **age-50 (Manchester, 2014–2016):** hair more salt-and-pepper than silver
  and slightly fuller, fewer lines, warm energetic expression, navy cardigan.
- **age-55 (Mira arrives, 2019–2021):** the anchor look, silver waves.
