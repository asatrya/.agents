---
name: pdf-tools
description: Process PDF files with utilities for downloading, extracting outlines, adding navigable bookmarks, OCR, and compression.
---

# PDF Tools

Use the executable helpers in `/Users/autama/.agents/skills/pdf-tools/scripts` for PDF acquisition and processing:

- `scripts/download_khazanah_muhammadiyah_pdf.py` downloads a Khazanah Muhammadiyah collection as a PDF.
- `scripts/extract_pdf_outline.py` reads existing PDF bookmarks or detects likely headings and writes a compatible `outline.txt`.
- `scripts/add_pdf_bookmarks.py` adds the entries from `outline.txt` as navigable bookmarks in the PDF reader sidebar.
- `scripts/ocr_pdf.py` creates a searchable PDF from scanned pages.
- `scripts/compress_pdf.py` compresses a PDF with Ghostscript while preserving the input.

## Choose the operation

- Download a document: use `download_khazanah_muhammadiyah_pdf.py`.
- Create an outline file: use `extract_pdf_outline.py`.
- Add sidebar navigation: use `add_pdf_bookmarks.py` with the generated outline file.
- Make an existing scanned PDF searchable: use `ocr_pdf.py`.
- Reduce PDF size: use `compress_pdf.py`.
- For a complete preparation workflow, download first, OCR second, create or review the outline, add bookmarks, and compress last.

Use the exact script path above when it exists. Run each script with `uv run --script` so its inline Python dependencies are installed and honored:

```bash
uv run --script /Users/autama/.agents/skills/pdf-tools/scripts/download_khazanah_muhammadiyah_pdf.py --help
uv run --script /Users/autama/.agents/skills/pdf-tools/scripts/ocr_pdf.py --help
uv run --script /Users/autama/.agents/skills/pdf-tools/scripts/compress_pdf.py --help
```

## Dependencies

The Python dependencies are declared in each script's inline `uv` metadata and move with the scripts; no separate Python requirements file is needed:

- Downloader: `Pillow>=10.0`
- Outline extraction, bookmark creation, and OCR: `pypdf>=5.0,<7`
- Compression: Python standard library only

OCR also requires Tesseract and Poppler's `pdftoppm`. Compression requires Ghostscript. Keep these as system dependencies rather than copying them into the skill folder.

## Outline and sidebar bookmarks

Generate an outline from a PDF that already has bookmarks:

```bash
uv run --script /Users/autama/.agents/skills/pdf-tools/scripts/extract_pdf_outline.py \
  document.pdf \
  --output outline.txt
```

If the PDF has no bookmarks, `extract_pdf_outline.py` automatically falls back to conservative heading detection from extracted page text. Use `--source heuristic` to request that mode explicitly. Heuristic results are candidates and must be reviewed; a PDF's visible table of contents is not guaranteed to map cleanly to headings extracted from page text.

After reviewing `outline.txt`, add it to the PDF:

```bash
uv run --script /Users/autama/.agents/skills/pdf-tools/scripts/add_pdf_bookmarks.py \
  document.pdf \
  outline.txt \
  --output document_bookmarked.pdf
```

The outline format is one entry per line, with one-based page numbers:

```text
# Pendahuluan | 1
## Latar Belakang | 3
## Tujuan | 5
# Bab 2 | 7
```

Leading `#` characters define the bookmark hierarchy. Empty lines and lines beginning with `;` are ignored. `add_pdf_bookmarks.py` preserves existing bookmarks by default; pass `--replace-existing` when replacing them intentionally.

## Downloading

The downloader accepts a Khazanah Muhammadiyah collection URL. If no URL is supplied, it uses the script's built-in default collection.

```bash
uv run --script /Users/autama/.agents/skills/pdf-tools/scripts/download_khazanah_muhammadiyah_pdf.py \
  "https://khazanah.muhammadiyah.or.id/collections/<collection-slug>" \
  --output document.pdf
```

It first attempts to download the original PDF and falls back to assembling the public rendered pages when the original is unavailable. Use `--timeout SECONDS` to change the HTTP timeout and `--force` only when replacing an existing output is intended.

## OCR

OCR requires Tesseract and Poppler's `pdftoppm` to be installed. The default language is `eng`; use a `+` expression such as `eng+ind` when the corresponding Tesseract language data is installed.

```bash
uv run --script /Users/autama/.agents/skills/pdf-tools/scripts/ocr_pdf.py \
  document.pdf \
  --language eng+ind \
  --output document_ocr.pdf
```

Useful options:

- `--pages N` or `--pages N-M` to OCR only selected one-based pages.
- `--dpi DPI` to change the page rendering resolution; the default is 300.
- `--psm MODE` to change Tesseract page segmentation mode; the default is 3.
- `--temp-dir PATH` to choose where temporary rendered images and OCR files go.

The default output is `<input>_ocr.pdf`. Do not use the input path as the output path.

## Compression

Compression requires Ghostscript. The default quality preset is `ebook`.

```bash
uv run --script /Users/autama/.agents/skills/pdf-tools/scripts/compress_pdf.py \
  document_ocr.pdf \
  --output document_final.pdf \
  --quality ebook
```

Available presets are `screen`, `ebook`, `printer`, `prepress`, and `default`. `screen` generally produces the smallest file; choose a higher-quality preset when readability or print quality matters. The default output is `<input>_compressed.pdf`.

## Safety and output handling

- Preserve the user's original PDF and write derived files to a distinct output path.
- The outline and bookmark utilities refuse to overwrite existing output files unless `--force` is supplied. Do not add `--force` unless replacement is explicitly requested or clearly intended.
- Let the scripts report failures rather than treating a partial file as successful output; they use temporary files and finalize outputs only after successful completion.
- Review heuristic outline output before using it as input to `add_pdf_bookmarks.py`; detection is intentionally conservative and cannot infer every document's table of contents reliably.
- If OCR fails because a Tesseract language is missing, report the missing language data and ask the user to install it before retrying.
- If a required external executable is missing, report which dependency is needed: Tesseract and `pdftoppm` for OCR, Ghostscript for compression.
