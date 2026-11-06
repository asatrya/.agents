# Data Request Pipeline — Architecture Overview

End-to-end pipeline for fulfilling ad-hoc data requests using dbt, cloud storage, and Jira.

## Pipeline stages

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Orchestrator (n8n / Temporal)                    │
│                                                                         │
│  ┌───────────┐   ┌────────────────┐   ┌──────────┐   ┌──────────────┐ │
│  │  Trigger  │──▶│  Stage 1:      │──▶│  Gate:   │──▶│  Stage 2:    │ │
│  │           │   │  Analyze &     │   │  Human   │   │  Build,      │ │
│  │  • Jira   │   │  generate      │   │  approve │   │  export,     │ │
│  │    webhook│   │  models        │   │          │   │  sign URLs   │ │
│  │  • Manual │   │                │   │          │   │              │ │
│  │  • API    │   │  (AI + Skill1) │   │  (Jira)  │   │  (MCP tools) │ │
│  └───────────┘   └────────────────┘   └──────────┘   └──────┬───────┘ │
│                                                              │         │
│                                                              ▼         │
│                                                       ┌──────────────┐ │
│                                                       │  Stage 3:    │ │
│                                                       │  Deliver     │ │
│                                                       │  (post URLs  │ │
│                                                       │   to Jira)   │ │
│                                                       └──────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## Component mapping

| Component | Type | Purpose | Stateless? |
|-----------|------|---------|-----------|
| **fulfilling-data-requests-with-dbt** | AI Skill | Analyze request, map fields to manifest, generate dbt models | Yes |
| **executing-data-extract** | AI Skill | Orchestrate build → validate → export → deliver within IDE | Yes |
| **dbt-runner** | MCP Server | Execute dbt CLI commands (build, compile, show, test) | Yes |
| **cloud-storage** | MCP Server | Export data to GCS, generate signed URLs, list objects | Yes |
| **jira-connector** | MCP Server | Fetch tickets, post comments, transition issues | Yes |
| **n8n / Temporal** | Orchestrator | Glue: trigger → AI → gate → execute → deliver | Stateful |

## When to use what

### AI Skills (reasoning required)

Use skills when the step requires **judgment, ambiguity handling, or interpretation**:

- Analyzing a data request against the dbt manifest (coverage mapping)
- Interpreting build failures (is it a SQL error? permission issue? data problem?)
- Deciding whether partial coverage is acceptable
- Generating dbt SQL models with correct joins, filters, and grain

### MCP Tools (deterministic actions)

Use MCP tools when the step is a **well-defined operation with clear inputs/outputs**:

- Running `dbt build --select <selector>`
- Exporting a table to GCS
- Generating a signed URL
- Posting a comment to Jira

### Orchestrator (state + flow control)

Use the orchestrator when you need:

- **Triggers**: React to a Jira webhook, schedule, or API call
- **State persistence**: Remember where the pipeline is across minutes/hours
- **Human-in-the-loop**: Post a question to Jira, wait for a reply, then continue
- **Retries and timeouts**: Retry a failed dbt build, timeout after N minutes
- **Fan-out**: Process multiple tables/tenants in parallel

## Data flow

```
Jira ticket (TDP-2484)
  │
  ▼
[Orchestrator: extract ticket body, fields, attachments]
  │
  ▼
[AI Agent + Skill 1: analyze coverage, generate models]
  │
  ├── Field coverage.md
  ├── Request_Response.md
  ├── models/*.sql
  └── schema.yml
  │
  ▼
[Orchestrator: post coverage report to Jira, wait for approval]
  │
  ▼
[MCP dbt-runner: dbt build --select path:models/ad_hoc/TDP-2484/*]
  │
  ▼
[MCP dbt-runner: dbt_get_run_results() → validate success + row counts]
  │
  ▼
[MCP cloud-storage: export_bigquery_to_gcs(table, bucket, prefix)]
  │
  ▼
[MCP cloud-storage: generate_signed_urls_for_prefix(bucket, prefix)]
  │
  ▼
[MCP jira-connector: post_comment(TDP-2484, signed_urls_table)]
  │
  ▼
[Orchestrator: transition ticket to "Done" or "Delivered"]
```

## Deployment models

### Model A: IDE-centric (Phase 1)

Everything runs in the IDE (Cursor / Claude Desktop). The user triggers each step.

- Skills provide the reasoning
- Scripts (`export_to_gcs.py`, `generate_signed_url.py`) run locally
- No orchestrator needed
- Human is the orchestrator

### Model B: MCP-enabled (Phase 2)

MCP servers run as sidecar processes. The AI agent calls them as tools.

- Skills still provide reasoning
- MCP servers handle execution (dbt, storage, Jira)
- Agent can run the full pipeline in one conversation
- Human approves at gate points

### Model C: Fully automated (Phase 3)

Orchestrator (n8n/Temporal) manages the pipeline end-to-end.

- Jira webhook triggers the workflow
- Orchestrator calls AI agent API for analysis (Stage 1)
- Orchestrator posts coverage report, waits for human approval
- Orchestrator calls MCP tools for execution (Stage 2)
- Orchestrator posts results to Jira (Stage 3)
- Human only intervenes at the approval gate

## n8n workflow sketch

See [n8n-workflow-reference.json](n8n-workflow-reference.json) for an importable workflow skeleton.

Key n8n nodes:

1. **Webhook Trigger** — receives Jira webhook on ticket creation/update
2. **HTTP Request** — calls AI agent API with ticket body
3. **Wait** — pauses for human approval (polls Jira comment or uses webhook callback)
4. **Code** — calls MCP tools via HTTP or subprocess
5. **HTTP Request** — posts signed URLs to Jira
6. **IF** — error handling branches (retry or escalate)

## Security considerations

- **Signed URLs**: 7-day max expiry; rotate if needed. Don't embed in Jira description (comments are better — access controlled).
- **Jira API token**: Store in orchestrator secrets, not in code.
- **GCS credentials**: Use workload identity in production; service account key only for development.
- **PII**: The fulfilling skill already flags PII fields. The orchestrator should enforce that PII-flagged fields require explicit approval before export.
