// newstore.js — NewStore brand system + reusable slide builders for pptxgenjs.
//
// CANVAS: this deck is authored at the Google Slides native 16:9 size (10" × 5.625"),
// so the .pptx imports into Google Slides at the SAME page size as the NewStore
// company decks and every point size matches the template 1:1 (content title 28pt,
// body 14pt, etc. — measured from the template). Build in inches on a 10×5.625 grid.
//
// HOUSE STYLE (from the NewStore Company Slidedeck 2025 Template):
//  - Content slides lead with a TITLE + optional SUBTITLE. No "eyebrow/kicker" tags
//    (AGENDA/OVERVIEW/etc.) — that is a consultant style, not NewStore's. `eyebrow`
//    still exists for the rare case, but the default is `slideHeader(title, red, subtitle)`.
//  - Title = Poppins bold, navy, one keyword in red. Body = Figtree.
//  - Bullets are dot bullets with a bold lead-in (template "Simple Bullet List").
//
//   const NS = require("./newstore.js");
//   const pres = NS.newDeck();
//   const s = pres.addSlide(); NS.slideHeader(s, "Simple ", "Bullet List", "Optional supporting line.");
//   NS.bulletList(s, { items: [{lead:"Guidelines", desc:"formatting and color usage"}] });

let pptxgen;
try { pptxgen = require("pptxgenjs"); }
catch (e) { pptxgen = require((process.env.NODE_PATH || "/usr/local/lib/node_modules_global/lib/node_modules") + "/pptxgenjs"); }

// ---- Colors ----
const C = {
  navy: "1E293B", text: "334155", muted: "64748B", red: "EF1B53", lightBg: "F1F5F9", white: "FFFFFF",
  blue: "0171B7", green: "3BB273", orange: "FFAE03", purple: "9B5DE5", redAlt: "F03A47",
  lblue: "DBEAFE", lgreen: "CCEDE3", lorange: "FDDEC7", lpurple: "E6D0F1", lred: "ECBFCA",
  slate300: "CBD5E1", slate200: "E2E8F0", slate400: "94A3B8", grid: "EEF2F6",
};
const F = { head: "Poppins", body: "Figtree" };

// ---- Type scale (points) ----------------------------------------------------
// ONE place for every font size. Builders reference T.* instead of hardcoding numbers, so the
// whole deck's type can be tuned from here. Tuned smaller than the raw template (which reads
// large on a laptop) for a more refined, exec-appropriate density. To go bigger/smaller across
// the entire deck, change these values — nothing else.
const T = {
  title: 28,        // content-slide title (slideHeader) — matches the live NewStore deck
  subtitle: 14,     // supporting line under the title (deck uses 14; bump to 15 to soften the jump)
  body: 12,         // bullets, card bodies — the default reading size (deck body/table = 12)
  banner: 13,       // takeaway banner copy on the dark strip
  lead: 12,         // bold lead-in in lists/checklists
  cardTitle: 13,    // title inside a card / icon row
  cardBody: 11.5,   // description inside a card / icon row
  kicker: 10,       // small caps labels (YOUR GOAL, RECOMMENDED, column headers)
  small: 9.5,       // captions, notes, legends, footnotes
  tableCell: 12,    // table body + header cells (matches the deck)
  statLabel: 12,    // label under a big stat number
  // display sizes for full-bleed cover / section / closing slides
  cover: 30, section: 34, closing: 42, quote: 22,
  // hero-number caps (auto-fit still shrinks to fit; these are the max)
  statBig: 40, compareBig: 30, metricBig: 20, railBig: 16, progressBig: 12,
};

// ---- Layout: 10" × 5.625" (Google Slides native 16:9) ----
const L = { W: 10, H: 5.625, margin: 0.5 };
L.contentW = L.W - L.margin * 2; // 9.0

// One consistent icon-circle diameter used by every icon layout, so icons are the same
// size and treatment across all slides. The icon image inside is 0.56 × this (see iconCircle).
const ICON_D = 0.72;

// NOTE: there is deliberately NO "estimate how many lines this text wraps to" helper here.
// Guessing line counts from character width is fragile (bold/wide glyphs break it) and was the
// source of title/description overlap bugs. Instead, builders stack related text in a SINGLE
// text frame (runs with breakLine + paraSpaceAfter) and let the renderer flow it with real
// metrics, or reserve a deterministic band. Positioning never depends on a text-length estimate.

// ---- Real icons (lucide-static, recolored) --------------------------------
// NewStore uses monochrome pictograms from its icon library, recolored to brand colors.
// This renders them to PNG data for embedding. It is ASYNC — call once up front:
//   const ic = await NS.icons(["shopping-cart","message-circle","star"]);   // navy by default
//   NS.iconCards(s, { items: [{ icon: ic["star"], title, desc }, ...] });
// Names are lucide icon names (kebab-case). See references/brand.md for the mapping from
// the NewStore icon library to lucide names.
let _sharp, _lucideIconsDir;
function _iconDeps() {
  if (_sharp) return true;
  try {
    _sharp = require("sharp");
    _lucideIconsDir = require("path").dirname(require.resolve("lucide-static/package.json")) + "/icons";
    return true;
  } catch (e) { return false; }
}
async function icons(names, opts = {}) {
  const color = (opts.color || C.navy).replace("#", ""), size = opts.size || 160, sw = opts.strokeWidth || 1.9;
  if (!_iconDeps()) throw new Error("Icon rendering needs lucide-static + sharp. Run: npm install lucide-static sharp (render.sh does this automatically).");
  const fs = require("fs"), path = require("path"), out = {};
  for (const raw of names) {
    const name = String(raw), file = path.join(_lucideIconsDir, name + ".svg");
    if (!fs.existsSync(file)) { out[name] = null; continue; }
    const svg = fs.readFileSync(file, "utf8").replace(/currentColor/g, "#" + color).replace(/stroke-width="[^"]*"/g, `stroke-width="${sw}"`);
    const buf = await _sharp(Buffer.from(svg)).resize(size, size).png().toBuffer();
    out[name] = "image/png;base64," + buf.toString("base64");
  }
  return out;
}

function newDeck() {
  const pres = new pptxgen();
  pres.defineLayout({ name: "GS", width: 10, height: 5.625 });
  pres.layout = "GS";
  pres.defineSlideMaster({ title: "NS", background: { color: C.white } });
  // Robustness: make EVERY text box shrink-to-fit its box (PowerPoint/Google
  // "shrink text on overflow"). This means no text ever spills out of a card or
  // off the slide, whatever its length — the layout stays correct regardless of content.
  const origAddSlide = pres.addSlide.bind(pres);
  pres.addSlide = function (...a) {
    const s = origAddSlide(...a);
    const origAddText = s.addText.bind(s);
    s.addText = function (t, o) {
      if (o && typeof o === "object" && o.fit == null) {
        // Autofit policy (fixes "the text box is way taller than the text when I click it"):
        //  - Standalone text (top-aligned: titles, subtitles, bullets, checklist, card copy)
        //    RESIZES to hug its text. We also START the box at one line so autofit only ever
        //    GROWS it to the real text height — it can never be left taller than the text. In
        //    Google Slides the box then matches the text exactly, with nothing to shrink by hand.
        //  - Text overlaid on a shape and centered (valign middle/center: banners, pills, stat
        //    numbers, table-like cells, bar labels) stays SHRINK-to-fit, keeping its fixed size
        //    and centering so it can't drift off its shape.
        const hug = (o.valign == null || o.valign === "top");
        if (hug) {
          o = Object.assign({ fit: "resize" }, o);
          const fs = typeof o.fontSize === "number" ? o.fontSize : 14;
          const oneLine = +(fs * 1.3 / 72).toFixed(3);
          if (o.h == null || o.h > oneLine) o.h = oneLine;
        } else {
          o = Object.assign({ fit: "shrink" }, o);
        }
      }
      return origAddText(t, o);
    };
    return s;
  };
  return pres;
}

// Optional red caps kicker. NewStore rarely uses this — prefer slideHeader's subtitle.
function eyebrow(s, text) {
  s.addText(String(text).toUpperCase(), { x: L.margin, y: 0.42, w: 8, h: 0.3, fontFace: F.head, fontSize: T.kicker, bold: true, color: C.red, charSpacing: 2 });
}

// Content-slide title: navy with an optional red keyword.
function contentTitle(s, plain, red, opts = {}) {
  const runs = [];
  if (plain) runs.push({ text: plain, options: { color: C.text } });
  if (red) runs.push({ text: red, options: { color: C.red } });
  s.addText(runs, { x: L.margin, y: opts.y != null ? opts.y : 0.5, w: opts.w || L.contentW, h: opts.h || 0.62, fontFace: F.head, fontSize: opts.size || T.title, bold: true, valign: "top" });
}

// Title with arbitrary colored segments.
function titleRuns(s, segments, opts = {}) {
  s.addText(segments.map(([t, color]) => ({ text: t, options: { color } })),
    { x: L.margin, y: opts.y != null ? opts.y : 0.5, w: opts.w || L.contentW, h: opts.h || 0.62, fontFace: F.head, fontSize: opts.size || T.title, bold: true, valign: "top" });
}

// Standalone subtitle line under the title — sits close beneath it.
function subtitle(s, text, y) {
  s.addText(text, { x: L.margin, y: y != null ? y : 1.1, w: L.contentW, h: 0.4, fontFace: F.body, fontSize: T.subtitle, color: C.muted, valign: "top" });
}

// THE default content header: title (+ optional red keyword) + optional subtitle.
// Title and subtitle share ONE text frame, so the subtitle flows below the title with real
// metrics and can never overlap it no matter how many lines the title wraps to. Returns a
// DETERMINISTIC content-start y (a reserved header band, not an estimate of the actual title
// length), so content always starts at a consistent place and can never collide with the header.
function slideHeader(s, plain, red, sub, opts = {}) {
  const size = opts.size || T.title;
  const runs = [];
  if (plain) runs.push({ text: plain, options: { color: C.text } });
  if (red) runs.push({ text: red, options: { color: C.red } });
  if (runs.length && sub) { const last = runs[runs.length - 1].options; last.breakLine = true; last.paraSpaceAfter = 6; }
  if (sub) runs.push({ text: sub, options: { color: C.muted, fontFace: F.body, fontSize: T.subtitle, bold: false } });
  s.addText(runs, { x: L.margin, y: 0.5, w: L.contentW, h: 1.2, fontFace: F.head, fontSize: size, bold: true, valign: "top", lineSpacingMultiple: 1.03 });
  return opts.contentY || (sub ? 1.9 : 1.5);
}

function footer(s, page, confidential = "Confidential", onDark = false) {
  const col = onDark ? C.muted : C.slate400;
  if (confidential) s.addText(confidential, { x: L.margin, y: 5.28, w: 7, h: 0.25, fontFace: F.body, fontSize: 8, color: col });
  if (page != null) s.addText(String(page), { x: L.W - L.margin - 0.5, y: 5.28, w: 0.5, h: 0.25, align: "right", fontFace: F.body, fontSize: 8, color: col });
}

function card(s, x, y, w, h, fill = C.lightBg) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.08, fill: { color: fill }, line: { type: "none" } });
}

// Cover: navy panel left + image placeholder right (pricing-deck title treatment).
function titleSlide(pres, opts = {}) {
  const s = pres.addSlide(); s.background = { color: C.white };
  s.addShape("roundRect", { x: 0.35, y: 0.35, w: 5.1, h: 4.9, rectRadius: 0.13, fill: { color: C.navy }, line: { type: "none" } });
  s.addShape("roundRect", { x: 5.6, y: 0.35, w: 4.05, h: 4.9, rectRadius: 0.13, fill: { color: C.lightBg }, line: { type: "none" } });
  s.addShape("ellipse", { x: 7.25, y: 2.42, w: 0.76, h: 0.76, fill: { color: C.white }, line: { type: "none" } });
  s.addText("Replace with image", { x: 6.0, y: 3.3, w: 3.25, h: 0.3, align: "center", fontFace: F.body, fontSize: 9, italic: true, color: C.muted });
  if (opts.eyebrow) s.addText(String(opts.eyebrow).toUpperCase(), { x: 0.8, y: 0.75, w: 4.3, h: 0.3, fontFace: F.head, fontSize: T.kicker, bold: true, color: C.slate300, charSpacing: 3 });
  s.addText([
    { text: opts.plainTitle || "", options: { color: C.white, breakLine: true } },
    { text: opts.redTitle || "", options: { color: C.red } },
  ], { x: 0.8, y: 1.85, w: 4.5, h: 2.0, fontFace: F.head, fontSize: opts.titleSize || T.cover, bold: true, lineSpacingMultiple: 1.04, valign: "top" });
  if (opts.subtitle) s.addText(opts.subtitle, { x: 0.8, y: 4.05, w: 4.3, h: 0.55, fontFace: F.body, fontSize: T.subtitle, color: C.slate200, valign: "top" });
  if (opts.presenter) s.addText(opts.presenter, { x: 0.8, y: 4.75, w: 3.0, h: 0.3, fontFace: F.body, fontSize: T.small, color: C.slate400 });
  if (opts.date) s.addText(opts.date, { x: 3.55, y: 4.75, w: 1.5, h: 0.3, align: "right", fontFace: F.body, fontSize: T.small, color: C.slate400 });
  return s;
}

// Full-navy section divider.
function sectionSlide(pres, opts = {}) {
  const s = pres.addSlide(); s.background = { color: C.navy };
  if (opts.part) s.addText(String(opts.part).toUpperCase(), { x: L.margin, y: 1.95, w: 7, h: 0.35, fontFace: F.head, fontSize: T.kicker, bold: true, color: C.red, charSpacing: 3 });
  s.addText([
    { text: opts.plainTitle || "", options: { color: C.white } },
    { text: opts.redTitle || "", options: { color: C.red } },
  ], { x: L.margin, y: 2.3, w: 9.0, h: 1.0, fontFace: F.head, fontSize: opts.titleSize || T.section, bold: true });
  if (opts.subtitle) s.addText(opts.subtitle, { x: L.margin, y: 3.35, w: 8.2, h: 0.55, fontFace: F.body, fontSize: T.subtitle, color: C.slate300 });
  if (opts.page != null) footer(s, opts.page, opts.confidential != null ? opts.confidential : "Confidential", true);
  return s;
}

// Closing / thank-you. Default = navy, left-aligned. opts.light = gray panel + centered
// NEWSTORE wordmark + centered title (the proposal-deck variant).
function closingSlide(pres, opts = {}) {
  const s = pres.addSlide();
  const plain = opts.plainTitle || "Thank ", red = opts.redTitle || "you";
  if (opts.light) {
    s.background = { color: C.white };
    card(s, 0.35, 0.35, 9.3, 4.9);
    s.addText("N E W S T O R E", { x: 0, y: 2.05, w: 10, h: 0.4, align: "center", fontFace: F.head, fontSize: 15, bold: true, color: C.text, charSpacing: 2 });
    s.addText([{ text: plain, options: { color: C.text } }, { text: red, options: { color: C.red } }],
      { x: 0, y: 2.5, w: 10, h: 1.1, align: "center", fontFace: F.head, fontSize: T.closing, bold: true });
    if (opts.subtitle) s.addText(opts.subtitle, { x: 0, y: 3.7, w: 10, h: 0.5, align: "center", fontFace: F.body, fontSize: T.subtitle, color: C.muted });
    return s;
  }
  s.background = { color: C.navy };
  s.addText([{ text: plain, options: { color: C.white } }, { text: red, options: { color: C.red } }],
    { x: L.margin, y: 2.05, w: 8.7, h: 1.1, fontFace: F.head, fontSize: T.closing, bold: true });
  if (opts.subtitle) s.addText(opts.subtitle, { x: L.margin, y: 3.2, w: 8.2, h: 0.55, fontFace: F.body, fontSize: T.subtitle, color: C.slate300 });
  if (opts.contact) s.addText(opts.contact, { x: L.margin, y: 4.9, w: 7, h: 0.3, fontFace: F.body, fontSize: T.small, color: C.slate400 });
  return s;
}

// Genuine editable table. Size it to fill the slide — span most of the content width
// (w ≈ 7–9), not a corner. Defaults are roomy.
function styledTable(s, { x, y, w, colW, headers, rows, headerTint = C.lblue, rowH = 0.5, headerH = 0.44, emphasizeRow = -1, size = T.tableCell }) {
  const border = { type: "solid", color: C.slate200, pt: 1 };
  const pad = [6, 9, 6, 9];
  const H = headers.map(t => ({ text: t, options: { fill: { color: headerTint }, color: C.text, bold: true, fontFace: F.head, fontSize: size, valign: "middle", margin: pad } }));
  const body = rows.map((r, i) => r.map((cellText, ci) => {
    const emph = i === emphasizeRow;
    return { text: cellText, options: { color: emph ? C.red : (ci === 0 ? C.text : C.text), bold: emph || ci === 0, fontFace: F.body, fontSize: size, valign: "middle", margin: pad } };
  }));
  const heights = [headerH].concat(rows.map(() => rowH));
  s.addTable([H].concat(body), { x, y, w, colW, rowH: heights, border, align: "left", valign: "middle" });
}

// Dot-bullet list with bold lead-in (template "Simple Bullet List"). One row per item;
// increase rowH if a description wraps. Set arrow:true for the "Welcome"-style → variant.
function bulletList(s, { x = L.margin, y = 1.9, w = L.contentW, items, size = T.body, rowH = 0.52, color = C.text, leadColor = C.text, arrow = false, markerColor }) {
  const mk = arrow ? "→" : "•";
  const mc = markerColor || (arrow ? C.red : C.text);
  items.forEach((it, i) => {
    const cy = y + i * rowH;
    const lead = typeof it === "string" ? it : it.lead;
    const desc = typeof it === "string" ? "" : (it.desc || "");
    s.addText(mk, { x, y: cy, w: 0.3, h: rowH, fontFace: F.body, fontSize: size, bold: true, color: mc, valign: "top", margin: 0 });
    const runs = desc
      ? [{ text: lead, options: { bold: true, color: leadColor } }, { text: " — " + desc, options: { color } }]
      : [{ text: lead, options: { color } }];
    s.addText(runs, { x: x + 0.34, y: cy, w: w - 0.34, h: rowH, fontFace: F.body, fontSize: size, valign: "top", lineSpacingMultiple: 1.05, margin: 0 });
  });
}

function numberedList(s, { x = L.margin, y = 1.9, w = L.contentW, items, size = T.body, rowH = 0.52 }) {
  items.forEach((it, i) => {
    const cy = y + i * rowH;
    const lead = typeof it === "string" ? it : it.lead;
    const desc = typeof it === "string" ? "" : (it.desc || "");
    s.addText((i + 1) + ".", { x, y: cy, w: 0.4, h: rowH, fontFace: F.head, fontSize: size, bold: true, color: C.red, valign: "top", margin: 0 });
    const runs = desc
      ? [{ text: lead, options: { bold: true, color: C.text } }, { text: " — " + desc, options: { color: C.text } }]
      : [{ text: lead, options: { color: C.text } }];
    s.addText(runs, { x: x + 0.46, y: cy, w: w - 0.46, h: rowH, fontFace: F.body, fontSize: size, valign: "top", lineSpacingMultiple: 1.05, margin: 0 });
  });
}

// Row of feature/benefit/team cards with a colored icon circle.
// Grid of cards, centered content (NewStore "Themes"/"Support" style): a real pictogram
// (dark, on the light-gray card — no colored circle), bold title, muted description.
// items: [{ icon: dataURL from NS.icons(), title, desc }]
function iconCards(s, { y = 1.95, h = 2.75, items, x = L.margin, w = L.contentW, gap = 0.22 }) {
  const n = items.length, cw = (w - gap * (n - 1)) / n;
  items.forEach((it, i) => {
    const cx = x + i * (cw + gap);
    card(s, cx, y, cw, h);
    // icon in a consistent circle (white, for contrast on the gray card) — same size everywhere
    if (it.icon) iconCircle(s, cx + cw / 2, y + 0.34 + ICON_D / 2, ICON_D, { icon: it.icon, bg: C.white });
    const tY = y + (it.icon ? 0.34 + ICON_D + 0.18 : 0.34);
    // Title + description in ONE text frame: PowerPoint flows them with real font metrics, so the
    // description can NEVER overlap the title no matter how many lines the title wraps to. (No
    // line-count estimate, no fixed offset — the class of overlap bug those cause is gone.)
    const runs = [{ text: it.title, options: { fontFace: F.head, bold: true, fontSize: T.cardTitle, color: C.text, breakLine: true, paraSpaceAfter: it.desc ? 6 : 0 } }];
    if (it.desc) runs.push({ text: it.desc, options: { fontFace: F.body, fontSize: T.cardBody, color: C.muted } });
    s.addText(runs, { x: cx + 0.2, y: tY, w: cw - 0.4, h: y + h - tY - 0.16, align: "center", valign: "top", lineSpacingMultiple: 1.08 });
  });
}

// Rows of: light circle + real icon + bold title + optional description. 1–2 columns, on
// white (NewStore "Our Omnichannel POS" / "Transforming…" style). Pairs well as the left
// half of a text+image slide via split(). items: [{ icon: dataURL, title, desc }]
function iconRows(s, { items, x = L.margin, y = 1.9, w = L.contentW, cols = 2, colGap = 0.5, rowGap = 0.26, bottom = 5.05 }) {
  const colW = (w - colGap * (cols - 1)) / cols;
  const nRows = Math.ceil(items.length / cols);
  // Distribute rows to FILL the region evenly instead of packing at the top, so a
  // sparse set (2–3 rows) breathes across the canvas instead of leaving dead space
  // below. Each row gets an equal slice; content is centered in its slice.
  const pitch = (bottom - y) / nRows;
  const rowH = Math.min(1.15, pitch - rowGap);
  const pad = Math.max(0, (pitch - rowH) / 2);
  const d = ICON_D;
  items.forEach((it, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const cx = x + c * (colW + colGap), cy = y + r * pitch + pad;
    iconCircle(s, cx + d / 2, cy + d / 2, d, { icon: it.icon, bg: it.bg || C.lightBg });
    const tx = cx + d + 0.22, tw = colW - d - 0.22;
    // Title + description in ONE frame so the description can never overlap a 2-line title.
    const runs = [{ text: it.title, options: { fontFace: F.head, bold: true, fontSize: T.cardTitle, color: C.text, breakLine: true, paraSpaceAfter: it.desc ? 4 : 0 } }];
    if (it.desc) runs.push({ text: it.desc, options: { fontFace: F.body, fontSize: T.cardBody, color: C.muted } });
    s.addText(runs, { x: tx, y: cy - 0.02, w: tw, h: Math.max(0.5, rowH), valign: "top", lineSpacingMultiple: 1.06 });
  });
}

// Colored circle with an optional glyph/short label centered in it. Reliable "icon":
// use safe glyphs like "✓ ★ → + ↑ ↓ $ %" or 1–2 letters. No external icon deps.
// Light circle containing a real icon image (NewStore treatment: pictogram in a soft circle).
// opts: { icon: dataURL, bg (circle fill, default light gray), glyph, glyphColor }.
function iconCircle(s, cx, cy, d, opts = {}) {
  const bg = opts.bg || C.lightBg;
  s.addShape("ellipse", { x: cx - d / 2, y: cy - d / 2, w: d, h: d, fill: { color: bg }, line: { type: "none" } });
  if (opts.icon) {
    const isz = d * 0.56;
    s.addImage({ data: opts.icon, x: cx - isz / 2, y: cy - isz / 2, w: isz, h: isz });
  } else if (opts.glyph != null && opts.glyph !== "") {
    s.addText(String(opts.glyph), { x: cx - d / 2, y: cy - d / 2, w: d, h: d, align: "center", valign: "middle", fontFace: F.head, fontSize: Math.round(d * 24), bold: true, color: opts.glyphColor || C.navy, margin: 0 });
  }
}

// Big hero stat cards — tall, number vertically centered, label pinned low. Fills the row.
// items: [{ value, label, color? (value color), size? }]
function statCards(s, { y = 1.9, h = 2.85, items, x = L.margin, w = L.contentW, gap = 0.22 }) {
  const n = items.length, cw = (w - gap * (n - 1)) / n;
  const textW = cw - 0.3;
  // UNIFORM number size across the row: every value uses the SMALLEST size that fits the
  // longest number, so peers on one row read as the same size instead of each ballooning to
  // fill its own card. Legibility floor and cap still apply. (Per-item `size` overrides.)
  const fit = (v) => Math.max(15, Math.min(T.statBig, Math.floor(textW * 72 / (String(v).length * 0.72))));
  const rowSize = Math.min(...items.map((it) => fit(it.value)));
  items.forEach((it, i) => {
    const cx = x + i * (cw + gap);
    card(s, cx, y, cw, h);
    s.addText(it.value, { x: cx + 0.15, y: y + 0.15, w: textW, h: h - 0.75, align: "center", valign: "middle", fontFace: F.head, fontSize: it.size || rowSize, bold: true, color: it.color || C.blue });
    s.addText(it.label, { x: cx + 0.2, y: y + h - 0.62, w: cw - 0.4, h: 0.45, align: "center", valign: "top", fontFace: F.body, fontSize: T.statLabel, color: C.muted });
  });
}

// Two-column checkmark grid (template's signature "benefits" look). Fills the space.
// items: strings or { lead, desc }. cols 1 or 2.
function checklist(s, { items, x = L.margin, y = 1.95, w = L.contentW, cols = 2, colGap = 0.5, rowH = 0.95, bottom = 4.55 }) {
  const colW = (w - colGap * (cols - 1)) / cols;
  const nRows = Math.ceil(items.length / cols);
  // Distribute rows to FILL the region evenly instead of packing them at the top:
  // each row gets an equal vertical slice, and its content is centered in that slice.
  // This keeps a sparse checklist (2–4 items) from clustering up top with dead space
  // above the banner, while a full one (6 items) still fits. Default bottom clears the
  // takeaway banner (~4.7); pass a larger bottom if the slide has no banner.
  const pitch = (bottom - y) / nRows;
  const cellH = Math.min(rowH, pitch);
  const pad = Math.max(0, (pitch - cellH) / 2);
  const cd = 0.34; // check circle sized to the first text line (not an oversized badge)
  items.forEach((it, i) => {
    const r = Math.floor(i / cols), c = i % cols;
    const cx = x + c * (colW + colGap), cy = y + r * pitch + pad;
    // Check aligned to the first line of text (center ≈ first-line center), not floating below it.
    iconCircle(s, cx + cd / 2, cy + 0.15, cd, { bg: C.lgreen, glyph: "✓", glyphColor: C.green });
    const lead = typeof it === "string" ? it : it.lead;
    const desc = typeof it === "string" ? "" : (it.desc || "");
    // With a description the lead is bold to lead the eye; WITHOUT one, keep it regular so a column
    // of short items doesn't read as a heavy wall of bold.
    const runs = desc
      ? [{ text: lead, options: { bold: true, color: C.text } }, { text: " — " + desc, options: { color: C.text } }]
      : [{ text: lead, options: { bold: false, color: C.text } }];
    const tx = cx + cd + 0.16;
    s.addText(runs, { x: tx, y: cy, w: colW - (tx - cx), h: cellH, fontFace: F.body, fontSize: T.body, valign: "top", lineSpacingMultiple: 1.08, margin: 0 });
  });
}

// Big light-gray container to hold a composition and fill the slide (like the
// pricing "overview" slide). Draw it first, then place content inside.
function panel(s, opts = {}) {
  card(s, opts.x != null ? opts.x : 0.4, opts.y != null ? opts.y : 1.65, opts.w || 9.2, opts.h || 3.6, opts.fill || C.lightBg);
}

// Split the content area into left/right regions with a guaranteed gutter, so
// side-by-side elements (chart + rail, text + visual) can NEVER overlap. Pass each
// returned rect straight to the builder. e.g.
//   const R = split({ y: cy }); panel(s, R.left); statRail(s, {...R.right, items});
function split({ y = 1.55, bottom = 5.1, gap = 0.3, ratioLeft = 0.6 } = {}) {
  const h = bottom - y;
  const leftW = (L.contentW - gap) * ratioLeft;
  const rightW = (L.contentW - gap) - leftW;
  return {
    left: { x: L.margin, y, w: leftW, h },
    right: { x: L.margin + leftW + gap, y, w: rightW, h },
    gap,
  };
}

// ============================================================================
// LAYOUT PRIMITIVES — the shared grid every improvised format snaps to.
// Format is open (bars, comparisons, timelines, whatever the content needs) but
// spacing/alignment is NOT freehand: compose new layouts from these so columns
// line up and gaps are consistent, exactly like the built-in builders. All of
// them pull color from C, font from F, and position against L.margin/contentW.
// ============================================================================

// Spacing scale (inches). Use these named steps instead of arbitrary numbers so
// every gap in the deck is one of a few consistent values.
const GAP = { xs: 0.08, sm: 0.14, md: 0.22, lg: 0.34, xl: 0.5 };

// Equal columns across the content width (or within a given x/w), separated by a
// consistent gutter. Returns an array of {x,y,w,h} rects — use for ANY N-up card
// or column layout so columns are always the same width and aligned to the margins.
function grid(n, { x = L.margin, y = 1.6, w = L.contentW, bottom = null, h = 1.5, gap = GAP.md } = {}) {
  const colW = (w - gap * (n - 1)) / n;
  const H = bottom != null ? bottom - y : h;
  return Array.from({ length: n }, (_, i) => ({ x: x + i * (colW + gap), y, w: colW, h: H }));
}

// Full-width (or [x,w]) tinted band — the "swimlane" row used across the exec
// decks. Draws the rounded background and returns the padded inner rect so callers
// place content inside it consistently.
function band(s, { x = L.margin, y, w = L.contentW, h, fill = C.lightBg, radius = 0.08, pad = 0.24 } = {}) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: radius, fill: { color: fill }, line: { type: "none" } });
  return { x: x + pad, y: y + pad, w: w - pad * 2, h: h - pad * 2 };
}

// Pill / status chip (e.g. "IN MOTION", "+11.3%", owner tags). Auto-widths to its
// label unless a width is given. Returns its rect so you can place things beside it.
function pill(s, { x, y, text, fill = C.blue, color = C.white, fontSize = 9, w = null, h = 0.32, align = "center" }) {
  const width = w != null ? w : Math.max(0.55, String(text).length * fontSize * 0.0125 + 0.28);
  s.addShape("roundRect", { x, y, w: width, h, rectRadius: h / 2, fill: { color: fill }, line: { type: "none" } });
  s.addText(String(text), { x, y, w: width, h, align, valign: "middle", fontFace: F.head, fontSize, bold: true, color });
  return { x, y, w: width, h };
}

// Horizontal bar primitive: a light rounded track with one or more colored segments
// drawn left-to-right from `start` (as fractions of the track width). Covers:
//   single data bar   → segments:[{frac:.76, color:C.blue}]
//   stacked/segmented  → segments:[{frac:.49,color:C.green,label:"LEGO 49%"},{frac:.18,color:C.blue,label:"Clarks 18%"}]
//   gantt span         → start:.2, segments:[{frac:.5,color:C.green,label:"$77K",labelAlign:"right"}]
//   two-tone coverage  → segments:[{frac:.27,color:C.green,label:"27% today"},{frac:.44,color:C.lgreen,label:"71%",labelColor:C.green}]
function hbar(s, { x, y, w, h = 0.3, start = 0, segments = [], track = true, trackColor = C.slate200, radius = null }) {
  const r = radius != null ? radius : h / 2;
  if (track) s.addShape("roundRect", { x, y, w, h, rectRadius: r, fill: { color: trackColor }, line: { type: "none" } });
  let cx = x + start * w;
  for (const seg of segments) {
    const segW = Math.max(0.04, seg.frac * w);
    s.addShape("roundRect", { x: cx, y, w: segW, h, rectRadius: r, fill: { color: seg.color || C.blue }, line: { type: "none" } });
    if (seg.label) {
      const labSize = seg.labelSize || 9;
      // Does the label fit INSIDE the segment on one line? If not, place it just to the RIGHT of
      // the segment in dark text instead of letting it wrap mid-word inside a narrow bar.
      const needed = String(seg.label).length * (labSize / 72) * 0.62;
      if (segW - 0.24 >= needed) {
        s.addText(String(seg.label), { x: cx + 0.12, y, w: segW - 0.24, h, valign: "middle",
          align: seg.labelAlign || "left", fontFace: F.head, fontSize: labSize, bold: true, color: seg.labelColor || C.white });
      } else {
        s.addText(String(seg.label), { x: cx + segW + 0.1, y, w: Math.max(1.2, w - (cx - x) - segW - 0.1), h, valign: "middle",
          align: "left", fontFace: F.head, fontSize: labSize, bold: true, color: seg.labelOutColor || C.text });
      }
    }
    cx += segW;
  }
}

// KPI card with colored header bar (master "Metric Collection" style).
function metricCard(s, { x, y, w = 2.9, h = 1.65, name, value, delta, deltaColor = C.green, trend, headerColor = C.green }) {
  s.addShape("roundRect", { x, y, w, h, rectRadius: 0.06, fill: { color: C.white }, line: { color: C.slate200, pt: 1 } });
  s.addShape("roundRect", { x, y, w, h: 0.42, rectRadius: 0.06, fill: { color: headerColor }, line: { type: "none" } });
  s.addText(name, { x: x + 0.18, y: y + 0.04, w: w - 0.36, h: 0.34, valign: "middle", fontFace: F.head, fontSize: T.kicker, bold: true, color: C.white });
  // Value + delta share one frame below the header bar; trend stays pinned to the bottom.
  const runs = [{ text: value, options: { fontFace: F.head, bold: true, fontSize: T.metricBig, color: C.text, breakLine: true, paraSpaceAfter: delta ? 3 : 0 } }];
  if (delta) runs.push({ text: delta, options: { fontFace: F.body, bold: true, fontSize: T.small, color: deltaColor } });
  s.addText(runs, { x: x + 0.18, y: y + 0.5, w: w - 0.36, h: h - 0.5 - (trend ? 0.32 : 0.1), valign: "top", lineSpacingMultiple: 1.04 });
  if (trend) s.addText(trend, { x: x + 0.18, y: y + h - 0.32, w: w - 0.36, h: 0.26, fontFace: F.body, fontSize: T.small, color: C.muted });
}

// 2/3/4 equal column cards. items: [{ title, body, color?, glyph?/label?, tint? }].
// Give each an icon (color + glyph or 1–2 letter label) to add life; keeps the card
// from reading as an empty gray box.
function columns(s, { y = 1.95, h = 2.75, items, x = L.margin, w = L.contentW, gap = 0.22, tint = C.lightBg }) {
  const n = items.length, cw = (w - gap * (n - 1)) / n;
  items.forEach((it, i) => {
    const cx = x + i * (cw + gap);
    card(s, cx, y, cw, h, it.tint || tint);
    let ty = y + 0.32;
    if (it.icon) { iconCircle(s, cx + 0.3 + ICON_D / 2, y + 0.32 + ICON_D / 2, ICON_D, { icon: it.icon, bg: C.white }); ty = y + 0.32 + ICON_D + 0.18; }
    // Title + body in ONE text frame so the body can never overlap a multi-line title (see iconCards).
    const runs = [{ text: it.title, options: { fontFace: F.head, bold: true, fontSize: T.cardTitle, color: it.titleColor || C.text, breakLine: true, paraSpaceAfter: it.body ? 6 : 0 } }];
    if (it.body) runs.push({ text: it.body, options: { fontFace: F.body, fontSize: T.cardBody, color: C.text } });
    s.addText(runs, { x: cx + 0.28, y: ty, w: cw - 0.56, h: y + h - ty - 0.2, valign: "top", lineSpacingMultiple: 1.12 });
  });
}

// Text list one side, image placeholder the other. side: "right"|"left".
function listWithImage(s, { side = "right", items, imageLabel = "Replace with image", y = 1.8, h = 3.4 }) {
  const textW = 4.5, imgW = 4.0, gap = 0.3;
  const textX = side === "right" ? L.margin : L.margin + imgW + gap;
  const imgX = side === "right" ? L.margin + textW + gap : L.margin;
  s.addShape("roundRect", { x: imgX, y, w: imgW, h, rectRadius: 0.1, fill: { color: C.lightBg }, line: { type: "none" } });
  s.addShape("ellipse", { x: imgX + imgW / 2 - 0.34, y: y + h / 2 - 0.42, w: 0.68, h: 0.68, fill: { color: C.white }, line: { type: "none" } });
  s.addText(imageLabel, { x: imgX, y: y + h / 2 + 0.34, w: imgW, h: 0.3, align: "center", fontFace: F.body, fontSize: 9, italic: true, color: C.muted });
  bulletList(s, { x: textX, y: y + 0.1, w: textW, items });
}

// Vertical milestone timeline. items: [{ label, text, emphasize? }]
function timeline(s, { x = 5.3, y = 1.9, step = 0.82, items, bottom = 5.05 }) {
  step = Math.min(step, (bottom - y) / Math.max(1, items.length - 1)); // fit all milestones
  items.forEach((it, i) => {
    const cy = y + i * step;
    if (i < items.length - 1) s.addShape("line", { x: x + 0.1, y: cy + 0.22, w: 0, h: step - 0.02, line: { color: C.slate200, width: 1.5 } });
    s.addShape("ellipse", { x, y: cy, w: 0.2, h: 0.2, fill: { color: it.emphasize ? C.red : C.blue }, line: { type: "none" } });
    s.addText(it.label, { x: x + 0.4, y: cy - 0.05, w: 1.3, h: 0.3, fontFace: F.head, fontSize: T.cardBody, bold: true, color: it.emphasize ? C.red : C.text });
    s.addText(it.text, { x: x + 1.7, y: cy - 0.05, w: 3.0, h: 0.5, fontFace: F.body, fontSize: T.cardBody, color: it.emphasize ? C.red : C.text, valign: "top" });
  });
}

// Large centered pull-quote / safe-harbor. dark:true -> navy background.
function quote(s, { text, attribution, dark = false }) {
  if (dark) s.background = { color: C.navy };
  const col = dark ? C.white : C.text;
  s.addText([
    { text: "“", options: { color: C.red } },
    { text: text, options: { color: col } },
    { text: "”", options: { color: C.red } },
  ], { x: 0.9, y: 1.7, w: 8.2, h: 2.0, fontFace: F.head, fontSize: T.quote, bold: true, align: "center", valign: "middle", lineSpacingMultiple: 1.12 });
  if (attribution) s.addText(attribution, { x: 0.9, y: 3.85, w: 8.2, h: 0.35, align: "center", fontFace: F.body, fontSize: T.subtitle, color: dark ? C.slate300 : C.muted });
}

// Numbered process/next-steps rows with an optional right-hand timeframe pill.
function processSteps(s, { y0 = 1.9, items, gap = 0.16, rh }) {
  const n = items.length, avail = 5.05 - y0; // keep clear of the footer
  rh = Math.min(rh || 1.05, (avail - (n - 1) * gap) / n);
  const circ = Math.min(0.52, rh - 0.38);
  items.forEach((r, i) => {
    const y = y0 + i * (rh + gap), cy = y + (rh - circ) / 2;
    card(s, L.margin, y, L.contentW, rh);
    s.addShape("ellipse", { x: L.margin + 0.32, y: cy, w: circ, h: circ, fill: { color: C.red }, line: { type: "none" } });
    s.addText(String(r.n != null ? r.n : i + 1), { x: L.margin + 0.32, y: cy, w: circ, h: circ, align: "center", valign: "middle", fontFace: F.head, fontSize: T.cardTitle, bold: true, color: C.white });
    // Title + desc share one frame, vertically centered in the row, so a 2-line title can't
    // overlap the desc; width leaves room for the timeframe pill when present.
    const tRuns = [{ text: r.title, options: { fontFace: F.head, bold: true, fontSize: T.cardTitle, color: C.text, breakLine: true, paraSpaceAfter: r.desc ? 4 : 0 } }];
    if (r.desc) tRuns.push({ text: r.desc, options: { fontFace: F.body, fontSize: T.cardBody, color: C.muted } });
    s.addText(tRuns, { x: L.margin + 1.1, y: y + 0.08, w: r.tag ? 5.9 : 7.6, h: rh - 0.16, valign: "middle", lineSpacingMultiple: 1.06 });
    if (r.tag) {
      s.addShape("roundRect", { x: 7.45, y: cy, w: 1.95, h: circ, rectRadius: circ / 2, fill: { color: C.white }, line: { type: "none" } });
      s.addText(r.tag, { x: 7.45, y: cy, w: 1.95, h: circ, align: "center", valign: "middle", fontFace: F.head, fontSize: T.cardBody, bold: true, color: C.red });
    }
  });
}

// Two side-by-side option cards; recommend "left"|"right" renders that one navy.
// Two option cards. The recommended one is a light card with a RED BORDER (not a heavy
// navy fill) + a red "RECOMMENDED" tag and red figure — lighter and more on-brand.
function comparisonCards(s, { y = 1.95, h = 2.7, left, right, recommend }) {
  const w = 4.15, gap = 0.3;
  [["left", left, L.margin], ["right", right, L.margin + w + gap]].forEach(([key, it, cx]) => {
    const rec = recommend === key;
    // grey cards throughout; the recommended one gets a subtle navy border + small label — no red
    s.addShape("roundRect", { x: cx, y, w, h, rectRadius: 0.08, fill: { color: C.lightBg }, line: rec ? { color: C.slate300, width: 1 } : { type: "none" } });
    // Whole card content (recommended tag → title → hero figure → body) flows in ONE frame, so a
    // long title or body can never overlap the figure. The figure is just a large run.
    const runs = [];
    if (rec) runs.push({ text: "RECOMMENDED", options: { fontFace: F.head, bold: true, fontSize: T.small, color: C.muted, charSpacing: 1, breakLine: true, paraSpaceAfter: 4 } });
    runs.push({ text: it.title, options: { fontFace: F.head, bold: true, fontSize: T.cardTitle, color: C.text, breakLine: true, paraSpaceAfter: (it.big || it.body) ? 6 : 0 } });
    if (it.big) runs.push({ text: it.big, options: { fontFace: F.head, bold: true, fontSize: T.compareBig, color: C.blue, breakLine: true, paraSpaceAfter: it.body ? 6 : 0 } });
    if (it.body) runs.push({ text: it.body, options: { fontFace: F.body, fontSize: T.cardBody, color: C.text } });
    s.addText(runs, { x: cx + 0.32, y: y + 0.26, w: w - 0.64, h: h - 0.5, valign: "top", lineSpacingMultiple: 1.12 });
  });
}

// ===== Price-heavy add-ons (from real NewStore pricing decks) =====

// Financial / comparison pricing table. Navy header by default; mark one column as
// `recommendedCol` (red header). Rows can be strings or { cells:[...], total:true }.
// Cells can be strings or { t, color, bold, fill }. align[] sets per-column alignment.
function pricingTable(s, { x = L.margin, y = 1.9, w = L.contentW, colW, headers, rows, align = [], headerFill = C.navy, recommendedCol = -1, zebra = false, rowH = 0.5, headerH, size, footerY = 5.1 }) {
  const nRows = rows.length, nCols = headers.length;
  // Guarantee the whole table fits between y and footerY, for ANY row count / label length.
  // 1) default a WIDE label column so labels wrap to ~2 lines, not 3
  if (!colW) { const first = w * 0.34, rest = (w - first) / (nCols - 1); colW = [first, ...Array(nCols - 1).fill(rest)]; }
  // 2) header height (a touch shorter when dense) and the row height that fits nRows
  const hasSub = headers.some(h => typeof h === "object" && h.sub);
  if (headerH == null) headerH = hasSub ? 0.6 : 0.5;
  const targetRowH = (footerY - y - headerH) / nRows;
  // 3) pick the font so up to TWO wrapped lines fit that row height — legible floor 8pt.
  //    pptxgenjs grows rows to content, so controlling the font (not just rowH) is what
  //    actually prevents the table from running off the bottom.
  const padV = nRows > 6 ? 0.07 : 0.11;
  const maxFontForFit = Math.floor((targetRowH - padV) * 72 / (2 * 1.15));
  if (size == null) size = T.tableCell;
  size = Math.max(8, Math.min(size, maxFontForFit));
  rowH = targetRowH;
  const border = { type: "solid", color: C.slate200, pt: 1 };
  const pad = nRows > 6 ? [3, 7, 3, 7] : [6, 9, 6, 9];
  const H = headers.map((h, ci) => {
    const t = typeof h === "string" ? h : h.t;
    const sub = typeof h === "object" ? h.sub : null;
    const txt = sub
      ? [{ text: t, options: { breakLine: true, bold: true, fontFace: F.head, fontSize: size, color: C.white } }, { text: sub, options: { fontFace: F.body, fontSize: Math.max(8, size - 3), color: C.slate300 } }]
      : t;
    return { text: txt, options: { fill: { color: (typeof h === "object" && h.fill) || headerFill }, color: C.white, bold: true, fontFace: F.head, fontSize: size, align: ci === 0 ? "left" : "center", valign: "middle", margin: pad } };
  });
  const body = rows.map((r, ri) => {
    const isObj = !Array.isArray(r); // arrays have a .fill METHOD — never read r.fill on them
    const cells = isObj ? r.cells : r;
    const rowFill = (isObj && r.fill) ? r.fill : ((isObj && r.total) ? C.lightBg : (zebra && ri % 2 === 1 ? C.lightBg : null));
    return cells.map((c, ci) => {
      const cell = (typeof c === "object" && c !== null) ? c : { t: c };
      // recommended column gets a subtle grey tint (no red), so it still reads as distinct
      const recTint = ci === recommendedCol ? C.lightBg : null;
      const o = { color: cell.color || (ci === 0 ? C.text : C.text), bold: cell.bold != null ? cell.bold : (ci === 0 || !!r.total), fontFace: F.body, fontSize: size, align: align[ci] || (ci === 0 ? "left" : "center"), valign: "middle", margin: pad, fill: { color: cell.fill || rowFill || recTint || C.white } };
      return { text: cell.t, options: o };
    });
  });
  const heights = [headerH].concat(rows.map(() => rowH));
  s.addTable([H].concat(body), { x, y, w, colW, rowH: heights, border, valign: "middle" });
}

// Stacked "takeaway" stat cards, usually beside a chart/table. side "right"|"left"
// or pass explicit x/w. items: [{ value, label, desc, color? }]
function statRail(s, { side = "right", x, y = 1.75, w = 3.4, items, gap = 0.16, bottom = 5.1 }) {
  const rx = x != null ? x : (side === "right" ? L.W - L.margin - w : L.margin);
  const n = items.length, h = (bottom - y - (n - 1) * gap) / n;
  // UNIFORM value size across the stacked cards (smallest that fits the longest value; cap 17,
  // floor 11) so the numbers in the group read as the same size rather than one shrinking alone.
  const vTextW = w - 0.52;
  const vSize = Math.min(...items.map((it) => Math.max(11, Math.min(T.railBig, Math.floor(vTextW * 72 / (String(it.value).length * 0.64))))));
  items.forEach((it, i) => {
    const cy = y + i * (h + gap);
    card(s, rx, cy, w, h);
    // Value + label + desc flow in ONE frame (value keeps the uniform size), so a 2-line label
    // can't overlap the description. Vertically centered within the card.
    const runs = [{ text: it.value, options: { fontFace: F.head, bold: true, fontSize: vSize, color: it.color || C.blue, breakLine: true, paraSpaceAfter: 3 } },
      { text: it.label, options: { fontFace: F.head, bold: true, fontSize: T.cardBody, color: C.text, breakLine: !!it.desc, paraSpaceAfter: it.desc ? 3 : 0 } }];
    if (it.desc) runs.push({ text: it.desc, options: { fontFace: F.body, fontSize: T.small, color: C.muted } });
    s.addText(runs, { x: rx + 0.26, y: cy + 0.1, w: w - 0.52, h: h - 0.2, valign: "middle", lineSpacingMultiple: 1.04 });
  });
}

// Full-width summary banner. segments: [[text, color?, bold?], ...]. dark=true -> navy.
function summaryBanner(s, { y = 4.7, h = 0.7, segments, dark = true }) {
  s.addShape("roundRect", { x: L.margin, y, w: L.contentW, h, rectRadius: 0.08, fill: { color: dark ? C.text : C.lightBg }, line: { type: "none" } });
  const runs = segments.map(seg => ({ text: seg[0], options: { color: seg[1] || (dark ? C.white : C.text), bold: !!seg[2], fontFace: seg[2] ? F.head : F.body, fontSize: T.banner } }));
  s.addText(runs, { x: L.margin + 0.4, y, w: L.contentW - 0.8, h, align: "center", valign: "middle" });
}

// Horizontal "offer evolution" — labeled value cards with chevrons; last can be highlighted.
// items: [{ label, title, value, note, body }]
function progressionCards(s, { y = 1.7, h = 2.75, items, highlightLast = true, gap = 0.16 }) {
  const n = items.length, chev = 0.26;
  const cw = (L.contentW - (n - 1) * (gap + chev)) / n;
  const px = 0.22; // inner padding
  // UNIFORM value size across the row (smallest that fits the longest value; cap 12.5 keeps
  // the normal look, floor 9 keeps it legible) so the numbers read as peers, not each its own size.
  const vTextW = cw - px * 2;
  const vals = items.filter((it) => it.value);
  const vSize = vals.length ? Math.min(...vals.map((it) => Math.max(9, Math.min(T.progressBig, Math.floor(vTextW * 72 / (String(it.value).length * 0.64)))))) : T.progressBig;
  items.forEach((it, i) => {
    const cx = L.margin + i * (cw + gap + chev);
    const isLast = highlightLast && i === n - 1;
    s.addShape("roundRect", { x: cx, y, w: cw, h, rectRadius: 0.08, fill: { color: C.lightBg }, line: isLast ? { color: C.slate300, width: 1 } : { type: "none" } });
    // Label → title → value → note → body all flow in ONE frame, so any of them wrapping to an
    // extra line just pushes the rest down instead of overlapping. Value keeps the uniform size.
    const runs = [];
    if (it.label) runs.push({ text: String(it.label).toUpperCase(), options: { fontFace: F.head, bold: true, fontSize: T.small, color: C.muted, charSpacing: 1, breakLine: true, paraSpaceAfter: 3 } });
    runs.push({ text: it.title, options: { fontFace: F.head, bold: true, fontSize: T.cardBody, color: C.text, breakLine: true, paraSpaceAfter: (it.value || it.note || it.body) ? 4 : 0 } });
    if (it.value) runs.push({ text: it.value, options: { fontFace: F.head, bold: true, fontSize: vSize, color: C.blue, breakLine: true, paraSpaceAfter: (it.note || it.body) ? 4 : 0 } });
    if (it.note) runs.push({ text: it.note, options: { fontFace: F.body, italic: true, fontSize: T.small, color: C.muted, breakLine: true, paraSpaceAfter: it.body ? 3 : 0 } });
    if (it.body) runs.push({ text: it.body, options: { fontFace: F.body, fontSize: T.small, color: C.text } });
    s.addText(runs, { x: cx + px, y: y + 0.22, w: cw - px * 2, h: h - 0.4, valign: "top", lineSpacingMultiple: 1.05 });
    if (i < n - 1) s.addText("›", { x: cx + cw, y, w: gap + chev, h, align: "center", valign: "middle", fontFace: F.head, fontSize: 16, bold: true, color: C.slate400, margin: 0 });
  });
}

// Bottom "open questions / what to confirm" banner (soft pink, red label). items: [{ q, a }]
function confirmBanner(s, { y = 3.5, h = 1.5, label = "What we need to confirm together", items }) {
  s.addShape("roundRect", { x: L.margin, y, w: L.contentW, h, rectRadius: 0.06, fill: { color: C.lightBg }, line: { type: "none" } });
  s.addText(String(label).toUpperCase(), { x: L.margin + 0.35, y: y + 0.16, w: L.contentW - 0.7, h: 0.26, fontFace: F.head, fontSize: T.kicker, bold: true, color: C.text, charSpacing: 1 });
  const n = items.length, colW = (L.contentW - 0.7 - (n - 1) * 0.35) / n;
  items.forEach((it, i) => {
    const cx = L.margin + 0.35 + i * (colW + 0.35);
    // Question + answer in ONE frame so a 2-line question can't overlap the answer.
    const runs = [{ text: it.q, options: { fontFace: F.head, bold: true, fontSize: T.cardBody, color: C.text, breakLine: true, paraSpaceAfter: it.a ? 4 : 0 } }];
    if (it.a) runs.push({ text: it.a, options: { fontFace: F.body, fontSize: T.small, color: C.muted } });
    s.addText(runs, { x: cx, y: y + 0.5, w: colW, h: h - 0.62, valign: "top", lineSpacingMultiple: 1.05 });
  });
}

// Grouped feature/benefit grid: a left title, then rows — each row a light band with a green
// check + group label on the left and N white sub-cards. Mark one row `highlight:true` for a
// red dotted outline. groups: [{ label, items:[strings], highlight? }]. title: [[plain,color],...]
function groupedRows(s, { title, groups, x = L.margin, y = 0.85, bottom = 5.15, titleW = 2.45, gap = 0.16 }) {
  if (title && title.length) {
    s.addText(title.map(([t, c]) => ({ text: t, options: { color: c } })),
      { x, y: y + (bottom - y) / 2 - 1.0, w: titleW, h: 2.0, fontFace: F.head, fontSize: T.title, bold: true, valign: "middle", lineSpacingMultiple: 1.04 });
  }
  const gx = x + titleW + 0.2, gw = L.W - L.margin - gx, labW = 1.7;
  const n = groups.length, rh = (bottom - y - (n - 1) * gap) / n;
  groups.forEach((g, i) => {
    const gy = y + i * (rh + gap);
    s.addShape("roundRect", { x: gx, y: gy, w: gw, h: rh, rectRadius: 0.08, fill: { color: C.lightBg }, line: g.highlight ? { color: C.red, dashType: "dash", width: 1.5 } : { type: "none" } });
    // Check badge at a fixed spot; label flows below it in its own frame (no line-count estimate —
    // a 1- or 2-line label just fills more of the space below the badge, never overlapping anything).
    iconCircle(s, gx + 0.55, gy + 0.44, 0.34, { bg: C.lgreen, glyph: "✓", glyphColor: C.green });
    s.addText(g.label, { x: gx + 0.28, y: gy + 0.66, w: labW - 0.32, h: rh - 0.76, fontFace: F.head, fontSize: T.cardTitle, bold: true, color: C.text, valign: "top", lineSpacingMultiple: 1.05 });
    const items = g.items || [], m = items.length;
    if (m) {
      const sxx = gx + labW, sgap = 0.12, avail = gw - labW - 0.15, cw = (avail - sgap * (m - 1)) / m, ch = rh - 0.3, cy2 = gy + 0.15;
      items.forEach((it, j) => {
        const cxx = sxx + j * (cw + sgap);
        s.addShape("roundRect", { x: cxx, y: cy2, w: cw, h: ch, rectRadius: 0.06, fill: { color: C.white }, line: { type: "none" } });
        s.addText(String(it), { x: cxx + 0.12, y: cy2, w: cw - 0.24, h: ch, align: "center", valign: "middle", fontFace: F.body, fontSize: T.cardBody, color: C.muted, lineSpacingMultiple: 1.05 });
      });
    }
  });
}

// Capability / feature matrix: grid of cards. `on` cards get a light tint + star; others plain
// with a border. items: [{ label, on }]. Add the title with slideHeader first. Legend bottom-right.
function capabilityGrid(s, { items, x = L.margin, y = 1.7, w = L.contentW, cols = 4, gap = 0.2, bottom = 5.0, onLabel = "Have today", offLabel = "Can unleash" }) {
  const n = items.length, rows = Math.ceil(n / cols);
  const cw = (w - gap * (cols - 1)) / cols, ch = Math.min(1.25, (bottom - y - (rows - 1) * gap) / rows);
  items.forEach((it, i) => {
    const r = Math.floor(i / cols), c = i % cols, cx = x + c * (cw + gap), cy = y + r * (ch + gap), on = !!it.on;
    s.addShape("roundRect", { x: cx, y: cy, w: cw, h: ch, rectRadius: 0.08, fill: { color: on ? C.lightBg : C.white }, line: on ? { type: "none" } : { color: C.slate200, width: 1 } });
    if (on) s.addText("★", { x: cx, y: cy + 0.16, w: cw, h: 0.3, align: "center", fontFace: F.head, fontSize: 13, color: C.muted, margin: 0 });
    s.addText(it.label, { x: cx + 0.15, y: cy + (on ? 0.5 : 0.15), w: cw - 0.3, h: ch - (on ? 0.6 : 0.3), align: "center", valign: "middle", fontFace: F.head, fontSize: T.cardTitle, bold: true, color: C.text, lineSpacingMultiple: 1.05 });
  });
  const ly = y + rows * (ch + gap) + 0.02;
  [[onLabel, C.lightBg, C.text, null], [offLabel, C.white, C.muted, C.slate200]].forEach(([lab, bg, col, brd], k) => {
    const bx = L.W - L.margin - (2 - k) * 1.55 + (k * 0.05);
    s.addShape("roundRect", { x: bx, y: ly, w: 1.45, h: 0.3, rectRadius: 0.15, fill: { color: bg }, line: brd ? { color: brd, width: 1 } : { type: "none" } });
    s.addText(lab, { x: bx, y: ly, w: 1.45, h: 0.3, align: "center", valign: "middle", fontFace: F.body, fontSize: T.small, color: col, margin: 0 });
  });
}

// Place a user-provided image (path or dataURL) in a region, or a labeled placeholder if none.
// Pass this the region from split() for a text + image slide.
function imageBox(s, { x, y, w, h, src, label = "Add image" }) {
  if (src) {
    s.addImage({ path: src, x, y, w, h, sizing: { type: "cover", w, h } });
  } else {
    card(s, x, y, w, h);
    s.addShape("ellipse", { x: x + w / 2 - 0.38, y: y + h / 2 - 0.5, w: 0.76, h: 0.76, fill: { color: C.white }, line: { type: "none" } });
    s.addText(label, { x, y: y + h / 2 + 0.34, w, h: 0.3, align: "center", fontFace: F.body, fontSize: T.small, italic: true, color: C.muted });
  }
}

// Scope / pricing "package" card (the "POS Implementation & Onboarding" look): a big card with a
// title + price chip + dashed divider, then category groups laid out in balanced columns. Each
// group = an icon, a CAPS label with an hours pill, and a green-check item list.
//   title: [[plain,color],[keyword,C.red], ...] runs (wraps to 2 lines fine)
//   price: "€35,000", currency: "EUR"
//   groups: [{ icon: dataURL, iconBg, label, hours, items:[strings] }]
// Robustness: groups are balanced across `cols` by content weight, and each group's item list is
// drawn in a FIXED region sized to its (estimated) content with shrink-to-fit — so mixed 1–2 line
// items can never overlap the next group or leave uneven gaps. No hand-tuning per slide.
function packageCard(s, { title, price, currency, groups, cols = 2, accent = C.blue, fill = C.lightBg }) {
  const CX = 0.35, CY = 0.3, CW = L.W - 0.7, CH = L.H - 0.6;
  card(s, CX, CY, CW, CH, fill);
  // title (top-left, wraps)
  const tRuns = (title || []).map(([t, c], i) => ({ text: t, options: { color: c, breakLine: i < title.length - 1 } }));
  s.addText(tRuns, { x: CX + 0.35, y: CY + 0.22, w: 5.6, h: 1.05, fontFace: F.head, fontSize: 30, bold: true, valign: "top", lineSpacingMultiple: 1.0, fit: "shrink" });
  // price chip (top-right)
  if (price) {
    const chW = 2.5, chH = 0.9, chX = CX + CW - 0.35 - chW, chY = CY + 0.3;
    s.addShape("roundRect", { x: chX, y: chY, w: chW, h: chH, rectRadius: 0.1, fill: { color: C.white }, line: { color: C.slate200, width: 1 } });
    s.addShape("roundRect", { x: chX + 0.22, y: chY + chH / 2 - 0.26, w: 0.52, h: 0.52, rectRadius: 0.1, fill: { color: C.lblue }, line: { type: "none" } });
    s.addText([{ text: price, options: { color: C.text, bold: true, fontSize: 22 } }, { text: currency ? " " + currency : "", options: { color: C.muted, bold: true, fontSize: 11 } }],
      { x: chX + 0.88, y: chY, w: chW - 0.98, h: chH, valign: "middle", fontFace: F.head, fit: "shrink" });
  }
  // dashed divider — placed clear below the (up-to-2-line) title
  const divY = CY + 1.4;
  s.addShape("line", { x: CX + 0.35, y: divY, w: CW - 0.7, h: 0, line: { color: C.slate300, width: 1, dashType: "dash" } });
  // ---- balance groups across columns by estimated content ----
  const innerX = CX + 0.35, innerW = CW - 0.7, colGap = 0.4;
  const colW = (innerW - colGap * (cols - 1)) / cols;
  const estLn = (t, w, pt) => Math.max(1, Math.ceil(String(t).length / Math.max(1, Math.floor(w * 72 / (pt * 0.62)))));
  const nomFont = T.body;
  const glines = (g, f) => (g.items || []).reduce((a, it) => a + estLn(it, colW - 0.5, f), 0);
  const bins = Array.from({ length: cols }, () => ({ groups: [], h: 0 }));
  groups.forEach((g) => { const b = bins.reduce((m, x) => (x.h < m.h ? x : m)); b.groups.push(g); b.h += 2 + glines(g, nomFont); });
  const topY = divY + 0.28, botY = CY + CH - 0.38, headH = 0.44, groupGap = 0.2, availH = botY - topY;
  const lineIn = (f) => f * 1.28 / 72;
  // ONE item font size for the WHOLE card: start at nominal, shrink uniformly only if the fullest
  // column would overflow. Both columns then use the same size; the lighter one just ends earlier.
  let font = nomFont;
  bins.forEach((b) => {
    const G = b.groups.length; if (!G) return;
    const need = G * headH + (G - 1) * groupGap + b.groups.reduce((a, g) => a + glines(g, nomFont) * lineIn(nomFont), 0);
    if (need > availH) font = Math.min(font, nomFont * availH / need);
  });
  font = Math.max(9, +font.toFixed(1));
  bins.forEach((b, ci) => {
    const x = innerX + ci * (colW + colGap);
    let y = topY;
    b.groups.forEach((g) => {
      if (g.icon) iconCircle(s, x + 0.28, y + 0.25, 0.5, { icon: g.icon, bg: g.iconBg || C.lightBg });
      const hx = g.icon ? x + 0.66 : x;
      s.addText([{ text: g.label.toUpperCase(), options: { color: C.text, bold: true } }, { text: g.hours ? "   —   " + g.hours : "", options: { color: accent, bold: true } }],
        { x: hx, y: y + 0.04, w: colW - (hx - x), h: 0.42, fontFace: F.head, fontSize: T.cardTitle, valign: "middle", fit: "shrink" });
      y += headH;
      const region = Math.max(0.3, glines(g, font) * lineIn(font) + 0.06);
      const runs = [];
      (g.items || []).forEach((it) => { runs.push({ text: "✓  ", options: { color: C.green, bold: true, fontFace: F.head } }); runs.push({ text: it, options: { color: C.text, fontFace: F.body, breakLine: true, paraSpaceAfter: 2 } }); });
      s.addText(runs, { x: x + 0.22, y, w: colW - 0.28, h: region, fontFace: F.body, fontSize: font, valign: "top", lineSpacingMultiple: 1.1, fit: "shrink" });
      y += region + groupGap;
    });
  });
}

function columnChartOptions(extra = {}) {
  return Object.assign({
    barDir: "col", showLegend: false, showTitle: false,
    showValue: true, dataLabelPosition: "outEnd", dataLabelFontFace: F.body, dataLabelFontSize: T.small, dataLabelColor: C.muted,
    catAxisLabelFontFace: F.body, catAxisLabelFontSize: T.small, catAxisLabelColor: C.muted, catGridLine: { style: "none" },
    valAxisLabelFontFace: F.body, valAxisLabelFontSize: T.small, valAxisLabelColor: C.muted,
    valGridLine: { color: C.grid, size: 1 }, valAxisLineShow: false, barGapWidthPct: 50,
  }, extra);
}

const ChartType = pptxgen.ChartType || (new pptxgen()).ChartType;

module.exports = {
  pptxgen, C, F, L, newDeck,
  eyebrow, contentTitle, titleRuns, subtitle, slideHeader, footer, card,
  titleSlide, sectionSlide, closingSlide, styledTable, columnChartOptions,
  bulletList, numberedList, iconCards, statCards, metricCard, columns,
  listWithImage, timeline, quote, processSteps, comparisonCards,
  iconCircle, checklist, panel, split, icons, iconRows,
  pricingTable, statRail, summaryBanner, progressionCards, confirmBanner,
  groupedRows, capabilityGrid, imageBox, packageCard,
  GAP, grid, band, pill, hbar,
  ChartType,
};
