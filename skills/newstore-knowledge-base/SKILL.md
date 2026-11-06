---
name: newstore-knowledge-base
description: >-
  Writes durable notes in the Obsidian Knowledge Base: Newstore/TIDE
  architecture and runbooks under NS Specific Knowledge, and non-Newstore
  long-lasting knowledge under Aditya-Pro/Knowledge Base. Use when capturing
  knowledge that should outlive a ticket, updating NS Specific Knowledge, or
  promoting a Journal note into a reusable article. Do not use for strategy
  snapshots, 1:1s, or meeting recaps — those go to newstore-notes.
---

# Newstore Knowledge Base

Durable personal wiki. No ticket narrative. If it needs a TDP/SR key to make sense, it belongs in the Journal (`newstore-journal`). Strategy snapshots, 1:1s, and meeting recaps belong in Notes (`newstore-notes`).

Also read `obsidian-markdown` and `newstore-context`.

## Paths

```
KB="/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/NewStore/NS Specific Knowledge"
GENKB="/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/Knowledge Base"
```

Write files directly with `Write` / `StrReplace` on the path that matches the routing below. Use `obsidian` CLI only if Obsidian is open.

## Routing

- Newstore-specific (TIDE, tenants, NS services, NS runbooks) → `$KB`.
- for long-lasting knowledge that is not Newstore specific, add it to /Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/Knowledge Base with proper categorization

Proper categorization: put the note in an existing `$GENKB` topic folder (`Airflow`, `AWS`, `BigQuery`, `Data Engineering`, `Data Vault`, `Docker`, `GCP`, `Gitlab Runner`, `Interview Preparation`, `Java`, `Kafka`, `Kubernetes`, `Node`, `Python`, `RabbitMQ`, `Shell`, `Spark`, `Terraform`, …). Create a new topic folder only when none fits. Do not leave generic tooling under `NewStore/NS Specific Knowledge`.

`$GENKB` frontmatter uses `tags: knowledge-base` plus the folder name. Do not add `NewStore` / `TIDE` tags there.

## What belongs here

Write or update a KB note when the content would still be true in six months without a ticket id:

- Architecture (how a system is wired)
- Runbooks (how to inspect Kafka, test E2E, find a cluster)
- Org maps (teams, services, GitLab groups)
- Lasting decisions (with date and source, not the debate)

Leave in Journal: RCA timelines, WIP, “what I did this week”, blocked-by lists, per-tenant firefighting.

Leave in Notes (`newstore-notes`): Think strategic, 1:1s, meeting recaps.

## Before writing

1. `Grep` `$KB` and `$GENKB` for the topic. Update the existing note if found. Choose `$KB` vs `$GENKB` using Routing above.
2. `Grep` `$JOURNAL` for related tickets. Wikilink them as sources; do not copy the ticket story into the KB.
3. If the note would duplicate Document360 or Confluence, prefer a short local summary plus a link, unless the user wants a personal runbook with commands those docs lack.

## Filename and folder

Descriptive title, no ticket key.

```
GraphQL Architecture.md
Check Kafka events by topic name.md
MSK Clusters.md
```

| Folder | `context` | Use for |
|---|---|---|
| `Event Stream` | `Event-Stream` | Kafka, MSK, event-receiver, producers, stream runbooks |
| `GraphQL` | `GraphQL` | GraphQL architecture and standing behavior |
| `SFCC` | `SFCC` | SFCC catalog/import standing knowledge |
| `NewStore` | `NewStore` | Org-wide maps, team landscape |

Folder names use a **space** (`Event Stream`). The `context` property uses a **hyphen** (`Event-Stream`) to match Journal. Do not invent a third spelling.

## Frontmatter

```yaml
---
context: Event-Stream
created: 2026-08-21T14:44:00.000+02:00
tags:
  - NewStore
  - TIDE
  - GraphQL
  - Kafka
---
```

- `context`: required. Hyphenated values as above.
- `created`: set on create; do not change on update.
- `tags`: always `NewStore`; add `TIDE` for TIDE systems; add topic tags.
- No `ticket` or `status` properties on KB notes.

## Body

Lead with what the thing **is**, in 2–4 sentences. Then structure, commands, and diagrams.

```markdown
One-paragraph definition of the system or procedure.

Related: [[Team and Service Landscape]] · [[MSK Clusters]] · [[relevant Journal note]]

Source: Confluence/GitLab/Dash0 pointers (so a later reader can re-verify).

# Heading that names the idea

Tables, mermaid, commands. Prefer copy-pasteable commands over prose.
```

- Wikilink other KB notes and the Journal notes that justified a change.
- Use mermaid for paths (see `GraphQL Architecture.md`).
- Call out environment differences (staging vs production) in tables, not in the title.
- When a fact is time-sensitive (cluster migration, restructure), put the date in the sentence: `Contacts last updated 22 Jul 2026`.

## Updates vs new notes

- Same system, new fact → update the existing note.
- New procedure that does not fit → new note, wikilink both ways.
- After a Journal ticket ships a lasting change (URL, cluster, architecture), update the KB in the same session when the user is capturing knowledge — or ask once if it was not requested.
