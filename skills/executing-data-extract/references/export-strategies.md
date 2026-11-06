# Export Strategies

How to get data out of the warehouse and into cloud storage for delivery.

## BigQuery → GCS

**Preferred method**: `EXPORT DATA` SQL statement. Runs server-side, no data passes through the client.

```sql
EXPORT DATA OPTIONS(
  uri = 'gs://bucket/prefix/*.parquet',
  format = 'PARQUET',          -- or CSV, JSON
  overwrite = true,
  compression = 'SNAPPY'       -- PARQUET default; use GZIP for CSV
) AS
SELECT * FROM `project.dataset.table`;
```

**Considerations**:
- BigQuery splits output into multiple files (~256 MB each by default).
- Parquet is strongly preferred: columnar, compressed, typed. CSV only when the consumer requires it.
- Wildcard `*` in the URI is required for multi-file output.
- No egress cost when exporting to a GCS bucket in the same region.

**Large exports** (> 1 GB exported):
- Parquet with SNAPPY compression keeps files small.
- If the consumer needs a single file, export as CSV with `GZIP` and note the size.

## Snowflake → S3 / GCS

Use `COPY INTO` with a named stage:

```sql
COPY INTO @my_stage/exports/TDP-2484/orders/
FROM my_schema.my_table
FILE_FORMAT = (TYPE = PARQUET)
OVERWRITE = TRUE
HEADER = TRUE;
```

For GCS, configure an external stage with a GCS integration.

## Signed URLs

**GCS**: Use `generate_signed_url()` from the `google-cloud-storage` Python SDK. Requires either:
- A service account key file (`GOOGLE_APPLICATION_CREDENTIALS`), or
- Workload Identity Federation (preferred in production).

V4 signatures support up to 7 days expiry. For longer access, use IAM-based access or a shared bucket with lifecycle rules.

**S3**: Use `generate_presigned_url()` from `boto3`. Max expiry depends on the signing credentials (IAM user: 7 days; IAM role/STS: up to 12 hours by default).

## Format recommendations

| Use case | Format | Compression | Notes |
|----------|--------|-------------|-------|
| Data engineering / analytics | Parquet | SNAPPY | Best for downstream processing |
| Non-technical consumer | CSV | GZIP | Universal compatibility |
| API / programmatic access | JSON (newline-delimited) | GZIP | Easy to stream-parse |
