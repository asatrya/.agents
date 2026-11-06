---
name: 2025-newstore-slides
description: >-
  Build, reformat, or extend presentations in NewStore's brand format (16:9 PowerPoint,
  Poppins/Figtree, navy + red, light-gray cards, genuine editable tables). Use this
  ANY time someone wants a NewStore deck, slides, presentation, pitch, pricing slides,
  QBR, exec/board deck, or sales deck — whether they paste raw content, attach a deck to
  reformat, or ask to add a few slides to a presentation they already have. Trigger on
  "NewStore deck/slides/presentation", "reformat this into our format", "add slides to
  this deck", "make this on-brand", "pricing slides", or when a .pptx/Google Slides is
  shared with NewStore branding in mind. The brand formatting is built in — the user does not
  need to attach the template. The default audience is senior (CEO, COO, sales, clients), so
  quality and consistency are priorities.
---

# NewStore Slides

Produce decks that match the NewStore brand — colors, fonts, title treatment, tables, cards, spacing,
margins. The brand system is encoded in `scripts/newstore.js` (tokens in `C`/`F`, a set of layout
builders) and `references/brand.md`, so you never approximate and the user need not attach a template.
Skim `references/brand.md` once at the start of a build.

## Get oriented (quick — at most one question)

- **Scenario** — reformat a deck / build a new one / add to an existing one (see below). Infer it.
- **Voice** — resolve with the rule below.
- **If they point you at an example** — a link, an attached deck, or "make it like these slides" —
  actually look at it before building (see *Look at the example first*). Don't build from memory or
  reach for a familiar layout.

### Voice rule

- Given **written content** (a deck, doc, or copy) → follow its language and tone. Offer to reproduce
  word-for-word or lightly tighten.
- Given **notes / raw info** only → write in NewStore's voice, consultant style: short titles with one
  red keyword, a one-line takeaway per slide, no filler.
- **Extending an existing deck** → match the language already in that deck (terminology,
  capitalization, rhythm, formality) so new slides are indistinguishable from the originals.

## Look at the example first

When the user gives or references an example — a Google Slides link, a `.pptx`, or "like the other
slides / the examples I sent" — **open it and study it before you build.** This is the step that keeps
output from collapsing into the same layout every time.

1. Load the Claude for Chrome tools (via ToolSearch), open a tab, navigate to the deck.
2. Look at the real slides: which layouts they use, how much text per slide, the spacing and density,
   and — importantly — how the layout **varies** slide to slide. Click a text box to read exact font
   sizes if you need them.
3. Build to match what you actually saw: its layout variety and density, not this skill's habits.

If Chrome isn't connected, ask them to connect it or to share screenshots — don't quietly fall back to
a default layout. The same Chrome step tunes against the NewStore master/pricing templates when output
looks off (alignment, exact colors, icon style):
- Master: `https://docs.google.com/presentation/d/18kmQ6vnvFPQaXxHZTq9c6NMo0wqxFqeYrT_-09T4_tM`
- FY26 Pricing: `https://docs.google.com/presentation/d/17yEnIEJX0mGdxxTmvvT3vQeXzhCLIKWl77uwKGy3ZaM`

Templates and internal decks are NewStore Google Slides — the person must be signed into Chrome with
access.

## Scenarios

- **A) Reformat** — they attach a deck and want it on-brand. Read every slide (Chrome if possible, else
  `markitdown`/render), capture all content exactly (figures, names, claims), then rebuild each slide
  with the layout that fits it. Convert the old styling into NewStore tokens; don't carry the old look.
- **B) Build new** — they paste content or notes. Draft a short outline (slide → layout) and confirm it,
  then build.
- **C) Add to an existing deck** — match the deck they give you, not this skill's defaults. Open and read
  it first; follow its palette, fonts, footer, page-numbering, and language. Treat the deck as the
  reference for layout and voice, and their new input as the source for new content. Only if the new
  input directly contradicts a figure/date/term in the deck, flag that one item and ask which is current
  — otherwise just build. If the base is a real `.pptx`, prefer editing it directly (duplicate the
  closest slide → edit its XML) so theme, master, and fonts carry over (see the pptx skill).

## Choosing layouts — fit the content, and vary

There is **no default layout.** Pick the one that fits what the slide is actually saying, and change it
up across the deck:

- A few parallel points → `iconCards` / `columns`. A sequence or steps → `processSteps` or `timeline`.
  Numbers → `statCards` / `statRail` / `metricCard`. A comparison → `comparisonCards` or a table. A
  trend or share → a chart or `hbar`. A scope/price package → `packageCard`. A list of inclusions →
  `checklist`.
- **A checklist is one option among many, not the fallback.** If the last slide was a checklist, use
  something else. Two adjacent slides shouldn't share a layout, and a whole deck of green-check lists is
  the exact failure to avoid — it's what happens when layout isn't chosen deliberately.
- `references/brand.md` has a content → layout menu. If nothing fits, compose from the primitives
  (`grid` / `band` / `hbar` / `pill` / `split`) — the format is open.

## Builders (your menu — compose slides from these)

- **Header:** `slideHeader(s, plain, red, subtitle)` — title with a red keyword + optional supporting
  line; returns the y to start content. Use on every content slide.
- **Structure:** `titleSlide`, `sectionSlide`, `closingSlide`, `footer`.
- **Points:** `iconCards` (cards with a centered pictogram), `columns` (2–4 cards), `iconRows`
  (icon+text rows, great beside an image via `split()`), `checklist` (green-check grid),
  `processSteps` (numbered rows, optional timeframe pill).
- **Numbers / data:** `statCards`, `metricCard`, `statRail` (numbers beside a chart), `styledTable`,
  `pricingTable` (comparison/financial table), `columnChartOptions` + `addChart` (native charts),
  `hbar` (data bars, stacked comparison bars, gantt spans).
- **Narrative:** `timeline`, `comparisonCards`, `quote`, `summaryBanner` / `confirmBanner` (bottom
  takeaway / open-questions strip).
- **Rich grids:** `packageCard` (scope/price package — title, price chip, category groups balanced
  across two columns), `groupedRows` (benefit bands), `capabilityGrid` (what's-on vs. can-turn-on),
  `imageBox` (image or placeholder well).
- **Helpers / primitives:** `icons(names)` (async — real pictograms; call once, pass the data URLs to
  the card builders), `iconCircle`, `panel`, `split` (non-overlapping left/right regions), `grid`,
  `band`, `pill`, `GAP` (spacing scale).
- **Plain `bulletList` / `numberedList`** only for genuinely long or nested lists.

## Principles (brand is fixed; everything else is flexible)

- **Brand is fixed.** Colors come from `C`, fonts from `F` (Poppins headings, Figtree body). Red is for
  the title keyword and the occasional key figure only — never on cards, borders, or table columns.
  Navy backgrounds only for cover / section / closing.
- **Real icons, consistent.** Use `NS.icons()` pictograms, one color and one size across the whole
  deck. Never letters or colored discs.
- **Fill the canvas, keep it aligned.** Content should reach the lower half; blocks line up to the 0.5"
  margins (or run full-bleed on purpose); spacing even, nothing lopsided or clipped. The builders
  already auto-fit text and auto-space — pass content and trust them; if something's off, fix the
  builder so every slide benefits, not the one slide.
- **Vary the layout** across the deck (see above) — this is a quality bar, not a rule to work around.
- **Render and look** at every slide before delivering.

## Build workflow

1. Skim `references/brand.md`. If there's an example, study it in Chrome first.
2. Outline slide → layout (varying the layouts); for a new/large deck, confirm the outline before building.
3. Write a `build.js` that `require("./scripts/newstore.js")` and composes the slides.
4. Render and self-QA — look at the JPGs yourself:
   ```bash
   bash scripts/render.sh build.js MyDeck.pptx
   ```
   (Builds, validates, scans for leftover placeholders, renders fresh timestamped JPGs.) Check every
   slide for overflow/clipping, overlaps, footer collisions, uneven gaps, tight margins, misalignment.
5. Deliver the `.pptx` with `present_files` and a short summary. Show **two representative slides** to
   confirm look/voice — not every slide, unless they ask.

Run scripts with `NODE_PATH=/usr/local/lib/node_modules_global/lib/node_modules` (render.sh sets this).
The `.pptx` is built at Google Slides' native size (10 × 5.625"), so it imports 1:1 — the team can
upload it to Drive and open with Google Slides.

## Minimal build example

Icons are async, so wrap the build in an `async` function and render the pictograms first.

```js
const NS = require("./scripts/newstore.js");

(async () => {
  const pres = NS.newDeck();                 // 10 x 5.625" — Google Slides native size
  const ic = await NS.icons(["smartphone", "shopping-cart", "message-circle", "package"]); // navy pictograms

  NS.titleSlide(pres, { plainTitle: "NewStore Overview and", redTitle: "Pricing",
    subtitle: "Prepared for [Prospect]", presenter: "[Presenter] · NewStore", date: "[Date]" });

  NS.sectionSlide(pres, { part: "Part One", plainTitle: "Why ", redTitle: "NewStore", page: 2 });

  let s = pres.addSlide();
  let cy = NS.slideHeader(s, "One platform for commerce and ", "payments", "You already run NewStore across every channel.");
  NS.iconRows(s, { y: cy, items: [
    { icon: ic["smartphone"], title: "Embedded", desc: "Native to the platform you already run." },
    { icon: ic["shopping-cart"], title: "Simplified checkout", desc: "For complex transactions." },
    { icon: ic["message-circle"], title: "Native clienteling", desc: "Remote selling built in." },
    { icon: ic["package"], title: "Omnichannel", desc: "Store fulfillment, BOPIS & BORIS." },
  ] });
  NS.footer(s, 3);

  s = pres.addSlide();
  cy = NS.slideHeader(s, "Optional ", "Add-Ons", "Priced separately, activated as you need them.");
  NS.styledTable(s, { x: 0.5, y: cy, w: 9.0, colW: [3.8, 2.7, 2.5],
    headers: ["Add-On", "Price", "Notes"], headerTint: NS.C.lpurple,
    rows: [["Clienteling", "$1,200/store/year", "In top 30 stores"],
           ["Advanced Reporting", "$25,000/year", "Custom dashboards"],
           ["Global Coverage", "$75,000/year", "Required if multi-region"]], emphasizeRow: 2 });
  NS.footer(s, 4);

  NS.closingSlide(pres, { subtitle: "Let's build unified commerce together.", contact: "[name]@newstore.com" });
  await pres.writeFile({ fileName: "MyDeck.pptx" });
})();
```

## Remind the user (once, at the right moment)

- **Chrome extension** — if they have a deck/example to match and it isn't connected, mention once that
  connecting Claude for Chrome lets you read their formatting accurately.
- **Placeholders** — at delivery, flag anything still unfilled (`~$XXXK`, `[DATE]`, `[PROSPECT]`,
  "Replace with image") and ask them to complete it.
- **Re-apply the NewStore theme** after they hand-edit in PowerPoint / Google Slides, so brand styles stay applied.

## Notes

- Genuine editable tables only — never shapes faked to look like a table.
- Preserve names, numbers, dates, and claims exactly; never invent figures.
- Keep confidentiality footer + page numbers if the source has them.
- Dependencies: `pptxgenjs` (global), the `pptx` skill's `soffice.py`/`validate.py`, `markitdown`,
  `pdftoppm`, `lucide-static` + `sharp` (for `NS.icons()`). `scripts/render.sh` locates/installs them.
- `references/brand.md` maps the NewStore icon library to lucide names.
