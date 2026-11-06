#!/usr/bin/env python3
"""
Dump a concise list of dbt models and their columns (and refs) from manifest.json.
Useful for coverage analysis without parsing the full manifest by hand.

Usage (from repo root):
  python .cursor/skills/fulfilling-data-requests-with-dbt/scripts/dump_manifest_models.py
  python scripts/dump_manifest_models.py --manifest dbt/target/manifest.json
  python scripts/dump_manifest_models.py --json   # output JSON
"""

import argparse
import json
import sys
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description="Dump dbt models and columns from manifest.json")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("dbt/target/manifest.json"),
        help="Path to manifest.json (default: dbt/target/manifest.json)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON instead of readable text",
    )
    args = parser.parse_args()

    path = args.manifest
    if not path.is_absolute():
        path = Path.cwd() / path
    if not path.exists():
        print(f"Manifest not found: {path}", file=sys.stderr)
        print("Run 'dbt compile' from the project root first.", file=sys.stderr)
        sys.exit(1)

    with open(path) as f:
        manifest = json.load(f)

    nodes = manifest.get("nodes", {})
    parent_map = manifest.get("parent_map", {})

    models = []
    for uid, node in nodes.items():
        if node.get("resource_type") != "model":
            continue
        columns = node.get("columns") or {}
        refs = []
        for dep in node.get("depends_on", {}).get("nodes", []):
            if dep.startswith("model."):
                refs.append(dep.split(".")[-1])  # simple name
        models.append({
            "name": node.get("name") or node.get("alias"),
            "alias": node.get("alias"),
            "schema": node.get("schema"),
            "description": (node.get("description") or "")[:200],
            "materialized": node.get("config", {}).get("materialized"),
            "columns": list(columns.keys()),
            "refs": refs,
        })

    if args.json:
        print(json.dumps(models, indent=2))
        return

    for m in models:
        name = m["name"]
        schema = m["schema"] or ""
        desc = (m["description"] or "").replace("\n", " ").strip()
        cols = m["columns"]
        refs = m["refs"]
        print(f"## {name}")
        if schema:
            print(f"  schema: {schema}")
        if desc:
            print(f"  description: {desc}")
        if refs:
            print(f"  refs: {', '.join(refs)}")
        print(f"  columns ({len(cols)}): {', '.join(cols[:15])}" + (" ..." if len(cols) > 15 else ""))
        print()


if __name__ == "__main__":
    main()
