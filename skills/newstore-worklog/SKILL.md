---
name: newstore-worklog
description: >-
  Builds evidence-backed Newstore/TIDE work logs, accomplishment summaries,
  performance-review inputs, weekly status updates, and impact statements. Use
  this skill whenever the user asks what they delivered, their work or
  involvements, accomplishments, contribution, impact, measurable outcomes,
  or a concise work log—even if they do not say “work log”. Gather the user's
  work across the mapped organization sources, identify the current
  organization-level initiatives or goals, filter for staff-level
  accomplishments, deduplicate the evidence, and write each item as
  “Delivered X, changing Y by Z, which contributed to goal A and
  enabled/saved/generated B.”
compatibility: >-
  Requires read access to the applicable Newstore source connectors and local
  Newstore notes. Read-only by default; use the Newstore/work Google account
  autama@newstore.com when Google Workspace sources are relevant.
---

# Newstore Worklog

Create a concise, evidence-backed record of the user's Newstore/TIDE work. The
value of this workflow is not a longer activity list; it is a defensible chain
from work performed to outcome, measurable change, strategic relevance, and
business value.

## Scope and guardrails

- Use this skill only for Newstore/TIDE work. Read `newstore-context` first and
  follow its source map, search order, routing, and no-invention rules.
- Keep the workflow read-only unless the user explicitly asks to save or send
  the result. Do not write to Slack, GitLab, Jira, Confluence, Document360, or
  Jira Product Discovery by default.
- For Gmail, Google Calendar, and Google Drive, use connector/app tools only.
  Verify the Newstore/work account `autama@newstore.com`; never silently use
  the Personal account and never fall back to a browser if the connector is
  unavailable.
- Do not claim a number, owner, tenant, URL, system name, or business effect
  unless a source supports it. If a source is unavailable or the evidence is
  incomplete, say so and omit the unsupported clause.
- Treat “my work” as work attributable to the user through the source's
  identity, authorship, assignee, attendee, reviewer, or explicit mention. If
  the user's identity cannot be resolved in a source, report that limitation
  rather than guessing.

## Workflow

### 1. Set the reporting scope

Determine the requested period, team or service scope, and purpose. If the
user did not specify a period, use the most useful current reporting period
implied by the request and state the assumption in one short line. Ask a
clarifying question only when the missing period or identity would materially
change the result.

Use the user's own terms and identifiers first: ticket keys, project names,
service names, MR links, initiative names, or distinctive phrases. Search
only the relevant time range and terms; do not dump or preload every source.

### 2. Gather work and involvement evidence

Cover each applicable source family below. A source may be skipped only when it
is clearly irrelevant to the requested scope or unavailable; record the gap in
the final source note.

| Source family | Look for | Prefer as evidence |
| --- | --- | --- |
| Newstore Obsidian Journal, Notes, and NS Specific Knowledge | prior work, ticket narratives, decisions, outcomes, links | the user's existing note and its primary links |
| Strategic Now notes (`NewStore/Notes/Strategic Now/`) | current organization direction, strategic initiatives, company changes, and cross-team priorities | the latest relevant note, then its primary links |
| Jira / Atlassian | assigned or reported tickets, status changes, acceptance criteria, comments, linked initiatives | issue history, resolution, and linked goal |
| Jira Product Discovery | planned work, product ideas, roadmap context, strategic themes | the current idea or canonical roadmap view |
| GitLab | authored/reviewed MRs, commits, issues, CI results, releases | merged MR, review record, release or test evidence |
| Slack, especially `#staff-plus-newsletter` | authored decisions, incident participation, requests, handoffs, acknowledgements, follow-up outcomes, and company-wide context | the thread or message with a stable link |
| Confluence and Document360 | plans, architecture, product behavior, operating guidance | the current page or article, not a remembered summary |
| Google Calendar | meetings the user organized or materially contributed to, workshops, incident calls | event title, date, attendees/context, and resulting artifact |
| Gmail and Google Drive | sent decisions, project coordination, documents, approvals, deliverables | the relevant thread or document and its date |
| Dash0 | before/after reliability, latency, error, volume, or incident metrics | an exact query, permalink, time window, and value |

Use the search order and connector names in `newstore-context`. For source
families that require an app connector, use the connector rather than a
browser. Do not treat a calendar attendance record or a message mention as a
delivered outcome by itself; find the resulting artifact or decision.

Treat `#staff-plus-newsletter` as an important organization-level context
source: it can establish current company priorities, security or operational
changes, and cross-team outcomes. It does not establish the user's personal
contribution by itself; pair it with evidence of the user's role and result.
Treat the latest Strategic Now note as a high-value synthesized source, and
follow its links back to primary evidence when a claim is material.

Build a private evidence ledger while researching. For each candidate item,
record:

```text
item key | date/period | what the user did | outcome | measurable change |
lens/lenses | role evidence | non-BAU rationale | goal/initiative | business value |
source links | confidence/gaps
```

Search for the same ticket, MR, incident, initiative, or decision across
multiple systems and merge it into one item. Prefer primary evidence, but keep
secondary sources when they establish the outcome or business context.

### 3. Use the five categories as lenses from the beginning

Do not use the five categories as an eligibility filter. Use them while
searching and organizing evidence so the work log surfaces the strongest
accomplishments and frames them in language senior leaders recognize.

For every source or candidate item, ask:

> What accomplishment can this support, and how can it be credibly framed
> through one or more of these lenses?

- **Leaving things better (Boy Scout rules)**
- **Driving cross-team shared outcomes**
- **Increasing organizational data fluency**
- **Championing the right solutions**
- **Scaling impact beyond TIDE**

Map each candidate to the strongest lens or lenses early in the evidence
ledger. Do not force a fit: a lens is a perspective for explaining the
accomplishment, not proof that the accomplishment happened. Use one primary
lens in the final item unless a second lens materially improves the framing.

#### Lens coverage rule: no lens is dropped

All five lenses must be assessed and visible in every work log. This is a
reporting rule, not permission to force a fit:

1. **Run a dedicated pass per lens.** After building the evidence ledger, go
   through the five lenses one at a time and ask: "Which candidate, including
   ones already filed under another lens, can credibly be framed this way?"
   A candidate that supports two lenses with separately evidenced outcomes
   becomes two items, not one blended item. Examples: a runbook or tooling
   that makes future work safer or easier (Leaving things better) is separate
   from the cross-team test run it enabled (Driving cross-team shared
   outcomes).
2. **Every lens ends in one of two states.** Either at least one retained item
   carries it as its primary lens, or the log states "No supported item for
   this lens" with a one-line reason (for example, role not evidenced,
   outcome not yet landed, or no source found). Silence about a lens is never
   acceptable.
3. **Account for prior entries.** If a Work Log note, Journal note, or other
   earlier record for the same period already lists an accomplishment, carry
   it forward, merge it into another item and say so, or drop it with a
   stated reason (for example, "claim not supported by sources"). Never drop
   or merge an entry silently.
4. **Do not weaken evidence to fill a lens.** If a prior entry's claim is
   stronger than the sources support (for example, an inferred limit stated
   as a finding, or a benefit to a future user with no evidence of use),
   keep the entry and rewrite the claim to what the evidence supports, with
   the gap in a caveat. A lens may be reported empty only after the search
   above; it may not be filled with an unsupported claim.

Keep an item for the work log when the user's role was significant and
evidenced by leading, driving, proposing, championing, or implementing a key
part, and when the outcome was more than business-as-usual. Passive attendance,
generic participation, being mentioned, routine execution, or activity counts
are not accomplishments by themselves. If either the role or outcome is not
supported, do not present it as an item; list it under "Held back" with the
reason, and under its lens in the coverage block where relevant, rather than
dropping it unmentioned. List a full inventory only when the user asks.

### 4. Establish the current organization-level goals

Find the current strategic initiative, plan, or goal that gives the work its
context. Search in this order:

1. The latest relevant Strategic Now note in `NewStore/Notes/Strategic Now/`.
2. Current Jira Product Discovery roadmap or idea views.
3. Current organization or department planning pages in Confluence or the
   relevant Newstore notes.
4. Recent planning or leadership discussion, including
   `#staff-plus-newsletter`, Slack, Calendar, or Drive.
5. A linked initiative in the work item itself.

For each goal used in the output, capture its exact title or a faithful short
paraphrase and a source link. Distinguish clearly between:

- **Explicit:** the source directly connects the work to the goal.
- **Supported:** the connection follows from a linked initiative or plan.
- **Inferred:** plausible but not established by the sources; do not present
  it as fact. Prefer omitting the goal connection or label it as an inference.

If no current organization-level goal can be established, say “No current
organization-level goal was established in the available sources” and do not
invent one.

### 5. Convert activity into impact

For each retained item, follow this chain:

1. **What you did:** start with a concrete action verb and the deliverable.
2. **Outcome:** state what changed for a user, service, team, or business.
3. **Measurable change:** give the exact delta, baseline and end value,
   percentage, count, duration, coverage, or time saved when available.
4. **Connection to goals:** name the explicit or supported current goal.
5. **Business value:** state what it enabled, saved, generated, or protected
   in revenue, cost, time, user experience, reliability, capacity, or risk.

Use deltas instead of praise words. Replace vague language as follows:

| Avoid | Prefer |
| --- | --- |
| improved performance | reduced p95 latency from A to B, or reduced latency by C% |
| helped the team | unblocked X people / removed Y hours of waiting / enabled Z |
| worked on | delivered, migrated, investigated, reviewed, documented, or decided |
| fixed an issue | restored X, prevented Y, or reduced recurrence from A to B |
| made it more reliable | reduced error rate, incident count, recovery time, or alert noise |
| significant / impactful | the measured value and the evidence link |
| collaborated with | aligned X decisions across Y teams, or completed Z handoff |

Do not convert an estimate into a fact. Label estimates, proxies, and
qualitative outcomes as such. A smaller, fully supported claim is better than
an impressive but unverified one.

### 6. Write the work log

Start with a short scope line, then write one item per meaningful outcome. Use
this template fully when the evidence supports every clause:

```text
Delivered X, changing Y by Z, which contributed to goal A and enabled/saved/generated B.
```

Use a partial form when a clause is not supported; omit it instead of guessing:

```text
Delivered X, changing Y by Z, which contributed to goal A.
Delivered X, changing Y by Z; business impact was not measured in the available sources.
Delivered X, improving Y toward goal A; see the linked evidence for the qualitative outcome.
```

### Senior-leader brevity

Make every item quick to scan:

- Aim for **25–30 words** in the accomplishment sentence.
- Set a hard maximum of **40 words per item**, including the lens label but
  excluding the separate evidence line and URLs.
- Keep one outcome, one measurable delta, one goal connection, and one business
  value per item. Remove secondary context before removing the delta or source.
- Combine related activities into one outcome-led item, unless they support
  different lenses with separately evidenced outcomes (see the lens coverage
  rule in step 3). Do not exceed eight items unless the user explicitly asks
  for a full inventory. Lens coverage takes precedence over item merging: do
  not merge items in a way that leaves a lens uncovered.

Recommended output shape:

```markdown
## Work log — [period]

Assumption or scope: [one short line, only when useful]

- Delivered [X], changing [Y] by [Z], which contributed to [goal A] and
  enabled/saved/generated [B]. **Lens:** [one of the five perspectives]
  Evidence: [primary source](URL) · [supporting source](URL)
- Delivered [X], changing [Y] by [Z]; [goal or business value, if supported].
  **Lens:** [one of the five perspectives]
  Evidence: [primary source](URL)

Lens coverage:
- Leaving things better: [item above, or "No supported item: reason"]
- Driving cross-team shared outcomes: [item above, or "No supported item: reason"]
- Increasing organizational data fluency: [item above, or "No supported item: reason"]
- Championing the right solutions: [item above, or "No supported item: reason"]
- Scaling impact beyond TIDE: [item above, or "No supported item: reason"]

Held back (role or outcome not yet supported): [item and one-line reason, only
if any]. Prior entries merged or dropped: [entry and reason, only if any].

Source coverage: [source families searched]. Unavailable or unresolved: [only
if relevant].
```

Always print all five lens lines, even when a lens has no item.

Keep each item to one clear sentence plus an evidence line. Group related
activities under the outcome they produced, rather than listing every meeting,
comment, or commit. Keep the user's voice and avoid internal jargon unless it
is needed to identify a product, service, or source.

### 7. Quality check before returning

Verify that:

- each item starts with what the user delivered or materially changed;
- each accomplishment sentence is ideally 25–30 words and never exceeds 40
  words, excluding its evidence line and URLs;
- each item has evidence of a significant role and a non-business-as-usual
  outcome, and is labeled with its primary lens;
- the outcome and delta are concrete, with units and a baseline when known;
- the goal is current and linked to evidence, or explicitly marked as absent;
- the business value is supported and uses revenue, cost, time, user, quality,
  reliability, capacity, or risk language;
- duplicate evidence has been merged;
- all five lenses appear in the "Lens coverage" block, each with either an
  item or a stated reason, and no lens is missing;
- every entry from an existing note for the same period is accounted for as
  carried forward, merged (disclosed), or dropped (with reason);
- no item blends two lenses with separately evidenced outcomes;
- vague praise and unexplained jargon have been removed;
- every important claim has a source link or an explicit evidence gap; and
- the output does not imply that attendance, authorship, or activity alone was
  an accomplishment.

## Saving the result

The default output is the work log in chat. If the user asks to write it to a
Work Log note, use this destination and workflow:

- Target directory: `/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/NewStore/Notes/Work Log/`.
- Read `Work Log.md` and the relevant period note before writing. Update an
  existing note for the same period instead of creating a duplicate.
- If no period note exists, use the existing naming pattern `Work log –
  [period].md`, with frontmatter `type: work-log` and the standard `NewStore`,
  `TIDE`, and `Work-Log` tags plus relevant topic/lens tags.
- Preserve source links, goal links, caveats, and evidence gaps. Do not turn
  an unsupported claim into a stronger one just because it is being saved.

If the user asks for a different kind of saved note, follow the appropriate
downstream skill:

- use `newstore-journal` for ticket-scoped or work-in-progress notes;
- use `newstore-notes` for strategy, 1:1, or meeting snapshots; and
- use `newstore-knowledge-base` only when the result is durable technical
  knowledge or a runbook.

Before writing a note, follow that skill's duplicate-check, path, frontmatter,
and write rules. Do not turn a work-log request into a new Journal note unless
the user asks for a saved note.
