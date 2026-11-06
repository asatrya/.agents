#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "Pillow>=10.0",
# ]
# ///

"""Download a Khazanah Muhammadiyah document as a PDF."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import BinaryIO, cast
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urljoin, urlsplit
from urllib.request import Request, urlopen

from PIL import Image

DEFAULT_PAGE_URL = (
    "https://khazanah.muhammadiyah.or.id/collections/"
    "manifestasi-gerakan-tarbiyah-bagaimana-sikap-muhammadiyah"
)
USER_AGENT = "khazanah-pdf-downloader/1.0"
CHUNK_SIZE = 1024 * 1024


class DownloadError(RuntimeError):
    """Raised when a document cannot be downloaded or assembled."""


@dataclass(frozen=True)
class DocumentInfo:
    """Metadata needed to retrieve a document and its rendered pages."""

    page_url: str
    api_base_url: str
    slug: str
    title: str
    year: int
    file_id: str
    storage_key: str
    page_count: int


def build_request(url: str, referer: str, accept: str) -> Request:
    """Build an HTTP request with headers accepted by the source site.

    :param url: URL to request.
    :param referer: Collection page to send as the HTTP referrer.
    :param accept: Value for the HTTP ``Accept`` header.
    :return: A configured request object.
    """
    parsed_url = urlsplit(url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        raise DownloadError(f"Refusing to request a non-HTTP URL: {url}")
    return Request(
        url,
        headers={
            "Accept": accept,
            "Referer": referer,
            "User-Agent": USER_AGENT,
        },
    )


def parse_json_object(payload: str, source_url: str) -> dict[str, object]:
    """Parse a JSON object returned by the source site.

    :param payload: Response body as text.
    :param source_url: URL used for error messages.
    :return: Parsed JSON object.
    :raises DownloadError: If the body is not a JSON object.
    """
    try:
        parsed: object = cast(object, json.loads(payload))
    except json.JSONDecodeError as error:
        raise DownloadError(f"Invalid JSON response from {source_url}: {error}") from error

    if not isinstance(parsed, dict):
        raise DownloadError(f"Expected a JSON object from {source_url}")
    return cast(dict[str, object], parsed)


def require_mapping(value: object, field_name: str) -> dict[str, object]:
    """Return a JSON object value or raise a descriptive error.

    :param value: Value read from a JSON response.
    :param field_name: Human-readable field name for diagnostics.
    :return: The value as a JSON object.
    :raises DownloadError: If the value is not an object.
    """
    if not isinstance(value, dict):
        raise DownloadError(f"Expected {field_name} to be an object")
    return cast(dict[str, object], value)


def require_string(value: object, field_name: str) -> str:
    """Return a JSON string value or raise a descriptive error.

    :param value: Value read from a JSON response.
    :param field_name: Human-readable field name for diagnostics.
    :return: The value as a string.
    :raises DownloadError: If the value is not a string.
    """
    if not isinstance(value, str) or not value:
        raise DownloadError(f"Expected {field_name} to be a non-empty string")
    return value


def require_integer(value: object, field_name: str) -> int:
    """Return a JSON integer value or raise a descriptive error.

    :param value: Value read from a JSON response.
    :param field_name: Human-readable field name for diagnostics.
    :return: The value as an integer.
    :raises DownloadError: If the value is not an integer.
    """
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise DownloadError(f"Expected {field_name} to be a non-negative integer")
    return value


def read_json(url: str, referer: str, timeout: float) -> dict[str, object]:
    """Fetch and parse a JSON endpoint.

    :param url: JSON endpoint URL.
    :param referer: Collection page to send as the HTTP referrer.
    :param timeout: Request timeout in seconds.
    :return: Parsed JSON object.
    :raises DownloadError: If the request fails or returns invalid JSON.
    """
    request = build_request(url, referer, "application/json,*/*;q=0.8")
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - build_request permits HTTP(S) only.
            body = response.read().decode("utf-8")
    except HTTPError as error:
        raise DownloadError(f"HTTP {error.code} while requesting {url}") from error
    except URLError as error:
        raise DownloadError(f"Could not request {url}: {error.reason}") from error

    return parse_json_object(body, url)


def collection_slug(page_url: str) -> str:
    """Extract and validate a collection slug from a page URL.

    :param page_url: Khazanah Muhammadiyah collection page URL.
    :return: Collection slug.
    :raises DownloadError: If the URL is not a valid collection page URL.
    """
    parsed_url = urlsplit(page_url)
    path_parts = [part for part in parsed_url.path.split("/") if part]
    if parsed_url.scheme not in {"http", "https"} or len(path_parts) != 2 or path_parts[0] != "collections":
        raise DownloadError("The page URL must look like https://.../collections/<slug>")
    return path_parts[1]


def load_document(page_url: str, timeout: float) -> DocumentInfo:
    """Load collection metadata from the public Khazanah API.

    :param page_url: Khazanah Muhammadiyah collection page URL.
    :param timeout: Request timeout in seconds.
    :return: Metadata for the requested document.
    :raises DownloadError: If metadata is missing or malformed.
    """
    parsed_url = urlsplit(page_url)
    api_base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    slug = collection_slug(page_url)
    metadata_url = urljoin(api_base_url, f"/api/collections/{quote(slug, safe='')}")
    payload = read_json(metadata_url, page_url, timeout)

    data = require_mapping(payload.get("data"), "data")
    file_data = require_mapping(data.get("file"), "data.file")
    render_data = require_mapping(file_data.get("render"), "data.file.render")
    render_ref = require_mapping(render_data.get("ref"), "data.file.render.ref")

    page_count = require_integer(render_data.get("numPages"), "data.file.render.numPages")
    if page_count == 0:
        raise DownloadError("The document has no rendered pages")

    return DocumentInfo(
        page_url=page_url,
        api_base_url=api_base_url,
        slug=slug,
        title=require_string(data.get("title"), "data.title"),
        year=require_integer(data.get("year"), "data.year"),
        file_id=require_string(render_ref.get("fileId"), "data.file.render.ref.fileId"),
        storage_key=require_string(file_data.get("storageKey"), "data.file.storageKey"),
        page_count=page_count,
    )


def load_page_urls(document: DocumentInfo, timeout: float) -> list[str]:
    """Load the public rendered-page URLs for a document.

    :param document: Document metadata.
    :param timeout: Request timeout in seconds.
    :return: Page URLs in document order.
    :raises DownloadError: If the page manifest is missing or malformed.
    """
    encoded_file_id = quote(document.file_id, safe="")
    manifest_url = urljoin(document.api_base_url, f"/api/stream/pages/{document.year}/{encoded_file_id}")
    manifest_url = f"{manifest_url}?year={document.year}&fileId={quote(document.file_id, safe='')}"
    payload = read_json(manifest_url, document.page_url, timeout)
    data = require_mapping(payload.get("data"), "data")
    pages_value = data.get("pages")
    if not isinstance(pages_value, list):
        raise DownloadError("Expected data.pages to be a list")

    pages = cast(list[object], pages_value)
    page_urls: list[str] = []
    for index, page_value in enumerate(pages, start=1):
        page = require_mapping(page_value, f"data.pages[{index}]")
        relative_url = require_string(page.get("url"), f"data.pages[{index}].url")
        page_urls.append(urljoin(document.api_base_url, relative_url))

    if len(page_urls) != document.page_count:
        raise DownloadError(
            f"The API reports {document.page_count} pages, but returned {len(page_urls)} page URLs"
        )
    return page_urls


def write_response_to_file(response: BinaryIO, destination: Path) -> None:
    """Stream an HTTP response into a local file.

    :param response: File-like HTTP response object.
    :param destination: Destination path.
    """
    with destination.open("wb") as output_file:
        shutil.copyfileobj(response, output_file, length=CHUNK_SIZE)


def try_download_original(document: DocumentInfo, destination: Path, timeout: float) -> bool:
    """Try to download the original PDF storage object.

    :param document: Document metadata.
    :param destination: Temporary destination path.
    :param timeout: Request timeout in seconds.
    :return: ``True`` if the original PDF was downloaded; otherwise ``False``.
    :raises DownloadError: If the endpoint fails for an unexpected reason.
    """
    original_url = urljoin(document.api_base_url, document.storage_key)
    request = build_request(original_url, document.page_url, "application/pdf,*/*;q=0.8")
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - build_request permits HTTP(S) only.
            if response.headers.get_content_type() != "application/pdf":
                return False
            write_response_to_file(response, destination)
            return True
    except HTTPError as error:
        if error.code in {401, 403, 404}:
            return False
        raise DownloadError(f"HTTP {error.code} while requesting the original PDF") from error
    except URLError:
        return False


def download_page_as_jpeg(page_url: str, referer: str, destination: Path, timeout: float) -> None:
    """Download one rendered page and convert it to JPEG.

    :param page_url: Rendered page URL.
    :param referer: Collection page to send as the HTTP referrer.
    :param destination: JPEG destination path.
    :param timeout: Request timeout in seconds.
    :raises DownloadError: If the page cannot be downloaded or decoded.
    """
    request = build_request(page_url, referer, "image/avif,image/webp,image/png,image/jpeg,*/*;q=0.8")
    try:
        with urlopen(request, timeout=timeout) as response:  # nosec B310 - build_request permits HTTP(S) only.
            with tempfile.NamedTemporaryFile(suffix=".page", delete=False) as temporary_file:
                temporary_path = Path(temporary_file.name)
            try:
                with temporary_path.open("wb") as page_file:
                    shutil.copyfileobj(response, page_file, length=CHUNK_SIZE)
                with Image.open(temporary_path) as page_image:
                    converted_image = page_image.convert("RGB")
                    try:
                        converted_image.save(destination, format="JPEG", quality=95, optimize=True)
                    finally:
                        converted_image.close()
            finally:
                temporary_path.unlink(missing_ok=True)
    except HTTPError as error:
        raise DownloadError(f"HTTP {error.code} while requesting page {page_url}") from error
    except (URLError, OSError) as error:
        raise DownloadError(f"Could not decode rendered page {page_url}: {error}") from error


def assemble_pdf(page_urls: list[str], document: DocumentInfo, destination: Path, timeout: float) -> None:
    """Download rendered pages and combine them into a PDF.

    :param page_urls: Rendered page URLs in document order.
    :param document: Document metadata.
    :param destination: Temporary PDF destination.
    :param timeout: Request timeout in seconds.
    """
    with tempfile.TemporaryDirectory(prefix="khazanah-pages-") as temporary_directory:
        temporary_path = Path(temporary_directory)
        jpeg_paths: list[Path] = []
        for page_number, page_url in enumerate(page_urls, start=1):
            jpeg_path = temporary_path / f"page-{page_number:04d}.jpg"
            download_page_as_jpeg(page_url, document.page_url, jpeg_path, timeout)
            jpeg_paths.append(jpeg_path)
            print(f"Downloaded page {page_number}/{len(page_urls)}")

        images: list[Image.Image] = []
        try:
            for jpeg_path in jpeg_paths:
                with Image.open(jpeg_path) as source_image:
                    images.append(source_image.convert("RGB"))
            if not images:
                raise DownloadError("No rendered pages were downloaded")
            images[0].save(destination, format="PDF", save_all=True, append_images=images[1:], resolution=150.0)
        except OSError as error:
            raise DownloadError(f"Could not create PDF {destination}: {error}") from error
        finally:
            for loaded_image in images:
                loaded_image.close()


def default_output_path(slug: str) -> Path:
    """Return a safe default output path for a collection slug.

    :param slug: Collection slug.
    :return: PDF path in the current directory.
    """
    safe_slug = re.sub(r"[^A-Za-z0-9._-]+", "-", slug).strip("-.") or "document"
    return Path(f"{safe_slug}.pdf")


def download_document(document: DocumentInfo, output_path: Path, force: bool, timeout: float) -> None:
    """Download a document, falling back to its public rendered pages.

    :param document: Document metadata.
    :param output_path: Final PDF path.
    :param force: Whether an existing output may be replaced.
    :param timeout: Request timeout in seconds.
    :raises DownloadError: If the output cannot be created.
    """
    if output_path.exists() and not force:
        raise DownloadError(f"Output already exists: {output_path} (use --force to replace it)")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_output = output_path.with_name(f".{output_path.name}.part")
    try:
        if try_download_original(document, temporary_output, timeout):
            print("Downloaded the original PDF")
        else:
            print("Original PDF is not publicly downloadable; assembling the public preview pages")
            page_urls = load_page_urls(document, timeout)
            assemble_pdf(page_urls, document, temporary_output, timeout)
        temporary_output.replace(output_path)
    except (OSError, DownloadError) as error:
        raise DownloadError(f"Could not save {output_path}: {error}") from error
    finally:
        temporary_output.unlink(missing_ok=True)


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments.

    :return: Parsed command-line arguments.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("page_url", nargs="?", default=DEFAULT_PAGE_URL, help="Khazanah collection page URL")
    parser.add_argument("-o", "--output", type=Path, help="Output PDF path")
    parser.add_argument("--timeout", type=float, default=30.0, help="HTTP timeout in seconds (default: 30)")
    parser.add_argument("--force", action="store_true", help="Replace an existing output file")
    return parser.parse_args()


def main() -> None:
    """Download the requested Khazanah Muhammadiyah collection as a PDF."""
    arguments = parse_arguments()
    if arguments.timeout <= 0:
        raise SystemExit("--timeout must be greater than zero")

    try:
        document = load_document(arguments.page_url, arguments.timeout)
        output_path = arguments.output or default_output_path(document.slug)
        print(f"Document: {document.title} ({document.page_count} pages)")
        download_document(document, output_path, arguments.force, arguments.timeout)
    except DownloadError as error:
        raise SystemExit(str(error)) from error

    print(f"Saved PDF to {output_path}")


if __name__ == "__main__":
    main()
