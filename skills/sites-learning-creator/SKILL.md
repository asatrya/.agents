---
name: sites-learning-creator
description: Create a self-contained, single-file HTML e-learning site from one or more Markdown notes, using the canonical Manhaj Haraki course-player layout. Use when the user asks to turn Markdown files or a Markdown folder into a learning course, knowledge-base course, module/lesson site, or responsive study interface; ask for the source Markdown path when it is not provided.
---

# Sites Learning Creator

Create a polished learning site from Markdown source while preserving the source content exactly. Deliver one standalone `.html` file with all CSS, JavaScript, and source content embedded inline.

**Canonical visual system:** copy [layout.css](layout.css) and [skeleton.html](skeleton.html). Do not invent a new palette, type scale, grid, or chrome. The reference look is the Manhaj Haraki e-learning player: editorial paper surface, deep green, gold blockquotes, coral active/status accents, sharp corners, Georgia headings, Inter/system UI.

## Input and clarification

- If the user provides a Markdown file, folder, or glob, inspect that source directly.
- If no Markdown source is provided, ask one concise question for the file or folder path before building.
- Do not invent course content or replace note text with a summary. UI labels and navigation copy may be added, but the source content itself must remain present and faithful.
- Preserve the user's language, punctuation, heading text, emphasis, lists, blockquotes, code spans, tables where present, and ordering.
- Match UI copy language to the source notes (Indonesian labels in the skeleton are the default when the source is Indonesian).

## Module and lesson rules

Determine the course topology from the source:

1. Multiple Markdown files: each file is one module. The module title is the filename without `.md` unless a clearly stronger title is present in the file.
2. One Markdown file: level-1 headings become modules. If there are no level-1 headings, treat the file as one module and use its headings as lessons.
3. Lessons follow the heading hierarchy within each module. Keep the heading level and order in the parsed model even if the sidebar presents all lesson rows with one shared visual alignment.
4. Use a 400-word grouping threshold for both topologies. When consecutive heading sections are individually or cumulatively shorter than 400 words, combine adjacent sections into one lesson until the combined lesson reaches at least 400 words or the source ends. Preserve every merged heading inside the lesson body. Do not merge across file boundaries in the multiple-file case, and do not merge level-1 modules into one module in the single-file case.
5. Count words from the source text, not rendered HTML. A final group may remain below 400 words when no following section exists.
6. Keep the first heading of a grouped lesson as its navigation title; render subsequent original headings inside the lesson content.

## Canonical layout (required)

Read [layout.css](layout.css) and paste it **verbatim** into the HTML `<style>` block. Read [skeleton.html](skeleton.html) and keep this chrome:

```
header.topbar > .nav
  button.sidebar-toggle (left) · a.brand (.mark + title) · .learning-progress · nav.navlinks
.sidebar-backdrop
main#top > section.course
  aside.sidebar#lessonList
  article.article#article
```

### Tokens and type (do not restyle)

| Token | Value | Role |
|---|---|---|
| `--ink` | `#17231f` | body text |
| `--muted` | `#63736d` | secondary text |
| `--paper` | `#f0f3ed` | page background |
| `--card` | `#fffdf8` | sidebar + article |
| `--line` | `#d9e1d8` | borders |
| `--green` | `#0f5148` | brand, headings, primary |
| `--green-2` | `#1d7565` | primary hover |
| `--gold` | `#d3a84d` | blockquote accent |
| `--coral` | `#b6614b` | active lesson bar, tags, checkbox |

- Sharp corners everywhere: `border-radius: 0 !important`.
- UI font: Inter, then system UI sans. Headings and `.mark`: Georgia serif.
- Desktop grid: `310px` sidebar + fluid article, `16px` gap, sticky sidebar `top: 80px`.
- Article reading padding: `65px clamp(28px, 11vw, 160px) 24px`.
- Mobile breakpoint: `850px`. Hamburger on the left; sidebar becomes a left drawer with backdrop.
- Mobile drawer: keep `.module-head.module-toggle` rows visible above their lesson rows so users can see and collapse/expand the module menu on small screens.
- Never hide `.module-head.module-toggle` at mobile widths. The mobile drawer must show the module title and caret before its lesson rows, and each module header must remain visible and interactive.
- Desktop collapse: `body.sidebar-collapsed` removes the sidebar column so the article is full width. Do not leave an empty grid column.

### Allowed substitutions

Only swap these strings; keep class names, spacing, and colors:

- `{{COURSE_TITLE}}`, `{{DESCRIPTION}}`, `{{LANG}}`
- `.mark` character: first distinctive letter of the course title (Arabic letter is fine for Islamic courses)
- Sidebar title (course name + optional subtitle, two lines with `<br>`)
- Progress/reset/nav labels to match source language
- `localStorage` key prefix derived from a short course slug, versioned (e.g. `slc-{slug}-v1-current`)

Do not add remote fonts, images, SVG illustrations, extra CSS files, or a different radius system.

## Required chrome behavior

- Header: course brand, `N/N lesson` plus `.progress-fill` width, reset-progress control.
- Sidebar: sticky title, then one `.module-head.module-toggle` per module. Caret `⌃`/`⌄`. Persist open/closed module state.
- Module completion `✓` (`.module-check`) only when every lesson in that module is done.
- Lesson rows: `.lesson-button` with zero-padded `.lesson-index` (`01`, `02`, …), title in `<strong>`, done `✓`. Active row uses coral inset bar. Keep all lesson rows visually aligned; do not indent by heading level unless the user asks.
- Selecting a lesson on mobile closes the drawer. Entering a lesson in another module opens that module.
- Previous/next at the article footer. Last-lesson next wraps to the first lesson.
- Persist current lesson, done indexes, and open modules in `localStorage`.
- Keyboard access: real `<button>`s; `aria-expanded` / `aria-controls` on the sidebar toggle and module toggles; accessible completion labels.

### Mobile drawer acceptance criteria

At a `390px` viewport width, opening the hamburger must show, in order:

1. The sidebar title.
2. Every module header.
3. The lesson rows under each expanded module.

The number of visible module headers must equal the number of modules. Tapping a module header must collapse or expand only that module's lessons while keeping the header visible. Module headers must remain keyboard-accessible, and the caret state must match `aria-expanded`.

Use a minimal two-module fixture when testing drawer behavior:

```md
# Module A
- Lesson A1

# Module B
- Lesson B1
```

For generated CSS validation, fail if a mobile media query contains `.module-head { display: none; }`. Verify that the generated CSS keeps `.module-head` visible, for example with `.module-head { display: flex; }`.

## Article composition

Render each lesson in this order:

1. `<span class="tag">Modul N · Lesson M</span>`
2. `<h1>` lesson title (Georgia, centered)
3. `<div class="source-label">` module name · source filename
4. `<div class="lesson-banner" aria-hidden="true"></div>` — CSS stripe only, never an image
5. Parsed Markdown body
6. `.checklist` pinned to the bottom: completion checkbox, then `.lesson-nav` with `.secondary` prev and `.primary` next

## Markdown rendering

Embed the exact Markdown source in the HTML as escaped JSON (`sourceNotes: [{name, content}, ...]`). Parse it in the browser into safe HTML:

- Escape text before applying inline formatting.
- Render paragraphs, headings retained inside grouped lessons, ordered and unordered lists, nested indentation where possible, blockquotes, horizontal rules, emphasis, strong text, code spans, and links.
- Do not use `innerHTML` with unsanitized source fragments. Only inject escaped/rendered content produced by the parser.
- Keep source headings in the reading panel even when the navigation uses a shortened display title.

## Implementation workflow

1. Identify the source path or ask for it if missing.
2. Inspect all source Markdown files and build a structured, deterministic module/lesson model before writing HTML.
3. Copy [layout.css](layout.css) and [skeleton.html](skeleton.html) into one self-contained HTML file. Inline all CSS and JavaScript. Do not create a `.css`, `.js`, or asset dependency for the final learning artifact.
4. Validate that the embedded source text exactly matches the current Markdown files. Check that module counts, heading counts, and grouped lesson counts match the topology rules.
5. Validate HTML/JavaScript syntax and exercise: module collapse, module completion, lesson completion, next/previous, desktop sidebar collapse, mobile hamburger drawer, backdrop close, and local progress persistence.
6. Test the mobile drawer at `390px`: use the two-module fixture or the real course, open the hamburger, confirm every module header is visible above its lessons, toggle each module, and verify `aria-expanded` and caret state.
7. Run the CSS guard: reject any mobile rule that hides `.module-head.module-toggle`; compare the embedded CSS with [layout.css](layout.css) after applying the required visible mobile rule.
8. When browser testing is requested or visual fidelity matters, inspect desktop and mobile. Confirm hamburger on the left, visible module headers in the mobile drawer, full-width desktop collapse, aligned lesson rows, coral active bar, gold blockquotes, and no empty grid column.
9. Use Sites hosting after validation when the user requests publication. If the user asks only for a local standalone HTML artifact, deliver the file without inventing a deployment.

## Completion checklist

- [ ] Source Markdown path was provided or requested.
- [ ] All source files are embedded exactly in the HTML.
- [ ] `layout.css` was copied verbatim; no new palette or layout was invented.
- [ ] Multiple files map one-to-one to modules; single-file H1 topology is supported.
- [ ] Lessons follow heading order and 400-word grouping rules.
- [ ] No external CSS file, JavaScript file, dependency, or runtime fetch is required.
- [ ] Module collapse/expand and module completion marks work.
- [ ] Lesson completion, progress, and previous/next navigation work.
- [ ] Desktop sidebar collapse expands the reading content to full width.
- [ ] Mobile hamburger is on the left and opens a drawer with backdrop close.
- [ ] Mobile drawer visibly includes module headers and their collapse/expand controls.
- [ ] At `390px`, every module header is visible above its lesson rows.
- [ ] Mobile module toggles collapse/expand only their own lessons.
- [ ] Mobile module caret state matches `aria-expanded`.
- [ ] CSS validation rejects hidden mobile module headers.
- [ ] Final syntax and source-integrity checks pass.
