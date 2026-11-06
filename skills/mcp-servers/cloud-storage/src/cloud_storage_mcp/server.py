"""MCP server for cloud storage operations: export, signed URLs, object listing.

Currently supports GCP (BigQuery + GCS). Extend with S3/Snowflake as needed.
"""

import datetime
import json

from google.cloud import bigquery, storage
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "cloud-storage",
    description="Export data to cloud storage and generate signed URLs.",
)


@mcp.tool()
def export_bigquery_to_gcs(
    project: str,
    dataset: str,
    table: str,
    bucket: str,
    prefix: str,
    fmt: str = "PARQUET",
    compression: str = "SNAPPY",
) -> dict[str, object]:
    """Export a BigQuery table to GCS using server-side EXPORT DATA.

    No data passes through the client — the export runs entirely in BigQuery.
    Returns the job ID and destination URI.
    """
    fmt = fmt.upper()
    if fmt not in ("PARQUET", "CSV", "JSON"):
        return {"error": f"Unsupported format: {fmt}. Use PARQUET, CSV, or JSON."}

    extension = {"PARQUET": "parquet", "CSV": "csv", "JSON": "json"}[fmt]
    destination_uri = f"gs://{bucket}/{prefix}/*.{extension}"
    source_ref = f"`{project}.{dataset}.{table}`"

    compression_opt = ""
    if fmt == "PARQUET":
        compression_opt = f", compression = '{compression}'"
    elif fmt == "CSV":
        compression_opt = ", compression = 'GZIP'"

    export_sql = f"""
    EXPORT DATA OPTIONS(
      uri = '{destination_uri}',
      format = '{fmt}',
      overwrite = true{compression_opt}
    ) AS
    SELECT * FROM {source_ref};
    """

    client = bigquery.Client(project=project)
    job = client.query(export_sql)
    job.result()

    return {
        "job_id": job.job_id,
        "destination_uri": destination_uri,
        "bytes_processed": job.total_bytes_processed,
        "source": f"{project}.{dataset}.{table}",
    }


@mcp.tool()
def export_query_to_gcs(
    project: str,
    query: str,
    bucket: str,
    prefix: str,
    fmt: str = "PARQUET",
) -> dict[str, object]:
    """Export an arbitrary SQL query result to GCS.

    Useful when you need to apply filters or transformations before export.
    """
    fmt = fmt.upper()
    if fmt not in ("PARQUET", "CSV", "JSON"):
        return {"error": f"Unsupported format: {fmt}. Use PARQUET, CSV, or JSON."}

    extension = {"PARQUET": "parquet", "CSV": "csv", "JSON": "json"}[fmt]
    destination_uri = f"gs://{bucket}/{prefix}/*.{extension}"

    export_sql = f"""
    EXPORT DATA OPTIONS(
      uri = '{destination_uri}',
      format = '{fmt}',
      overwrite = true
    ) AS
    {query};
    """

    client = bigquery.Client(project=project)
    job = client.query(export_sql)
    job.result()

    return {
        "job_id": job.job_id,
        "destination_uri": destination_uri,
        "bytes_processed": job.total_bytes_processed,
    }


@mcp.tool()
def generate_signed_url(
    bucket_name: str,
    object_path: str,
    expiry_hours: int = 168,
) -> dict[str, str]:
    """Generate a V4 signed URL for a single GCS object.

    Default expiry: 7 days (168 hours). Max for V4: 7 days.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(object_path)

    if not blob.exists():
        return {"error": f"Object not found: gs://{bucket_name}/{object_path}"}

    expiry = datetime.timedelta(hours=min(expiry_hours, 168))
    url = blob.generate_signed_url(expiration=expiry, version="v4")
    expires_at = datetime.datetime.now(datetime.timezone.utc) + expiry

    return {
        "object": f"gs://{bucket_name}/{object_path}",
        "signed_url": url,
        "expires": expires_at.strftime("%Y-%m-%d %H:%M UTC"),
    }


@mcp.tool()
def generate_signed_urls_for_prefix(
    bucket_name: str,
    prefix: str,
    expiry_hours: int = 168,
) -> list[dict[str, str]]:
    """Generate signed URLs for all objects under a GCS prefix.

    Returns a list of {file, size, signed_url, expires} for each object.
    """
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))

    expiry = datetime.timedelta(hours=min(expiry_hours, 168))
    expires_at = datetime.datetime.now(datetime.timezone.utc) + expiry
    results: list[dict[str, str]] = []

    for blob in blobs:
        if blob.name.endswith("/"):
            continue
        url = blob.generate_signed_url(expiration=expiry, version="v4")
        size_mb = (blob.size or 0) / (1024 * 1024)
        results.append({
            "file": blob.name,
            "size": f"{size_mb:.1f} MB",
            "signed_url": url,
            "expires": expires_at.strftime("%Y-%m-%d %H:%M UTC"),
        })

    return results


@mcp.tool()
def list_objects(
    bucket_name: str,
    prefix: str,
) -> list[dict[str, object]]:
    """List objects under a GCS prefix with metadata (name, size, updated)."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))

    return [
        {
            "name": blob.name,
            "size_bytes": blob.size,
            "size_mb": round((blob.size or 0) / (1024 * 1024), 2),
            "updated": blob.updated.isoformat() if blob.updated else None,
            "content_type": blob.content_type,
        }
        for blob in blobs
        if not blob.name.endswith("/")
    ]


def main() -> None:
    """Run the MCP server."""
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
