#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""Compress a PDF with Ghostscript while preserving the original file."""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

QUALITY_PRESETS = ("screen", "ebook", "printer", "prepress", "default")


class CompressionError(RuntimeError):
    """Raised when a PDF cannot be compressed."""


def require_ghostscript() -> str:
    """Find the Ghostscript executable on ``PATH``.

    :return: The path to the Ghostscript executable.
    :raises CompressionError: If Ghostscript is not installed.
    """
    for executable in ("gs", "gswin64c", "gswin32c"):
        command_path = shutil.which(executable)
        if command_path is not None:
            return command_path

    raise CompressionError(
        "Ghostscript was not found on PATH. Install Ghostscript and try again."
    )


def default_output_path(input_pdf: Path) -> Path:
    """Build the default output path next to the input PDF.

    :param input_pdf: Input PDF path.
    :return: Input path with ``_compressed`` appended to its stem.
    """
    return input_pdf.with_name(f"{input_pdf.stem}_compressed{input_pdf.suffix}")


def format_size(size_bytes: int) -> str:
    """Format a byte count using a human-readable binary unit.

    :param size_bytes: Number of bytes.
    :return: Human-readable size.
    """
    size = float(size_bytes)
    for unit in ("B", "KiB", "MiB", "GiB"):
        if size < 1024 or unit == "GiB":
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size_bytes} B"


def compress_pdf(
    input_pdf: Path,
    output_pdf: Path,
    quality: str,
    ghostscript: str,
) -> None:
    """Compress ``input_pdf`` into ``output_pdf`` with Ghostscript.

    :param input_pdf: PDF to compress.
    :param output_pdf: Destination PDF.
    :param quality: Ghostscript PDF settings preset.
    :param ghostscript: Ghostscript executable path.
    :raises CompressionError: If Ghostscript fails or creates no output.
    """
    command = [
        ghostscript,
        "-q",
        "-dBATCH",
        "-dNOPAUSE",
        "-dSAFER",
        "-sDEVICE=pdfwrite",
        "-dCompatibilityLevel=1.4",
        f"-dPDFSETTINGS=/{quality}",
        f"-sOutputFile={output_pdf}",
        str(input_pdf),
    ]

    try:
        completed = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError as error:
        raise CompressionError(f"Could not start Ghostscript: {error}") from error

    if completed.returncode != 0:
        details = (completed.stderr or completed.stdout).strip()
        if len(details) > 2_000:
            details = details[-2_000:]
        suffix = f"\n{details}" if details else ""
        raise CompressionError(
            f"Ghostscript failed with exit code {completed.returncode}.{suffix}"
        )

    if not output_pdf.is_file() or output_pdf.stat().st_size == 0:
        raise CompressionError("Ghostscript completed without creating a valid output PDF")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser.

    :return: Configured argument parser.
    """
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=Path, help="PDF file to compress")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="Output PDF (default: <input>_compressed.pdf)",
    )
    parser.add_argument(
        "-q",
        "--quality",
        choices=QUALITY_PRESETS,
        default="ebook",
        help=(
            "Ghostscript quality preset: screen (smallest), ebook (balanced), "
            "printer, prepress, or default (default: ebook)"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Replace the output file if it already exists",
    )
    return parser


def main() -> None:
    """Parse arguments and compress a PDF."""
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
        ghostscript = require_ghostscript()
        with tempfile.TemporaryDirectory(
            prefix=f".{output_pdf.stem}-", dir=output_pdf.parent
        ) as temp_directory:
            temporary_output = Path(temp_directory) / output_pdf.name
            compress_pdf(input_pdf, temporary_output, args.quality, ghostscript)
            temporary_output.replace(output_pdf)
    except CompressionError as error:
        parser.error(str(error))

    original_size = input_pdf.stat().st_size
    compressed_size = output_pdf.stat().st_size
    change_percent = (1 - compressed_size / original_size) * 100
    direction = "smaller" if change_percent >= 0 else "larger"
    print(
        f"Created {output_pdf}\n"
        f"Size: {format_size(original_size)} -> {format_size(compressed_size)} "
        f"({abs(change_percent):.1f}% {direction})",
        file=sys.stdout,
    )


if __name__ == "__main__":
    main()
