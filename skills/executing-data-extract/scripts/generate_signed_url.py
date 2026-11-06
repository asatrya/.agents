#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "google-cloud-storage",
# ]
# ///

"""Generate signed URLs for GCS objects under a given prefix."""

import argparse
import datetime
import json
import sys

from google.cloud import storage


def generate_signed_urls(
    *,
    bucket_name: str,
    prefix: str,
    expiry_hours: int,
    output_json: bool,
) -> list[dict[str, str]]:
    """List objects under prefix and generate a signed URL for each."""
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blobs = list(bucket.list_blobs(prefix=prefix))

    if not blobs:
        print(f"No objects found under gs://{bucket_name}/{prefix}", file=sys.stderr)
        sys.exit(1)

    expiry = datetime.timedelta(hours=expiry_hours)
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
            "url": url,
            "expires": expires_at.strftime("%Y-%m-%d %H:%M UTC"),
        })

    return results


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bucket", required=True, help="GCS bucket name")
    parser.add_argument("--prefix", required=True, help="Object prefix (e.g. exports/TDP-2484/)")
    parser.add_argument("--expiry-hours", type=int, default=168, help="URL expiry in hours (default: 168 = 7 days)")
    parser.add_argument("--json", action="store_true", dest="output_json", help="Output as JSON")
    args = parser.parse_args()

    results = generate_signed_urls(
        bucket_name=args.bucket,
        prefix=args.prefix,
        expiry_hours=args.expiry_hours,
        output_json=args.output_json,
    )

    if args.output_json:
        print(json.dumps(results, indent=2))
    else:
        print(f"\nSigned URLs ({len(results)} files, expire in {args.expiry_hours}h):\n")
        print(f"{'File':<60} {'Size':>10}  URL")
        print("-" * 120)
        for r in results:
            print(f"{r['file']:<60} {r['size']:>10}  {r['url'][:80]}...")
        print(f"\nExpires: {results[0]['expires']}")


if __name__ == "__main__":
    main()
