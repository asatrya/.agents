---
name: newstore-journal
description: >-
  Writes and updates Newstore work-journal notes in the Obsidian vault
  (tickets, incidents, WIP). Use when logging Newstore/TIDE work, creating or
  updating a Journal note, recording an RCA, or the user asks to journal a
  TDP/NCS/SR ticket. Do not use for Think strategic, 1:1s, or meeting recaps
  — those go to newstore-notes.
---

# Newstore Journal

Personal work log. Ticket-scoped, allowed to go stale. Index is automatic — do not edit `Journal/Index Work Journal.md`.

Also read `obsidian-markdown` (syntax) and `newstore-context` (paths and sources). Prefer `newstore-notes` for strategy, 1:1s, and meeting recaps. Prefer `newstore-knowledge-base` when the content would still be true in six months without a ticket id.

## Paths

```
JOURNAL="/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/NewStore/Journal"
```

Write files directly with `Write` / `StrReplace` on that path (Google Drive). Use `obsidian` CLI only if Obsidian is open.

## Before writing

1. `Grep` `$JOURNAL` for the ticket key and a unique phrase from the title.
2. Update the existing note if found. Do not create a duplicate.
3. If the destination folder or `context` is unclear, ask.

## Filename and folder

```
{TICKET} – {Short title}.md
```

- En-dash with spaces: ` – `
- Ticket key: `TDP-1234`, `SR-8584`, `SD-5690`, `ITSD-4027`, `NCS-9363`, or `NO-TICKET`
- Optional trailing ` ⌛` when waiting on someone else
- Folder = `context` (create the folder if needed)

| `context` / folder | Use for |
|---|---|
| `Event-Stream` | Kafka, event-receiver, producers, GraphQL-on-stream |
| `GraphQL` | GraphQL API / ingestion incidents and tickets |
| `Airflow-dbt` | Composer, dbt, BigQuery pipelines |
| `SFCC` | Salesforce Commerce Cloud import/export |
| `General` | Cross-cutting ticket work (BFCM, RTBF, workshops) |
| `Career Development` | Personal career notes only (not 1:1s — those go to `newstore-notes`) |

GraphQL **incidents** may live under `GraphQL/` with `context: Event-Stream` when the failure is on the stream path — match nearby notes rather than inventing a new split.

## Frontmatter

```yaml
---
context: Event-Stream
service: graphql-ingestion
ticket: https://goodscloud.atlassian.net/browse/TDP-4067
status: In Progress
created: 2026-08-24T10:57:00.000+02:00
tags:
  - NewStore
  - TIDE
  - GraphQL
---
```

- `context`: required. Must match the folder name. Unquoted unless it needs YAML quoting.
- `service`: optional. Service or area name.
- `ticket`: Jira URL when one exists; omit for `NO-TICKET`.
- `status`: `Open` · `In Progress` · `Blocked` · `Done`. Keep it short; extra detail belongs in the body.
- `created`: ISO-8601 with timezone. Set on create; do not change on update.
- `tags`: always include `NewStore` and `TIDE` when it is TIDE work. Add topic tags (`GraphQL`, `Kafka`, `Incident`, `SFCC`).

## Body template

Keep the first paragraph to 1–3 sentences: what happened and the current conclusion.

```markdown
One- or two-sentence summary.

Related: [[existing note]] · [[NS Specific Knowledge note]]

## Important links

* Slack: [channel or thread](url)
* Ticket: [TDP-1234](https://goodscloud.atlassian.net/browse/TDP-1234)
* GitLab: [project !mr](url)

## Context

Why this exists. Facts, not a diary.

## Notes

Working detail, commands, Dash0 links, decisions.
```

- Wikilink related Journal and Knowledge Base notes.
- Put Dash0 / GitLab / Slack URLs under **Important links** or a **Dash0** section (see `TDP-4067` for the incident style).
- Do not dump raw log walls. Quote the few lines that matter.

## Updates

- Append or revise the body; bump `status`.
- Do not rename the file unless the user asks.
- When a durable runbook or architecture falls out of the work, offer to promote it with `newstore-knowledge-base` instead of leaving it only in the ticket note. for long-lasting knowledge that is not Newstore specific, add it to /Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/Knowledge Base with proper categorization
- If the user asks to journal a 1:1, meeting, or Think strategic snapshot, switch to `newstore-notes`. Do not create a `NO-TICKET` Journal file for those.
