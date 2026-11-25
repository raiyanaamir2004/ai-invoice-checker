// Compares every invoice with its purchase order (3-way check idea, simplified to 2-way).
// Output fields match the column headers of the Invoice_Log tab exactly.
const TOLERANCE = 0.01; // allow 1 cent rounding difference

// Reads numbers written as 1234.5, "1,234.50" or German "1.234,50"
const toNum = (v) => {
  if (v === null || v === undefined || v === '') return NaN;
  if (typeof v === 'number') return v;
  let s = String(v).replace(/[^0-9,.\-]/g, '');
  if (s.lastIndexOf(',') > s.lastIndexOf('.')) s = s.replace(/\./g, '').replace(',', '.');
  else s = s.replace(/,/g, '');
  return parseFloat(s);
};
const differs = (a, b) => !Number.isFinite(a) || !Number.isFinite(b) || Math.abs(a - b) > TOLERANCE;
const fmt = (n) => (Number.isFinite(n) ? n.toFixed(2) : '?');
const round2 = (n) => (Number.isFinite(n) ? Math.round(n * 100) / 100 : '');
const norm = (s) => String(s ?? '').trim().toUpperCase();
const loose = (s) => String(s ?? '').toLowerCase().replace(/[^a-z0-9äöüß]/g, '');

const invoices = $('Parse AI Result').all().map(i => i.json);
const poRows = $input.all().map(i => i.json).filter(r => r.PO_Number);
const processedAt = (typeof $now !== 'undefined') ? $now.toFormat('yyyy-MM-dd HH:mm') : new Date().toISOString();

return invoices.map(inv => {
  const issues = [];
  let status = 'OK';
  const poNumber = norm(inv.po_number);
  const lines = poRows.filter(r => norm(r.PO_Number) === poNumber);
  const poNet = lines.length ? lines.reduce((s, r) => s + toNum(r.Quantity) * toNum(r.Unit_Price), 0) : NaN;
  const items = Array.isArray(inv.line_items) ? inv.line_items : [];
  let invNet = toNum(inv.net_total);
  if (!Number.isFinite(invNet)) invNet = items.reduce((s, li) => s + toNum(li.line_total), 0);

  if (inv.parse_error) {
    status = 'ERROR';
    issues.push(inv.parse_error);
  } else if (!poNumber) {
    status = 'NO PO';
    issues.push('No purchase order number found on the invoice');
  } else if (lines.length === 0) {
    status = 'NO PO';
    issues.push(`${poNumber} was not found in Purchase_Orders`);
  } else {
    // 1. Supplier name should match the PO
    const a = loose(inv.supplier_name), b = loose(lines[0].Supplier);
    if (!a || !(a.includes(b) || b.includes(a))) {
      issues.push(`Supplier "${inv.supplier_name}" differs from PO supplier "${lines[0].Supplier}"`);
    }
    // 2. Every invoice line must match an ordered line (by item code, else by description)
    const used = new Set();
    for (const li of items) {
      const code = norm(li.item_code);
      let idx = code ? lines.findIndex((r, i) => !used.has(i) && norm(r.Item_Code) === code) : -1;
      if (idx === -1) idx = lines.findIndex((r, i) => !used.has(i) && norm(r.Description) === norm(li.description));
      if (idx === -1) {
        issues.push(`${li.item_code || li.description}: billed but not on the purchase order`);
        continue;
      }
      used.add(idx);
      const r = lines[idx];
      const qInv = toNum(li.quantity), qPo = toNum(r.Quantity);
      const pInv = toNum(li.unit_price), pPo = toNum(r.Unit_Price);
      if (differs(qInv, qPo)) issues.push(`${r.Item_Code}: quantity ${qInv} billed, ${qPo} ordered`);
      if (differs(pInv, pPo)) issues.push(`${r.Item_Code}: unit price ${fmt(pInv)} billed, ${fmt(pPo)} agreed`);
    }
    // 3. Ordered items missing from the invoice
    lines.forEach((r, i) => { if (!used.has(i)) issues.push(`${r.Item_Code}: ordered but not on the invoice`); });
    // 4. Totals
    if (differs(invNet, poNet)) issues.push(`Net total ${fmt(invNet)} billed vs ${fmt(poNet)} on the PO`);
    const vat = toNum(inv.vat_amount), gross = toNum(inv.gross_total);
    if (Number.isFinite(vat) && Number.isFinite(gross) && Math.abs(invNet + vat - gross) > 0.02) {
      issues.push(`Invoice maths: net ${fmt(invNet)} + VAT ${fmt(vat)} is not the total ${fmt(gross)}`);
    }
    if (issues.length) status = 'MISMATCH';
  }

  return {
    json: {
      Processed_At: processedAt,
      Invoice_Number: inv.invoice_number ?? '',
      Invoice_Date: inv.invoice_date ?? '',
      Supplier: inv.supplier_name ?? '',
      PO_Number: poNumber,
      Invoice_Net: status === 'ERROR' ? '' : round2(invNet),
      PO_Net: round2(poNet),
      Difference: status === 'ERROR' ? '' : round2(invNet - poNet),
      Status: status,
      Issues: issues.length ? issues.join('; ') : 'All items match the purchase order',
    },
  };
});
