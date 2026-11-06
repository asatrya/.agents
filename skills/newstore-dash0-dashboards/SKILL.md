---
name: newstore-dash0-dashboards
description: >-
  Newstore conventions for Dash0 PersesDashboard YAML and PromQL panels in
  dash0-platform-config (TIDE, Event Stream, and other teams). Use when creating
  or editing a Newstore Dash0 dashboard, adding or changing panels or PromQL
  queries, or when a chart shows disconnected dots or gaps at short time ranges.
---

# Newstore Dash0 dashboards

Dashboards are `PersesDashboard` YAML under `teams/<team>/dashboards/` or `platform/dashboards/`.
ArgoCD syncs every file to both datasets (staging and production); the Dash0 UI folder is set by
the `dash0.com/folder-path` annotation, not the git path.

## Rules

### Use `$__rate_interval` with `minStep: 2m` for rate()/increase()/delta()

Write `[$__rate_interval]` in every range-vector query and set `minStep: 2m` on that query's
`PrometheusTimeSeriesQuery` spec. Do not add an `interval` dashboard variable and do not
hard-code `[5m]` in panel queries.

```yaml
kind: TimeSeriesQuery
spec:
  plugin:
    kind: PrometheusTimeSeriesQuery
    spec:
      datasource:
        kind: PrometheusDatasource
      minStep: 2m
      query: sum by (tenant) (rate(sales_order_created_count_total[$__rate_interval]))
```

```yaml
# Bad: no minStep, so at short time ranges the step (and $__rate_interval) drops below the
# 60s collection interval, rate() sees one sample and the chart shows disconnected dots
query: sum by (tenant) (rate(sales_order_created_count_total[$__rate_interval]))

# Bad: a fixed window is noisy at 30 days and hides spikes at 30 min
query: sum by (tenant) (rate(sales_order_created_count_total[5m]))

# Bad: a home-made variable duplicates what $__rate_interval + minStep already does
query: sum by (tenant) (rate(sales_order_created_count_total[$interval]))
```

Why: Dash0 derives `$__rate_interval` from the query step. `minStep` clamps the step, so
`$__rate_interval` never shrinks below 2x the collection interval and `rate()` always has at least
two samples. See
[Range misaligned to collection intervals](https://www.dash0.com/docs/dash0/telemetry/metrics/common-metric-query-issues#range-misaligned-to-collection-intervals).

`minStep` must be at least 2x the collection interval. Measured in the production dataset on
2026-08-26 (samples per minute per series):

| Metric source | Collection interval | `minStep` |
|---|---|---|
| Istio (`istio_requests_total`), app counters, cAdvisor | 60s | `2m` |
| CloudWatch (`aws_*`, via `dash0-metric-stream`) | 60s | `2m` |
| API gateway (`api_gateway_requests_total`, vector) | 30s | `2m` |
| Slow cron-job metrics | job period | 2x the period |

Re-measure before assuming: `count_over_time(<metric>[10m]) / 10` gives samples per minute.

Fixed windows are allowed only where the window is part of the panel's meaning, e.g. a
"1d SLI" stat panel that must always compute over exactly one day. Say so in the panel name.

`$__range` is fine: it is the whole selected time range and is used for "total over the
period" stat panels.

### Use `$__interval` for avg_over_time() and other non-rate aggregations

`$__rate_interval` is only for `rate()`, `increase()`, and `delta()`. For `avg_over_time()`,
`max_over_time()`, `min_over_time()`, and other range-vector aggregations, use `$__interval`
instead, with the same `minStep` as above.

```yaml
# Good
query: avg_over_time(sales_order_created_count_total[$__interval])

# Bad: a fixed window falls out of alignment with the chart's actual step size, so the window
# either misses part of the data (window narrower than the step) or double-counts (wider)
query: avg_over_time(sales_order_created_count_total[2m])
```

Why: Dash0 picks the step size dynamically from the selected time range and chart width.
`$__interval` and `$__rate_interval` both track the current step size; a hard-coded window
does not. See
[Range misaligned to step sizes](https://www.dash0.com/docs/dash0/telemetry/metrics/common-metric-query-issues#range-misaligned-to-step-sizes).

### Dashboards exported from the Dash0 UI

The UI export already writes `$__rate_interval` but omits `minStep`. Add `minStep: 2m` to every
`PrometheusTimeSeriesQuery` spec that uses a range vector before committing.

### Thresholds must agree across panels

Where two panels on one dashboard measure the same operation from opposite sides (success rate
and error rate sum to 1), set thresholds so both panels show the same colour at the same moment.
If success turns orange at 95-98%, error turns orange at 2-5%; if success turns red below 95%,
error turns red above 5%.

Dash0 compares thresholds against the raw query value. A ratio query returns 0.0-1.0, so write
threshold values as decimals: 99% is `0.99`, not `99`. `mode: percent` in Perses means
"percentage of the panel's min/max span", not "the value is a percentage", so do not use it for
ratio panels.

```yaml
# Success rate panel (query returns 0.0-1.0)
thresholds:
  defaultColor: red
  steps:
  - value: 0.95   # orange from 95%
    color: orange
  - value: 0.98   # green from 98%
    color: green

# Error rate panel: same boundaries, mirrored (1 - 0.98 = 0.02, 1 - 0.95 = 0.05)
thresholds:
  defaultColor: green
  steps:
  - value: 0.02   # orange from 2%
    color: orange
  - value: 0.05   # red from 5%
    color: red
```

The same applies to any pair of complementary panels (e.g. "routed" vs "unrouted", "paid" vs
"unpaid") and to the same metric shown as a stat and as a time series: one set of boundaries per
operation, reused in every panel that shows it.

### Use the `categorical` palette on every time series panel

Set `palette.mode: categorical` on every `TimeSeriesChart`. Some dashboards hard-code series
colours or use named schemes (`schemeDark2`) whose shades are too close to tell apart when five
tenants overlap. `categorical` picks colours that stay distinguishable. `auto` is not wrong, but
use `categorical` so every dashboard looks the same.

```yaml
plugin:
  kind: TimeSeriesChart
  spec:
    visual:
      palette:
        mode: categorical
```

### Match as specifically as the question

Match with the identity of the thing you are measuring. Do not copy Grafana-era selectors
(`=~`, k8s labels, `[5m]`) unless you can say why each one is needed.

**`=` vs `=~`:** use `=` for a single known value. Use `=~` only when the right-hand side is
a pattern: a dashboard variable (`tenant=~"$tenant"`, All = `.+`), a prefix/alternation, or
a real regex such as `url=~"^(/events/.+)$"`. PromQL already anchors `=~`, so a literal with
no metacharacters (`label=~"event-stream"`) is the same as `=` and reads like you meant
"maybe more than this namespace."

```yaml
# Good: one namespace, one service
query: sum by (tenant) (rate(eventstream_processed_events_total{service_name="event-receiver", service_namespace="event-stream", tenant=~"$tenant"}[$__rate_interval]))

# Good: real pattern
url=~"^(/events/.+)$"

# Bad: regex around a single literal
k8s_namespace_name=~"event-stream"
```

**Which identity:** app counters, RED, traces, and logs → `service_name` / `service_namespace`.
CPU, memory, restarts, cAdvisor → `k8s_container_name` / `k8s_namespace_name`. They often
coincide today; service labels still stay correct if the container or runtime changes.
Sidecar containers belong in k8s filters, not in application charts.

Before opening an MR, every `{...}` matcher is either `="value"` or a justified `=~`.

### Other conventions

Existing dashboards do not all follow these rules yet. When a neighbouring panel disagrees
with this skill, follow the skill.


- `connectNulls: false` on time series unless the series is expected to be sparse (errors,
  cron-job output); do not use it to hide gaps caused by a too-small range window.
- Filter by the dashboard's variables where they exist (e.g. `tenant=~"$tenant"`).
- Ratios: guard the numerator with `or vector(0)` so a zero-error period renders 0, not empty.
- Use `{otel_metric_name="..."}` selectors for OTel-exported metrics; bare metric names work
  only for metrics scraped as Prometheus.
- Panel keys are `'<row>_<col>'` strings; layouts reference them via `$ref: '#/spec/panels/<key>'`.
- Terminology: "Location" not node, "ATP" not stock, "line item" not product.

## Verify

CI runs kubeconform, pint, and `dash0 apply --dry-run` on MRs (warn-only). Locally:

```bash
make lint
grep -c '__rate_interval' <file>.perses.yaml; grep -c 'minStep' <file>.perses.yaml   # counts must match
grep -n '\[\$interval\]' <file>.perses.yaml        # expect no hits
grep -n '\[[0-9]*[mhd]\]' <file>.perses.yaml     # each hit must be a deliberate fixed window (e.g. 1d SLI)
grep -n '=~"' <file>.perses.yaml                   # each hit must be a $variable or a real pattern, not a single literal
```

Then open the dashboard in Dash0 at a 30 min range and check no chart shows isolated dots.

### Never set a maximum on the y-axis

Do not set `yAxis.max` (or a `max` on a stat/gauge panel). If a series exceeds the maximum, the
chart clips it flat against the top edge and the reader sees a stable value when the real one is
climbing. This also applies to ratio panels: a rate computed from two counters can exceed 1
briefly after a restart or a scrape gap, and a `max: 1` hides that it happened. Let the axis
auto-scale.

```yaml
# Wrong
yAxis:
  format:
    unit: percent-decimal
  max: 1

# Right
yAxis:
  format:
    unit: percent-decimal
```

### Legend with few series and one value goes at the bottom as a list

When a time series panel has only a few series (roughly five or fewer) and the legend shows one
value per series (no extra columns such as min/max/mean), put the legend at the bottom in list
mode with an empty `values` array. This keeps the chart full-width and stops a short legend from
being rendered as a near-empty table. Panels with many series or several legend columns keep
the right-hand table.

```yaml
legend:
  position: bottom
  mode: list
  values: []
```

## Common mistakes

| Mistake | Fix |
|---|---|
| `[$__rate_interval]` without `minStep` on the query | Add `minStep: 2m` to the `PrometheusTimeSeriesQuery` spec |
| Hard-coding `[5m]` in a time series panel | Use `[$__rate_interval]` with `minStep: 2m` |
| Adding an `interval` variable and writing `[$interval]` | Remove it; use `[$__rate_interval]` with `minStep` |
| Hard-coding `[2m]` in `avg_over_time()`/`max_over_time()`/`min_over_time()` | Use `[$__interval]` |
| Setting `connectNulls: true` to hide gaps | Fix the window instead |
| Success and error panels for one operation with unrelated thresholds | Mirror the boundaries: orange 95-98% success means orange 2-5% error |
| Writing `value: 99` for a 99% threshold on a ratio panel | Ratios are 0.0-1.0; write `value: 0.99` |
| Hard-coded series colours or `schemeDark2` that look alike | Remove them; set `palette.mode: categorical` |
| Setting `yAxis.max` (e.g. `max: 1` on a ratio panel) | Remove it; a series above the max is clipped and looks flat |
| Few series with a one-value legend shown as a right-hand table | `legend: {position: bottom, mode: list, values: []}` |
| `label=~"event-stream"` (literal, no metacharacters) | Use `label="event-stream"` |
| App counter filtered by `k8s_container_name` / `k8s_namespace_name` | Use `service_name` / `service_namespace` |
