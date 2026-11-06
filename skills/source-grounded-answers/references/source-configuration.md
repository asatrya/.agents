# Allowed source intake

This skill has no built-in source list and must not read a source merely because it appears in deployment configuration, the skill folder, or an unrelated environment path.

Sources may enter a search only through one of these channels:

1. A file uploaded in the current conversation.
2. Text pasted into the current prompt, or a URL explicitly included in the prompt.
3. A file or folder inside the current workspace that the user identifies or explicitly asks the skill to search.

Use the deterministic helper with the matching argument:

```text
uv run --script scripts/search_sources.py \
  --query "the user's question" \
  --prompt-source https://example.com/explicitly-provided-page
```

The helper fetches explicitly supplied `http://` and `https://` pages using Python's standard library and extracts visible text by HTML heading. No PDF package is needed for website-only searches. If the source set includes a PDF, add `--with pypdf==5.9.0` to the `uv run` command; keep the dependency optional so a web-only search does not try to download it. For example:

```text
uv run --with pypdf==5.9.0 --script scripts/search_sources.py \
  --query "the user's question" \
  --prompt-source https://example.com/explicitly-provided-page \
  --upload /path/to/an-attached-file.pdf
```

If direct page retrieval fails because the runtime cannot reach the host, use an available connected web tool to open only the exact user-selected URL. If the tool returns the page in line-numbered chunks, collect the visible page text and headings from the chunks needed for the answer, retaining paragraph breaks and the original URL. Save a JSON object with this shape and pass its file to the helper:

```json
{
  "url": "https://example.com/explicitly-provided-page",
  "title": "Page title",
  "text": "# Page heading\nL12: Visible page text..."
}
```

```text
uv run --script scripts/search_sources.py \
  --query "the user's question" \
  --prompt-source https://example.com/explicitly-provided-page \
  --web-content-file /path/to/captured-page.json
```

The helper requires the URL in the JSON file to match `--prompt-source` exactly. It strips web-tool line-number prefixes, splits captured text by Markdown headings, and returns ranked quotations attributed to the original URL. Do not search the web for substitute sources or follow page links. If the connected tool also cannot retrieve the selected URL, report the URL as skipped.

Rules:

- Do not pass fixed paths, URLs, or a source manifest from the skill instructions.
- Do not search the whole workspace unless the user asks to use workspace sources broadly. Prefer the specific files or folders the user identifies.
- A website may be fetched only when its URL appears in the current prompt or comes from an uploaded/workspace source that the user explicitly selected.
- Fetch only the explicitly supplied URL; do not crawl links from that page.
- Website locations include the page title, detected heading, and URL when available. If the page has no headings, the location uses its title and URL.
- Use `--web-content-file` only for content captured from the exact user-selected URL, not for search-result snippets or unrelated pages. Pass that same URL with `--prompt-source` so the helper can verify the source selection.
- `--inline-source-json` requires a JSON object with string fields `name` and `text`.
- If an upload, prompt source, or workspace path is missing or unreadable, report it as a skipped source.
