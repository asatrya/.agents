---
name: fulfilling-data-requests-with-dbt
description: Determines whether a data request (tables, entities, fields) can be fulfilled from a dbt project using manifest and lineage; produces a field-coverage report (achievable vs not, with source model and how); optionally generates ad-hoc dbt models under models/ad_hoc/<ticket-id> with 2-week table expiry. Use when the user describes a data request or data extract (tables/entities and fields), asks whether the dbt project can fulfill it, or wants models generated for a support/partner extract. If tenant(s) are not provided, ask which tenant(s) the extract should target.
---

# Fulfilling Data Requests with dbt

Assess whether a **data request** (requested tables/entities and fields) can be fulfilled from the dbt project, report field coverage, and optionally generate ad-hoc models in `models/ad_hoc/<support-ticket-id>/`.

## When to use

- User describes a **data request** or **data extract** in terms of tables/entities and fields (e.g. "Orders, OrderItems, Returns with these columns").
- User asks whether the dbt project **can fulfill** such a request.
- User wants **models generated** for a support/partner extract.

## Prerequisites

- **Manifest**: `dbt/target/manifest.json` must exist and be up to date. From project root, run `dbt compile` (or use the Makefile if it exposes a compile target). Use the **running-dbt-commands** skill for CLI usage. Prefer Makefile when available per project rules.

## Workflow

1. **Gather the request** from the user or spec:
   - **Tables/entities** (e.g. Orders, OrderItems, Returns).
   - **Fields** per table (names and, if provided, semantics).
   - **Support ticket ID** (e.g. TDP-2484) for output paths and tags. **Required** — if not provided, ask: "What is the support ticket ID for this request (e.g. TDP-2484, NCS-7193)?"
   - **Tenant(s)**: **Required** — if not provided, ask: "Which tenant(s) should this extract target?"
   - Optional: date filters, grain (e.g. one row per order vs per order item).

   **STOP** — Do **not** proceed to step 2 or any subsequent step until both the **ticket ID** and **tenant name(s)** have been provided by the user. Ask for whichever is missing and wait for the answer.

2. **Ensure manifest**: Run `dbt compile` so `dbt/target/manifest.json` exists. Optionally, from project root: `python ~/.cursor/skills/fulfilling-data-requests-with-dbt/scripts/dump_manifest_models.py` to get a concise model/column list (see [references/manifest-and-lineage.md](references/manifest-and-lineage.md)).

3. **Analyze coverage**:
   - Load manifest: `nodes` (models), `sources`, and for each node `columns`, `depends_on` / `parent_map`, `description`.
   - For each requested table, identify **candidate models** (and sources) that could serve it (by name, description, tags, or lineage).
   - For each requested field, determine: **achievable** (exact model + field and "how": direct column, expression, join, aggregation) or **not achievable** (reason: not modeled, PII not exposed, wrong grain, etc.).
   - **When not sure, do not state Supported or Approximate.** Only use **Supported**, **Derived (supported)**, or **Approximate / derived** when you have clear evidence (column exists, expression is defined, or grain is confirmed). If you are uncertain (e.g. proxy might not match semantics, source not verified), use a conservative status such as **Not modeled** or describe what would need to be verified instead of claiming support.
   - **Check joinable parents for missing fields:** If a requested field is *not* in the candidate model’s columns (especially PII-like: email, name, etc.), do **not** mark "Not available (PII)" until you have checked the candidate’s **parent models** (`depends_on.nodes` / `parent_map`). For each parent (e.g. `vw_employee`, customer/associate dimensions), inspect its columns; if the field exists there and the candidate already `ref()`s that parent, the field is **achievable via join** (document as "Available (PII)" or "Available via join" and name the ref). This avoids missing fields that exist in joined dimensions but are not selected in the curated model.
   - **Prefer semantically matching columns over loose proxies:** When a requested field has a clear semantic name (e.g. `shippingServiceLevel`, `service level`), **search the project** for that concept (column names, model names in related domains—e.g. fulfillment, shipment, shipping) before settling on an approximate proxy from the main candidate model. Prefer a column that **matches the semantics** (e.g. `fulfillment__service_level` or `service_level` in fulfillment/shipping models for "shippingServiceLevel") over a looser proxy (e.g. `sale__fulfillment_group_type`). This avoids missing the better source in a related model.
   - **Check grain-derived and aggregation-derived values:** If a requested field has no matching column (e.g. `quantity`, `count`), do **not** mark "Not modeled" or "Not clearly modeled" until you have considered the **model grain**. For example: one row per order line item (per `uuid`) implies each row represents one unit sold → `quantity` is **Supported** as literal `1` per row, and the retailer can `group by orderId, productId` and `count(*)` for quantity per product per order. Document the expression (e.g. `1 as quantity` or "count(uuid) grouped by order, product") and mark **Supported** or **Derived (supported)** so these are not missed.
   - **Prefer non–extent-limited sources for historical date ranges:** If the request has **historical or all-time date filters** (e.g. "before 2020-04-01"), any model you use or join to must cover that range. Check whether candidate models (or models joined for a field) are **extent-limited** (e.g. use `extent_filter`, `ACTIVITY_EXTENT`, or similar time bounds in SQL). If they are, joins will return no rows for dates outside the extent. **Prefer upstream parents or sources that are not extent-limited** (e.g. views that are `select * from source(...)` without time filters, or all-time staging models) so the extract can fulfill the full requested date range. Document in the report when you use an upstream ref for this reason.
   - Infer **granularity** from model/column descriptions and lineage (e.g. order-level vs item-level) to avoid wrong grains.

4. **Write the report**: Produce a **Field coverage** document (Markdown) in the same style as the reference. Save it under `dbt/models/ad_hoc/<ticket-id>/Field coverage.md`. Include:
   - Intro and ticket link.
   - Source models used.
   - Per-table field mapping: requested field | source/expression | status (Supported, Derived, Not modeled, Not available (PII), **Available (PII) / Available via join** when the field exists in a ref’d parent—see step 3).
   - Summary per table and overall.
   - PII/fallback section if relevant. If the request cannot be fulfilled (e.g. critical fields missing), explain why clearly.

5. **Summarize the data request response**: Add **Request_Response.md** in `dbt/models/ad_hoc/<ticket-id>/` with one table per requested entity. Each table has columns:
   - **Requested Fields** – the field name from the request / Field coverage.
   - **Status** – same status as in Field coverage (Supported, Derived, Not modeled, Available (PII), etc.).
   - **Description** – taken from **schema.yml**: the `description` of the matching column in the ad-hoc model when the field is present in the extract; use "—" for fields not in the extract or not described in schema. Keep the file in sync with Field coverage and schema.yml (e.g. after adding or changing columns in models, update Request_Response.md).

6. **Optional – generate models**: If the user wants dbt models:
   - Create directory `dbt/models/ad_hoc/<ticket-id>/`.
   - For each requested table, add one or more `.sql` models that select/aggregate from existing `ref()` (and `source()` if needed), with tenant and date filters as appropriate.
   - Add `schema.yml` with model and column descriptions. Descriptions must be **semantic or business-focused** (what the value means), based on **our understanding** from the manifest (column semantics), lineage (where it comes from), and the transformation applied (aggregation, join, literal). **Do not** derive descriptions from the requester’s field names; describe the underlying concept (e.g. “When the order was placed” not “placedAt”; “Store or fulfillment node where the order was taken” not “demandLocationId”).
   - Include `Field coverage.md` and **Request_Response.md** (summary tables: Requested Fields | Status | Description from schema.yml) in the same folder. Models inherit the **ad_hoc** config (schema, 2-week expiry); no extra config needed unless overrides are required.
   - In each model config block: `materialized = "table"`, tags including `ad_hoc` and the ticket id (e.g. `TDP-2484`).

7. **Define data tests in `schema.yml`** — do this **before** the first build, not as an afterthought:
   - **Model-level uniqueness**: Add `unique` (single column) or `dbt_expectations.expect_compound_columns_to_be_unique` (composite key) for every model's grain key.
   - **Not-null on key columns**: Add `dbt_expectations.expect_column_values_to_not_be_null` on columns that define the grain and critical foreign keys (e.g. `orderId`, `id`, `createdAt`).
   - **Tenant guard**: Add `accepted_values` on the `tenant` column with the expected tenant(s) to catch filter errors.
   - **Quantity / literal checks**: When a column is a literal (e.g. `1 as quantity`), add `accepted_values` to confirm the assumption.
   - Use existing ad-hoc extracts (e.g. `TDP-2484/schema.yml`) as a reference for test patterns.

8. **Build, test, and iterate in test** — run `dbt build` against the **test** target (not just `dbt compile`) and fix until green:
   - Run: `make build s='path:models/ad_hoc/<ticket-id>/*' TARGET=test` (or equivalent). `dbt build` materializes tables **and** runs all `data_tests` in one pass.
   - **Do not stop at compile.** Compile only validates SQL parsing and ref resolution — it does not catch data-quality issues (duplicates, nulls, wrong grain, wrong tenant).
   - **Inspect failures**: When tests fail, check the failure count and compiled test SQL in `target/compiled/` to understand the root cause.
   - **Common fixes** (iterate on the model SQL, then rebuild):
     - **Duplicate keys**: Source tables (especially report streams and CDC-backed views) often contain multiple versions of the same record. Add `QUALIFY ROW_NUMBER() OVER (PARTITION BY <grain_key> ORDER BY <recency_col> DESC) = 1` to keep only the latest.
     - **Null key fields**: Incomplete or in-flight records in the source may have NULL on critical columns (e.g. `returned_at`, `sales_order_uuid`). Filter them out with explicit `WHERE <col> IS NOT NULL` predicates and document the exclusion.
     - **Unexpected tenant values**: Verify the tenant slug matches the source exactly (case, hyphens, etc.).
   - **Rebuild and retest** after every fix: run the full `dbt build` again in test. Repeat until **PASS=N, ERROR=0, WARN=0**.

9. **Promote to production** — only after **all tests pass in test**:
   - Run: `make build s='path:models/ad_hoc/<ticket-id>/*' TARGET=production`.
   - This materializes the same models in the **production** BigQuery project with production-environment variables and project IDs.
   - Verify the build finishes with **PASS=N, ERROR=0, WARN=0** (same test suite runs again against production data).
   - Only after the production build is fully green, report the final row counts and test results to the user.

10. **Export to GCS and download locally** — after the production build is green:

    #### 10a. Discover table names
    List the `.sql` model files for the ticket to get the table names (they vary per ticket):
    ```bash
    ls dbt/models/ad_hoc/<ticket-id>/*.sql
    ```
    Each file's stem (without `.sql`) is the BigQuery table name in the `ad_hoc` dataset (e.g. `ncs7193_fulfillments.sql` → table `ncs7193_fulfillments`).

    #### 10b. Export from BigQuery to GCS
    Use `bq extract` with `--destination_format=CSV --compression=GZIP`. BigQuery may shard large tables (>1 GB compressed), so always use a wildcard `_*` suffix:
    ```bash
    PROJECT=p-t-business-intelligence-0da1
    GCS_PATH=gs://adhoc-data-export/<ticket-id>

    for TABLE in <table1> <table2> ...; do
      bq extract --project_id=${PROJECT} --destination_format=CSV --compression=GZIP \
        "${PROJECT}:ad_hoc.${TABLE}" \
        "${GCS_PATH}/${TABLE}_*.csv.gz"
    done
    ```
    - If the bucket does not exist, create it first: `gsutil mb -p ${PROJECT} -l us-east4 gs://adhoc-data-export/`
    - The GCS destination pattern is `gs://adhoc-data-export/<ticket-id>/<table>_*.csv.gz`.

    #### 10c. Set 2-week expiration on GCS objects
    Apply a lifecycle rule so exported files auto-delete after 14 days:
    ```bash
    echo '{"rule": [{"action": {"type": "Delete"}, "condition": {"age": 14}}]}' > /tmp/lifecycle.json
    gsutil lifecycle set /tmp/lifecycle.json gs://adhoc-data-export/
    rm /tmp/lifecycle.json
    ```
    This is idempotent — safe to run even if the rule already exists.

    #### 10d. Download from GCS to local
    ```bash
    mkdir -p temp/<ticket-id>/_shards
    gsutil -m cp "gs://adhoc-data-export/<ticket-id>/*.csv.gz" temp/<ticket-id>/_shards/
    ```

    #### 10e. Merge shards into one file per table
    BigQuery may export a table as multiple sharded files (each with its own CSV header). Merge them into a single `<table>.csv.gz`, keeping only one header row:
    ```bash
    cd temp/<ticket-id>
    for TABLE in <table1> <table2> ...; do
      SHARDS=($(ls _shards/${TABLE}_*.csv.gz | sort))
      FIRST=true
      for SHARD in "${SHARDS[@]}"; do
        if $FIRST; then
          gunzip -c "$SHARD"
          FIRST=false
        else
          gunzip -c "$SHARD" | tail -n +2
        fi
      done | gzip > "${TABLE}.csv.gz"
    done
    rm -rf _shards
    ```
    The final output is one `<table>.csv.gz` per table in `./temp/<ticket-id>/`.

    #### 10f. Report
    List the final files with sizes (`ls -lh temp/<ticket-id>/*.csv.gz`) and report to the user.

## Manifest usage

- **Location**: `dbt/target/manifest.json` (after `dbt compile`).
- **Nodes**: `manifest["nodes"]` — filter `resource_type == "model"`. Each node: `name`, `alias`, `schema`, `database`, `columns` (dict of column name → description etc.), `depends_on.nodes`, `description`, `config.materialized`, `original_file_path`.
- **Lineage**: `manifest["parent_map"]` and `manifest["child_map"]` for first-order dependencies; use to trace which models/sources feed a model and to reason about grain. When a requested field is missing from a candidate model, use `parent_map` (or `depends_on.nodes`) to list parents and check their `columns` for that field—e.g. associate email in `vw_employee`.
- **Sources**: `manifest["sources"]` for raw/source tables and their columns.
- **Granularity**: Not stored explicitly; infer from model/column descriptions, primary keys, and lineage.

See [references/manifest-and-lineage.md](references/manifest-and-lineage.md) for details. See [references/field-coverage-example.md](references/field-coverage-example.md) for report structure and style.

### Avoiding common misses

- **Joinable fields (e.g. PII):** Do not mark "Not available (PII)" after only checking the candidate model’s columns. If the candidate already joins a dimension, the field may exist there (e.g. `email`) but not be selected. **Always check parent models** (`depends_on.nodes` / `parent_map`) for requested PII-like fields before concluding "not available."
- **Grain-derived fields (e.g. quantity):** Do not mark "Not modeled" or "Not clearly modeled" for fields like `quantity` or `count` without considering **grain**. If the model is one row per line item (e.g. per `uuid`), then quantity can be 1 per row or derived by grouping and counting. **Infer from grain** and document the expression (e.g. `1 as quantity`; or "count(uuid) group by orderId, productId") so the field is marked Supported/Derived instead of missed.
- **Extent-limited models for historical extracts:** When the request has **historical or all-time date filters**, do **not** use or join to a model that is **extent-limited** (e.g. `extent_filter` in the model SQL) to supply a field. For those dates the join will return no rows. **Use upstream models or sources that are not extent-limited** (e.g. `vw_*` over a source, or all-time staging) and document that choice in the report.
- **Semantically matching fields:** Do **not** default to a loose proxy (e.g. `fulfillment_group_type` for "shippingServiceLevel") without checking whether a **semantically matching** column exists elsewhere (e.g. `service_level` in fulfillment/shipping models). Search the codebase for the requested concept (e.g. "service_level", "shipping", "fulfillment") and prefer that column when joinable; document it in the report.

- **Source data quality (duplicates and nulls):** Report-stream and CDC-backed views (e.g. `vw_item_return`, `vw_fulfillment_request_item_shipments`) may contain **multiple versions** of the same entity or **incomplete records** with NULL key fields. Do **not** assume a `SELECT DISTINCT` upstream is sufficient for uniqueness. Always add dedup logic (`QUALIFY ROW_NUMBER() OVER (PARTITION BY <grain_key> ORDER BY <recency_col> DESC) = 1`) when the source is a report stream or CDC view, and filter out records with NULL on required fields (e.g. `WHERE returned_at IS NOT NULL`). Define the corresponding uniqueness and not-null tests in `schema.yml` **before** the first build so failures surface immediately.

### Status discipline

**If not sure, do not state Approximate or Supported.** Use **Supported** or **Approximate / derived** only when you have clear evidence (column present, expression defined, or grain confirmed). When uncertain—e.g. whether a proxy matches semantics, or a source column exists—use **Not modeled** (or similar) and note what would need to be verified rather than claiming support.

## Output conventions

- **Path**: All new ad-hoc assets under `dbt/models/ad_hoc/<support-ticket-id>/` (e.g. `TDP-2484`).
- **Naming**: Model SQL filenames **must** use the pattern `<ticket-id>_<entity>.sql` — ticket id first, then entity name (e.g. `ncs7193_fulfillments.sql`, `tdp2484_orders.sql`). When a tenant qualifier is needed, append it: `<ticket-id>_<entity>_<tenant>.sql` (e.g. `tdp2484_orders_aninebing.sql`). Colocate `schema.yml`, `Field coverage.md`, and **Request_Response.md** in the same directory.
- **Request_Response.md**: Summary of the data request response: one Markdown table per requested table, with columns **Requested Fields**, **Status**, **Description**. Description is copied from the corresponding column in `schema.yml` when the field exists in the ad-hoc model; use "—" otherwise.
- **Materialization**: `materialized = "table"` in config; schema and 2-week expiry come from `dbt_project.yml` ad_hoc block (`+schema`, `+hours_to_expiration: 336`).
- **Tags**: At least `ad_hoc` and the ticket id in model `tags`.

### Schema (schema.yml) descriptions

Model and column descriptions in `schema.yml` must be **semantic or business-oriented** (what the field means in domain terms), not technical SQL or internal column names. Base them on **our understanding** from: (1) **manifest** — what the source column represents in the project; (2) **lineage** — which model(s) and joins supply the value; (3) **transformation** — aggregation, coalesce, literal, or pass-through. **Do not** copy or paraphrase the requester’s field names (e.g. do not define a column by “the requested demandLocationId”); describe the concept (e.g. “Store or fulfillment node where the order was taken or demanded”). This keeps documentation accurate to the pipeline and reusable regardless of the request’s naming.
