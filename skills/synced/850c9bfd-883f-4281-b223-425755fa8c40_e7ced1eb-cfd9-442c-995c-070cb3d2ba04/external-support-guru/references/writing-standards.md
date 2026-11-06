# Writing standards

For the customer reply, the NCS internal note, the engineering handover and the product feedback.

## Language

- ASD-STE100 Simplified Technical English: simple common words with one meaning each, active voice in procedures, one instruction per sentence, at most 20 words per procedural sentence and 25 per descriptive sentence
- Quotations, and names and IDs where they are allowed, stay as they are
- No epigrams, no rhetorical questions as headings, no phrases whose job is to sound considered: `S3. Confirmed the customer's severity from data`, not `S3. Not raised, not lowered — measured`
- No self-narration: no "earlier this looked like", "I first thought", "it turned out", "on closer inspection", and no justification of the method ("routing is settled by evidence, not judgement")
- Where the text already says something later found wrong, correct the text; do not add a correction on top of it
- State what happened, not what did not, except in Ruled out: `The capture call reached Adyen at 20:37:14`, not `The capture call was not dropped`

## Layout

- The finding first, then the evidence
- An `Action required` line in the header, before anything else: one short sentence with the retailer's demand only. Follow-up asks go under Open questions
- An `Investigation in short` block at the top: five or six bullets that carry the whole finding. The heading names what is summarised; a bare "In short" does not. No IDs or keys in these bullets
- Field, short value bullets: `Placed: 2026-09-12 20:37:11 UTC`, not a sentence containing the timestamp
- Field-and-value sets (record details, scope counts) in a two-column table
- Timelines as tables with short cells: one step per row, service and action, no pasted log lines. Long strings go in the Observations section at the end
- Sections a reader can skip: what was ruled out, what is still open
- A paragraph only for the rare thing that needs one; a section over three lines of prose becomes bullets
- ✅ / ❌ / ⚠️ mark outcome in tables and status lists
- In the severity assessment, ➖ / ➕ per criterion for the direction it pushes severity, ❗ for what would raise it further and ➿ for not measured. No arrows (🔽 🔼 ⬆️) and no hands (👇 👆)

## Ruled out

- "Ruled out: X, because Y", never "I believed X until I found Y"
- One line per item: the tool, the query or filter, the time window, the control it was compared against, and what the suspicion predicted
- Only suspicions engineering would otherwise chase; sources probed and found irrelevant go in the evidence ledger
- No heading that tells engineering what to do ("don't re-chase")
