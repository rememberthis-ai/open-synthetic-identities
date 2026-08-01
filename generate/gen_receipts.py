#!/usr/bin/env python3
"""Render synthetic thermal-paper-style receipt images for demo identities.

All merchants and transactions are fictional. Deterministic under --seed.

Usage:
  python3 gen_receipts.py --identity alex-carter --month 2026-06 --seed 42 \
      --out ../fixtures/clerkai/receipts
"""
import argparse
import random
from datetime import datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- persona data

MERCHANTS = {
    "alex-carter": [
        # (name, city line, language, VAT rate, items: (label, min€, max€))
        ("Brew & Bean", "Torstr. 71, 10119 Berlin", "en", 0.19,
         [("Flat white", 3.8, 4.6), ("Cappuccino", 3.4, 4.2), ("Croissant", 2.4, 3.2),
          ("Lunch special", 9.5, 14.5), ("Sparkling water", 2.8, 3.4)]),
        ("Bürobedarf Kern", "Kantstr. 24, 10623 Berlin", "de", 0.19,
         [("Notizbuch A5", 6.9, 12.9), ("Fineliner 0.4 (4er)", 8.5, 11.9),
          ("Druckerpapier A4 500Bl", 5.9, 7.9), ("Versandtaschen C4", 4.5, 6.9)]),
        ("Nimbus Cloud Hosting", "online — nimbus.example", "en", 0.19,
         [("Compute S plan (monthly)", 24.0, 24.0), ("Object storage 250GB", 6.0, 6.0),
          ("Managed DB starter", 15.0, 15.0)]),
        ("Fontrack Pro", "online — fontrack.example", "en", 0.19,
         [("Pro seat (monthly)", 18.0, 18.0)]),
        ("RailLink", "Hauptbahnhof, Berlin", "en", 0.07,
         [("Berlin–Amsterdam return", 118.0, 176.0), ("Seat reservation", 5.9, 5.9),
          ("Berlin–Hamburg return", 74.0, 102.0)]),
        ("Werkraum Kollektiv", "Ritterstr. 12, 10969 Berlin", "en", 0.19,
         [("Flex desk (monthly)", 240.0, 240.0), ("Meeting room 2h", 30.0, 30.0)]),
        ("K-Kulma Kioski", "Fleminginkatu 7, Helsinki", "fi", 0.14,
         [("Kahvi iso", 3.2, 3.9), ("Korvapuusti", 3.5, 4.2), ("Vesipullo 0,5l", 2.2, 2.8)]),
        ("Kaffebaren Söder", "Hornsgatan 43, Stockholm", "sv", 0.12,
         [("Bryggkaffe", 3.4, 4.1), ("Kanelbulle", 3.8, 4.6), ("Macka ost", 6.5, 8.2)]),
        ("Bäckerei Sonnenschein", "Bergmannstr. 5, Berlin", "de", 0.07,
         [("Roggenbrot", 4.2, 5.4), ("Brezel", 1.4, 1.8), ("Apfeltasche", 2.6, 3.2)]),
        ("Café del Sol", "Calle Mayor 18, Madrid", "es", 0.10,
         [("Café con leche", 2.2, 2.9), ("Tostada con tomate", 3.5, 4.5),
          ("Zumo de naranja", 3.8, 4.4)]),
        # --- Kletterfreunde Kreuzberg e.V. (Alex's second set of books) ---
        # The club buys from different shops than the studio does, which is
        # half of why the allocation demo works: a reader can tell the two
        # sets of books apart from the vendor alone.
        ("Vertikal Sport Berlin", "Skalitzer Str. 104, 10997 Berlin", "de", 0.19,
         [("Seil 60m", 189.00, 189.00), ("Karabiner-Set 12er", 128.90, 128.90),
          ("Expressen 8er", 118.00, 118.00), ("Sicherungsgerät", 64.90, 64.90)]),
        ("Gasthaus Alte Wand", "Wiener Str. 18, 10999 Berlin", "de", 0.19,
         [("Buffet 18 Pers.", 198.00, 198.00), ("Getränke", 16.60, 16.60)]),
        # --- Vendors that appear in June's ledger and are PHOTOGRAPHED ---
        ("Supermercado Listo", "Skalitzer Str. 60, 10997 Berlin", "de", 0.07,
         [("Tomaten 1kg", 3.49, 3.49), ("Serrano 200g", 7.99, 7.99),
          ("Manchego 250g", 8.95, 8.95), ("Oliven 400g", 4.29, 4.29),
          ("Chorizo 300g", 6.49, 6.49), ("Paprika 500g", 2.99, 2.99),
          ("Rotwein Rioja", 7.00, 7.00), ("Baguette", 1.80, 1.80),
          ("Brot", 1.39, 1.39)]),
        # --- DECOYS: real documents that OCR flags and a person rejects ---
        # The photo-review grid's claim is "I cast a wide net on purpose — drop
        # the ones that aren't". Twenty genuine business receipts would leave
        # nothing to drop and the sentence would refute itself, so the dataset
        # has to carry plausible false positives too.
        ("Kaufhalle Nord", "Skalitzer Str. 12, 10999 Berlin", "de", 0.07,
         [("Windeln Gr.4 44St", 12.99, 12.99), ("Waschmittel 2.5l", 8.49, 8.49),
          ("Milch 1l", 1.29, 1.29), ("Bananen 1kg", 2.19, 2.19),
          ("Weißwein trocken", 6.99, 6.99), ("Katzenfutter 12er", 5.49, 5.49)]),
        ("Apotheke am Kottbusser Tor", "Adalbertstr. 4, 10999 Berlin", "de", 0.19,
         [("Ibuprofen 400 20St", 5.95, 5.95), ("Nasenspray", 4.45, 4.45),
          ("Vitamin D3 Tropfen", 9.90, 9.90), ("Pflaster wasserfest", 3.20, 3.20)]),
    ]
}

I18N = {
    "en": {"receipt": "RECEIPT", "vat": "VAT", "total": "TOTAL", "card": "CARD ****",
           "thanks": "Thank you for your visit!", "net": "Net"},
    "de": {"receipt": "KASSENBON", "vat": "MwSt.", "total": "SUMME", "card": "KARTE ****",
           "thanks": "Vielen Dank für Ihren Einkauf!", "net": "Netto"},
    "fi": {"receipt": "KUITTI", "vat": "ALV", "total": "YHTEENSÄ", "card": "KORTTI ****",
           "thanks": "Kiitos käynnistä!", "net": "Netto"},
    "sv": {"receipt": "KVITTO", "vat": "Moms", "total": "TOTALT", "card": "KORT ****",
           "thanks": "Tack för ditt besök!", "net": "Netto"},
    "es": {"receipt": "RECIBO", "vat": "IVA", "total": "TOTAL", "card": "TARJETA ****",
           "thanks": "¡Gracias por su visita!", "net": "Neto"},
}

W = 576  # thermal 80mm at ~180dpi
MARGIN = 28
FONT_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Monaco.ttf",
    "/System/Library/Fonts/Courier.ttc",
]


def load_font(size):
    for p in FONT_CANDIDATES:
        try:
            return ImageFont.truetype(p, size)
        except OSError:
            continue
    return ImageFont.load_default()


def render_receipt(merchant, city, lang, vat_rate, items, when, rng, out_path):
    t = I18N[lang]
    f_big, f, f_small = load_font(30), load_font(22), load_font(18)
    lines = []  # (text, font, align) — build first, measure, then draw
    lines.append((merchant.upper(), f_big, "center"))
    lines.append((city, f_small, "center"))
    lines.append(("", f, "left"))
    lines.append((t["receipt"], f, "center"))
    lines.append((when.strftime("%d.%m.%Y  %H:%M"), f_small, "center"))
    lines.append(("-" * 38, f, "left"))
    total = 0.0
    for label, price in items:
        total += price
        price_s = f"{price:6.2f}"
        pad = 38 - len(label[:28]) - len(price_s)
        lines.append((f"{label[:28]}{' ' * max(1, pad)}{price_s}", f, "left"))
    lines.append(("-" * 38, f, "left"))
    net = total / (1 + vat_rate)
    vat = total - net
    lines.append((f"{t['net']:<28}{net:10.2f}", f_small, "left"))
    lines.append((f"{t['vat']} {int(vat_rate * 100)}%{'':<{24 - len(str(int(vat_rate * 100)))}}{vat:10.2f}", f_small, "left"))
    lines.append((f"{t['total']:<24}{total:10.2f} EUR", f, "left"))
    lines.append(("", f, "left"))
    lines.append((f"{t['card']}{rng.randint(1000, 9999)}", f_small, "left"))
    lines.append(("", f, "left"))
    lines.append((t["thanks"], f_small, "center"))

    line_h = 34
    h = MARGIN * 2 + line_h * len(lines) + 20
    img = Image.new("L", (W, h), 252)
    d = ImageDraw.Draw(img)
    y = MARGIN
    for text, font, align in lines:
        if text:
            if align == "center":
                w = d.textlength(text, font=font)
                d.text(((W - w) / 2, y), text, font=font, fill=20)
            else:
                d.text((MARGIN, y), text, font=font, fill=20)
        y += line_h
    # subtle paper noise for realism
    px = img.load()
    for _ in range(W * h // 60):
        x, yy = rng.randrange(W), rng.randrange(h)
        px[x, yy] = max(0, px[x, yy] - rng.randrange(18))
    img.convert("RGB").save(out_path, "PNG")
    return total


def render_from_spec(spec_path, out_dir, seed):
    """Render receipts whose totals are EXACTLY specified, not sampled.

    A period-close packet's ledger row and its receipt image must agree to the
    cent: the receipt is the document the accountant sees, so it — not the
    markdown — is the source of truth for the amount. Random sampling can't
    hit a chosen total, hence this mode. Spec is JSON:

      [{"merchant": "Fontrack Pro", "when": "2026-04-03T09:14",
        "items": [["Pro seat (monthly)", 18.00]]}, ...]

    `merchant` must exist in MERCHANTS (city/language/VAT come from there, so
    a spec can't invent an inconsistent merchant). Filenames follow the same
    `YYYYMMDD-slug.png` convention as the sampled mode.
    """
    import json

    spec = json.loads(Path(spec_path).read_text())
    by_name = {m[0]: m for m in MERCHANTS["alex-carter"]}
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = random.Random(seed)

    manifest = []
    for entry in spec:
        name = entry["merchant"]
        if name not in by_name:
            raise SystemExit(f"unknown merchant {name!r} — add it to MERCHANTS first")
        _, city, lang, vat_rate, _ = by_name[name]
        when = datetime.fromisoformat(entry["when"])
        items = [(label, float(price)) for label, price in entry["items"]]
        slug = name.lower().replace(" ", "-").replace("&", "and")
        fname = f"{when.strftime('%Y%m%d')}-{slug}.png"
        total = render_receipt(name, city, lang, vat_rate, items, when, rng, out / fname)
        expected = entry.get("total")
        if expected is not None and abs(total - float(expected)) > 0.005:
            raise SystemExit(
                f"{fname}: items sum to {total:.2f} but spec says {expected} — "
                "the receipt and the ledger row would disagree"
            )
        manifest.append(f"{fname}\t{name}\t{total:.2f} EUR\t{lang}")

    (out / "MANIFEST.tsv").write_text("\n".join(manifest) + "\n")
    print(f"wrote {len(spec)} receipts + MANIFEST.tsv to {out}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", default="alex-carter")
    ap.add_argument("--month", default="2026-06")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--count", type=int, default=14)
    ap.add_argument("--out", default="../fixtures/clerkai/receipts")
    ap.add_argument("--spec", help="JSON file of exact receipts (see render_from_spec)")
    args = ap.parse_args()

    if args.spec:
        render_from_spec(args.spec, args.out, args.seed)
        return

    rng = random.Random(args.seed)
    merchants = MERCHANTS[args.identity]
    year, month = map(int, args.month.split("-"))
    first = datetime(year, month, 1)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    manifest = []
    for i in range(args.count):
        name, city, lang, vat_rate, catalog = merchants[
            i % len(merchants) if i < len(merchants) else rng.randrange(len(merchants))
        ]
        n_items = rng.randint(1, min(3, len(catalog)))
        items = [(lbl, round(rng.uniform(lo, hi), 2))
                 for lbl, lo, hi in rng.sample(catalog, n_items)]
        day = rng.randint(1, 28)
        when = first + timedelta(days=day - 1, hours=rng.randint(8, 19),
                                 minutes=rng.randint(0, 59))
        slug = name.lower().replace(" ", "-").replace("&", "and")
        fname = f"{when.strftime('%Y%m%d')}-{slug}.png"
        total = render_receipt(name, city, lang, vat_rate, items, when, rng, out / fname)
        manifest.append(f"{fname}\t{name}\t{total:.2f} EUR\t{lang}")

    (out / "MANIFEST.tsv").write_text("\n".join(manifest) + "\n")
    print(f"wrote {args.count} receipts + MANIFEST.tsv to {out}")


if __name__ == "__main__":
    main()
