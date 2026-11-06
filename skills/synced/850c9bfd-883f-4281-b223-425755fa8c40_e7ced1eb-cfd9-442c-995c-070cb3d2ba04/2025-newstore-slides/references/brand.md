# NewStore brand system (baked in)

Source of truth: **NewStore Company Slidedeck 2025 Template** (the "Use of Colors" and
"Use of Fonts" guideline slides) and the **NewStore FY26 Pricing Slides** template.
These tokens are already encoded in `scripts/newstore.js` — this file is the human-readable
spec plus the layout catalog. When in doubt, match these values exactly rather than
approximating, and open the live templates in Chrome (see SKILL.md) for pixel reference.

Canonical template links (view in Chrome extension when available):
- Master template: https://docs.google.com/presentation/d/18kmQ6vnvFPQaXxHZTq9c6NMo0wqxFqeYrT_-09T4_tM
- Pricing template: https://docs.google.com/presentation/d/17yEnIEJX0mGdxxTmvvT3vQeXzhCLIKWl77uwKGy3ZaM

## Colors (hex)

Primary
- Highlight red `#EF1B53` — the NewStore accent. Use sparingly: one keyword in a title, a key number, a status. Never as a body-text color or as a stripe/bar.
- Dark navy `#1E293B` — dark backgrounds and dark cards (title panel, section dividers, one emphasis card per content slide at most). "Reserved for special cases requiring contrast. Use minimally."
- Primary text `#334155` — default for body copy.
- Secondary text `#64748B` — subtitles, captions, supporting text.
- Light gray `#F1F5F9` — the workhorse card / grouping background. Most content sits in these rounded cards.

Secondary (data & status): Blue `#0171B7`, Green `#3BB273`, Orange `#FFAE03`, Purple `#9B5DE5`, Red `#F03A47`.
Tertiary tints (table headers, soft fills): Light blue `#DBEAFE`, Light green `#CCEDE3`, Light orange `#FDDEC7`, Light purple `#E6D0F1`, Light red `#ECBFCA`.
Text-on-navy neutrals: `#CBD5E1`, `#E2E8F0`, `#94A3B8`.

## Fonts

- **Poppins (bold)** — headings, section titles, big numbers, any large standout text.
- **Figtree (normal)** — body text, descriptions, captions, table cells.
- The sandbox has Poppins; Figtree is aliased to Lato for QA previews only. The `.pptx`
  always writes "Figtree", which renders correctly on NewStore machines. Leave ~10% width
  slack on Figtree text and don't fully trust QA fit on it.

## Title treatment (the signature look)

- Content slides lead with a **title + optional subtitle** (`slideHeader`). This is the house
  style — do **not** put an "eyebrow/kicker" tag (AGENDA, OVERVIEW, NEXT STEPS) above the title.
  Kicker tags are a consultant style, not NewStore's; the template uses title + a supporting line.
- Title = Poppins bold, navy, with **one trailing/key word in red** — e.g. "Store-Based **Pricing**",
  "Simple **Bullet List**". Subtitle = Figtree, muted gray, one supporting sentence.
- No underlines or accent bars under titles — use whitespace.

## Canvas & spacing

- **Canvas = 10 × 5.625 in** — the Google Slides native 16:9 size. The team builds in Google
  Slides, so authoring at this size means the exported `.pptx` imports 1:1 (same page size as the
  company decks) and every point size matches the template exactly. `newDeck()` sets this.
- Equal left/right margins of **0.5"**; content width **9.0"**. Keep ≥0.4" from all edges.
- Generous whitespace. Group content into light-gray rounded cards (`rectRadius ≈ 0.08`).
- Title y ≈ 0.5; subtitle ≈ 1.28; content starts ≈ 1.9; footer ≈ 5.28.

### Type scale — one central knob (`T` in newstore.js)

Every font size lives in the `T` object at the top of `scripts/newstore.js`; builders reference
`T.*` and never hardcode a number. To resize the whole deck, change `T` — one place, nothing else.
The scale **matches the live NewStore deck** (title 28 / supporting line 14 / body-table 12) — a
readable exec scale. Keep the hierarchy right-way-up: title > subtitle > body; never let the
supporting line drop below the body size.

| Element | `T` key | Size | Used by |
|---|---|---|---|
| Content title | `T.title` | 28pt | `slideHeader`, `contentTitle`, `groupedRows` |
| Subtitle / supporting line | `T.subtitle` | 14pt | `slideHeader`, `subtitle`, display subtitles |
| Body / bullets / checklist | `T.body` | 12pt | `bulletList`, `numberedList`, `checklist`, `iconRows` text |
| Takeaway banner | `T.banner` | 13pt | `summaryBanner` |
| Card title | `T.cardTitle` | 13pt | `iconCards`, `columns`, `processSteps`, `capabilityGrid`, `groupedRows` label |
| Card body / description | `T.cardBody` | 11.5pt | card descriptions, `timeline`, `confirmBanner` Q |
| Small caps label | `T.kicker` | 10pt | `eyebrow`, section PART, `confirmBanner` label |
| Caption / note / legend | `T.small` | 9.5pt | notes, legends, deltas, chart labels |
| Table cell + header | `T.tableCell` | 12pt | `styledTable`, `pricingTable` (auto-shrinks with rows) |
| Big stat number (cap) | `T.statBig` … | 40 / 30 / 20 / 16 / 12 | `statCards` / `comparisonCards` / `metricCard` / `statRail` / `progressionCards` (auto-fit to one line) |
| Cover / section / closing | `T.cover` / `T.section` / `T.closing` | 30 / 34 / 42 | `titleSlide`, `sectionSlide`, `closingSlide` |
| Footer / page number | (literal) | 8pt | `footer` |

**Tables:** when a table is the slide's main content, span most of the content width (`w` ≈ 7–9,
not 3–4) with `size` 12 and `rowH` ≈ 0.5. The template's own tables use 7–8pt only because they sit
in narrow one-third cards; on a full slide that's far too small. `styledTable` defaults are generous.

**Sparse content:** a short list will leave whitespace at the bottom — that's on-brand (the
template's own list slides do too). Don't cram; if a slide feels bare, pair the list with an image
(`listWithImage`) or add a supporting subtitle rather than inflating the type.

## Icons

NewStore uses monochrome pictograms from its icon library (retail-specific + general), placed on
white or light-gray, recolored to primary/secondary colors. In this skill, `NS.icons(names)` renders
the closest open equivalents (lucide) as PNGs recolored to navy (default) or any brand color.

- **Treatment:** icon in a **light-gray circle on white** (`iconRows`), or **directly on a light-gray
  card, no circle** (`iconCards`). Color = navy (`#334155`/`#1E293B`) or muted grey by default; recolor
  to a brand color only for deliberate emphasis. Never a colored disc with initials.
- **Never invent letters.** If no pictogram fits (e.g., a company/entity name), omit the icon.

Common library → lucide names: mobile/POS `smartphone` · cart/checkout `shopping-cart` · chat/clienteling
`message-circle` · box/fulfillment `package` · inventory/layers `layers` · reporting/chart `bar-chart-3` ·
store `store` · runner/requests `footprints` or `zap` · bell/replenishment `bell` · star `star` · check
`check` / `check-circle` · rocket `rocket` · headset/support `headset` · expertise `brain` · shield/SLA
`shield-check` · list `list-checks` · calendar `calendar` · globe/region `globe` · lock/security `lock` ·
clock/time `clock` · users/team `users` · tag/pricing `tag` · shuffle/flow `shuffle` · search `search`.
(Any of lucide's 2,000+ names works; pick the closest match to the library icon.)

## Cards & tables

- **Cards**: light-gray `#F1F5F9` rounded rectangles. A single navy card per slide may be used
  to emphasize one figure. Inside cards: bold navy title, Figtree muted body, red or blue for key numbers.
- **Tables must be genuine editable tables** (`addTable`), never shapes/text boxes faked to look like one.
  Header row = a tertiary tint fill (`#DBEAFE`/`#FDDEC7`/`#E6D0F1`) with bold navy text; body rows white
  with thin `#E2E8F0` borders. Emphasize a key row with red bold text. `styledTable()` does this.
- Icon circles: solid brand color (blue/orange/purple/green) or tinted, ~0.7" diameter, white bold glyph/initials.

## Layout catalog → when to use each

Map incoming content to the closest layout; vary layouts across the deck (don't repeat one).

| Content you're given | Layout | Helper |
|---|---|---|
| Cover / opening | Navy panel left + image placeholder right | `titleSlide()` |
| Section break ("Part Two") | Full-navy divider, red PART label | `sectionSlide()` |
| Close / thank-you | Navy thank-you + contact | `closingSlide()` |
| Agenda / "what we'll cover" | Numbered full-width rows | `processSteps()` (omit `tag`) or `numberedList()` |
| Benefits / "what's included" (3–6 pts) | 2-col green-check grid — fills the slide | `checklist()` |
| 3–5 feature/benefit/capability points | Cards w/ colored icon circles | `iconCards()` |
| Steps / how-it-works / agenda | Full-width numbered cards | `processSteps()` |
| Long or nested list (only) | Dot/arrow bullets, bold lead-in | `bulletList()` / `numberedList()` |
| Team / people | Same card row, initials in circles (swap in photos later) | `iconCards()` |
| 2/3/4 parallel ideas or definitions | Equal column cards (green caps headers if defining terms) | `columns()` |
| A few big numbers / stats | Big Poppins numbers + labels | `statCards()` |
| KPI dashboard / metrics with deltas | Colored-header KPI cards (green/red/orange) | `metricCard()` |
| 2 options / before-after / pros-cons | Side-by-side cards; recommended one navy | `comparisonCards()` |
| Pricing (platform/modules/add-ons) | Cards w/ icon circles + **styledTable** for line items | `iconCards()`/`card()` + `styledTable()` |
| Any real table (line items, matrix, terms) | **Genuine editable table**, tinted header, emphasize key row | `styledTable()` |
| Price comparison / financial table (options, fees, year-by-year) | Navy-header table, recommended column, zebra, bold total row, green savings/credits | `pricingTable()` |
| Data + takeaways (chart + 3 headline numbers) | Chart in a grey `panel()` on the left, stacked stat cards on the right — get the two regions from `split()` so they never overlap | `split()` + `panel()` + chart + `statRail()` |
| Offer / commercial evolution over time | Row of labeled value cards with chevrons; navy summary figure below | `progressionCards()` + `summaryBanner()` |
| Open questions / what to confirm | Grey footer strip with 2–3 bold Q + muted A | `confirmBanner()` |
| Time-series / trend | Native column chart, highlight final/peak bar in red | `columnChartOptions()` + `addChart` |
| Scenario comparison (low/base/high) | Native column chart, per-bar colors + considerations card | `columnChartOptions()` + `bulletList()` |
| Milestones / roadmap / contract timeline | Vertical dots + a short left intro paragraph to balance | `timeline()` (+ intro text) |
| Next steps w/ dates | Rows: red circle #, title, desc, white timeframe pill | `processSteps()` |
| Big quote / customer proof / safe-harbor | Centered pull-quote | `quote()` |
| Grouped benefits (2–3 themes, each with 2–4 supporting points) | Left title + stacked bands; ✓ + theme label and white sub-cards; one band can be red-dotted highlighted | `groupedRows()` |
| What's live vs. what you can turn on (feature checklist / capability map) | Grid of feature cards — active ones tinted w/ ★, the rest white/bordered, with a legend | `capabilityGrid()` |
| Text + supporting image (points beside a photo) | Icon rows on one half, image well on the other, split by `split()` | `iconRows()` + `imageBox()` |
| Ranked amounts / opportunity by segment (bars) | Tinted rows, each a proportional horizontal bar + big value | `band()` + `hbar()` |
| Comparison table with in-cell bars (option A vs B by row) | Table rows with a colored `hbar` in each cell + % label; navy total row | `band()` + `hbar()` |
| Segmented / stacked share bar (A + B vs a whole) | One track, multiple colored segments with inline labels | `hbar({segments:[…]})` |
| Timeline / gantt (who runs when over months) | Swimlane `band`s + month gridlines + offset `hbar` spans | `band()` + `hbar({start,frac})` |
| Status / owner tags (IN MOTION, +11.3%, names) | Rounded chips in brand colors | `pill()` |
| Any N-up layout that must align to the margins | Equal columns with a consistent gutter | `grid(n)` |
| Scope / pricing package (title + price + categories with hours & checklists) | Full card, price chip, dashed divider, groups balanced across 2 columns with uniform item text | `packageCard()` |

Available but used sparingly: `listWithImage()` (list + image placeholder) — only when you genuinely
have an image to drop in; a bare placeholder looks unfinished, so prefer the layouts above otherwise.

If content matches a master-template slide not covered by a helper (e.g. device mockups),
open the master template in Chrome, find that slide, and mirror its structure using `card()`
plus `addText`/`addImage`/`addTable`/`addChart` in these exact tokens.
