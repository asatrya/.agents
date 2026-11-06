---
name: newstore-context
description: >-
  Routes Newstore/TIDE work to the right knowledge sources and searches them
  on demand. Use when the repo, ticket, or topic is Newstore, TIDE, Event
  Stream, GraphQL, SFCC, Airflow/dbt at Newstore, Dash0, Document360,
  Confluence, GitLab newstore, Jira Product Discovery, product roadmap,
  initiatives, or tickets TDP-/NCS-/SR-/SD-/THQ-/FO-/CHEX-/CAM-/PRD-.
  When capturing strategy, 1:1s, or meeting notes, use newstore-notes.
  When capturing or reading TickTick to-dos in this context, use only space Work.
  After reading this skill, apply Mandatory skill routing — read every matching
  newstore-* skill (e.g. newstore-git for MRs and Jira web links) before acting.
---

# Newstore context router

Do not answer Newstore facts from memory when a source can be checked. Search, then cite.

## Mandatory skill routing

On every Newstore/TIDE task:

1. Read **this** skill.
2. Match the task to the table below. **Read every matching skill in full** before tools, MCP, or code changes. Skipping a matched row is not allowed.
3. In chat, announce `newstore-context` and **each** routed skill by name (for example `newstore-git`).

| If the task involves… | Also read |
|---|---|
| Branch, commit, push, MR, GitLab, **Jira web/remote link for an MR**, listing MRs on a ticket | **`newstore-git`** |
| AWS CLI, IAM, Terragrunt, MSK/S3 in Newstore AWS repos | `newstore-aws-cli` |
| Dash0 dashboard YAML / PromQL panels in platform config | `newstore-dash0-dashboards` |
| Dash0 permalink / dashboard URL formatting | `dash0-permalinks` |
| Ticket/WIP journal note | `newstore-journal` |
| Strategy, 1:1s, meeting recaps | `newstore-notes` |
| Durable Newstore runbook or architecture note | `newstore-knowledge-base` (`$KB`) |
| Durable note not specific to Newstore | `newstore-knowledge-base` (`$GENKB`) |
| TickTick to-do in Work space | `tick-tick-create-todo` |
| Kafka internals (beyond routing) | `kafka-engineer` |
| Bugs / incidents / production symptoms | `systematic-debugging` |
| dbt / BigQuery at Newstore | existing dbt/BigQuery skills |

When you add a new `newstore-*` skill, add a row here, create it under `~/.agents/skills/`, and symlink from `~/.cursor/skills/` (same pattern as `newstore-journal` → `~/.agents/skills/newstore-journal`). Canonical copy lives in `~/.agents/skills`; do not duplicate files in `~/.cursor/skills`.

## Vault paths

Obsidian vault: `Aditya-Pro`

```
NS="/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/NewStore"
JOURNAL="$NS/Journal"
NOTES="$NS/Notes"
KB="$NS/NS Specific Knowledge"
GENKB="/Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/Knowledge Base"
```

Org map (who owns what): `$KB/NewStore/Team and Service Landscape.md`

Prefer `Grep` / `Read` on those absolute paths. Use `obsidian` CLI only if Obsidian is open (`obsidian vault="Aditya-Pro" search query="..."`).

## Source map

| Need | First | Then | MCP |
|---|---|---|---|
| Prior personal work, RCA, ticket narrative | **Journal** | Slack, Jira | filesystem, then `plugin-atlassian-atlassian`, `plugin-slack-slack` |
| Strategy, 1:1s, meeting recaps | **Notes** | Journal, Slack | filesystem |
| Durable how-it-works, runbooks (Newstore-specific) | **NS Specific Knowledge** | Confluence | filesystem, then Atlassian |
| Durable how-it-works that is not Newstore-specific | **Knowledge Base** | existing topic folder | filesystem |
| Official product behavior | **Document360** | Confluence | `user-Document360` |
| Roadmap, planned work, product ideas | **Jira Product Discovery** | Slack, Confluence | Atlassian `search` / JQL `project = PRD` |
| Internal process, ADRs, team pages | **Confluence** | Slack | Atlassian `search` |
| Code, MRs, CI, GitLab issues | **local repo + GitLab** | Confluence | `plugin-gitlab-GitLab` |
| Live logs, traces, RED, incidents | **Dash0** (read tools) | Slack, Journal | `user-dash0` |
| People, recent discussion | **Slack** | Confluence | Slack search |

Do not preload these sources. Query only what the current question needs.

## Search order

1. Ticket / service / keyword in `$JOURNAL`, `$NOTES`, and `$KB`. For non-Newstore tooling (Spark, Kafka, Python, …), also `$GENKB`.
2. Official or internal docs via the table above.
3. Code in the current repo; GitLab MCP if the clone is missing or you need MRs/CI.
4. Live telemetry last, and only for symptoms (not for architecture).

Stop when you have a cited answer. Say which source you used.

## MCP cheatsheet

**Document360** (`user-Document360`): `document360-mcp-search` then `document360-mcp-get-article`.

**Atlassian** (`plugin-atlassian-atlassian`): `search` for mixed Jira/Confluence. Site `goodscloud.atlassian.net`. TIDE Jira is **TDP**; Confluence space **TIDE**. Product ideas are **PRD** (Jira Product Discovery). Use `getJiraIssue` / `getConfluencePage` after you have an id. Use CQL/JQL tools only when the user asks for CQL/JQL, except for PRD: `project = PRD` is the lookup when the question is roadmap, planned work, or product ideas.

Canonical JPD views (cite these; Polaris views are not Confluence pages):

- Jira Product Discovery (planned work / feature overview): https://goodscloud.atlassian.net/jira/polaris/projects/PRD/ideas/view/12326396
- idea backlog: https://goodscloud.atlassian.net/jira/polaris/projects/PRD/ideas/view/12326392

Do not use Productboard. It is deprecated.

**GitLab** (`plugin-gitlab-GitLab`): `search` or `semantic_code_search`. Host `gitlab.com/newstore`. TIDE groups include `newstore/engineering/data/services`, `newstore/engineering/dre`, `newstore/engineering/event-stream`.

**Slack** (`plugin-slack-slack`): `slack_search_public_and_private` for internal work; `slack_read_thread` / `slack_read_channel` after you have ids. Workspace `newstoreinc`.

**Dash0** (`user-dash0`): org `a7bab625-e089-4307-a00f-a8531ac46c97`. Dataset is `staging` or `production` from prompt context — do not assume production. Known value (a count, a percentile, a named metric) → `getMetricQuery` / `promql` / `getLogRecords` / `getSpans` / `getServiceDetails`. Open-ended “why is X broken?” → ask before `runTask` (Agent0 is billed). Setup questions → `searchKnowledgeBase`. Dash0 link / permalink / dashboard URL → `dash0-permalinks`.

## Write policy

- Personal notes: `newstore-journal` (tickets/WIP), `newstore-notes` (strategy, 1:1s, meetings), or `newstore-knowledge-base` (runbooks/architecture).
- for long-lasting knowledge that is not Newstore specific, add it to /Users/autama/Library/CloudStorage/GoogleDrive-aditya.satrya@gmail.com/My Drive/Personal/Obsidian-Vault/Aditya-Pro/Knowledge Base with proper categorization
- Do **not** create/edit Confluence, Document360, Slack, GitLab, or Jira Product Discovery unless the user explicitly asks.
- Do not invent cluster ids, tenant names, URLs, or owners. Look them up.

## TickTick (`tick-tick-create-todo`)

When this skill is in effect, TickTick reads and creates stay in space `Work` only.

- Follow `tick-tick-create-todo` for title, list, due date, prefixes, and tags.
- Do not list, search, read, or create items in other TickTick spaces (Personal, Family, Money, Mission, Wellbeing, and so on).
- Do not ask which space to use. `Work` is required.

## Related skills

See **Mandatory skill routing** above. That table is the canonical index of `newstore-*` and companion skills.
