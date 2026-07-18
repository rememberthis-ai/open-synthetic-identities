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


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--identity", default="alex-carter")
    ap.add_argument("--month", default="2026-06")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--count", type=int, default=14)
    ap.add_argument("--out", default="../fixtures/clerkai/receipts")
    args = ap.parse_args()

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
