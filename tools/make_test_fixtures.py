"""Write the test fixtures used by tests/test_logic.js.

- po_rows.json:    the Purchase_Orders tab as Google Sheets would return it to n8n
- ai_outputs.json: what a correct AI extraction of each sample invoice looks like
"""
import json
from pathlib import Path

from data import INVOICES, PURCHASE_ORDERS, VAT_RATE

OUT = Path(__file__).resolve().parent.parent / "tests" / "fixtures"
OUT.mkdir(parents=True, exist_ok=True)

rows, n = [], 2
for order in PURCHASE_ORDERS:
    for code, desc, qty, price in order["items"]:
        price_value = price
        # PO-2026-005 uses German-formatted text prices, to test the number reader
        if order["po"] == "PO-2026-005":
            price_value = f"{price:.2f}".replace(".", ",") + " €"
        rows.append({"row_number": n, "PO_Number": order["po"], "PO_Date": order["date"],
                     "Supplier": order["supplier"], "Item_Code": code, "Description": desc,
                     "Quantity": qty, "Unit_Price": price_value, "Line_Total": round(qty * price, 2)})
        n += 1

ai = []
for inv in INVOICES:
    items = [{"item_code": c, "description": d, "quantity": q, "unit_price": p,
              "line_total": round(q * p, 2)} for c, d, q, _unit, p in inv["items"]]
    net = round(sum(i["line_total"] for i in items), 2)
    vat = round(net * VAT_RATE, 2)
    ai.append({"invoice_number": inv["number"], "invoice_date": inv["date"],
               "supplier_name": inv["supplier"]["name"], "po_number": inv["po"], "currency": "EUR",
               "line_items": items, "net_total": net, "vat_amount": vat,
               "gross_total": round(net + vat, 2), "_expected": inv["expected"]})

(OUT / "po_rows.json").write_text(json.dumps(rows, indent=2, ensure_ascii=False))
(OUT / "ai_outputs.json").write_text(json.dumps(ai, indent=2, ensure_ascii=False))
print(f"wrote {len(rows)} PO rows and {len(ai)} AI outputs to {OUT}")
