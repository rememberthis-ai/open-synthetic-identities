#!/usr/bin/env python3
"""Render a synthetic supplier invoice as a real, openable PDF.

Why a PDF and not another receipt image: a ledger row's document is drawn as
either *invoice* or *receipt*, and the app decides which by looking at the
file — a `.pdf` beside a purchase is an invoice, a photo is a receipt. With
every document in the fixture a `.png`, the invoice wording could not occur, so
the row state existed in the app and nowhere in anything anybody could see.

Everything here is fictional: Fontrack Pro, Carter Studio UG, the numbers and
the addresses. Deliberately written by hand rather than via a PDF library — the
file is a dozen lines of text on one page, and a dependency for that would be a
dependency the rest of this repo does not need.

Each document is written to its period's `receipts/` folder — the period's own
store of what it holds. Staged copies under `attachments-to-send/` and
`attachments-sent-*/` are made by hand, because which of them went out on which
day is a fact about the sending and not about the document.

Usage:
  python3 gen_invoice_pdf.py                     # writes every document below
  python3 gen_invoice_pdf.py --doc vellum-order
"""
import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "fixtures/clerkai/period-close/Notes/bookkeeping"

# One document, one page. (x, y from the bottom-left, font size, text.)
FONTRACK_JUNE = [
    (56, 780, 20, "Fontrack Pro"),
    (56, 762, 9, "fontrack.example - Type foundry subscriptions"),
    (56, 750, 9, "VAT ID: DE 000 000 000"),
    (56, 706, 14, "Rechnung / Invoice FP-2026-06-4471"),
    (56, 684, 10, "Invoice date: 3 June 2026"),
    (56, 670, 10, "Billing period: 3 June 2026 - 2 July 2026"),
    (56, 640, 10, "Billed to:"),
    (56, 626, 10, "Carter Studio UG"),
    (56, 612, 10, "Oranienstr. 183, 10999 Berlin, Germany"),
    (56, 570, 10, "Description                                     Qty        Amount"),
    (56, 556, 10, "----------------------------------------------------------------"),
    (56, 540, 10, "Pro seat (monthly)                                1        15.13 EUR"),
    (56, 526, 10, "----------------------------------------------------------------"),
    (56, 506, 10, "Net                                                        15.13 EUR"),
    (56, 492, 10, "VAT 19%                                                     2.87 EUR"),
    (56, 476, 12, "Total                                                      18.00 EUR"),
    (56, 440, 10, "Paid 3 June 2026 by card ending 4417. No further action required."),
    (56, 400, 9, "Fontrack Pro is a fictional company. This document is synthetic"),
    (56, 388, 9, "sample data and is not a real invoice."),
]

# The document that settled the accountant's April question: a customer's own
# order, carrying the VAT number he needed for the quarterly EU listing.
VELLUM_ORDER = [
    (56, 780, 20, "Vellum & Co"),
    (56, 762, 9, "Neubaugasse 12, 1070 Wien, Austria"),
    (56, 750, 9, "UID / VAT ID: ATU72104588"),
    (56, 706, 14, "Auftragsbestaetigung / Order confirmation VC-2026-0418"),
    (56, 684, 10, "Order date: 18 April 2026"),
    (56, 670, 10, "Your reference: Carter Studio UG, invoice INV-2026-04B"),
    (56, 640, 10, "Supplier:"),
    (56, 626, 10, "Carter Studio UG"),
    (56, 612, 10, "Oranienstr. 183, 10999 Berlin, Germany"),
    (56, 570, 10, "Description                                            Amount"),
    (56, 556, 10, "----------------------------------------------------------------"),
    (56, 540, 10, "Brand system and type direction, phase 1              950.00 EUR"),
    (56, 526, 10, "----------------------------------------------------------------"),
    (56, 506, 12, "Total                                                 950.00 EUR"),
    (56, 470, 10, "Cross-border service between businesses in the EU."),
    (56, 456, 10, "Please quote our VAT ID above on the invoice."),
    (56, 420, 10, "Settled 23 April 2026 by bank transfer."),
    (56, 380, 9, "Vellum & Co is a fictional company. This document is synthetic"),
    (56, 368, 9, "sample data and is not a real order confirmation."),
]

# July's, one month on. Same subscription, same shape — the point of it is that
# the live period has a document of its own to stage.
FONTRACK_JULY = [
    (56, 780, 20, "Fontrack Pro"),
    (56, 762, 9, "fontrack.example - Type foundry subscriptions"),
    (56, 750, 9, "VAT ID: DE 000 000 000"),
    (56, 706, 14, "Rechnung / Invoice FP-2026-07-4913"),
    (56, 684, 10, "Invoice date: 3 July 2026"),
    (56, 670, 10, "Billing period: 3 July 2026 - 2 August 2026"),
    (56, 640, 10, "Billed to:"),
    (56, 626, 10, "Carter Studio UG"),
    (56, 612, 10, "Oranienstr. 183, 10999 Berlin, Germany"),
    (56, 570, 10, "Description                                     Qty        Amount"),
    (56, 556, 10, "----------------------------------------------------------------"),
    (56, 540, 10, "Pro seat (monthly)                                1        15.13 EUR"),
    (56, 526, 10, "----------------------------------------------------------------"),
    (56, 506, 10, "Net                                                        15.13 EUR"),
    (56, 492, 10, "VAT 19%                                                     2.87 EUR"),
    (56, 476, 12, "Total                                                      18.00 EUR"),
    (56, 440, 10, "Paid 3 July 2026 by card ending 4417. No further action required."),
    (56, 400, 9, "Fontrack Pro is a fictional company. This document is synthetic"),
    (56, 388, 9, "sample data and is not a real invoice."),
]

DOCS = {
    "fontrack-june": (
        FONTRACK_JUNE,
        FIXTURE / "carter-studio/2026-06/receipts/2026-06-03-fontrack-pro-rechnung.pdf",
    ),
    "fontrack-july": (
        FONTRACK_JULY,
        FIXTURE / "carter-studio/2026-07/receipts/2026-07-03-fontrack-pro-rechnung.pdf",
    ),
    "vellum-order": (
        VELLUM_ORDER,
        FIXTURE / "carter-studio/2026-04/receipts"
        / "2026-04-23-vellum-and-co-auftragsbestaetigung.pdf",
    ),
}


def escape(text: str) -> str:
    return text.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")


def build(lines) -> bytes:
    content = "BT\n"
    for x, y, size, text in lines:
        content += f"/F1 {size} Tf\n1 0 0 1 {x} {y} Tm\n({escape(text)}) Tj\n"
    content += "ET\n"
    stream = content.encode("latin-1")

    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
        b"/Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream",
    ]

    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"
    xref_at = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for off in offsets:
        out += f"{off:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_at}\n%%EOF\n"
    ).encode()
    return bytes(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--doc", choices=sorted(DOCS) + ["all"], default="all")
    ap.add_argument("--out", help="override the destination (single --doc only)")
    args = ap.parse_args()
    names = sorted(DOCS) if args.doc == "all" else [args.doc]
    if args.out and len(names) != 1:
        raise SystemExit("--out needs a single --doc")
    for name in names:
        lines, default_out = DOCS[name]
        out = Path(args.out) if args.out else default_out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(build(lines))
        print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
