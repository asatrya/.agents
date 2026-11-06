#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pypdf>=5.0,<7",
# ]
# ///

"""Add a navigable bookmark tree to a PDF from a plain-text outline.

The outline file uses one entry per line.  The format is::

    # Pendahuluan | 1
    ## Latar Belakang | 3
    ## Tujuan | 5
    # Bab 2 | 7

The number of leading ``#`` characters determines the bookmark level, and the
number after the final ``|`` is the one-based PDF page number.  Lines without
leading ``#`` are treated as top-level bookmarks.  Empty lines and lines whose
first non-whitespace character is ``;`` are ignored.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader, PdfWriter


@dataclass(frozen=True, slots=True)
class BookmarkEntry:
    """Represent one bookmark parsed from the outline file."""

    title: str
    page_number: int
    level: int


def parse_outline(outline_path: Path, page_count: int) -> list[BookmarkEntry]:
    """Parse and validate an outline file.

    :param outline_path: Path to the UTF-8 text outline.
    :param page_count: Number of pages in the input PDF.
    :return: Validated bookmark entries in file order.
    :raises ValueError: If an outline line has invalid syntax or values.
    """
    entries: list[BookmarkEntry] = []
    previous_level = 0

    for line_number, raw_line in enumerate(
        outline_path.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        line = raw_line.strip()
        if not line or line.startswith(";"):
            continue

        try:
            title_part, page_part = line.rsplit("|", maxsplit=1)
        except ValueError as exc:
            raise ValueError(
                f"Baris {line_number}: gunakan format 'Judul | nomor_halaman'."
            ) from exc

        title_with_level = title_part.strip()
        if not title_with_level:
            raise ValueError(f"Baris {line_number}: judul bookmark kosong.")

        level, title = _parse_level_and_title(title_with_level)
        try:
            page_number = int(page_part.strip())
        except ValueError as exc:
            raise ValueError(
                f"Baris {line_number}: nomor halaman harus berupa bilangan bulat."
            ) from exc

        if page_number < 1 or page_number > page_count:
            raise ValueError(
                f"Baris {line_number}: halaman {page_number} di luar rentang "
                f"PDF (1-{page_count})."
            )
        if level > previous_level + 1:
            raise ValueError(
                f"Baris {line_number}: level bookmark meloncat dari "
                f"{previous_level} ke {level}; gunakan level bertahap."
            )

        entries.append(BookmarkEntry(title, page_number, level))
        previous_level = level

    if not entries:
        raise ValueError("File outline tidak berisi bookmark yang valid.")

    return entries


def _parse_level_and_title(value: str) -> tuple[int, str]:
    """Extract a level marker and title from one outline field."""
    heading_match = re.match(r"^(#+)\s*(.*?)\s*$", value)
    if heading_match:
        level = len(heading_match.group(1))
        title = heading_match.group(2)
    else:
        level = 1
        title = value

    if not title:
        raise ValueError("judul bookmark kosong")
    return level, title


def add_bookmarks(
    input_pdf: Path,
    output_pdf: Path,
    entries: list[BookmarkEntry],
    replace_existing: bool,
) -> None:
    """Write a PDF containing the requested navigable bookmarks.

    :param input_pdf: Existing PDF to read.
    :param output_pdf: Destination PDF to create.
    :param entries: Validated bookmark entries.
    :param replace_existing: Whether to remove existing PDF bookmarks first.
    """
    reader = PdfReader(str(input_pdf))
    writer = PdfWriter()
    writer.append(reader, import_outline=not replace_existing)

    outline_stack: list[tuple[int, object]] = []
    for entry in entries:
        while outline_stack and outline_stack[-1][0] >= entry.level:
            outline_stack.pop()

        parent = outline_stack[-1][1] if outline_stack else None
        bookmark = writer.add_outline_item(
            title=entry.title,
            page_number=entry.page_number - 1,
            parent=parent,
        )
        outline_stack.append((entry.level, bookmark))

    output_pdf.parent.mkdir(parents=True, exist_ok=True)
    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{output_pdf.stem}-",
            suffix=output_pdf.suffix or ".pdf",
            dir=output_pdf.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            writer.write(temporary_file)
        temporary_path.replace(output_pdf)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def default_output_path(input_pdf: Path) -> Path:
    """Return the default output path for an input PDF."""
    return input_pdf.with_name(f"{input_pdf.stem}_bookmarked{input_pdf.suffix}")


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line argument parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Tambahkan bookmark navigasi ke PDF dari file teks outline. "
            "Contoh baris: ## Latar Belakang | 3"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Format outline:\n"
            "  # Pendahuluan | 1\n"
            "  ## Latar Belakang | 3\n"
            "  ; komentar"
        ),
    )
    parser.add_argument("input_pdf", type=Path, help="File PDF sumber.")
    parser.add_argument(
        "outline_file",
        type=Path,
        help="File teks UTF-8 berisi judul dan nomor halaman.",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="File PDF hasil; default: <nama>_bookmarked.pdf.",
    )
    parser.add_argument(
        "--replace-existing",
        action="store_true",
        help="Ganti bookmark lama; defaultnya bookmark lama dipertahankan.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Timpa file output jika sudah ada.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the bookmark-generation command.

    :param argv: Optional argument list; defaults to the process arguments.
    :return: Process exit status, where zero indicates success.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    input_pdf = args.input_pdf.resolve()
    outline_file = args.outline_file.resolve()
    output_pdf = (args.output or default_output_path(input_pdf)).resolve()

    if not input_pdf.is_file():
        parser.error(f"File PDF tidak ditemukan: {input_pdf}")
    if input_pdf.suffix.lower() != ".pdf":
        parser.error(f"File input harus berekstensi .pdf: {input_pdf}")
    if not outline_file.is_file():
        parser.error(f"File outline tidak ditemukan: {outline_file}")
    if output_pdf == input_pdf:
        parser.error("File output harus berbeda dari file PDF sumber.")
    if output_pdf.exists() and not args.force:
        parser.error(
            f"File output sudah ada: {output_pdf}. Gunakan --force jika ingin menimpanya."
        )
    if output_pdf.suffix.lower() != ".pdf":
        parser.error(f"File output harus berekstensi .pdf: {output_pdf}")

    try:
        page_count = len(PdfReader(str(input_pdf)).pages)
        entries = parse_outline(outline_file, page_count)
        add_bookmarks(
            input_pdf=input_pdf,
            output_pdf=output_pdf,
            entries=entries,
            replace_existing=args.replace_existing,
        )
    except Exception as exc:
        print(f"Gagal: {exc}", file=sys.stderr)
        return 1

    print(f"Berhasil membuat {len(entries)} bookmark: {output_pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
