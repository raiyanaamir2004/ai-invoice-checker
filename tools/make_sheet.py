"""Generate the Google-Sheets-ready workbook: README, Purchase_Orders, Invoice_Log."""
import sys

from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

from data import PURCHASE_ORDERS

OUT = sys.argv[1]
FONT = "Arial"
HEAD_FILL = PatternFill("solid", fgColor="1F4E79")
HEAD_FONT = Font(name=FONT, bold=True, color="FFFFFF")
BODY = Font(name=FONT)
INPUT = Font(name=FONT, color="0000FF")  # hardcoded inputs in blue

wb = Workbook()

# --- Purchase_Orders: one row per ordered item. n8n reads this tab. ---
po = wb.active
po.title = "Purchase_Orders"
po_headers = ["PO_Number", "PO_Date", "Supplier", "Item_Code", "Description",
              "Quantity", "Unit_Price", "Line_Total"]
po.append(po_headers)
r = 2
for order in PURCHASE_ORDERS:
    for code, desc, qty, price in order["items"]:
        po.cell(r, 1, order["po"])
        po.cell(r, 2, order["date"])  # kept as text (YYYY-MM-DD) so n8n reads it cleanly
        po.cell(r, 3, order["supplier"])
        po.cell(r, 4, code)
        po.cell(r, 5, desc)
        po.cell(r, 6, qty)
        po.cell(r, 7, price)
        po.cell(r, 8, f"=F{r}*G{r}")
        for c in range(1, 8):
            po.cell(r, c).font = INPUT
        po.cell(r, 8).font = BODY
        po.cell(r, 7).number_format = "#,##0.00"
        po.cell(r, 8).number_format = "#,##0.00"
        r += 1

# --- Invoice_Log: empty, the workflow fills it. ---
log = wb.create_sheet("Invoice_Log")
log_headers = ["Processed_At", "Invoice_Number", "Invoice_Date", "Supplier", "PO_Number",
               "Invoice_Net", "PO_Net", "Difference", "Status", "Issues"]
log.append(log_headers)

for ws, widths in ((po, [14, 12, 36, 14, 34, 10, 12, 12]),
                   (log, [22, 16, 14, 36, 14, 13, 13, 13, 12, 70])):
    for i, w in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = w
        ws.cell(1, i).fill = HEAD_FILL
        ws.cell(1, i).font = HEAD_FONT
    ws.freeze_panes = "A2"

# --- README: kept on its own tab so n8n never reads it as data. ---
rd = wb.create_sheet("README", 0)
notes = [
    ("Invoice vs Purchase Order checker – sample data", True),
    ("", False),
    ("Purchase_Orders: what the company ordered, one row per item. The workflow reads this tab.", False),
    ("  Blue cells are sample inputs you can change. Line_Total is a formula (Quantity x Unit_Price).", False),
    ("  Example row format: PO-2026-001 | 2026-10-27 | Lindhof Industriebedarf GmbH | LH-1001 | "
     "Safety gloves, size L (pair) | 200 | 2.50", False),
    ("Invoice_Log: leave empty. The workflow adds one row per invoice it checks.", False),
    ("", False),
    ("Rules:", True),
    ("  Do not rename the tabs or the column headers in row 1 – the workflow looks for these exact names.", False),
    ("  Do not add notes or blank rows inside the Purchase_Orders table.", False),
    ("  All companies and numbers are fictional (sample data for a portfolio project).", False),
    ("", False),
    ("Expected results with the 5 sample invoices:", True),
    ("  PO-2026-001 Lindhof – OK", False),
    ("  PO-2026-002 Donautal – MISMATCH (stretch film billed 14.40, ordered at 12.90)", False),
    ("  PO-2026-003 Vilstal – OK", False),
    ("  PO-2026-004 Naabwerk – MISMATCH (25 steel pipes billed, 20 ordered)", False),
    ("  PO-2026-005 Haidenaab – OK (German invoice)", False),
]
for i, (text, bold) in enumerate(notes, start=1):
    c = rd.cell(i, 1, text)
    c.font = Font(name=FONT, bold=bold, size=12 if i == 1 else 10)
    c.alignment = Alignment(wrap_text=False)
rd.column_dimensions["A"].width = 110

wb.active = 1  # open on Purchase_Orders
wb.save(OUT)
print("saved", OUT, "rows:", r - 2)
