// Tests the workflow's Code-node logic on the sample data, without n8n or an API key.
// Run from the repository root:  node tests/test_logic.js
const fs = require('fs');
const path = require('path');

const root = path.join(__dirname, '..');
const read = (p) => JSON.parse(fs.readFileSync(path.join(root, p), 'utf8'));
const wf = read('workflow/invoice_checker_workflow.json');
const codeOf = (name) => wf.nodes.find((n) => n.name === name).parameters.jsCode;
// Runs a Code node: $input = incoming items, $('Node') = another node's items
const run = (code, items, refs = {}) =>
  new Function('$input', '$', code)({ all: () => items }, (name) => ({ all: () => refs[name] }));

let failures = 0;
const check = (ok, label) => {
  console.log(`${ok ? 'PASS' : 'FAIL'}  ${label}`);
  if (!ok) failures++;
};

// 1. Build AI Request: produces a valid request body for the OpenAI API
const built = run(codeOf('Build AI Request'), [{ json: { text: 'sample invoice text' } }]);
const body = built[0].json.requestBody;
check(body.messages.length === 2 && body.response_format.type === 'json_object',
      `AI request built for model ${body.model}`);

// 2. Parse AI Result: handles clean JSON, JSON in ``` fences, and non-JSON answers
const aiOutputs = read('tests/fixtures/ai_outputs.json');
const responses = aiOutputs.map((o, i) => ({
  json: { choices: [{ message: { content: i === 4 ? '```json\n' + JSON.stringify(o) + '\n```' : JSON.stringify(o) } }] },
}));
responses.push({ json: { choices: [{ message: { content: 'Sorry, I cannot read this.' } }] } });
const parsed = run(codeOf('Parse AI Result'), responses);
check(parsed.length === 6 && parsed[5].json.parse_error, 'AI answers parsed, bad answer marked as error');

// 3. Compare Invoice vs PO: the 5 samples + an error + an unknown PO
const poRows = read('tests/fixtures/po_rows.json').map((r) => ({ json: r }));
const unknownPo = { json: { invoice_number: 'X-1', supplier_name: 'Unknown GmbH', po_number: 'PO-2099-999',
                            line_items: [], net_total: 10, vat_amount: 1.9, gross_total: 11.9 } };
const results = run(codeOf('Compare Invoice vs PO'), poRows,
                    { 'Parse AI Result': parsed.concat([unknownPo]) }).map((r) => r.json);
const expected = aiOutputs.map((o) => o._expected).concat(['ERROR', 'NO PO']);

console.log('');
results.forEach((r, i) => {
  check(r.Status === expected[i],
        `${String(r.Invoice_Number || '(no number)').padEnd(13)} ${r.Status.padEnd(8)} ${r.Issues}`);
});

const headers = ['Processed_At', 'Invoice_Number', 'Invoice_Date', 'Supplier', 'PO_Number',
                 'Invoice_Net', 'PO_Net', 'Difference', 'Status', 'Issues'];
check(results.every((r) => JSON.stringify(Object.keys(r)) === JSON.stringify(headers)),
      'Output columns match the Invoice_Log headers');

console.log(failures ? `\n${failures} test(s) failed` : '\nAll tests passed');
process.exit(failures ? 1 : 0);
