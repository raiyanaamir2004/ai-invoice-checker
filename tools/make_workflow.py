"""Assemble the importable n8n workflow JSON."""
import json
import sys
import uuid
from pathlib import Path

HERE = Path(__file__).parent
OUT = sys.argv[1]
code = lambda name: (HERE.parent / "workflow" / "code" / name).read_text()
nid = lambda: str(uuid.uuid4())

Y = 300
nodes = [
    {
        "name": "New Invoice Email",
        "type": "n8n-nodes-base.gmailTrigger",
        "typeVersion": 1.3,
        "position": [0, Y],
        "parameters": {
            "pollTimes": {"item": [{"mode": "everyMinute"}]},
            "simple": False,
            "filters": {
                "q": "has:attachment filename:pdf (subject:invoice OR subject:rechnung)",
                "readStatus": "both",
            },
            "options": {"downloadAttachments": True},
        },
    },
    {
        "name": "Extract PDF Text",
        "type": "n8n-nodes-base.extractFromFile",
        "typeVersion": 1,
        "position": [220, Y],
        "parameters": {"operation": "pdf", "binaryPropertyName": "attachment_0", "options": {}},
    },
    {
        "name": "Build AI Request",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [480, Y],
        "parameters": {"jsCode": code("build_ai_request.js")},
    },
    {
        "name": "AI Reads Invoice",
        "type": "n8n-nodes-base.httpRequest",
        "typeVersion": 4.2,
        "position": [700, Y],
        "parameters": {
            "method": "POST",
            "url": "https://api.openai.com/v1/chat/completions",
            "authentication": "predefinedCredentialType",
            "nodeCredentialType": "openAiApi",
            "sendBody": True,
            "specifyBody": "json",
            "jsonBody": "={{ JSON.stringify($json.requestBody) }}",
            "options": {},
        },
    },
    {
        "name": "Parse AI Result",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [920, Y],
        "parameters": {"jsCode": code("parse_ai_result.js")},
    },
    {
        "name": "Read Purchase Orders",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": [1180, Y],
        "executeOnce": True,
        "alwaysOutputData": True,
        "parameters": {
            "operation": "read",
            "documentId": {"__rl": True, "value": "", "mode": "list"},
            "sheetName": {"__rl": True, "value": "Purchase_Orders", "mode": "name"},
            "options": {},
        },
    },
    {
        "name": "Compare Invoice vs PO",
        "type": "n8n-nodes-base.code",
        "typeVersion": 2,
        "position": [1400, Y],
        "parameters": {"jsCode": code("compare_invoice_po.js")},
    },
    {
        "name": "Log to Invoice_Log",
        "type": "n8n-nodes-base.googleSheets",
        "typeVersion": 4.5,
        "position": [1660, Y - 110],
        "parameters": {
            "operation": "append",
            "documentId": {"__rl": True, "value": "", "mode": "list"},
            "sheetName": {"__rl": True, "value": "Invoice_Log", "mode": "name"},
            "columns": {"mappingMode": "autoMapInputData", "value": {},
                        "matchingColumns": [], "schema": []},
            "options": {},
        },
    },
    {
        "name": "Problem Found?",
        "type": "n8n-nodes-base.if",
        "typeVersion": 2,
        "position": [1660, Y + 110],
        "parameters": {
            "conditions": {
                "options": {"caseSensitive": True, "leftValue": "", "typeValidation": "strict"},
                "conditions": [{
                    "id": nid(),
                    "leftValue": "={{ $json.Status }}",
                    "rightValue": "OK",
                    "operator": {"type": "string", "operation": "notEquals"},
                }],
                "combinator": "and",
            },
            "options": {},
        },
    },
    {
        "name": "Send Alert Email",
        "type": "n8n-nodes-base.gmail",
        "typeVersion": 2.1,
        "position": [1900, Y + 100],
        "parameters": {
            "sendTo": "YOUR_EMAIL@gmail.com",
            "subject": "=Invoice check: {{ $json.Status }} – {{ $json.Invoice_Number }} ({{ $json.Supplier }})",
            "emailType": "text",
            "message": (
                "=An invoice did not pass the purchase order check.\n\n"
                "Invoice: {{ $json.Invoice_Number }} from {{ $json.Supplier }}\n"
                "Purchase order: {{ $json.PO_Number }}\n"
                "Invoice net: {{ $json.Invoice_Net }} | PO net: {{ $json.PO_Net }} | "
                "Difference: {{ $json.Difference }}\n\n"
                "Issues:\n- {{ $json.Issues.split('; ').join('\\n- ') }}\n\n"
                "Please check this invoice before it is paid.\n"
                "Sent automatically by the n8n invoice checker."
            ),
            "options": {"appendAttribution": False},
        },
    },
]

notes = [
    ("## 1. Get the invoice\nA new email with \"invoice\" or \"Rechnung\" in the subject and a PDF "
     "attached starts the workflow. The PDF text is pulled out.", [-60, 110], 480, 360, 7),
    ("## 2. AI reads it\nThe text is sent to OpenAI, which returns the supplier, PO number, items, "
     "quantities, prices and totals as clean JSON (works for English and German).",
     [420, 110], 660, 360, 4),
    ("## 3. Check and report\nThe invoice is compared with the purchase order in Google Sheets. "
     "Every result is logged. If something is wrong, an alert email is sent.",
     [1120, 40], 1000, 520, 5),
]

for n in nodes:
    n["id"] = nid()
for i, (content, pos, w, h, color) in enumerate(notes, start=1):
    nodes.append({
        "id": nid(), "name": f"Note {i}", "type": "n8n-nodes-base.stickyNote", "typeVersion": 1,
        "position": pos, "parameters": {"content": content, "width": w, "height": h, "color": color},
    })

chain = ["New Invoice Email", "Extract PDF Text", "Build AI Request", "AI Reads Invoice",
         "Parse AI Result", "Read Purchase Orders"]
link = lambda target: {"node": target, "type": "main", "index": 0}
connections = {a: {"main": [[link(b)]]} for a, b in zip(chain, chain[1:])}
connections["Read Purchase Orders"] = {"main": [[link("Compare Invoice vs PO")]]}
connections["Compare Invoice vs PO"] = {"main": [[link("Log to Invoice_Log"), link("Problem Found?")]]}
connections["Problem Found?"] = {"main": [[link("Send Alert Email")], []]}

workflow = {
    "name": "Invoice vs Purchase Order Checker (AI)",
    "nodes": nodes,
    "connections": connections,
    "pinData": {},
    "settings": {"executionOrder": "v1"},
    "meta": {"templateCredsSetupCompleted": False},
}
Path(OUT).write_text(json.dumps(workflow, indent=2, ensure_ascii=False))
print("saved", OUT, len(nodes), "nodes")
