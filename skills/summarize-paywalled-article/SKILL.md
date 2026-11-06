---
name: summarize-paywalled-article
description: Summarize a paywalled article from an open authenticated browser tab and write the result to a destination path explicitly supplied by the user.
---

# Summarize Paywalled Article

Use this skill when the user asks for a detailed summary of a paywalled article and provides an article tab definition or URL plus a destination for the written summary.

Before taking browser or file actions, check that both required inputs are present. If the user has not defined the article tab or URL, ask them to identify it. If the user has not defined the write destination, ask them to provide the exact path or destination. If either input is missing, ask a concise clarification question and wait; do not guess, open a different article, or write to a default location.

## Required inputs

- **Source:** the article tab definition or URL supplied by the user. If the user defines a tab to open, use Computer Use with the named browser (normally Chrome) to open a new tab or navigate the appropriate browser tab to that exact URL. Then verify the visible title and URL. Do not silently substitute another tab, browser, URL, or source.
- **Destination:** the exact path, note, document, or other output location supplied by the user. Do not infer a destination from prior tasks, default folders, or the article topic. If no destination is supplied, ask for it before writing.

### Knowledge Base routing

When the supplied destination is `Knowledge Base` or a folder within it:

1. Inspect the existing `Knowledge Base` subfolders and identify the best topical match for the article.
2. Place the note in that matching subfolder rather than directly in the `Knowledge Base` root.
3. If no suitable subfolder exists, create a concise, topic-appropriate subfolder inside `Knowledge Base` before writing the note.
4. Preserve the vault's existing folder-naming conventions and verify the final note path before writing.

Apply this routing only when the user explicitly names `Knowledge Base` as the destination; do not infer or impose it for other destinations.

## Workflow

1. Connect to the named browser using Computer Use. Open a new browser tab when the user supplies a URL or tab definition and the article is not already open; reuse an existing tab only when the user explicitly identifies it or it clearly matches the requested article. Verify the visible title and URL match the requested article.
2. Read the **full article** through the authenticated session. Use accessibility text, page text, scrolling, and screenshots as needed to capture every section, heading, example, research claim, recommendation, and conclusion. When the page is long, collect it in sequential sections and preserve section order. Do not rely on the abstract, teaser, search snippet, audio-player metadata, or first viewport as a substitute for the article.
3. Apply a completeness gate before summarizing: confirm that the page exposes the complete article body from its opening through its final conclusion, that no section is hidden behind a paywall or “read more” control, and that the captured text does not end mid-sentence or omit visible headings. If needed, scroll to the bottom and inspect intermediate sections again. If completeness cannot be established, do not write a definitive summary; tell the user what remains inaccessible and ask them to make the full article available.
4. If the article is not accessible because the user is signed out, the tab is missing, or a paywall blocks any part of the article, stop and tell the user exactly what is needed. Never bypass a paywall, CAPTCHA, login barrier, or browser security warning.
5. Separate the article's claims from your synthesis. Preserve named studies, organizations, dates, numbers, examples, mechanisms, and limitations. Do not turn plausible implications into claims attributed to the authors.
6. Produce a systematic summary that normally includes:
   - bibliographic details and source link;
   - executive summary and central thesis;
   - the problem or context;
   - the article's argument, model, or causal logic;
   - section-by-section explanation;
   - examples, evidence, cases, and research findings;
   - practical implications or implementation steps;
   - risks, limitations, assumptions, and counterpoints;
   - key takeaways and a concise checklist when useful.
7. Write the finished summary to the exact user-supplied destination, preserving its existing conventions. For Markdown or Obsidian notes, use valid frontmatter only when appropriate, internal wikilinks for vault notes, external Markdown links for web sources, and readable headings. Avoid reproducing the article or lengthy verbatim excerpts.
8. Verify the output exists at the requested destination, renders coherently, and records that full-article access was confirmed. If the completeness gate failed, do not create or overwrite the definitive summary.

## Quality rules

- Aim for completeness of ideas, not verbatim completeness. A summary must be substantially shorter than the source.
- Full-article access is a prerequisite, not an optional quality improvement; never label a partial-page synthesis as a complete summary.
- Keep the distinction between direct article content, evidence reported by the authors, and your own synthesis visible.
- Retain uncertainty when the article is tentative or early-stage.
- Do not invent missing sections, citations, quotations, page numbers, or findings.
- Do not modify any other file, note, sharing setting, or browser state unless the user explicitly asks.
