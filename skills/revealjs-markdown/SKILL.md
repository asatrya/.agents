---
name: revealjs-markdown
description: Create a single self-contained reveal.js HTML deck from markdown using the revealjs skill plus house conventions. Themes: Amiri Teal, Naskhi Slate, Diwan Burgundy, Mishkah Indigo. Ask which theme to use if the user does not name one. Use when the user asks for revealjs-markdown, invokes /revealjs-markdown, supplies markdown as slide source, or wants a reveal.js presentation with these layout conventions.
---

# Reveal.js Markdown

Wrapper around the `revealjs` skill. Follow `revealjs` fully, then apply the conventions in this skill. Do not invent a parallel HTML/CSS stack.

## Prerequisite

1. Locate and **read** the sibling skill `../revealjs/SKILL.md` (or search skills directories for `revealjs/SKILL.md`).
2. Follow its workflow: design approach, scaffold via `create-presentation.js`, CSS theming, incremental HTML fill, overflow check, screenshot review of every slide, browser-edit suggestion.
3. Then overlay the conventions below. If this skill and `revealjs` conflict, **this skill wins** for structure, eyebrow, page numbers, content fidelity, **single-file output**, **visual identity**, and the **verification loop**. Everything else stays with `revealjs`.

**Do not pick a reveal.js color palette.** Choose one of the four house themes (palette + type only). Layout stays [references/theme.css](references/theme.css). Palettes: [references/themes.md](references/themes.md).

## Theme choice

Resolve the theme **before scaffolding**. If the prompt already names one of these (or a clear synonym), use it and do not re-ask:

1. **Amiri Teal** — Amiri / DM Sans · cream, teal, gold — default house look
2. **Naskhi Slate** — Cormorant Garamond / Outfit · cool paper, slate, copper
3. **Diwan Burgundy** — Fraunces / Nunito Sans · warm paper, wine, saffron
4. **Mishkah Indigo** — Literata / Source Sans 3 · ivory, indigo, brass

If the user did **not** name a theme, **stop and ask**. List all four options with the one-line hints above. Use AskQuestion when that tool is available; otherwise ask in the conversation and wait. Do not start the deck until they answer.

Only self-select when they clearly delegate (“you decide”, “don’t ask”) **or** the run cannot ask follow-ups. Then use **Amiri Teal** and state that assumption.

Inline `references/themes/<id>.css` first, then `references/theme.css`. IDs: `amiri-teal`, `naskhi-slate`, `diwan-burgundy`, `mishkah-indigo`.

## Custom conventions

* jika dalam source konten ditentukan section, maka dibuat slide section divider tersendiri untuk setiap section. eyebrow pada slide section divider merupakan numberin (contoh: section 1,2,... / bagian 1,2,dst)
* Seluruh isi, kutipan, sumber per bagian, metadata, dan referensi dari source konten dipertahankan.
* Eyebrow berfungsi sebagai breadcrumb navigasi: section, tema/topik
* halaman slide (contoh: 12/23) dipindahkan semuanya ke kanan bawah
* slide ke-2 adalah outline atau alur pembahasan
* jika source konten adalah 1 halaman markdown, maka gunakan organisasi heading untuk menentukan organisasi section dan title pada slides. jika lebih dari 1 markdown files, gunakan nama files sebagai section dan organisasi heading di dalam setiap file untuk menentukan organisasi title slides.
* setiap slide yg bukan slide divider, sebisa mungkin tambahkan subtitle
* only will create 1 self-contained html file without css or other referenced file
* Gunakan format 7 / 17 atau 7/17 dengan tipografi yang bersih dan warna muted. Letakkan nomor slide di kanan bawah dengan jarak aman dari tepi, progress bar, dan elemen navigasi.
* Jangan sampai nomor slide bertabrakan dengan tombol panah navigasi Reveal.js. Pastikan nomor slide tidak memiliki garis bawah, efek aneh, atau tampilan seperti link.
* Terapkan style nomor slide secara global pada seluruh deck. tombol navigasi tetap di kanan bawah tapi tidak overlap dengan nomor slide

## Deck sequence

Default horizontal order:

1. **Title** — cover only. No section breadcrumb.
2. **Outline / alur pembahasan** — always slide 2. Map every upcoming section (or topic block if the source has no sections) in narrative order.
3. **Body** — if the source defines sections, insert a **section divider** immediately before that section’s content slides. Repeat for each section.
4. **Closing** — references, metadata, and any leftover sources that belong to the whole deck.

`--structure` always starts with `1,1` (title, outline). Insert `d` before each section’s content slides. Example with three sections: `1,1,d,3,d,4,d,2,1`.

If the source has **no** sections, skip dividers. Slide 2 still remains the outline.

Match numbering language to the source: `Section 1`, `Section 2` for English; `Bagian 1`, `Bagian 2` for Indonesian. Do not mix labels in one deck.

For markdown sources, derive sections and slide titles as in **Markdown source mapping** below. Do not invent a parallel outline.

## Markdown source mapping

Count distinct `.md` files in the source (not heading count). Front matter is metadata — preserve it; do not treat YAML keys as headings.

### One markdown file

Use the heading tree for both sections and slide titles.

1. **Deck title** — first H1 if it is the document title (the only H1, or H1 before any sibling headings). Else use the filename, humanized.
2. **Sections** — the highest heading level that groups the body after the title.
   - One H1 + several H2 → H2 = sections, H3 = slide titles
   - Several H1 → H1 = sections, H2 = slide titles
   - Title plus only one heading level beneath it → those headings are slide titles; skip section dividers unless the headings are clearly chapter/section labels
3. **Slide titles** — the heading level immediately under the section (or under the title if there are no sections). Use the heading text as the slide `h2`.
4. Deeper headings stay **on the same slide** as subheads. Split only on overflow, keeping the same slide title and eyebrow.

### Several markdown files

1. **Order** — the order the user gave, else numeric prefix then alphabetical (`01-…`, `02-…`).
2. **Each file = one section.** Divider `h1` = humanized filename: strip extension and a leading `NN-` / `NN_` prefix; replace `-` / `_` with spaces. If the file’s first heading is a single top-level title that names the same topic, prefer that heading text as the section title (still one section per file).
3. **Slide titles** — heading organization **inside that file** after the optional file-title heading. Next level down = slide titles; deeper = in-slide subheads, same as the single-file rule.

Do not promote inner headings into extra sections when multiple files are present. File names own the section layer.

## Section dividers

Use `class="section-divider"` and `data-state="divider"` (not `is-section-divider`). One divider per source section. Do not fold the divider into the first content slide.

```html
<section id="divider-1" class="section-divider" data-state="divider">
  <p class="eyebrow">Bagian 1</p>
  <h1>Judul Section</h1>
  <p class="sub">Satu baris kerangka section</p>
</section>
```

Divider eyebrow is **numbering only** (`BAGIAN 2` / `SECTION 2`), uppercase. Title of the section goes in `h1`, not in the eyebrow. Optional `.sub` under the title. No content cards on divider slides.

## Subtitles

Every slide that is **not** a section divider gets a subtitle whenever the source supports one. Applies to title (`.deck-meta` or `.sub`), outline, content, and closing.

Place `<p class="subtitle">` immediately after the content-slide `h2`. On dividers use `<p class="sub">`. One line. Do not repeat the heading or the eyebrow.

Pick the subtitle from the source, in order:

1. Explicit dek under the heading (italic line, blockquote lead-in, or a short first paragraph that frames the section)
2. First sentence of that heading’s body, shortened if needed
3. Parent heading or section title used as a framing line — only if it does not duplicate the eyebrow `tema/topik`

Skip the subtitle only when that heading has no body and no usable framing line. Do not invent a claim that is not in the source.

## Eyebrow (breadcrumb)

Every slide except a bare closing/review (if it has no kicker) has `<p class="eyebrow">` as the first child of `<section>`.

| Slide | Eyebrow |
|-------|---------|
| Title | series/kicker (uppercase), e.g. the source series name — omit only if the source has none |
| Outline (slide 2) | `PETA PEMBAHASAN` / `OUTLINE` (match deck language) |
| Section divider | numbering only (`BAGIAN N` / `SECTION N`) |
| Content in a section | `BAGIAN N / TEMA` (slash, spaces, uppercase) |
| Content with no sections | current tema/topik only, uppercase |
| Closing / references | `REFERENSI` / `REFERENCES` (or the source’s own label) |

`tema/topik` is the current section title or the slide’s topic — short, same wording as the source heading when possible.

Do not put page numbers in the eyebrow. Do not invent a third breadcrumb level.

HTML pattern:

```html
<section id="slide-4">
  <p class="eyebrow">Bagian 1 / Nama tema</p>
  <h2>Judul slide</h2>
  <p class="subtitle">Kalimat kerangka dari sumber</p>
  <div class="content">
    <div class="cards two">
      <div><h3>Label</h3><p>Isi.</p></div>
      <div><h3>Label</h3><p>Isi.</p></div>
    </div>
  </div>
  <p class="source"><b>Sumber:</b> …</p>
</section>
```

## Content fidelity

Preserve from the source: body text, quotes, per-section sources, metadata, and references. Shorten only flexible wording. Never drop a citation, quote, source list, or metadata field to make a layout fit.

If a slide overflows: **split** onto the next slide (same eyebrow/section). Put per-section sources on a slide at the end of that section when they do not fit beside the argument. Put deck-level references and metadata on the closing slide(s).

Quotes stay as `<blockquote>` (dark teal, gold rule) with `<cite>` when the source names an author. Quran/Arabic lines use `<p class="quran-arabic" lang="ar" dir="rtl">`. Sources and metadata stay visible as `<p class="source">` (alias `.footnote`) — not only in speaker notes.

## Page numbers (bottom right)

Do **not** draw `7 / 17` inside slide copy, eyebrows, or footnotes. Inject one `<p class="slide-page">` per horizontal `<section>` (see script in [examples.md](examples.md)). Set `slideNumber: false`.

Format: zero-padded `01 / 24` (or `7 / 17` if totals are under 10 and padding looks odd — prefer zero-pad). Typography comes from [references/theme.css](references/theme.css): DM Sans, 10pt, weight 700, letter-spacing 0.08em, muted on cream slides, `--gold-muted` on dividers. Not a link: no underline, hover, outline, or `pointer-events`.

**Layout (both stay bottom-right, no overlap):**

| Chrome | Position |
|--------|----------|
| Progress bar | full width, `bottom: 0`, height 3px, gold fill |
| Navigation arrows | `right: 14px; bottom: 16px`, above the progress bar |
| Slide number | same bottom band, **to the left of** the arrows (`right: 120px; bottom: 17px`) |

Keep `.source` / `.footnote` at the **bottom left** (`right: 200px` so they miss the number and arrows).

After scaffolding:

```javascript
controls: true,
controlsLayout: 'bottom-right',
progress: true,
slideNumber: false,
transition: 'fade',
```

## Visual identity

Do not invent a new palette. After **Theme choice**, inline the chosen `references/themes/<id>.css` then [references/theme.css](references/theme.css). Do not use `revealjs` base-styles.css. Themes differ only in color tokens and Latin fonts; components stay the same. Catalog: [references/themes.md](references/themes.md).

**Components (use these classes, not ad-hoc boxes):**

- Peer facts: `.cards.two` / `.three` / `.four` (stretch equal height in the row)
- Outline: `.outline-flow` with `.outline-number` `01`… and arrow between columns
- Sequence/chip list: `.faces` or `.ten`
- Takeaway: `.takeaway`
- Quote slide: `.content.quote`
- Assumption vs correction: `.assumption-card` / `.correction-card`
- Closing bibliography: `.refs` + `.references`

Title slide: `class="section-divider title" data-state="divider"`, optional series `.eyebrow`, `h1`, `.deck-meta`.

## Single-file output

The only deliverable is **one** `.html` file. Do not leave `styles.css`, JS, images, fonts, or any other sibling file that the HTML references.

1. Scaffold with `create-presentation.js` as `revealjs` requires.
2. **Do not copy** `../revealjs/references/base-styles.css`. Inline the chosen `references/themes/<id>.css` (fonts + `:root` palette) then the full [references/theme.css](references/theme.css) into one `<style>` block.
3. Replace `<link rel="stylesheet" href="styles.css">` with that `<style>` block.
4. Delete `styles.css` if the scaffold wrote it. Delete any other local file the HTML would load.
5. Images: embed as `data:` URIs, or omit. Do not link to local image paths.
6. Keep reveal.js / Font Awesome / Chart.js as the same CDN URLs from the `revealjs` scaffold. Do not add local copies of those libraries.
7. Inject `.slide-page` counters and initialize with `transition: 'fade'` and `slideNumber: false` (see [examples.md](examples.md)).

QA screenshots and overflow-check temp files are not deliverables; do not ship them next to the deck as referenced assets.

## Workflow additions

Copy this checklist and track progress:

```
Task Progress:
- [ ] Read ../revealjs/SKILL.md and follow its workflow
- [ ] Ask for theme if unspecified (Amiri Teal, Naskhi Slate, Diwan Burgundy, Mishkah Indigo)
- [ ] Parse source: md file count, headings, quotes, per-section sources, metadata, references
- [ ] Map sections/titles (1 md → headings; many md → filenames + inner headings)
- [ ] Plan sequence: title, outline (slide 2), divider+content per section, closing
- [ ] Scaffold with --structure starting 1,1 and `d` for each section
- [ ] Inline themes/<id>.css then theme.css; delete styles.css
- [ ] Inject .slide-page 01 / N; fade transition; arrows and number do not overlap
- [ ] Fill slides with house components; series eyebrow on title when source has one; .source footnotes
- [ ] Confirm deliverable is one HTML file with no local CSS/asset references
- [ ] Verify nothing from the source was dropped
- [ ] Run the verification loop until every check passes
```

## Verification loop

This loop **replaces** the `revealjs` visual-review step. Still use that skill’s overflow checker and Decktape screenshots of **every** slide. Copy this checklist and do not deliver until it passes:

```
Task Progress:
- [ ] Overflow check on the HTML
- [ ] Screenshot every slide
- [ ] Audit every screenshot against the criteria below
- [ ] Fix the single HTML file (content preserved)
- [ ] Re-run overflow check
- [ ] Re-screenshot every changed slide (all slides if chrome/global CSS changed)
- [ ] Repeat until every check passes
```

If a check fails: read the failure, fix, screenshot again. **Only proceed when validation passes.**

Audit and fix the presentation design from the available screenshots or renders.

### Look for

- Unbalanced composition or too much empty space.
- Panels, boxes, and cards that are too large, too small, or out of proportion.
- Cards in the same group with inconsistent height or alignment.
- Misaligned columns, elements, titles, and body copy.
- Weak visual hierarchy among titles, subtitles, subheadings, lists, quotes, callouts, takeaways, highlights, and source notes.
- Repeated lists or facts that are hard to scan because of inconsistent spacing, numbering, markers, or grouping.
- Emphasis, quote, callout, takeaway, or highlight elements that:
  - are so large that they look like a second title;
  - use quote styling for content that is not actually a quotation;
  - lack clear visual separation from the main content;
  - sit too close to cards, lists, subtitles, or footnotes;
  - wrap awkwardly or split important phrases;
  - combine a bold label and a long explanation without clear hierarchy;
  - visually dominate the slide;
  - use the wrong semantic or visual treatment for their purpose.
- Callouts, takeaways, cards, and source notes that do not share a consistent content width or alignment.
- Callouts that are narrower than the main card group without a deliberate layout reason.
- Source notes that visually resemble regular body copy because they are too large, too dark, too wide, or insufficiently separated.
- Footnote styles that are not applied because `.footnote` is nested inside another container such as `.content`, rather than being a direct child of the slide.
- CSS selectors that depend on a specific DOM nesting level and fail when the same component is placed inside a different wrapper.
- Insufficient spacing or visual separation between the main content, takeaway/callout, and source attribution.
- Callouts and footnotes that appear to form one continuous block instead of distinct information layers.
- Inconsistent max-width, padding, left edge, right edge, or alignment between related content components.
- Elements that are cramped, too small, stacked, or hard to read.
- Weak padding, margin, gap, border, radius, color, line-height, font size, or contrast.
- Decorative or navigation chrome that competes with the main content.
- Slide number, progress bar, navigation arrows, and footer colliding or lacking a safe area.
- Style drift across slides that should match.
- Responsiveness issues, clipping, overflow, or truncated text.

### Fix principles

- Keep all content, quotes, sources, discussion structure, and meaning.
- Do not change wording except to fix wrapping or readability, and never drop information.
- Use empty space on purpose and in proportion.
- Cards in the same semantic group or grid row must share the same height, with top and bottom edges aligned.
- Equalize group height from the tallest card, or use grid/flex so every card fills the row.
- Card content starts at the same top inset, with uniform internal padding.
- Do not force one height across the whole deck. Cards in a different group, or standalone cards, may use their natural height.
- Match the component to the information:
  - cards for peer facts;
  - lists for sequence or grouped items;
  - blockquotes for actual quotations;
  - callouts or takeaways for conclusions, insights, warnings, or key messages;
  - footnotes for sources and attribution.
- Use the appropriate semantic HTML element where possible, such as `<blockquote>` for quotations and a dedicated callout structure for insights or takeaways.
- Separate labels from long explanations using sublabels, small headings, spacing, or clear internal structure.
- Do not make long paragraphs look like headlines through excessive font size or display styling.
- Use a suitable max-width so text wraps naturally and remains readable.
- Give quotes, callouts, and takeaways enough margin and padding to separate them from cards, titles, body copy, and footnotes.
- Use backgrounds, borders, colors, separators, or icons proportionally to clarify hierarchy without adding unnecessary decoration.
- If some cards in a group are very short, add proportional space so the row height stays even without looking empty or lopsided.
- Cards with different item counts should still share baseline, padding, and alignment.
- Align callouts, takeaways, cards, and related content blocks to a deliberate shared width and grid boundary. A callout should normally align with the card group above it unless a narrower width is intentional and visually justified.
- Use a consistent content container or shared alignment rule for cards, callouts, and source notes instead of assigning unrelated widths to each component.
- Treat source notes as footnotes, not body paragraphs:
  - use a smaller font size;
  - use a muted color;
  - use a shorter line length;
  - use a tighter line-height;
  - provide clear spacing from the main content.
- Make footnote styling robust to DOM nesting. Target `.footnote` wherever it appears inside a slide, including when nested inside `.content`, cards, or other layout wrappers. Do not rely only on selectors such as `section > .footnote` unless the markup structure guarantees that relationship.
- Keep the visual roles distinct:
  - main content carries the argument;
  - callouts or takeaways highlight the key implication;
  - footnotes provide attribution or source context.
- Add enough vertical spacing, padding, or a subtle divider between the callout and the source note so they do not read as one combined block.
- Ensure callouts and footnotes share the intended left alignment with surrounding content while preserving their distinct visual treatment.
- If an emphasis or callout element is too long for the available space, adjust its internal layout or split the content across slides without removing information.
- Apply the same fixes across the deck, especially:
  - two-column cards such as “Makna literal & teknis” and “Fiqh vs. Usul al-Fiqh”;
  - category cards in one row;
  - classification cards such as “Mutawatir”, “Ahad”, and “Musnad & Mursal”;
  - all quote, callout, takeaway, highlight, large-text, and footnote components.

Keep the deck’s visual identity. Improve proportion, readability, hierarchy, balance, semantics, and presentation quality.

### After each fix pass

- Check overflow and clipping on every slide.
- Screenshot-review every slide.
- Confirm no elements collide.
- Confirm cards in the same group share height and alignment.
- Confirm quote, callout, takeaway, highlight, and footnote elements are visually distinct and appropriately sized.
- Confirm long text wraps naturally without awkward breaks.
- Confirm callouts align with the intended card or content-container width.
- Confirm every source note receives the correct footnote styling regardless of its nesting level in the HTML.
- Confirm main content, callouts, and source notes are visually separated and readable as distinct layers.
- Inspect computed layout and styles for representative slides, including slides where `.footnote` is nested inside `.content`.
- Confirm layout, typography, spacing, cards, footer, navigation, and slide numbers are consistent.
- Keep the same single-file HTML output and structure this deck already uses.

## Additional resources

- Theme palettes: [references/themes.md](references/themes.md)
- Shared layout CSS: [references/theme.css](references/theme.css)
- HTML patterns: [examples.md](examples.md)
