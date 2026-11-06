---
name: newstore-notes
description: >-
  Writes Newstore strategic notes, 1:1 notes, and meeting notes in the
  Obsidian Notes folder. Use when the user asks to capture strategy, Think
  strategic, 1:1s, meeting recaps, or "Newstore notes"; not for ticket RCAs
  or durable architecture.
---

# Newstore Notes

Ongoing personal notes that are not a ticket log and not a runbook.

Also read `obsidian-markdown` and `newstore-context`. Use `newstore-journal` for TDP/NCS/SR tickets and RCAs. Use `newstore-knowledge-base` for architecture and how-tos.

## Paths

```
NOTES="/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/NewStore/Notes"
```

Write files directly with `Write` / `StrReplace` on that path. Use `obsidian` CLI only if Obsidian is open.

## What belongs here

| Folder | Use for |
|---|---|
| `Strategic Now` | Strategy snapshots, Think strategic, next-important-things |
| `1:1 Notes` | Recurring 1:1s (Gio, peers) |
| `Meeting Notes` | Named meetings that are not a 1:1 |

Create the folder if it is missing. Other subfolders under `$NOTES` are allowed; match an existing name before inventing one. Ask if the kind is unclear.

Do **not** put ticket RCAs, load-test logs, or incident timelines here — those stay in Journal. Do **not** put standing architecture or runbooks here — those stay in NS Specific Knowledge (Newstore-specific) or Knowledge Base (not Newstore-specific). for long-lasting knowledge that is not Newstore specific, add it to /Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/Knowledge Base with proper categorization

## Before writing

1. `Grep` `$NOTES` for the topic, person, or meeting name. Update the existing note if found.
2. `Grep` `$JOURNAL` and `$KB` for related tickets or systems. Wikilink them; do not copy the ticket story into Notes.
3. If the user said “Newstore notes” plus a kind (`strategic now`, `1:1`, meeting), write here even if a similar Journal note exists.

## Filename

No ticket prefix. Create the folder if needed.

```
Strategic Now/{Title}.md
1:1 Notes/{Person}.md
Meeting Notes/{YYYY-MM-DD} – {Topic}.md
```

- En-dash with spaces in meeting titles: ` – `
- One rolling note per 1:1 person (`Gio.md`). Append dated headings; do not create a new file per meeting unless asked.
- Strategic titles are descriptive (`Strategic now.md`), not `NO-TICKET – …`.

## Frontmatter

```yaml
---
type: strategic
created: 2026-08-26T18:40:00.000+02:00
tags:
  - NewStore
  - TIDE
  - Strategy
---
```

- `type`: `strategic` · `1on1` · `meeting`. Required.
- `person`: required on 1:1 notes (display name).
- `created`: set on create; do not change on update.
- `tags`: always `NewStore`; add `TIDE` for TIDE work; add `Strategy`, `1on1`, or `Meeting`.
- No `ticket` or `status` properties.

## Body

Lead with 1–3 sentences: what this note is and the current conclusion.

```markdown
One- or two-sentence summary.

Related: [[Journal ticket note]] · [[KB note]]

## Important links

* Slack: [thread](url)
* Calendar / deck: [url]

## Notes

Working detail. For 1:1s, use dated headings (`## 2026-08-26`).
```

Wikilink Journal tickets that the strategy depends on. Keep time-sensitive facts dated in the sentence (`PED 18 Aug 2026: Event Stream 65%`).

## Updates

- Append or revise in place. For 1:1s, add a new dated heading at the top of **Notes**.
- Do not rename the file unless the user asks.
- If a lasting architecture fact falls out of a strategic note, offer to promote it with `newstore-knowledge-base`. for long-lasting knowledge that is not Newstore specific, add it to /Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/Knowledge Base with proper categorization
