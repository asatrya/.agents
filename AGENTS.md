# Agent Context Routing

## Context selection

There are exactly two contexts: **Newstore** and **Personal**. Choose one context for each task; never apply both contexts to the same task.

Apply instructions in this order:

1. Follow the user’s instructions.
2. Follow the nearest applicable project-level `AGENTS.md` and any `_agents/` system it references.
3. Select the context using the rules below.

| Context | Select it when | Obsidian vault |
| --- | --- | --- |
| Newstore | The topic, workspace, ticket, or artifact concerns Newstore/TIDE, or the target is in the Newstore vault | `/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro` |
| Personal | The task is unrelated to Newstore/TIDE, or the target is in the Personal vault | `/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Notes` |

For note-editing tasks, the target vault is authoritative:

- A target in `Aditya-Pro` uses the Newstore context.
- A target in `Aditya-Notes` uses the Personal context.

If the task topic and target vault point to different contexts, treat that as a routing mismatch. Do not combine the contexts; confirm the intended context or target before editing.

Before doing any work, always state in writing which context you will use: **Newstore** or **Personal**. Do not proceed silently.

## Language output

For any context, whenever an agent provides or generates text in German—including emails, quotations, messages, or other reusable text—it must also provide an English translation alongside it.

## Google Workspace tools and account routing

For Gmail, Google Calendar, and Google Drive, always use connector/app tools. Do not use browser, Chrome, or computer use unless the user explicitly requests it. If the connector is unavailable, stop and report that the task cannot continue; do not fall back to browser-based access.

Account mapping:

- Personal: `aditya.satrya@gmail.com`
- Newstore/work: `autama@newstore.com`

Always verify the target account before creating, modifying, or sending anything.

## Newstore context

Use the Newstore context when the workspace, ticket, or topic concerns Newstore or TIDE, including:

- Event Stream
- GraphQL
- SFCC
- Airflow or dbt at Newstore
- Dash0
- Document360
- `gitlab.com/newstore`
- Jira Product Discovery
- Tickets beginning with `TDP-`, `NCS-`, `SR-`, `SD-`, `THQ-`, `FO-`, `CHEX-`, `CAM-`, or `PRD-`

### Event Stream repositories

When working in a repository under the `newstore/engineering/event-stream` GitLab group, also follow the Event Stream AI harness: read its README, then read and apply the relevant guidelines and rules, and use every skill that matches the task. The harness is at [event-stream/ai](https://gitlab.com/newstore/engineering/event-stream/ai/-/tree/main).

### Required context and research

When `omc-orchestrator` is active, the root must not read or search to satisfy this section. Delegate research to `omc-explorer` and note writes to `omc-writer`, and paste the constraints from `.cursor/rules/newstore-knowledge.mdc` into the Task prompt.

1. Before answering company-specific questions from memory, read and follow the `newstore-context` skill.
2. When an answer depends on current systems or prior work, search the mapped knowledge sources:
   - Obsidian Journal, Notes, and NS Specific Knowledge
   - Document360
   - Confluence
   - Jira Product Discovery
   - GitLab
   - Slack
   - Dash0
3. Do not invent tenant names, cluster IDs, URLs, owners, or other Newstore-specific details. If the available sources do not establish a fact, say so clearly.

### Newstore Obsidian vault

Store Newstore-related Obsidian notes under `NewStore/` (`Journal`, `Notes`, `NS Specific Knowledge`) in:

`/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/NewStore`

Long-lasting technical knowledge that is not Newstore-specific goes in `Aditya-Pro/Knowledge Base`.

When creating or updating personal notes about Newstore work, use the appropriate skill:

- `newstore-journal` for tickets and work-in-progress notes
- `newstore-notes` for strategy, 1:1s, and meeting notes
- `newstore-knowledge-base` for durable runbooks and architecture documentation

Do not write to Confluence, Document360, Slack, GitLab, or Jira Product Discovery unless the user explicitly asks you to do so.

## Personal context

Use the Personal context for work unrelated to Newstore/TIDE and for targets inside the Personal Obsidian vault:

`/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Notes`

For long-lasting personal knowledge, add it to:

`/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Notes/Knowledge Base`

Categorize notes appropriately and follow any more specific local instructions for the target path.

### Tadabbur Book

When the target is inside `Tadabbur Quran/Tadabbur Book/` within the Personal vault, read the following before creating or editing a note:

- `Tadabbur Quran/Tadabbur Book/_agents/README.md`
- `Tadabbur Quran/Tadabbur Book/_agents/BOOK.md`
- The applicable workflow in `Tadabbur Quran/Tadabbur Book/_agents/workflows/`
- The applicable skill in `Tadabbur Quran/Tadabbur Book/_agents/skills/`

Do not apply this system outside that path unless the user explicitly asks you to.

### Muhammadiyah DE — Sirah Nabawiyah

When the target is a Markdown article inside `Notulen Kajian/Muhammadiyah DE – Sirah Nabawiyah/` within the Personal vault, read the following before creating or editing the article:

- `Notulen Kajian/Muhammadiyah DE – Sirah Nabawiyah/_agents/README.md`
- All relevant rules in `Notulen Kajian/Muhammadiyah DE – Sirah Nabawiyah/_agents/rules/`
- `Notulen Kajian/Muhammadiyah DE – Sirah Nabawiyah/_agents/workflows/ringkasan-kajian.md`
- `Notulen Kajian/Muhammadiyah DE – Sirah Nabawiyah/_agents/skills/menulis-ringkasan-kajian-muhammadiyah/SKILL.md`

This system applies only to that collection. Do not classify its articles as manuscripts.

### All other personal-vault paths

Follow the user’s instructions and the applicable local instructions for the target project.

## Tasks outside both vaults

For tasks outside both Obsidian vaults, select Newstore or Personal from the subject matter. If neither applies, follow the applicable local project instructions without adding vault-specific routing.
