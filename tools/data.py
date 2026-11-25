"""Shared sample data for the invoice / purchase-order project.

All companies, addresses, tax IDs and bank details are fictional.
"""

BUYER = {
    "name": "Musterfirma Produktion GmbH",
    "street": "Musterstraße 1",
    "city": "92637 Weiden in der Oberpfalz",
    "country": "Germany",
}

VAT_RATE = 0.19

# One entry per purchase order. "items" are what the buyer ordered.
PURCHASE_ORDERS = [
    {
        "po": "PO-2026-001",
        "date": "2026-10-27",
        "supplier": "Lindhof Industriebedarf GmbH",
        "items": [
            ("LH-1001", "Safety gloves, size L (pair)", 200, 2.50),
            ("LH-2040", "Cable ties 300 mm, pack of 100", 50, 4.20),
            ("LH-3105", "Safety goggles, clear", 40, 6.75),
        ],
    },
    {
        "po": "PO-2026-002",
        "date": "2026-10-28",
        "supplier": "Donautal Verpackung & Logistik GmbH",
        "items": [
            ("DV-BX604040", "Cardboard box 600x400x400 mm", 500, 1.10),
            ("DV-SF500", "Stretch film roll 500 mm", 30, 12.90),
            ("DV-EP1208", "Euro pallet 1200x800 mm", 20, 14.50),
        ],
    },
    {
        "po": "PO-2026-003",
        "date": "2026-10-30",
        "supplier": "Vilstal Elektrokomponenten GmbH",
        "items": [
            ("VE-PS12", "Inductive proximity sensor M12", 25, 18.60),
            ("VE-PT100", "Temperature sensor PT100", 10, 32.00),
            ("VE-RM24", "Relay module 24 V", 15, 9.80),
        ],
    },
    {
        "po": "PO-2026-004",
        "date": "2026-11-02",
        "supplier": "Naabwerk Stahlhandel GmbH",
        "items": [
            ("NW-SB2010", "Steel sheet 2 mm, 1000x2000 mm", 12, 48.00),
            ("NW-SP4060", "Steel pipe 40 mm diameter, 6 m", 20, 27.50),
        ],
    },
    {
        "po": "PO-2026-005",
        "date": "2026-11-03",
        "supplier": "Haidenaab Bürobedarf GmbH",
        "items": [
            ("HB-PA4500", "Printer paper A4, 500 sheets", 40, 4.25),
            ("HB-TN220K", "Toner cartridge, black", 6, 39.90),
            ("HB-OR80", "Lever arch file 80 mm", 50, 2.30),
        ],
    },
]

# One entry per invoice. Each invoice looks different on purpose
# (labels, number formats, language) so the AI has to really read it.
INVOICES = [
    {
        "file": "01_Invoice_Lindhof_INV-24817.pdf",
        "po": "PO-2026-001",
        "number": "INV-24817",
        "date": "2026-11-10",
        "due": "2026-12-10",
        "lang": "en",
        "po_label": "Customer PO",
        "accent": (0.13, 0.36, 0.55),
        "supplier": {
            "name": "Lindhof Industriebedarf GmbH",
            "street": "Musterweg 14",
            "city": "92224 Amberg",
            "vat": "DE999999901",
            "iban": "DE00 1234 5678 0000 0001 01",
        },
        "items": [
            ("LH-1001", "Safety gloves, size L (pair)", 200, "pair", 2.50),
            ("LH-2040", "Cable ties 300 mm, pack of 100", 50, "pack", 4.20),
            ("LH-3105", "Safety goggles, clear", 40, "pcs", 6.75),
        ],
        "expected": "OK",
    },
    {
        "file": "02_Invoice_Donautal_DV-2026-1193.pdf",
        "po": "PO-2026-002",
        "number": "DV-2026-1193",
        "date": "2026-11-12",
        "due": "2026-11-26",
        "lang": "en",
        "po_label": "Your order reference",
        "accent": (0.10, 0.45, 0.30),
        "supplier": {
            "name": "Donautal Verpackung & Logistik GmbH",
            "street": "Musterallee 7",
            "city": "93047 Regensburg",
            "vat": "DE999999902",
            "iban": "DE00 1234 5678 0000 0002 02",
        },
        # MISMATCH: stretch film billed at 14.40 instead of the agreed 12.90
        "items": [
            ("DV-BX604040", "Cardboard box 600x400x400 mm", 500, "pcs", 1.10),
            ("DV-SF500", "Stretch film roll 500 mm", 30, "roll", 14.40),
            ("DV-EP1208", "Euro pallet 1200x800 mm", 20, "pcs", 14.50),
        ],
        "expected": "MISMATCH",
    },
    {
        "file": "03_Invoice_Vilstal_VE-50342.pdf",
        "po": "PO-2026-003",
        "number": "VE-50342",
        "date": "2026-11-13",
        "due": "2026-12-13",
        "lang": "en",
        "po_label": "PO Number",
        "accent": (0.45, 0.20, 0.50),
        "supplier": {
            "name": "Vilstal Elektrokomponenten GmbH",
            "street": "Musterring 3",
            "city": "92421 Schwandorf",
            "vat": "DE999999903",
            "iban": "DE00 1234 5678 0000 0003 03",
        },
        "items": [
            ("VE-PS12", "Inductive proximity sensor M12", 25, "pcs", 18.60),
            ("VE-PT100", "Temperature sensor PT100", 10, "pcs", 32.00),
            ("VE-RM24", "Relay module 24 V", 15, "pcs", 9.80),
        ],
        "expected": "OK",
    },
    {
        "file": "04_Invoice_Naabwerk_NW-2026-0788.pdf",
        "po": "PO-2026-004",
        "number": "NW/2026/0788",
        "date": "2026-11-16",
        "due": "2026-12-16",
        "lang": "en",
        "po_label": "Purchase order",
        "accent": (0.35, 0.35, 0.38),
        "supplier": {
            "name": "Naabwerk Stahlhandel GmbH",
            "street": "Musterstraße 88",
            "city": "92655 Grafenwöhr",
            "vat": "DE999999904",
            "iban": "DE00 1234 5678 0000 0004 04",
        },
        # MISMATCH: 25 steel pipes billed, only 20 were ordered
        "items": [
            ("NW-SB2010", "Steel sheet 2 mm, 1000x2000 mm", 12, "pcs", 48.00),
            ("NW-SP4060", "Steel pipe 40 mm diameter, 6 m", 25, "pcs", 27.50),
        ],
        "expected": "MISMATCH",
    },
    {
        "file": "05_Rechnung_Haidenaab_RE-2026-0457.pdf",
        "po": "PO-2026-005",
        "number": "RE-2026-0457",
        "date": "2026-11-18",
        "due": "2026-12-02",
        "lang": "de",
        "po_label": "Ihre Bestellnummer",
        "accent": (0.70, 0.30, 0.10),
        "supplier": {
            "name": "Haidenaab Bürobedarf GmbH",
            "street": "Mustergasse 5",
            "city": "92660 Neustadt an der Waldnaab",
            "vat": "DE999999905",
            "iban": "DE00 1234 5678 0000 0005 05",
        },
        # German invoice, German descriptions and number format, same item codes
        "items": [
            ("HB-PA4500", "Kopierpapier A4, 500 Blatt", 40, "Pck.", 4.25),
            ("HB-TN220K", "Tonerkartusche schwarz", 6, "Stk.", 39.90),
            ("HB-OR80", "Ordner, Rückenbreite 80 mm", 50, "Stk.", 2.30),
        ],
        "expected": "OK",
    },
]


def money(value, lang="en"):
    """Format a number as money in English (1,234.56) or German (1.234,56) style."""
    s = f"{value:,.2f}"
    if lang == "de":
        s = s.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"{s} €"
    return f"EUR {s}"
