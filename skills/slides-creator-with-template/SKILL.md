---
name: slides-creator-with-template
description: Turn supplied source material into a Google Slides or PowerPoint deck using another supplied deck as a layout catalog. Source may be an existing deck or any other content (doc, notes, article, outline, transcript, etc.). If it is not already a deck, create a deck concept first, then apply the template. Requires both source content and a template or slides layout reference before starting.
---

# Slides Creator with Template

Create a new editable copy; never modify the source material or the template.

## Required Inputs

Do not start until both of the following are already given. If either is missing, stop and ask for it. Do not invent content, pick a default template, or proceed with a placeholder.

1. **Source content** — the material to present. Accept a Google Slides or PPTX deck, PDF, doc, notes, article, outline, transcript, spreadsheet, pasted text, or any other substantive source. A topic-only request (“make a deck about X”) with no material is not enough.
2. **Template or slides layout reference** — the design system to apply. Accept a Google Slides or PPTX template/deck used as a layout catalog, or an explicit layout-reference deck. A brand name, color list, or “make it look professional” is not enough.

Confirm both are identified (file, URL, or in-chat content) before continuing. If the user supplied one but not the other, name the missing input and wait.

## Deck Concept

Decide whether the source is already a deck.

- **Already a deck** (Google Slides, PPTX, or slide-by-slide copy): treat it as the deck concept. Read, parse, and render it once. Extract every slide’s title, body text, claims, citations, notes, charts, tables, and media meaning.
- **Not a deck**: first create a deck concept before any visual rebuild. Structure the source into a slide-by-slide narrative: sequence, title, narrative role, claims, supporting evidence, citations, notes, and intended media. Preserve source facts and intended meaning; do not invent claims. Then use that concept as the source sequence for the rest of the workflow.

Do not map layouts or copy the template until the deck concept exists.

## Workflow

1. Identify the source content and template deck from the required inputs. For native Google Slides, use the Google Drive and Google Slides workflows. For local PPTX, use the Presentations workflow.
2. Produce the deck concept (see above). If the source was already a deck, this is the extracted slide sequence; otherwise it is the newly created concept.
3. Parse and render the template once. Treat it as a layout catalog, not a fixed slide sequence. Record its available masters, layouts, exemplar slides, typography, colors, recurring footers, spacing, and media frames.
4. Map every concept slide to the most suitable template exemplar based on narrative role, information density, evidence type, orientation, and hierarchy. Use a different layout family when the source role changes.
5. Copy the template, duplicate selected exemplars into the copy, and edit inherited objects in place. Explicitly keep, replace, or delete each meaning-bearing template image, chart, screenshot, device mockup, and speaker photo.
6. Preserve all source facts, intended meaning, citations, and section flow from the deck concept. Recreate narrative text as editable native text. Shorten only flexible wording; never reduce the clarity of required claims or citations to force content into a layout.
7. Adapt the layout to fit the source content. Prefer a better exemplar, a denser template layout, or a small local adjustment over uniformly shrinking text. Keep narrative body text at or above 12 pt unless the template’s established role is legitimately smaller.
8. Preserve image aspect ratios. Crop decorative images only when safe; fit screenshots, diagrams, charts, and other meaning-bearing visuals completely within their frames.
9. Reorder completed slides only after all duplicates and new slides are created. Delete unused template-library slides last.

## Design Rules

- Use the template’s typography, color system, alignment, and visual rhythm.
- Match each concept slide to a suitable layout, not the other way around.
- Preserve native citations on the slide. Retain source speaker notes and links when supported.
- Do not leave generic placeholder text or unmapped template media.
- Do not rasterize editable source text.
- Use native bulleted paragraphs; never type bullet glyphs to imitate lists.
- Keep titles to a deliberate number of lines. Change the layout or shorten flexible copy before allowing a title to wrap unexpectedly.

## Required Quality Check

Before delivery:

1. Run the available structural issue checker and repair every error.
2. Render the complete output deck once after final ordering.
3. Inspect every delivered slide at full size. Check visual proportions, alignment, spacing, contrast, text wrapping, clipping, overlap, media crops, citations, and consistency with adjacent slides.
4. Collect defects and make one consolidated repair pass; make a second pass only if defects remain.
5. Verify slide count, order, citations, and concept-to-output narrative fidelity through a final readback.

Return the editable copied deck’s verified URL or file link, with a concise summary of the rebuild (and of the deck concept if one was created from non-deck source).
