#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "pypdf>=5.0,<7",
# ]
# ///

"""Create an outline.txt file from a PDF outline or detected headings.

The output is compatible with ``add_pdf_bookmarks.py``.  When the PDF already
contains bookmarks, those bookmarks are exported exactly.  If it has no
bookmarks, the script falls back to conservative heading detection from page
text; heuristic output must be reviewed before it is used as a final table of
contents.
"""

from __future__ import annotations

import argparse
import re
import sys
import tempfile
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader


class OutlineExtractionError(RuntimeError):
    """Raised when a PDF outline cannot be extracted or detected."""


@dataclass(frozen=True, slots=True)
class OutlineEntry:
    """Represent one generated outline entry."""

    title: str
    page_number: int
    level: int


NUMBERED_HEADING_RE = re.compile(
    r"^(?:(?:bab|chapter|bagian|part)\s+"
    r"[\w.-]+|(?:\d+(?:\.\d+)*|[IVXLCDM]+|[A-Z])[.)]?)\s+\S",
    flags=re.IGNORECASE,
)


def default_output_path(input_pdf: Path) -> Path:
    """Build the default outline path next to the input PDF.

    :param input_pdf: Input PDF path.
    :return: Input path with ``_outline.txt`` appended to its stem.
    """
    return input_pdf.with_name(f"{input_pdf.stem}_outline.txt")


def read_pdf(input_pdf: Path) -> PdfReader:
    """Open a PDF and reject unsupported encrypted or empty documents.

    :param input_pdf: PDF to read.
    :return: Open ``PdfReader`` instance.
    :raises OutlineExtractionError: If the PDF cannot be read.
    """
    try:
        reader = PdfReader(str(input_pdf), strict=False)
        if reader.is_encrypted:
            raise OutlineExtractionError(
                "PDF terenkripsi; buka/dekripsi PDF terlebih dahulu."
            )
        if len(reader.pages) == 0:
            raise OutlineExtractionError("PDF tidak memiliki halaman.")
    except OutlineExtractionError:
        raise
    except Exception as error:
        raise OutlineExtractionError(f"Tidak dapat membaca PDF: {error}") from error
    return reader


def extract_pdf_bookmarks(reader: PdfReader) -> list[OutlineEntry]:
    """Export existing PDF bookmarks with their hierarchy and page numbers.

    :param reader: Open PDF reader.
    :return: Existing bookmarks in document order.
    """
    try:
        outline = reader.outline
    except Exception as error:
        raise OutlineExtractionError(
            f"Tidak dapat membaca bookmark PDF: {error}"
        ) from error

    entries: list[OutlineEntry] = []
    _walk_pdf_outline(outline, reader, level=1, entries=entries)
    return normalize_levels(entries)


def _walk_pdf_outline(
    items: object,
    reader: PdfReader,
    level: int,
    entries: list[OutlineEntry],
) -> None:
    """Recursively convert pypdf's nested outline representation."""
    if not isinstance(items, list):
        return

    for item in items:
        if isinstance(item, list):
            _walk_pdf_outline(item, reader, level + 1, entries)
            continue

        title = _pdf_outline_title(item)
        if title is None:
            continue

        try:
            page_index = reader.get_destination_page_number(item)
        except Exception:
            continue

        if page_index is not None and page_index >= 0:
            entries.append(OutlineEntry(title, page_index + 1, level))


def _pdf_outline_title(item: object) -> str | None:
    """Return a title from a pypdf outline item when available."""
    title = getattr(item, "title", None)
    if isinstance(title, str) and title.strip():
        return title.strip()

    if isinstance(item, dict):
        title_value = item.get("/Title")
        if isinstance(title_value, str) and title_value.strip():
            return title_value.strip()
    return None


def detect_text_headings(reader: PdfReader) -> list[OutlineEntry]:
    """Detect likely headings from extracted page text.

    :param reader: Open PDF reader.
    :return: Candidate headings with one-based page numbers.
    :raises OutlineExtractionError: If no likely headings are detected.
    """
    candidates: list[OutlineEntry] = []
    for page_index, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as error:
            raise OutlineExtractionError(
                f"Tidak dapat mengekstrak teks halaman {page_index + 1}: {error}"
            ) from error

        page_titles: set[str] = set()
        for raw_line in text.splitlines():
            title = _clean_text_line(raw_line)
            if title is None or title.casefold() in page_titles:
                continue
            if not _looks_like_heading(title):
                continue

            page_titles.add(title.casefold())
            candidates.append(
                OutlineEntry(
                    title=title,
                    page_number=page_index + 1,
                    level=_infer_level(title),
                )
            )

    candidates = _remove_repeated_non_numbered_headers(candidates)
    candidates = normalize_levels(candidates)
    if not candidates:
        raise OutlineExtractionError(
            "Tidak ditemukan heading yang cukup meyakinkan. "
            "Gunakan file outline manual atau PDF yang sudah memiliki bookmark."
        )
    return candidates


def _clean_text_line(raw_line: str) -> str | None:
    """Normalize one extracted text line and reject unusable values."""
    title = re.sub(r"\s+", " ", raw_line).strip()
    if not title or len(title) < 2 or len(title) > 120:
        return None
    if not any(character.isalpha() for character in title):
        return None
    return title


def _looks_like_heading(title: str) -> bool:
    """Return whether a line has conservative heading characteristics."""
    words = title.split()
    if len(words) > 14 or title[-1] in ".?!;":
        return False
    if NUMBERED_HEADING_RE.match(title):
        return True

    letters = [character for character in title if character.isalpha()]
    uppercase_count = sum(1 for character in letters if character.isupper())
    return len(letters) >= 3 and uppercase_count / len(letters) >= 0.8


def _infer_level(title: str) -> int:
    """Infer a nesting level from a heading's numbering prefix."""
    match = NUMBERED_HEADING_RE.match(title)
    if match is None:
        return 1

    prefix = title.split(maxsplit=1)[0].rstrip(".)")
    if re.fullmatch(r"\d+(?:\.\d+)*", prefix):
        return prefix.count(".") + 1
    return 1


def _remove_repeated_non_numbered_headers(
    entries: list[OutlineEntry],
) -> list[OutlineEntry]:
    """Remove likely running headers repeated throughout the document."""
    counts = Counter(entry.title.casefold() for entry in entries)
    return [
        entry
        for entry in entries
        if counts[entry.title.casefold()] < 3 or NUMBERED_HEADING_RE.match(entry.title)
    ]


def normalize_levels(entries: list[OutlineEntry]) -> list[OutlineEntry]:
    """Prevent level jumps that the bookmark-import script cannot represent.

    :param entries: Outline entries in document order.
    :return: Entries with levels starting at one and increasing gradually.
    """
    normalized: list[OutlineEntry] = []
    previous_level = 0
    for entry in entries:
        level = min(max(entry.level, 1), previous_level + 1)
        normalized.append(
            OutlineEntry(
                title=entry.title,
                page_number=entry.page_number,
                level=level,
            )
        )
        previous_level = level
    return normalized


def write_outline(
    output_path: Path,
    entries: list[OutlineEntry],
    source_description: str,
) -> None:
    """Write an add_pdf_bookmarks-compatible outline atomically.

    :param output_path: Destination text file.
    :param entries: Outline entries to write.
    :param source_description: Description included as a comment in the file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "; Generated by extract_pdf_outline.py; review before importing.",
        f"; Source: {source_description}",
        "; Format: # heading | one-based-page-number",
        "",
    ]
    lines.extend(
        f"{'#' * entry.level} {entry.title} | {entry.page_number}"
        for entry in entries
    )

    temporary_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            prefix=f".{output_path.stem}-",
            suffix=output_path.suffix or ".txt",
            dir=output_path.parent,
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write("\n".join(lines) + "\n")
        temporary_path.replace(output_path)
    finally:
        if temporary_path is not None and temporary_path.exists():
            temporary_path.unlink()


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        description=(
            "Buat outline.txt dari bookmark PDF, atau deteksi heading dari "
            "teks PDF jika bookmark tidak tersedia."
        )
    )
    parser.add_argument("input_pdf", type=Path, help="File PDF sumber.")
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        help="File outline hasil; default: <nama>_outline.txt.",
    )
    parser.add_argument(
        "--source",
        choices=("auto", "bookmarks", "heuristic"),
        default="auto",
        help=(
            "Sumber outline: auto (default), bookmarks, atau heuristic "
            "untuk deteksi heading dari teks."
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Timpa file outline jika sudah ada.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Run the PDF outline extraction command.

    :param argv: Optional argument list; defaults to process arguments.
    :return: Process exit status, where zero indicates success.
    """
    parser = build_parser()
    args = parser.parse_args(argv)

    input_pdf = args.input_pdf.expanduser().resolve()
    output_path = (args.output or default_output_path(input_pdf)).expanduser().resolve()

    if not input_pdf.is_file():
        parser.error(f"File PDF tidak ditemukan: {input_pdf}")
    if input_pdf.suffix.lower() != ".pdf":
        parser.error(f"File input harus berekstensi .pdf: {input_pdf}")
    if output_path == input_pdf:
        parser.error("File output harus berbeda dari file PDF sumber.")
    if output_path.exists() and not args.force:
        parser.error(
            f"File output sudah ada: {output_path}. Gunakan --force jika ingin "
            "menimpanya."
        )

    try:
        reader = read_pdf(input_pdf)
        entries: list[OutlineEntry]
        if args.source in ("auto", "bookmarks"):
            entries = extract_pdf_bookmarks(reader)
            if not entries and args.source == "bookmarks":
                raise OutlineExtractionError("PDF tidak memiliki bookmark.")
        else:
            entries = []

        if not entries:
            entries = detect_text_headings(reader)
            source_description = "heuristic heading detection; review required"
        else:
            source_description = "existing PDF bookmarks"

        write_outline(output_path, entries, source_description)
    except OutlineExtractionError as error:
        print(f"Gagal: {error}", file=sys.stderr)
        return 1
    except OSError as error:
        print(f"Gagal menulis outline: {error}", file=sys.stderr)
        return 1

    print(f"Berhasil membuat {len(entries)} outline entry: {output_path}")
    if source_description.startswith("heuristic"):
        print(
            "Catatan: hasil heuristic harus ditinjau sebelum dipakai untuk "
            "menambahkan bookmark."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
