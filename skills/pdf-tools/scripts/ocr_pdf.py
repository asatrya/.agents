#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pypdf>=5.0,<7",
# ]
# ///

"""Create a searchable PDF by OCR-ing the pages of an existing PDF."""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from collections.abc import Sequence
from pathlib import Path

from pypdf import PdfReader, PdfWriter


class OcrError(RuntimeError):
    """Raised when PDF OCR cannot be completed."""


def positive_integer(value: str) -> int:
    """Parse a positive integer for an argparse option.

    :param value: Text supplied on the command line.
    :return: The parsed positive integer.
    :raises argparse.ArgumentTypeError: If ``value`` is not positive.
    """
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"expected an integer, got {value!r}"
        ) from error
    if parsed <= 0:
        raise argparse.ArgumentTypeError("value must be greater than zero")
    return parsed


def page_segmentation_mode(value: str) -> int:
    """Parse a Tesseract page segmentation mode.

    :param value: Text supplied on the command line.
    :return: The parsed Tesseract page segmentation mode.
    :raises argparse.ArgumentTypeError: If the mode is outside Tesseract's range.
    """
    try:
        parsed = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f"expected an integer, got {value!r}"
        ) from error
    if parsed < 0 or parsed > 13:
        raise argparse.ArgumentTypeError(
            "Tesseract page segmentation mode must be between 0 and 13"
        )
    return parsed


def parse_page_spec(value: str) -> tuple[int, int]:
    """Parse a page selection such as ``1-3`` or ``7``.

    :param value: One-based page selection from the command line.
    :return: Inclusive ``(first_page, last_page)`` bounds.
    :raises argparse.ArgumentTypeError: If the selection is malformed.
    """
    match = re.fullmatch(r"(\d+)(?:-(\d+))?", value.strip())
    if match is None:
        raise argparse.ArgumentTypeError(
            "pages must be written as N or N-M, for example 1-3"
        )

    first_page = int(match.group(1))
    last_page = int(match.group(2) or match.group(1))
    if first_page <= 0 or last_page <= 0:
        raise argparse.ArgumentTypeError("page numbers must be greater than zero")
    if first_page > last_page:
        raise argparse.ArgumentTypeError(
            "the first page must not be greater than the last page"
        )
    return first_page, last_page


def require_command(command_name: str) -> str:
    """Find a required executable on ``PATH``.

    :param command_name: Executable name to find.
    :return: Absolute or PATH-resolved executable path.
    :raises OcrError: If the executable is unavailable.
    """
    command_path = shutil.which(command_name)
    if command_path is None:
        raise OcrError(
            f"Required command {command_name!r} was not found on PATH. "
            "Install Tesseract and Poppler, then try again."
        )
    return command_path


def run_command(command: Sequence[str], description: str) -> None:
    """Run an external command and convert failures into a useful error.

    :param command: Full command, including executable and arguments.
    :param description: Human-readable description of the operation.
    :raises OcrError: If the process cannot start or exits unsuccessfully.
    """
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise OcrError(f"Could not start {description}: {error}") from error

    if completed.returncode == 0:
        return

    details = (completed.stderr or completed.stdout).strip()
    if len(details) > 2_000:
        details = details[-2_000:]
    suffix = f"\n{details}" if details else ""
    raise OcrError(
        f"{description} failed with exit code {completed.returncode}.{suffix}"
    )


def available_tesseract_languages(tesseract: str) -> set[str]:
    """Return the language data installed for Tesseract.

    :param tesseract: Path to the Tesseract executable.
    :return: Installed language codes.
    :raises OcrError: If Tesseract cannot report its languages.
    """
    try:
        completed = subprocess.run(
            [tesseract, "--list-langs"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise OcrError(f"Could not query Tesseract languages: {error}") from error

    if completed.returncode != 0:
        details = (completed.stderr or completed.stdout).strip()
        raise OcrError(f"Tesseract could not list installed languages: {details}")

    languages: set[str] = set()
    for line in completed.stdout.splitlines():
        language = line.strip()
        if language and not language.startswith("List of available languages"):
            languages.add(language)
    return languages


def validate_language(language: str, tesseract: str) -> None:
    """Ensure every requested Tesseract language is installed.

    :param language: Tesseract language expression, such as ``eng+ind``.
    :param tesseract: Path to the Tesseract executable.
    :raises OcrError: If one or more language data files are missing.
    """
    requested = {part for part in language.split("+") if part}
    if not requested:
        raise OcrError("The OCR language cannot be empty")

    installed = available_tesseract_languages(tesseract)
    missing = sorted(requested - installed)
    if missing:
        installed_list = ", ".join(sorted(installed)) or "none"
        raise OcrError(
            f"Tesseract language data missing: {', '.join(missing)}. "
            f"Installed languages: {installed_list}. "
            "Install the matching .traineddata file in Tesseract's tessdata directory."
        )


def read_page_count(input_pdf: Path) -> int:
    """Read and validate the number of pages in a PDF.

    :param input_pdf: PDF to inspect.
    :return: Number of pages in the PDF.
    :raises OcrError: If the PDF cannot be read or has no pages.
    """
    try:
        reader = PdfReader(str(input_pdf), strict=False)
        if reader.is_encrypted:
            raise OcrError(
                "Encrypted PDFs are not supported unless they can be opened without a password"
            )
        page_count = len(reader.pages)
    except OcrError:
        raise
    except Exception as error:
        raise OcrError(f"Could not read PDF {input_pdf}: {error}") from error

    if page_count == 0:
        raise OcrError(f"PDF {input_pdf} does not contain any pages")
    return page_count


def page_numbers(page_count: int, selection: tuple[int, int] | None) -> tuple[int, int]:
    """Resolve an optional page selection against a PDF page count.

    :param page_count: Total number of pages in the input PDF.
    :param selection: Optional inclusive one-based page bounds.
    :return: Inclusive ``(first_page, last_page)`` bounds.
    :raises OcrError: If the selection exceeds the document.
    """
    first_page, last_page = selection or (1, page_count)
    if last_page > page_count:
        raise OcrError(
            f"Requested page {last_page}, but the PDF has only {page_count} pages"
        )
    return first_page, last_page


def rendered_page_paths(directory: Path) -> list[Path]:
    """Return rendered page images in numeric page order.

    :param directory: Directory containing ``pdftoppm`` PNG output.
    :return: Sorted page image paths.
    :raises OcrError: If a rendered file has an unexpected name.
    """
    paths = list(directory.glob("page-*.png"))

    def page_number(path: Path) -> int:
        """Extract the numeric page suffix from a rendered image path."""
        match = re.search(r"-(\d+)\.png$", path.name)
        if match is None:
            raise OcrError(f"Unexpected rendered image name: {path.name}")
        return int(match.group(1))

    return sorted(paths, key=page_number)


def render_pdf_pages(
    input_pdf: Path,
    directory: Path,
    first_page: int,
    last_page: int,
    dpi: int,
    pdftoppm: str,
) -> list[Path]:
    """Render selected PDF pages as PNG images.

    :param input_pdf: PDF to render.
    :param directory: Temporary directory for rendered images.
    :param first_page: Inclusive first one-based page number.
    :param last_page: Inclusive last one-based page number.
    :param dpi: Render resolution passed to Poppler.
    :param pdftoppm: Path to the Poppler ``pdftoppm`` executable.
    :return: Rendered page image paths in document order.
    :raises OcrError: If rendering does not produce the expected images.
    """
    prefix = directory / "page"
    run_command(
        [
            pdftoppm,
            "-png",
            "-r",
            str(dpi),
            "-f",
            str(first_page),
            "-l",
            str(last_page),
            str(input_pdf),
            str(prefix),
        ],
        f"rendering pages {first_page}-{last_page}",
    )

    paths = rendered_page_paths(directory)
    expected_count = last_page - first_page + 1
    if len(paths) != expected_count:
        raise OcrError(
            f"Poppler rendered {len(paths)} pages, but expected {expected_count}"
        )
    return paths


def ocr_page(
    image_path: Path,
    output_base: Path,
    page_number: int,
    total_pages: int,
    language: str,
    dpi: int,
    psm: int,
    tesseract: str,
) -> Path:
    """Run Tesseract on one rendered page and return its searchable PDF.

    :param image_path: Rendered PNG page image.
    :param output_base: Tesseract output path without the ``.pdf`` suffix.
    :param page_number: One-based page number for progress output.
    :param total_pages: Number of pages in this OCR operation.
    :param language: Tesseract language expression.
    :param dpi: Image resolution passed to Tesseract.
    :param psm: Tesseract page segmentation mode.
    :param tesseract: Path to the Tesseract executable.
    :return: Generated one-page searchable PDF path.
    :raises OcrError: If Tesseract does not produce a PDF.
    """
    print(f"OCR page {page_number}/{total_pages}", file=sys.stderr)
    run_command(
        [
            tesseract,
            str(image_path),
            str(output_base),
            "--dpi",
            str(dpi),
            "-l",
            language,
            "--psm",
            str(psm),
            "pdf",
        ],
        f"OCR for page {page_number}",
    )

    output_pdf = output_base.with_suffix(".pdf")
    if not output_pdf.is_file():
        raise OcrError(f"Tesseract completed without creating {output_pdf}")
    return output_pdf


def merge_ocr_pages(page_pdfs: Sequence[Path], output_pdf: Path, title: str) -> None:
    """Merge one-page OCR PDFs into the final searchable PDF.

    :param page_pdfs: One-page searchable PDFs in document order.
    :param output_pdf: Final PDF path.
    :param title: Title to store in the PDF metadata.
    :raises OcrError: If an OCR page cannot be read or written.
    """
    writer = PdfWriter()
    temporary_output: Path | None = None
    try:
        for page_pdf in page_pdfs:
            reader = PdfReader(str(page_pdf), strict=False)
            if len(reader.pages) != 1:
                raise OcrError(f"Expected one page in OCR output {page_pdf}")
            writer.add_page(reader.pages[0])
        writer.add_metadata({"/Title": title, "/Producer": "ocr_pdf.py"})
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{output_pdf.stem}-",
            suffix=".tmp.pdf",
            dir=output_pdf.parent,
            delete=False,
        ) as stream:
            temporary_output = Path(stream.name)
            writer.write(stream)
        temporary_output.replace(output_pdf)
    except OcrError:
        raise
    except Exception as error:
        raise OcrError(
            f"Could not assemble searchable PDF {output_pdf}: {error}"
        ) from error
    finally:
        if temporary_output is not None:
            temporary_output.unlink(missing_ok=True)


def default_output_path(input_pdf: Path) -> Path:
    """Build the default output path next to the input PDF.

    :param input_pdf: Input PDF path.
    :return: Input path with ``_ocr`` appended to its stem.
    """
    return input_pdf.with_name(f"{input_pdf.stem}_ocr{input_pdf.suffix}")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    :return: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=Path, help="PDF file to OCR")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output searchable PDF (default: <input>_ocr.pdf)",
    )
    parser.add_argument(
        "-l",
        "--language",
        default="eng",
        help="Tesseract language expression, for example eng or eng+ind (default: eng)",
    )
    parser.add_argument(
        "--dpi",
        type=positive_integer,
        default=300,
        help="Rendering resolution in DPI (default: 300)",
    )
    parser.add_argument(
        "--psm",
        type=page_segmentation_mode,
        default=3,
        help="Tesseract page segmentation mode (default: 3)",
    )
    parser.add_argument(
        "--pages",
        type=parse_page_spec,
        help="OCR only a one-based page or range, for example 7 or 1-3",
    )
    parser.add_argument(
        "--temp-dir",
        type=Path,
        default=Path("tmp/pdfs"),
        help="Directory for temporary render/OCR files (default: tmp/pdfs)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the output file if it already exists",
    )
    return parser


def main() -> None:
    """Parse arguments and create a searchable OCR PDF."""
    parser = build_parser()
    args = parser.parse_args()

    input_pdf = args.input_pdf.expanduser().resolve()
    if not input_pdf.is_file():
        parser.error(f"input PDF does not exist: {input_pdf}")

    output_pdf = (args.output or default_output_path(input_pdf)).expanduser().resolve()
    if output_pdf == input_pdf:
        parser.error("output PDF must be different from the input PDF")
    if output_pdf.exists() and not args.force:
        parser.error(f"output already exists: {output_pdf}; use --force to replace it")
    output_pdf.parent.mkdir(parents=True, exist_ok=True)

    try:
        tesseract = require_command("tesseract")
        pdftoppm = require_command("pdftoppm")
        validate_language(args.language, tesseract)
        total_page_count = read_page_count(input_pdf)
        first_page, last_page = page_numbers(total_page_count, args.pages)

        temp_root = args.temp_dir.expanduser().resolve()
        temp_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(
            prefix="ocr-", dir=temp_root
        ) as temp_directory:
            working_directory = Path(temp_directory)
            images = render_pdf_pages(
                input_pdf,
                working_directory,
                first_page,
                last_page,
                args.dpi,
                pdftoppm,
            )
            page_pdfs = [
                ocr_page(
                    image_path,
                    working_directory / f"ocr-page-{page_number}",
                    index,
                    len(images),
                    args.language,
                    args.dpi,
                    args.psm,
                    tesseract,
                )
                for index, (page_number, image_path) in enumerate(
                    zip(range(first_page, last_page + 1), images),
                    start=1,
                )
            ]
            merge_ocr_pages(
                page_pdfs,
                output_pdf,
                f"{input_pdf.stem} (OCR)",
            )
    except OcrError as error:
        parser.error(str(error))

    print(f"Created searchable PDF: {output_pdf}")


if __name__ == "__main__":
    main()
