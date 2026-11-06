#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "google-cloud-bigquery",
# ]
# ///

"""Export a BigQuery table to GCS in Parquet or CSV format."""

import argparse
import sys

from google.cloud import bigquery


def export_table(
    *,
    project: str,
    dataset: str,
    table: str,
    bucket: str,
    prefix: str,
    fmt: str,
) -> list[str]:
    """Run a BigQuery EXPORT DATA job and return the destination URIs."""
    client = bigquery.Client(project=project)
    source_ref = f"`{project}.{dataset}.{table}`"

    dest_format = fmt.upper()
    if dest_format not in ("PARQUET", "CSV", "JSON"):
        print(f"Unsupported format: {fmt}. Use parquet, csv, or json.", file=sys.stderr)
        sys.exit(1)

    extension = {"PARQUET": "parquet", "CSV": "csv", "JSON": "json"}[dest_format]
    destination_uri = f"gs://{bucket}/{prefix}/*.{extension}"

    export_sql = f"""
    EXPORT DATA OPTIONS(
      uri = '{destination_uri}',
      format = '{dest_format}',
      overwrite = true
    ) AS
    SELECT * FROM {source_ref};
    """

    print(f"Exporting {source_ref} → {destination_uri}")
    job = client.query(export_sql)
    job.result()

    print(f"Export complete. Job ID: {job.job_id}")
    print(f"Bytes processed: {job.total_bytes_processed:,}")
    return [destination_uri]


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", required=True, help="GCP project ID")
    parser.add_argument("--dataset", required=True, help="BigQuery dataset (schema)")
    parser.add_argument("--table", required=True, help="Table name to export")
    parser.add_argument("--bucket", required=True, help="GCS bucket name")
    parser.add_argument("--prefix", required=True, help="GCS object prefix (e.g. exports/TDP-2484/orders)")
    parser.add_argument("--format", dest="fmt", default="parquet", choices=["parquet", "csv", "json"])
    args = parser.parse_args()

    export_table(
        project=args.project,
        dataset=args.dataset,
        table=args.table,
        bucket=args.bucket,
        prefix=args.prefix,
        fmt=args.fmt,
    )


if __name__ == "__main__":
    main()
