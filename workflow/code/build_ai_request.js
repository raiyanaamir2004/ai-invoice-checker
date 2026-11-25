// Builds the request we send to the AI.
// If OpenAI ever retires this model, change MODEL to a current one
// (see platform.openai.com/docs/models) – nothing else needs to change.
const MODEL = 'gpt-6-luna';

const SYSTEM_PROMPT = `You read supplier invoices and return their data as JSON.
The invoice can be in English or German.
Return ONLY a JSON object with exactly these keys:
{
  "invoice_number": string,
  "invoice_date": "YYYY-MM-DD",
  "supplier_name": string,
  "po_number": string or null,
  "currency": string,
  "line_items": [
    { "item_code": string or null, "description": string, "quantity": number, "unit_price": number, "line_total": number }
  ],
  "net_total": number,
  "vat_amount": number,
  "gross_total": number
}
Rules:
- po_number is the BUYER purchase order reference (for example labelled PO Number, Customer PO, Your order reference, or in German Bestellnummer).
- Write numbers as plain numbers with a dot for decimals. Convert German style 1.234,56 to 1234.56. No currency signs.
- Write dates as YYYY-MM-DD, whatever format the invoice uses.
- If something is missing, use null. Never invent values.`;

return $input.all().map(item => ({
  json: {
    requestBody: {
      model: MODEL,
      response_format: { type: 'json_object' },
      messages: [
        { role: 'system', content: SYSTEM_PROMPT },
        { role: 'user', content: 'Invoice text:\n\n' + (item.json.text || '') }
      ]
    }
  }
}));
