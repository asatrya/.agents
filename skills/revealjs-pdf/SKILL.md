---
name: revealjs-pdf
description: Export HTML slide decks (reveal.js and other HTML presentations) to PDF on the local machine using DeckTape. Installs Node.js and decktape if missing. Use when the user asks to export, convert, or print a presentation, HTML deck, slideshow, or reveal.js file to PDF, or mentions decktape / revealjs-pdf.
---

# Reveal.js PDF Export

Export a local HTML slide deck to PDF with [DeckTape](https://github.com/astefanutti/decktape). Prefer the helper script; it installs missing dependencies and writes the PDF next to the HTML file by default.

## Workflow

Copy this checklist and track progress:

```
Task Progress:
- [ ] Resolve HTML source (ask if missing or unknown)
- [ ] Resolve PDF output path
- [ ] Create a temporary HTML copy without modifying the original
- [ ] Apply export-only cleanup to the temporary copy
- [ ] Run scripts/export-pdf.sh against the temporary copy (installs Node/decktape if needed)
- [ ] Delete the temporary HTML copy, including after failures
- [ ] Confirm the PDF exists and report the path
```

### 1. Resolve the HTML source

**If the user did not give an HTML file or URL, ask for it. Do not guess.**

**If the location is unknown** (relative path that does not exist, directory without a clear deck file, or only a title mentioned), ask which file to export.

Accept:

- A local `.html` file path
- An `http(s)://` URL
- A `file://` URL

If the user points at a **directory**, look for a single obvious deck (`index.html`, `presentation.html`, or the only `*.html` file). If several HTML files exist, ask which one.

Never append `?print-pdf`. DeckTape captures slides itself; reveal.js print stylesheets make export hang.

For decks created with the `revealjs` skill that use Chart.js, pass `presentation.html?export` so chart animations freeze. The script strips the query to find the file, then appends it to the `file://` URL.

### 2. Resolve the PDF output path

Default: **same directory as the HTML file, same basename, `.pdf` extension**.

| HTML | Default PDF |
|------|-------------|
| `/talks/q4/deck.html` | `/talks/q4/deck.pdf` |
| `./slides/index.html` | `./slides/index.pdf` |

Use a different path only when the user sets one (`-o` / `--output`, or wording like "save it to …").

If the source is a **URL** (no local file), there is no sibling directory — **ask where to write the PDF** unless the user already specified it.

### 3. Prepare an export-only HTML copy

Never edit the user’s original HTML file. For a local HTML source, create a temporary copy in the same directory as the source so relative CSS, JavaScript, fonts, and image paths continue to work. Use a distinctive temporary name such as `.revealjs-pdf-export-<random>.html` and register cleanup immediately with a shell `trap`, so the copy is removed on success, failure, or interruption.

Use this pattern for local sources:

```bash
source_html="/absolute/path/to/original.html"
source_dir="$(dirname "$source_html")"
temp_html="$(mktemp "$source_dir/.revealjs-pdf-export.XXXXXX.html")"
trap 'rm -f -- "$temp_html"' EXIT INT TERM
cp -- "$source_html" "$temp_html"
# Edit only "$temp_html", then export from "$temp_html".
```

Do not use a temporary directory separated from the source unless all relative assets are copied there too. Before reporting completion, confirm the temporary file is gone and the original source still exists.

Apply export-only CSS cleanup to the temporary copy when grey halos are visible around cards. Replace targeted decorative shadows with `box-shadow:none`, especially for selectors such as:

```css
.scope-card,
.misconception p,
.misconception .detail-list,
.misconception blockquote,
.review-path > div {
  box-shadow: none;
}
```

Also inspect for slide-specific selectors with stronger shadows, such as `.review-path>div`; removing only the common card shadows may leave a halo on a closing or review slide. Preserve borders, fills, and intentional rings unless they are themselves identified as the unwanted effect—for example, `.scope-core` may use a border and outer ring rather than a card shadow.

Apply export-only font safeguards when characters are missing, replaced by boxes, or visibly fragmented. This often happens when a decorative or script-specific font is inherited by prose, symbols, or another writing system that it does not fully support. Inspect both direct text inside elements and nested text elements; fixing only `p` children will not fix text written directly inside a `blockquote`, `div`, or heading.

Use a broad fallback for ordinary prose and reserve specialized fonts for the selectors that actually need them:

```css
/* Generic prose and quotation text */
.export-prose,
.misconception blockquote,
.misconception blockquote p:not(.script-text) {
  font-family: var(--body-font), Arial, sans-serif !important;
}

/* Keep a script-specific font only where that script is intended */
.script-text,
.arabic,
.quran-arabic {
  font-family: "Specialized Script Font", "Noto Sans", serif !important;
}
```

Adapt the selectors and font names to the deck. Do not blindly replace every font: preserve typography where the font has complete glyph coverage, and use a fallback stack that covers the actual scripts, punctuation, symbols, and diacritics in the content. If fonts are loaded from a remote stylesheet, ensure the capture environment can reach the font URLs and wait for `document.fonts.ready` before printing when the deck loads fonts dynamically.

Render screenshots for every slide after font safeguards are applied and inspect them at readable resolution, with particular attention to quotations, mixed-script text, symbols, diacritics, and slides using direct text nodes. Only then delete the temporary HTML copy.

If the source is a URL, do not modify the remote resource. Use it unchanged unless it is first downloaded into a temporary local HTML copy with its required relative assets available.

### 4. Export

Run the script from this skill directory (`~/.agents/skills/revealjs-pdf`) using the temporary HTML copy, not the original:

```bash
bash ~/.agents/skills/revealjs-pdf/scripts/export-pdf.sh "<temporary-html-path>"
```

Custom output:

```bash
bash ~/.agents/skills/revealjs-pdf/scripts/export-pdf.sh --output "/path/to/deck.pdf" "<temporary-html-path>"
```

Optional flags:

```bash
bash ~/.agents/skills/revealjs-pdf/scripts/export-pdf.sh \
  --size 1920x1080 \
  --slides 1-10 \
  --plugin reveal \
  --output "/path/to/deck.pdf" \
  "./temporary-deck.html"
```

The script:

1. Installs **Node.js / npm** if missing (Homebrew on macOS; `apt-get` on Debian/Ubuntu)
2. Installs **decktape** into `~/.cache/revealjs-pdf` if `decktape` is not on `PATH`
3. Detects reveal.js vs other frameworks (`reveal` vs `automatic`)
4. Passes Chrome flags needed for local files (`--allow-file-access-from-files`, `--disable-web-security`)
5. Writes the PDF and prints `Wrote <path>`

After DeckTape exits, remove the temporary HTML copy using the registered cleanup trap. Never delete the original source HTML.

First run may download Chromium via Puppeteer; that can take several minutes. Do not interrupt it.

### Export gotchas and lessons learned

- The helper script uses `set -u`; initialize optional arrays such as `extra_args=()` before expanding them. Otherwise an export with no extra arguments can fail with `extra_args[@]: unbound variable` after dependencies have installed.
- Do not assume an npm install succeeded just because the installer was invoked. Verify that `node_modules/.bin/decktape` exists before running it; report the actual npm error if it does not.
- `~/.cache/revealjs-pdf` may not be writable in managed or sandboxed environments. If cache creation fails, retry with the required permission or use a writable task-local cache when supported.
- The first run may be quiet for several minutes while npm and Chromium download. Continue polling before declaring the export hung.
- When using the manual command with a local file, construct a valid `file://` URI and URL-encode spaces, ampersands, and other special characters in the path.
- Missing or fragmented glyphs can come from font inheritance, not just failed font loading. Check the computed/inherited font on the affected element, especially when a decorative font is applied to direct text or prose. Override the whole prose container with a broad fallback stack and reapply the specialized font only to script-specific descendants.
- Check all slides—not only the first reported example—because direct text nodes, nested paragraphs, quotations, symbols, and mixed-script content may use different font rules. Render and inspect a complete slide screenshot set before reporting success.
- If the helper script fails after installing DeckTape, use the documented manual DeckTape command as a fallback rather than reinstalling dependencies.
- After a successful process exit, verify that the PDF exists, is non-empty, and—when practical—contains the expected slide/page count before reporting completion.

### 5. Confirm

Verify the PDF file exists and tell the user the absolute path.

## Rules

- Ask for the HTML source when it is not provided.
- Ask for the HTML location when it cannot be resolved.
- Put the PDF beside the HTML unless the user chose another path.
- Keep the original HTML unchanged; all export-only edits must be made to a temporary copy and that copy must be deleted afterward.
- Register cleanup before editing or exporting so temporary files are removed on both success and failure.
- Do not use reveal.js `?print-pdf`.
- Do not switch to Docker unless the user asks; this skill runs DeckTape on the local machine via npm.

## Troubleshooting

| Symptom | What to do |
|---------|------------|
| `HTML file not found` | Ask the user for the correct path |
| `Output PDF path is required when the source is a URL` | Ask where to save the PDF, then pass `--output` |
| Export hangs on reveal.js | Ensure the URL does **not** include `?print-pdf` |
| Layout looks wrong | Retry with `--size 1920x1080` or `--size 1024x768` |
| CSS/images missing from a local file | The script already sets local-file Chrome flags; confirm relative assets exist next to the HTML |
| `No usable sandbox` (Linux) | The script already adds `--no-sandbox` on Linux |
| Node install failed | Ask the user to install Node.js 18+ from https://nodejs.org/ and retry |

Manual DeckTape equivalent (only if the script cannot run):

```bash
npx --yes decktape reveal \
  --chrome-arg=--allow-file-access-from-files \
  --chrome-arg=--disable-web-security \
  "file:///absolute/path/to/deck.html" \
  "/absolute/path/to/deck.pdf"
```
