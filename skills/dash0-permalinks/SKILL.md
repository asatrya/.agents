---
name: dash0-permalinks
description: >-
  Finds an existing Dash0 dashboard or builds a Query Builder fallback and always
  returns a permanent link. When changing a Dash0 dashboard (Perses YAML in
  dash0-platform-config or live Dash0), always give paste-ready PromQL to try.
  Dataset is staging or production from prompt context. Use when the user asks
  for a Dash0 link, permalink, dashboard URL, query-builder share, PromQL/logs/traces
  view, or when editing Dash0 dashboard queries.
---

# Dash0 permalinks

## Guideline

Find a relevant existing dashboard for the asked view and context. If a dashboard exists, set the time period to the fixed interested period. If none exists, use Dash0 Query Builder (or the matching logs/traces explorer) and provide the queries. In both cases, share the permanent link.

When changing dashboard in dash0, always give me the promql that I can paste and try.

## Workflow

1. Identify **what** to show (metric, logs, traces, RED, a named service/pod), the **interested period** (from/to from the user or ticket), and the **dataset** from prompt context: `staging` or `production`. Do not default to production. Use the env named in the prompt, ticket, cluster, job, or URL; if both or neither are in scope, ask.
2. Search existing Dash0 dashboards (`listDashboards` on `user-dash0`; inspect GetDynamicTools first). Use GitLab `dash0-platform-config` for panel queries when the live definition is unclear. Do not invent dashboard ids or names.
3. If a relevant dashboard exists: set `from`/`to` to the interested period, set dashboard variables so the asked series are actually selected, share a **permanent link**.
4. If none exists: open Query Builder (metrics) or the matching explorer (logs/traces). Provide the query in the reply. Share a permanent link **and** the query — Query Builder deeplinks cannot embed PromQL.
5. Always return clickable permanent URLs. Grafana MCP/skills are the wrong product.
6. After any Dash0 dashboard edit (Perses YAML or live), paste every changed panel query in the reply with `$variables` expanded to the All / default values so the user can try them in Query Builder. Include the Query Builder link. Query Builder cannot embed PromQL.

## Paste-ready PromQL after dashboard edits

- Expand `$container` / other list variables to their `customAllValue` (often `.+`) unless the user asked for a specific selection. Keep `=~` on those expanded variables; do not turn a literal such as `service_namespace="event-stream"` into `=~`.
- Dataset matches prompt context (`staging` or `production`); put it in the Query Builder URL.
- One fenced `promql` block per panel, labeled with the panel name.

## Permalinks

Org: `a7bab625-e089-4307-a00f-a8531ac46c97`. Dataset: `staging` or `production` from prompt context (permalinks, MCP `dataset`, and PromQL all use the same one).

- Dashboard share (preferred when variables matter): `https://app.dash0.com/dashboards?org=<org>&s=<zlib+urlsafe-b64>` encoding dataset, from, to, dashboard id, variables
- Simple dashboard deeplink when vars are not needed: `/goto/dashboards?...&dashboard_id=...&from=...&to=...`
- Query Builder: `https://app.dash0.com/goto/metrics/query-builder?org=...&dataset=...&from=...&to=...` — **cannot embed PromQL**; paste the query; user can CMD+SHIFT+D for a live share link
- Do **not** treat `/goto/metrics/explorer?...` JSON `filter=` URLs as reliable (colon encoding / login redirect has failed)
- Do **not** invent `s=` JSON keys for Query Builder (`{tab, query}` is ignored)

## Query fallback

Build PromQL with `promql` / `getMetricQuery` on `user-dash0`. Match metric names and attributes that actually exist (OTel kubeletstats is not cAdvisor). Follow `newstore-dash0-dashboards` for matcher tightness: `=` for a single known value; `=~` only for `$variables` or a real pattern. App counters / RED / traces / logs use `service_name` and `service_namespace`; CPU, memory, restarts, cAdvisor use `k8s_container_name` and `k8s_namespace_name`.

Do not use `cpu="total"` on `container.cpu.usage` — that attribute is absent; the matcher returns zero series.

## MCP

`user-dash0` — `listDashboards`, `promql`, `getMetricQuery`, `getLogRecords`, `getSpans`, `searchKnowledgeBase`. Inspect schemas before calling.

## Known TIDE dashboards (examples, not the only targets)

Do not invent others. Search first; use these only when they match the ask.

- Tide **CPU & Memory** / `cpu-and-memory`, id `1def812c-71ff-46af-bb9a-1860c111c950`, folder `/Teams/Tide/Data`. Namespace `team-data-provisioning`. Group by `k8s_container_name` (not pod). All is `.+` scoped to that namespace.
- Event Stream **throughput** `cee814e7-6847-4b78-9d61-136d25f79446` — throughput, not CPU/memory.

CPU / memory PromQL when no dashboard fits (extend the container regex for other pods):

```
sum by (k8s_container_name) ({otel_metric_name = "container.cpu.usage", otel_metric_type = "gauge", k8s_container_name =~ "^(event-receiver|stream-publisher)$", k8s_namespace_name = "team-data-provisioning"})
```

```
sum by (k8s_container_name) ({otel_metric_name = "container.memory.working_set", otel_metric_type = "gauge", k8s_container_name =~ "^(event-receiver|stream-publisher)$", k8s_namespace_name = "team-data-provisioning"})
```
