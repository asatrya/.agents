---
name: doc-persona
version: 1.0.0
user-invocable: true
description: Guide users through a structured workflow for co-authoring documentation. Trigger when user wants to write documentation, proposals, technical specs, decision docs, or similar structured content. This workflow helps users efficiently transfer context, refine content through iteration, and verify the doc works for readers. Trigger when user mentions writing docs, creating proposals, drafting specs, or similar documentation tasks.
argument-hint: <persona-type> [persona name or description]
allowed-tools: Read, Grep, Glob, Bash(vale *)
---


# Documentation personas

Use this table to understand which user and persona groups currently use NewStore documentation.


| Persona Group                        | Roles / Titles                                                                 |
|--------------------------------------|-------------------------------------------------------------------------------|
| Store Staff                          | Store Associate; Store Manager; District Manager / Regional Manager          |
| Implementers (SI Partners and IT)    | Solution Architect; Developer / Solution Engineer; Engagement Manager (Project Manager) |
| Support (SI Partners & Retail IT)    | Level‑one Tech Support; Level‑two Tech Support                                |
| HQ or product manager                | Retail Operations; Change Management / Product Owner; Global Inventory Controller / Global Fulfillment Manager; Business Intelligence Specialist / System Analyst; Merchandiser (Buyer & Seller); Finance; Sales / Marketing |
| NewStore stakeholder                 | OSM; Expert Services; Support; Sales; Marketing; Engineering, includes personas like brand executive or retail operations                |

For a context of preferences for each persona, see [this section](#persona-preferences).

---

## Key questions for each persona

Use this table to understand what questions a user of the docs would typically ask, where a `Yes` means that this user persona will ask this questions, and a `No` means they won't.

Use these questions to better understand how a user benefits from reading the docs or content you are create or review. Note that these are only hints and are not absolute concrete directions.

> Legend: ✔ = Yes, - = No

| Category         | Questions to address                                           | Store Staff | Implementers | L1 Tech Support | L2 Tech Support | HQ – PO/Retail Ops/Fulfillment | HQ – BI | HQ – Merchandiser | HQ – Finance/Sales/Marketing | NS – OSM/Expert/Support | NS – Sales/Marketing | NS – Engineering |
|------------------|----------------------------------------------------------------|------------|-------------|----------------|----------------|---------------------------------|--------|-------------------|-----------------------------|-------------------------|----------------------|------------------|
| Release details  | When and where is the feature available                       | ✔          | ✔           | -              | -              | ✔                               | -      | -                 | -                           | -                       | -                    | -                |
| Release details  | Inventory reports (when using NewStore for inventory)         | -          | -           | -              | -              | -                               | -      | ✔                 | -                           | -                       | -                    | -                |
| Release details  | Inventory functionality details – receiving and transferring  | -          | -           | -              | -              | -                               | -      | ✔                 | -                           | -                       | -                    | -                |
| Release impact   | What is changing in my day‑to‑day work                        | ✔          | ✔           | ✔              | ✔              | ✔                               | ✔      | ✔                 | ✔                           | ✔                       | ✔                    | ✔                |
| Release impact   | What are the dependencies or prerequisites                    | -          | ✔           | ✔              | ✔              | ✔                               | -      | -                 | -                           | ✔                       | -                    | ✔                |
| Release impact   | What is the rollout / migration plan                          | -          | ✔           | ✔              | ✔              | ✔                               | -      | -                 | -                           | ✔                       | ✔                    | ✔                |
| Usage basics     | How do I perform my core tasks with this feature              | ✔          | ✔           | ✔              | ✔              | ✔                               | -      | -                 | -                           | ✔                       | -                    | ✔                |
| Usage basics     | What are the main limitations / known issues                  | ✔          | ✔           | ✔              | ✔              | ✔                               | ✔      | ✔                 | ✔                           | ✔                       | ✔                    | ✔                |
| Configuration    | How do I configure or customize this feature                  | -          | ✔           | ✔              | ✔              | ✔                               | -      | -                 | -                           | ✔                       | -                    | ✔                |
| Troubleshooting  | How do I identify and fix common problems                     | ✔          | ✔           | ✔              | ✔              | ✔                               | ✔      | -                 | -                           | ✔                       | -                    | ✔                |
| Data & reporting | What reports or metrics are available                         | -          | ✔           | ✔              | ✔              | ✔                               | ✔      | ✔                 | ✔                           | ✔                       | ✔                    | ✔                |
| Data & reporting | How do I interpret these reports or metrics                   | ✔          | ✔           | ✔              | ✔              | ✔                               | ✔      | ✔                 | ✔                           | ✔                       | ✔                    | ✔                |
| Integration      | How does this feature interact with other NewStore products   | -          | ✔           | ✔              | ✔              | ✔                               | ✔      | ✔                 | ✔                           | ✔                       | ✔                    | ✔                |
| Integration      | How does this feature integrate with external systems         | -          | ✔           | ✔              | ✔              | ✔                               | ✔      | ✔                 | ✔                           | ✔                       | ✔                    | ✔                |
| Security & access| Who has access and what permissions are required              | ✔          | ✔           | ✔              | ✔              | ✔                               | ✔      | ✔                 | ✔                           | ✔                       | ✔                    | ✔                |
| Security & access| How is data secured or audited                                | -          | ✔           | ✔              | ✔              | ✔                               | ✔      | -                 | ✔                           | ✔                       | ✔                    | ✔                |
| Training         | What training materials are available                         | ✔          | ✔           | ✔              | ✔              | ✔                               | -      | -                 | -                           | ✔                       | ✔                    | ✔                |
| Training         | How long does it take to become proficient                    | ✔          | ✔           | ✔              | ✔              | ✔                               | -      | -                 | -                           | ✔                       | ✔                    | ✔                |



## Persona preferences

View these persona preferences **only** for context, not to actively influence content authoring for these personas.

### Product Manager Newstore
Product Manager oriented to the retail context.
#### Prefer
- analytics
- CSVs, XLSX, PDF
- desktop applications
- web applications
#### Avoid
- heavy technical jargon
- JSON, YAML, XML
- terminals or command-line

---

### Store Manager
Oversees daily store operations, staff, and sales performance.
#### Prefer
- dashboards and KPI summaries
- mobile and tablet apps
- shift scheduling tools
- real-time alerts
#### Avoid
- raw data
- technical configurations
- command-line tools

---

### Store Associate
Front-line staff handling customers, inventory, and transactions.
#### Prefer
- simple mobile apps
- step-by-step workflows
- visual guides and checklists
- POS interfaces
#### Avoid
- complex reports
- back-office systems
- any technical tooling

---

### System Integrator
Technical consultant connecting retail platforms and data pipelines.
#### Prefer
- APIs and webhooks
- JSON, YAML, XML
- terminals and CLI tools
- technical documentation
#### Avoid
- business narrative summaries
- oversimplified UI flows
- non-exportable data

---

### Brand Executive
Senior stakeholder focused on brand performance, growth, and strategy.
#### Prefer
- executive summaries and decks
- high-level trend reports
- PDF and presentation formats
- visual storytelling
#### Avoid
- granular operational data
- technical jargon
- raw exports or logs

---

### Retail Operations
Coordinates cross-store processes, inventory flow, and operational efficiency.
#### Prefer
- operational dashboards
- CSV and XLSX exports
- process documentation
- inventory and logistics tools

#### Avoid
- high-level strategy abstractions
- heavy technical configurations
- command-line tools
