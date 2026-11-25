"""Generate the 5 sample invoice PDFs."""
import sys
from datetime import date

from reportlab.lib import colors
from reportlab.lib.enums import TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from data import BUYER, INVOICES, VAT_RATE, money

OUT_DIR = sys.argv[1]

LABELS = {
    "en": {
        "title": "INVOICE",
        "number": "Invoice No.",
        "date": "Invoice date",
        "due": "Due date",
        "bill_to": "Bill to",
        "cols": ["Item No.", "Description", "Qty", "Unit", "Unit price", "Amount"],
        "net": "Net amount",
        "vat": f"VAT {int(VAT_RATE * 100)}%",
        "total": "Total due",
        "terms": "Payment terms: please pay the total amount by the due date.",
        "bank": "Bank details",
        "vat_id": "VAT ID",
        "footer": "SAMPLE DOCUMENT – fictional company, created only for testing an automation project.",
    },
    "de": {
        "title": "RECHNUNG",
        "number": "Rechnungsnummer",
        "date": "Rechnungsdatum",
        "due": "Fällig am",
        "bill_to": "Rechnungsempfänger",
        "cols": ["Art.-Nr.", "Beschreibung", "Menge", "Einheit", "Einzelpreis", "Gesamt"],
        "net": "Nettobetrag",
        "vat": f"zzgl. {int(VAT_RATE * 100)} % MwSt.",
        "total": "Rechnungsbetrag",
        "terms": "Zahlbar innerhalb von 14 Tagen ohne Abzug.",
        "bank": "Bankverbindung",
        "vat_id": "USt-IdNr.",
        "footer": "MUSTERDOKUMENT – fiktive Firma, nur zum Testen eines Automatisierungsprojekts. "
                  "(SAMPLE DOCUMENT – fictional company.)",
    },
}

# Each invoice uses a different date style, like real suppliers do.
DATE_STYLES = ["%d %B %Y", "%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%d.%m.%Y"]


def fmt_date(iso, style):
    return date.fromisoformat(iso).strftime(style)


def build(inv, idx):
    L = LABELS[inv["lang"]]
    lang = inv["lang"]
    accent = colors.Color(*inv["accent"])
    s = inv["supplier"]
    dstyle = DATE_STYLES[idx]

    base = ParagraphStyle("base", fontName="Helvetica", fontSize=9.5, leading=13)
    small = ParagraphStyle("small", parent=base, fontSize=8, leading=10, textColor=colors.grey)
    right = ParagraphStyle("right", parent=base, alignment=TA_RIGHT)
    company = ParagraphStyle("company", parent=base, fontName="Helvetica-Bold", fontSize=16,
                             leading=20, textColor=accent)
    title = ParagraphStyle("title", parent=base, fontName="Helvetica-Bold", fontSize=22,
                           leading=26, textColor=accent)

    doc = SimpleDocTemplate(
        f"{OUT_DIR}/{inv['file']}", pagesize=A4,
        leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
        title=f"{L['title'].title()} {inv['number']}", author=s["name"],
    )
    story = []

    # Header: supplier left, VAT ID right
    header = Table(
        [[Paragraph(s["name"], company),
          Paragraph(f"{s['street']}<br/>{s['city']}<br/>{L['vat_id']}: {s['vat']}", right)]],
        colWidths=[105 * mm, 65 * mm],
    )
    header.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                                ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story += [header, Spacer(1, 4 * mm)]
    line = Table([[""]], colWidths=[170 * mm], rowHeights=[1.2])
    line.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), accent)]))
    story += [line, Spacer(1, 8 * mm), Paragraph(L["title"], title), Spacer(1, 6 * mm)]

    # Bill-to (left) and invoice details (right)
    bill_to = Paragraph(
        f"<b>{L['bill_to']}</b><br/>{BUYER['name']}<br/>{BUYER['street']}<br/>"
        f"{BUYER['city']}<br/>{BUYER['country']}", base)
    details = Table(
        [[L["number"], inv["number"]],
         [L["date"], fmt_date(inv["date"], dstyle)],
         [L["due"], fmt_date(inv["due"], dstyle)],
         [inv["po_label"], inv["po"]]],
        colWidths=[38 * mm, 37 * mm],
    )
    details.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.lightgrey),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
    ]))
    top = Table([[bill_to, details]], colWidths=[95 * mm, 75 * mm])
    top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 0),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
    story += [top, Spacer(1, 10 * mm)]

    # Line items
    rows = [L["cols"]]
    net = 0.0
    for code, desc, qty, unit, price in inv["items"]:
        amount = round(qty * price, 2)
        net += amount
        num = (lambda v: money(v, lang).replace("EUR ", "")) if lang == "en" else (lambda v: money(v, lang))
        rows.append([code, Paragraph(desc, base), str(qty), unit, num(price), num(amount)])
    net = round(net, 2)
    vat = round(net * VAT_RATE, 2)
    gross = round(net + vat, 2)

    items = Table(rows, colWidths=[27 * mm, 63 * mm, 14 * mm, 16 * mm, 25 * mm, 25 * mm],
                  repeatRows=1)
    items.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), accent),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.Color(0.96, 0.96, 0.96)]),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, accent),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    story += [items, Spacer(1, 4 * mm)]

    totals = Table(
        [[L["net"], money(net, lang)],
         [L["vat"], money(vat, lang)],
         [L["total"], money(gross, lang)]],
        colWidths=[45 * mm, 35 * mm], hAlign="RIGHT",
    )
    totals.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 1), "Helvetica"),
        ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9.5),
        ("FONTSIZE", (0, 2), (-1, 2), 11),
        ("ALIGN", (1, 0), (1, -1), "RIGHT"),
        ("LINEABOVE", (0, 2), (-1, 2), 0.8, accent),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story += [totals, Spacer(1, 12 * mm)]

    story += [
        Paragraph(L["terms"], base),
        Spacer(1, 3 * mm),
        Paragraph(f"<b>{L['bank']}:</b> {s['name']} · IBAN {s['iban']} · BIC MUSTDEXXXXX", base),
        Spacer(1, 18 * mm),
        Paragraph(L["footer"], small),
    ]
    doc.build(story)
    return net, vat, gross


if __name__ == "__main__":
    for i, inv in enumerate(INVOICES):
        net, vat, gross = build(inv, i)
        print(f"{inv['file']}: net {net:.2f}  vat {vat:.2f}  gross {gross:.2f}  ({inv['expected']})")
