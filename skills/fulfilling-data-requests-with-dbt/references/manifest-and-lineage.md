# Manifest and lineage

dbt writes a **manifest** after `dbt compile` (or run/build) to `dbt/target/manifest.json`. Use it to discover models, sources, columns, and dependencies for coverage analysis.

## Top-level keys

| Key | Purpose |
|-----|---------|
| `nodes` | All models, tests, snapshots, etc. Keyed by `unique_id`. |
| `sources` | Source definitions (raw tables). |
| `parent_map` | First-order parents of each resource: node id → list of parent ids. |
| `child_map` | First-order children: node id → list of child ids. |
| `metadata` | dbt version, project info. |

## Nodes (models)

Filter `nodes` by `resource_type == "model"`. Each model node has:

| Field | Description |
|-------|-------------|
| `unique_id` | e.g. `model.bi.stg_order_item__all_time`. |
| `name` | Model name (file base name). |
| `alias` | Final relation name (often same as `name`). |
| `schema`, `database` | Resolved schema and database. |
| `columns` | Dict: column name → `{"name": "...", "description": "..."}` (and meta/tests). |
| `depends_on.nodes` | List of unique_ids this model depends on (refs). |
| `depends_on.sources` | List of source unique_ids. |
| `description` | Model-level description from schema.yml. |
| `config.materialized` | view, table, incremental, etc. |
| `original_file_path` | e.g. `models/ad_hoc/TDP-2484/orders_legacy_extract_aninebing.sql`. |

Use `columns` to see which fields exist on a model. Use `depends_on` or `parent_map` to trace lineage (which models/sources feed this model).

## Sources

In `manifest["sources"]`, each entry has `source_name`, `name` (table name), `schema`, `database`, and often `columns` with the same shape as node columns. Use for raw/source tables when the request might be fulfillable from sources.

## Lineage and grain

- **parent_map**: For a given `unique_id`, `parent_map[unique_id]` is the list of direct parent nodes/sources. Follow parents to see upstream tables.
- **child_map**: `child_map[unique_id]` lists direct children (downstream models).
- **Grain** is not stored explicitly. Infer from:
  - Model and column `description` (e.g. "one row per order", "item-level").
  - Naming (e.g. `stg_order_item__all_time` suggests item grain; `stg_order_header` suggests order grain).
  - Lineage: an order-level model often aggregates from an item-level model.

## Example snippet (structure only)

```json
{
  "nodes": {
    "model.bi.stg_order_item__all_time": {
      "resource_type": "model",
      "name": "stg_order_item__all_time",
      "alias": "stg_order_item__all_time",
      "schema": "t_order_management",
      "columns": {
        "tenant": {"name": "tenant", "description": "Tenant identifier"},
        "sales_order_uuid": {"name": "sales_order_uuid", "description": "Order UUID"},
        "sale__placed_at": {"name": "sale__placed_at", "description": "Order placed timestamp"}
      },
      "depends_on": {"nodes": ["model.bi.stg_order_item__..."], "sources": []},
      "description": "Item-level order activity..."
    }
  },
  "parent_map": {
    "model.bi.stg_order_item__all_time": ["model.bi.some_upstream"]
  },
  "child_map": {
    "model.bi.stg_order_item__all_time": ["model.bi.ad_hoc.orders_legacy_extract_aninebing"]
  }
}
```

## Optional script

The skill can use `scripts/dump_manifest_models.py` to output a concise list of models and their columns (and refs) so you can quickly see what exists without parsing the full manifest by hand.
