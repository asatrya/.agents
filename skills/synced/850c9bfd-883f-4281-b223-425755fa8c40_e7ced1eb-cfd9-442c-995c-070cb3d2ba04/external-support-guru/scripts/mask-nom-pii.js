/**
 * Mask personal data in the live NOM page, before any screenshot is taken.
 *
 * Run via the Claude in Chrome javascript_tool on every page and after every
 * navigation or expand. Returns a JSON report; read `safe` before screenshotting.
 *
 * Masking happens in the DOM on purpose. A screenshot taken first and redacted
 * afterwards has already put the unmasked image into the model's context, which
 * is the thing the policy forbids.
 */
(() => {
  // Mirrored from external-support-guru/scripts/pii-patterns.json.
  // hooks/piiScan.test.ts fails on drift.
  const KEEP = [
    /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i,
    /^[A-Z]{2,5}[0-9]{6,12}$/i,
    /^(authorization|capture|refund|void)-[A-Z0-9]{8,}$/i,
    /^pi_[A-Za-z0-9]+$/i,
    /^\d{4}-\d{2}-\d{2}$/i,
    /^\d{4}-\d{2}-\d{2}[T ]\d{1,2}(:\d{2}(:\d{2})?(\.\d+)?)?$/i,
    /^\d{1,2}:\d{2}(:\d{2})?(\.\d+)?$/i,
  ];
  const keep = (s) => KEEP.some((re) => re.test(s.trim()));

  const PATTERNS = [
    ['email', /\b[\w.+-]+@[\w-]+\.[\w.]{2,}\b/g],
    ['phone', /(?<![\w-])(\+\d[\d\s().-]{7,}\d|\(\d{3}\)\s*\d{3}[-\s]?\d{4}|\d{3}-\d{3}-\d{4})(?![\w-])/g],
    ['pan', /\b(?:\d[ -]*?){13,19}\b/g],
    ['postcode_uk', /\b[A-Z]{1,2}\d[A-Z\d]?\s?\d[A-Z]{2}\b/g],
  ];

  // Labels whose adjacent value is personal. Matched case-insensitively against
  // an element's own text when that text is short (i.e. it looks like a label).
  const LABELS = /^(customer|customer ?id|consumer|shopper|recipient|associate|name|first name|last name|full name|e-?mail|email address|phone|telephone|mobile|contact|address|shipping address|billing address|ship to|bill to|deliver to|street|city|post(al)? ?code|zip)\s*:?$/i;

  // Product identifiers are evidence, not personal data. A 13-digit EAN under
  // an EAN13 label must survive while a 13-digit PAN under a Card label must
  // not, and no value-level pattern can tell those apart — only the label can.
  const KEEP_LABELS = /^(sku|upc|ean|ean13|isbn|gtin|barcode|product ?id|variant ?id|item ?id|shopify_inventory_item_id|style|colou?r|size|quantity|qty)\s*:?$/i;
  // Two layouts in the wild. Inline -- "SKU: 32602G2062029-02" in one element --
  // and split, where the label and the value are sibling elements and the value's
  // own parent holds no label at all (Ant Design descriptions, which is what the
  // NOM order page uses for product attributes). Only the inline form was handled,
  // so every product identifier on the order page fell through to the patterns and
  // was blacked out. Deliberately looks one level up and no further: a wider search
  // starts keeping values whose label belongs to a different field.
  const nearestLabel = (node) => {
    const parent = node.parentElement;
    const own = ((parent && parent.textContent) || '').trim();
    if (own.indexOf(':') !== -1) {
      const head = own.split(':', 1)[0].trim();
      if (head.length <= 40) return head;
    }
    const prev = parent && parent.previousElementSibling;
    if (prev) {
      const label = (prev.textContent || '').trim().replace(/:$/, '').trim();
      if (label && label.length <= 40) return label;
    }
    return own.length <= 40 ? own : '';
  };

  const counts = {};
  const bump = (k) => { counts[k] = (counts[k] || 0) + 1; };

  // 1. Replace matching values inside text nodes.
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const textNodes = [];
  while (walker.nextNode()) textNodes.push(walker.currentNode);

  for (const node of textNodes) {
    const parentTag = node.parentElement && node.parentElement.tagName;
    if (parentTag === 'SCRIPT' || parentTag === 'STYLE') continue;
    let text = node.nodeValue;
    if (!text || !text.trim() || keep(text)) continue;
    if (KEEP_LABELS.test(nearestLabel(node))) continue;  // product data, not PII
    let changed = false;
    for (const [kind, re] of PATTERNS) {
      text = text.replace(re, (m) => {
        if (keep(m)) return m;
        bump(kind);
        changed = true;
        return '█'.repeat(Math.min(m.trim().length, 24));
      });
    }
    if (changed) node.nodeValue = text;
  }

  // 2. Blur the value next to a personal-data label.
  // An element already masked by an earlier run must still be counted. Without
  // this the second run reports zero blurred fields, the structural gate below
  // fires, and a page that is in fact fully masked is refused as unsafe.
  const blur = (el) => {
    if (!el) return;
    if (el.dataset.nsMasked) { bump('already_masked'); return; }
    el.dataset.nsMasked = '1';
    el.style.filter = 'blur(7px)';
    el.style.userSelect = 'none';
    bump('blurred_field');
  };

  for (const el of document.querySelectorAll('dt,th,label,span,div,p,strong,b')) {
    const own = (el.textContent || '').trim();
    if (own.length > 40 || !LABELS.test(own)) continue;
    // dt -> dd, th -> matching td, otherwise the next sibling.
    if (el.tagName === 'DT' && el.nextElementSibling) blur(el.nextElementSibling);
    else if (el.tagName === 'TH') {
      const table = el.closest('table');
      const idx = Array.from(el.parentElement.children).indexOf(el);
      if (table) table.querySelectorAll('tbody tr').forEach((tr) => blur(tr.children[idx]));
    } else if (el.nextElementSibling) blur(el.nextElementSibling);
    else if (el.parentElement) blur(el.parentElement);
  }

  // 3. Address blocks are multi-line and rarely labelled per line.
  for (const el of document.querySelectorAll('address')) blur(el);

  // 4. Verify.
  //
  // Two separate gates, because the two masking methods fail differently.
  //
  // (a) Value patterns: emails, phones, card numbers. Regex both masks and
  //     verifies these, so a leak here means the replacement did not run.
  //
  // (b) Names and street lines. Regex cannot recognise these at all — a page
  //     reading "Jane Doe, 12 Market St" passes every pattern above. They are
  //     masked only by the label blur in step 2, which depends on NOM's markup.
  //     So the gate asks a structural question instead: does this page carry
  //     personal-data labels, and did the blur find values for them? A page with
  //     labels and no blurred fields means the markup was not understood, and
  //     the correct answer is to refuse the screenshot, not to trust the regex.
  // Deliberately not document.body.innerText. That version applied the raw
  // patterns with no label awareness, so every product identifier pass 1
  // legitimately kept came back as a leak and `safe` could only be reached by
  // masking the evidence too. A gate that is satisfiable only by over-masking is
  // worse than no gate: it teaches people to black out the useful half.
  // Blurred values are skipped for the same reason -- they are already covered,
  // and their text necessarily still exists in the DOM behind the blur.
  const remaining = [];
  const tally = {};
  const verifyWalker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (verifyWalker.nextNode()) {
    const node = verifyWalker.currentNode;
    const parentTag = node.parentElement && node.parentElement.tagName;
    if (parentTag === 'SCRIPT' || parentTag === 'STYLE') continue;
    const text = node.nodeValue;
    if (!text || !text.trim() || keep(text)) continue;
    if (KEEP_LABELS.test(nearestLabel(node))) continue;
    if (node.parentElement && node.parentElement.closest('[data-ns-masked]')) continue;
    for (const [kind, re] of PATTERNS) {
      const hits = text.match(new RegExp(re.source, 'g')) || [];
      const real = hits.filter((h) => !keep(h));
      if (real.length) tally[kind] = (tally[kind] || 0) + real.length;
    }
  }
  for (const kind of Object.keys(tally)) remaining.push({ kind, count: tally[kind] });

  const labelled = Array.from(document.querySelectorAll('dt,th,label,span,div,p,strong,b'))
    .some((el) => LABELS.test((el.textContent || '').trim()));
  const covered = (counts.blurred_field || 0) + (counts.already_masked || 0);
  const blurredNothing = labelled && !covered;
  if (blurredNothing) {
    remaining.push({ kind: 'unblurred_labelled_fields', count: 1 });
  }

  const safe = remaining.length === 0;
  return JSON.stringify({
    url: location.href,
    masked: counts,
    remaining,
    safe,
    note: blurredNothing
      ? 'DO NOT SCREENSHOT. This page has personal-data labels but nothing was blurred, so the markup was not recognised. Mask by hand or skip the view.'
      : !safe
        ? 'DO NOT SCREENSHOT. Unmasked values remain; mask by hand or skip this view.'
        : 'Value patterns clear and labelled fields blurred. Screenshot allowed — but this is not a guarantee: names and street lines in free text are covered only by the blur, never by the patterns.',
  }, null, 2);
})();
