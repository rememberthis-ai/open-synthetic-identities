#!/usr/bin/env python3
"""Render the DECOY documents for the receipt-photo grid.

The grid's claim is "I cast a wide net on purpose — drop the ones that aren't",
so the photo set needs things OCR flags and a person rejects: a menu, a parking
tariff sign, a handwritten list, a takeaway flyer.

**Why these are rendered rather than prompted.** Generating them straight from a
text-to-image model produces confident gibberish — a first pass gave a parking
sign reading "Tarit rábir / XAIl - 2:00/€M / Perter mouitchmen" and a menu whose
body was pseudo-German noise. That is fine at thumbnail size and indefensible at
full size in a public repo. The receipts avoid it by rendering real text with PIL
and letting the image model only *photograph* the result, which it does very well
— so the decoys go the same way.

Output feeds the same COMPOSITE path as the receipts: these PNGs are the input
image for a kontext "photographed in context" pass.

Usage:
  python3 gen_decoys.py --out ../fixtures/clerkai/decoy-photo-sources
"""
import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

SUPP = "/System/Library/Fonts/Supplemental/"
FONTS = {
    "sans": ["/System/Library/Fonts/Helvetica.ttc", SUPP + "Arial.ttf"],
    "sans_bold": [SUPP + "Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"],
    "hand": [SUPP + "Bradley Hand Bold.ttf", SUPP + "Chalkboard.ttc"],
    "display": [SUPP + "Arial Black.ttf", SUPP + "Arial Bold.ttf"],
}


def font(kind, size):
    for path in FONTS[kind]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            continue
    return ImageFont.load_default()


def right(d, x, y, text, f, fill=(20, 20, 20)):
    d.text((x - d.textlength(text, font=f), y), text, font=f, fill=fill)


def cafe_menu(path):
    """A5 table menu. German headings, real items, prices down the right."""
    W, H = 900, 1300
    img = Image.new("RGB", (W, H), (252, 250, 245))
    d = ImageDraw.Draw(img)
    d.text((60, 70), "KAFFEEHAUS SÜDSTERN", font=font("display", 44), fill=(25, 25, 25))
    d.text((60, 128), "Hasenheide 12 · Berlin-Neukölln", font=font("sans", 22), fill=(110, 110, 110))
    y = 210
    for heading, items in [
        ("GETRÄNKE", [("Filterkaffee", "2,80"), ("Espresso", "2,40"),
                      ("Cappuccino", "3,60"), ("Flat White", "4,10"),
                      ("Heiße Schokolade", "3,90"), ("Tee (versch. Sorten)", "3,20")]),
        ("SPEISEN", [("Croissant", "2,60"), ("Käsebrot", "4,80"),
                     ("Suppe des Tages", "6,50"), ("Quiche mit Salat", "9,80"),
                     ("Kuchen (Stück)", "4,20")]),
        ("FRÜHSTÜCK bis 12 Uhr", [("Kleines Frühstück", "8,50"),
                                  ("Großes Frühstück", "12,90")]),
    ]:
        d.text((60, y), heading, font=font("sans_bold", 28), fill=(25, 25, 25))
        d.line([(60, y + 40), (W - 60, y + 40)], fill=(190, 185, 175), width=2)
        y += 60
        for name, price in items:
            d.text((70, y), name, font=font("sans", 26), fill=(45, 45, 45))
            right(d, W - 60, y, price + " €", font("sans", 26))
            y += 42
        y += 34
    d.text((60, H - 90), "Alle Preise in Euro, inkl. MwSt.", font=font("sans", 20),
           fill=(130, 130, 130))
    img.save(path, "PNG")


def parking_sign(path):
    """Berlin-style Parkschein tariff plate. White enamel, black text."""
    W, H = 800, 1050
    img = Image.new("RGB", (W, H), (250, 250, 248))
    d = ImageDraw.Draw(img)
    d.rectangle([8, 8, W - 8, H - 8], outline=(40, 40, 40), width=5)
    d.text((W // 2, 70), "PARKSCHEIN", font=font("display", 58), fill=(20, 20, 20), anchor="mt")
    d.text((W // 2, 150), "gebührenpflichtig", font=font("sans", 30), fill=(60, 60, 60), anchor="mt")
    d.line([(60, 215), (W - 60, 215)], fill=(40, 40, 40), width=3)
    y = 260
    for label, value in [("Mo – Fr", "9 – 20 Uhr"), ("Samstag", "9 – 14 Uhr"),
                         ("Sonntag", "frei")]:
        d.text((70, y), label, font=font("sans_bold", 34), fill=(20, 20, 20))
        right(d, W - 70, y, value, font("sans", 34))
        y += 62
    d.line([(60, y + 16), (W - 60, y + 16)], fill=(40, 40, 40), width=3)
    y += 60
    for label, value in [("30 Minuten", "1,00 €"), ("1 Stunde", "2,00 €"),
                         ("Tageskarte", "8,00 €")]:
        d.text((70, y), label, font=font("sans", 34), fill=(20, 20, 20))
        right(d, W - 70, y, value, font("sans_bold", 34))
        y += 62
    d.text((W // 2, H - 110), "Höchstparkdauer 3 Stunden", font=font("sans", 26),
           fill=(60, 60, 60), anchor="mt")
    d.text((W // 2, H - 70), "Bezirksamt Friedrichshain-Kreuzberg", font=font("sans", 22),
           fill=(110, 110, 110), anchor="mt")
    img.save(path, "PNG")


def shopping_list(path):
    """Handwritten note. Real words — the first prompted attempt produced
    'Shoppiing List' over three lines of meaningless digits."""
    W, H = 900, 680
    img = Image.new("RGB", (W, H), (250, 247, 236))
    d = ImageDraw.Draw(img)
    for y in range(120, H, 54):  # feint ruling
        d.line([(40, y), (W - 40, y)], fill=(214, 218, 228), width=2)
    d.text((60, 46), "Einkauf Samstag", font=font("hand", 46), fill=(28, 40, 120))
    y = 130
    for item in ["Milch", "Brot (Roggen)", "Eier 10er", "Tomaten", "Kaffeebohnen",
                 "Waschmittel", "Zahnpasta", "Mira: Turnbeutel!", "Wein für Sam"]:
        d.text((70, y), "· " + item, font=font("hand", 38), fill=(28, 40, 120))
        y += 54
    img.save(path, "PNG")


def takeaway_flyer(path):
    """Pizza delivery leaflet — prices and a big phone number, no VAT block."""
    W, H = 850, 1200
    img = Image.new("RGB", (W, H), (255, 252, 240))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 190], fill=(178, 34, 34))
    d.text((W // 2, 46), "PIZZA NAPOLI", font=font("display", 56), fill=(255, 255, 255), anchor="mt")
    d.text((W // 2, 118), "Lieferservice · täglich 11 – 23 Uhr", font=font("sans", 26),
           fill=(255, 230, 230), anchor="mt")
    y = 240
    for name, price in [("Margherita", "8,50"), ("Salami", "9,50"),
                        ("Funghi", "9,50"), ("Prosciutto", "10,50"),
                        ("Quattro Formaggi", "11,00"), ("Diavola", "11,00"),
                        ("Calzone", "11,50"), ("Vegetaria", "10,00")]:
        d.text((70, y), name, font=font("sans", 32), fill=(35, 35, 35))
        right(d, W - 70, y, price + " €", font("sans_bold", 32))
        y += 52
    y += 20
    d.line([(70, y), (W - 70, y)], fill=(200, 190, 180), width=2)
    y += 30
    d.text((70, y), "Mindestbestellwert 15,00 €", font=font("sans", 26), fill=(90, 90, 90))
    d.text((70, y + 40), "Lieferung frei ab 25,00 €", font=font("sans", 26), fill=(90, 90, 90))
    d.rectangle([60, H - 210, W - 60, H - 70], outline=(178, 34, 34), width=4)
    d.text((W // 2, H - 190), "BESTELLUNG", font=font("sans", 26), fill=(120, 30, 30), anchor="mt")
    d.text((W // 2, H - 152), "030 / 55 12 08", font=font("display", 48),
           fill=(178, 34, 34), anchor="mt")
    img.save(path, "PNG")


DECOYS = {
    "decoy-cafe-menu.png": cafe_menu,
    "decoy-parking-sign.png": parking_sign,
    "decoy-shopping-list.png": shopping_list,
    "decoy-takeaway-flyer.png": takeaway_flyer,
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="../fixtures/clerkai/decoy-photo-sources")
    args = ap.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, fn in DECOYS.items():
        fn(out / name)
        print(f"wrote {name}")


if __name__ == "__main__":
    main()
