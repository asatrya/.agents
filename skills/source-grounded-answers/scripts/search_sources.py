#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///

"""Deterministically retrieve evidence candidates from approved sources."""

from __future__ import annotations

import argparse
import io
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as element_tree
import zipfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Literal
from urllib.parse import unquote, urlparse

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - exercised when uv dependencies are unavailable
    PdfReader = None


SourceKind = Literal["local", "web"]
SourceProvenance = Literal["upload", "prompt", "workspace"]

SUPPORTED_SUFFIXES = frozenset(
    {
        ".csv",
        ".docx",
        ".html",
        ".htm",
        ".json",
        ".markdown",
        ".md",
        ".pdf",
        ".rst",
        ".text",
        ".tsv",
        ".txt",
        ".xlsm",
        ".xlsx",
        ".yaml",
        ".yml",
    }
)

STOPWORDS = frozenset(
    {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "how",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "that",
        "the",
        "this",
        "to",
        "what",
        "when",
        "where",
        "which",
        "who",
        "why",
        "with",
    }
)

WORD_PATTERN = re.compile(r"\w+", re.UNICODE)
HEADING_PATTERN = re.compile(r"^\s{0,3}(#{1,6})\s+(.+?)\s*#*\s*$")
XML_NAMESPACES = {
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "x": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
}


@dataclass(frozen=True)
class SourceSpec:
    """One source explicitly supplied through an allowed intake channel."""

    kind: SourceKind
    value: str
    provenance: SourceProvenance
    recursive: bool = True


@dataclass(frozen=True)
class TextUnit:
    """A stable, locatable piece of source text."""

    source_type: str
    source_name: str
    source_reference: str
    location: str
    text: str
    order: tuple[int, str]


class WebPageParser(HTMLParser):
    """Extract visible text, the document title, and heading-delimited sections."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignore_depth = 0
        self._title_depth = 0
        self._title_parts: list[str] = []
        self._heading_tag: str | None = None
        self._heading_parts: list[str] = []
        self._section_heading = ""
        self._section_parts: list[str] = []
        self._completed_sections: list[tuple[str, str]] = []

    @staticmethod
    def _normalize_parts(parts: list[str]) -> str:
        lines = [" ".join(line.split()) for line in "".join(parts).splitlines()]
        return "\n".join(line for line in lines if line)

    def _flush_section(self) -> None:
        text = self._normalize_parts(self._section_parts)
        if text:
            self._completed_sections.append((self._section_heading, text))
        self._section_parts = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        """Handle an opening HTML tag."""
        del attrs
        lowered = tag.casefold()
        if lowered in {"script", "style", "noscript", "template"}:
            self._ignore_depth += 1
        elif lowered == "title" and self._ignore_depth == 0:
            self._title_depth += 1
        elif lowered in {"h1", "h2", "h3", "h4", "h5", "h6"} and self._ignore_depth == 0:
            self._flush_section()
            self._heading_tag = lowered
            self._heading_parts = []
        elif lowered in {"p", "div", "li", "br"}:
            if self._ignore_depth == 0:
                if self._heading_tag is None:
                    self._section_parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        """Handle a closing HTML tag."""
        lowered = tag.casefold()
        if lowered in {"script", "style", "noscript", "template"} and self._ignore_depth:
            self._ignore_depth -= 1
        elif lowered == "title" and self._title_depth:
            self._title_depth -= 1
        elif lowered == self._heading_tag:
            self._section_heading = " ".join("".join(self._heading_parts).split())
            self._heading_tag = None
            self._heading_parts = []

    def handle_data(self, data: str) -> None:
        """Collect visible text and title text."""
        if self._ignore_depth:
            return
        if self._title_depth:
            self._title_parts.append(data)
            return
        if self._heading_tag is not None:
            self._heading_parts.append(data)
        else:
            self._section_parts.append(data)

    @property
    def title(self) -> str:
        """Return the normalized page title."""
        return " ".join("".join(self._title_parts).split())

    @property
    def sections(self) -> list[tuple[str, str]]:
        """Return heading-delimited visible text sections in source order."""
        sections = list(self._completed_sections)
        current_text = self._normalize_parts(self._section_parts)
        if current_text:
            sections.append((self._section_heading, current_text))
        return sections


def source_from_argument(value: str, provenance: SourceProvenance) -> SourceSpec:
    """Convert an explicitly supplied path or URL into a source specification."""
    kind: SourceKind = "web" if value.casefold().startswith(("http://", "https://")) else "local"
    return SourceSpec(kind, value, provenance)


def inline_source_units(payload: str) -> list[TextUnit]:
    """Convert a JSON prompt source into locatable text units.

    :param payload: JSON object with string ``name`` and ``text`` fields.
    :returns: Searchable units attributed to the current prompt.
    :raises ValueError: If the payload is malformed.
    """
    try:
        value = json.loads(payload)
    except json.JSONDecodeError as error:
        raise ValueError("--inline-source-json must contain valid JSON") from error
    if not isinstance(value, dict):
        raise ValueError("--inline-source-json must be a JSON object")
    name = value.get("name")
    text = value.get("text")
    if not isinstance(name, str) or not name.strip() or not isinstance(text, str):
        raise ValueError("--inline-source-json requires non-empty string fields: name and text")
    reference = f"prompt:{name.strip()}"
    return split_text_units(text, "prompt", name.strip(), reference)


def split_text_units(
    text: str,
    source_type: str,
    source_name: str,
    source_reference: str,
) -> list[TextUnit]:
    """Split ordinary text into stable heading or line-range units."""
    units: list[TextUnit] = []
    buffer: list[str] = []
    start_line = 1
    current_heading = ""

    def flush(end_line: int) -> None:
        if not buffer or not "".join(buffer).strip():
            buffer.clear()
            return
        if current_heading:
            location = f"{source_name} — {current_heading}"
        else:
            location = f"{source_name} — lines {start_line}-{end_line}"
        units.append(
            TextUnit(
                source_type,
                source_name,
                source_reference,
                location,
                "".join(buffer),
                (len(units), location),
            )
        )
        buffer.clear()

    for line_number, line in enumerate(text.splitlines(keepends=True), start=1):
        heading_match = HEADING_PATTERN.match(line)
        if heading_match:
            flush(line_number - 1)
            current_heading = heading_match.group(2).strip()
            start_line = line_number
            buffer.append(line)
            continue
        if not buffer:
            start_line = line_number
        if not line.strip():
            flush(line_number - 1)
            continue
        buffer.append(line)
        if line_number - start_line >= 39:
            flush(line_number)
    flush(max(1, len(text.splitlines())))
    return units


def web_content_file_units(path: Path, allowed_urls: set[str]) -> list[TextUnit]:
    """Convert captured text from an explicitly selected web page into units.

    The JSON file must contain the selected page's URL, its page title, and
    visible text captured from that exact URL by an approved web connector.
    Web result line prefixes (for example ``L42:``) are removed before
    searching, while page headings and the source URL are retained as
    locations.
    """
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read web-content JSON: {error}") from error
    if not isinstance(value, dict):
        raise ValueError("web-content JSON must be an object")
    url = value.get("url")
    title = value.get("title")
    text = value.get("text")
    if not isinstance(url, str) or not url.casefold().startswith(("http://", "https://")):
        raise ValueError('web-content JSON requires an "url" field with an http(s) URL')
    if url not in allowed_urls:
        raise ValueError(
            "captured web text URL must exactly match a URL explicitly passed with --prompt-source"
        )
    if not isinstance(title, str) or not title.strip():
        raise ValueError('web-content JSON requires a non-empty "title" field')
    if not isinstance(text, str) or not text.strip():
        raise ValueError('web-content JSON requires a non-empty "text" field')

    clean_lines = [re.sub(r"^\s*L\d+:\s?", "", line) for line in text.splitlines()]
    captured_text = "\n".join(clean_lines)
    raw_units = split_text_units(captured_text, "website", title.strip(), url)
    units: list[TextUnit] = []
    for index, unit in enumerate(raw_units):
        prefix = f"{title.strip()} — "
        detail = unit.location[len(prefix) :] if unit.location.startswith(prefix) else ""
        if detail.startswith("lines "):
            detail = ""
        location = f"{title.strip()} — {detail} — {url}" if detail else f"{title.strip()} — {url}"
        units.append(TextUnit("website", title.strip(), url, location, unit.text, (index, location)))
    return units


def extract_pdf_units(
    data: bytes,
    source_name: str,
    source_reference: str,
    source_type: str = "pdf",
) -> list[TextUnit]:
    """Extract page-level text units from a PDF."""
    if PdfReader is None:
        raise RuntimeError(
            "PDF support requires pypdf; rerun with `uv run --with pypdf==5.9.0 --script ...`"
        )
    reader = PdfReader(io.BytesIO(data))
    units: list[TextUnit] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if not text.strip():
            continue
        location = f"{source_name}, page {page_number}"
        units.append(
            TextUnit(
                source_type,
                source_name,
                source_reference,
                location,
                text,
                (page_number, location),
            )
        )
    return units


def extract_docx_units(path: Path) -> list[TextUnit]:
    """Extract paragraph units and headings from a Word document."""
    with zipfile.ZipFile(path) as archive:
        root = element_tree.fromstring(archive.read("word/document.xml"))
    units: list[TextUnit] = []
    current_heading = ""
    paragraphs = root.findall(".//w:body/w:p", XML_NAMESPACES)
    for index, paragraph in enumerate(paragraphs, start=1):
        text = "".join(paragraph.itertext()).strip()
        if not text:
            continue
        style_element = paragraph.find("./w:pPr/w:pStyle", XML_NAMESPACES)
        style = "" if style_element is None else style_element.attrib.get(
            "{" + XML_NAMESPACES["w"] + "}val", ""
        )
        if style.casefold().startswith("heading"):
            current_heading = text
            location = f"{path.name} — {text}"
        elif current_heading:
            location = f"{path.name} — {current_heading}"
        else:
            location = f"{path.name} — paragraph {index}"
        units.append(TextUnit("docx", path.name, str(path), location, text, (index, location)))
    return units


def read_zip_xml(archive: zipfile.ZipFile, name: str) -> element_tree.Element:
    """Read and parse an XML member from a ZIP archive."""
    return element_tree.fromstring(archive.read(name))


def extract_xlsx_units(path: Path) -> list[TextUnit]:
    """Extract row-level text units from an XLSX or XLSM workbook."""
    with zipfile.ZipFile(path) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            shared_root = read_zip_xml(archive, "xl/sharedStrings.xml")
            for item in shared_root.findall("x:si", XML_NAMESPACES):
                shared_strings.append("".join(item.itertext()))

        workbook_root = read_zip_xml(archive, "xl/workbook.xml")
        sheet_names = [
            item.attrib.get("name", f"sheet{index}")
            for index, item in enumerate(workbook_root.findall("x:sheets/x:sheet", XML_NAMESPACES), start=1)
        ]
        units: list[TextUnit] = []
        worksheet_names = sorted(
            name
            for name in archive.namelist()
            if name.startswith("xl/worksheets/sheet") and name.endswith(".xml")
        )
        for sheet_index, worksheet_name in enumerate(worksheet_names, start=1):
            root = read_zip_xml(archive, worksheet_name)
            sheet_name = sheet_names[sheet_index - 1] if sheet_index <= len(sheet_names) else f"sheet{sheet_index}"
            for row in root.findall(".//x:sheetData/x:row", XML_NAMESPACES):
                row_reference = row.attrib.get("r", str(len(units) + 1))
                cells: list[str] = []
                for cell in row.findall("x:c", XML_NAMESPACES):
                    cell_reference = cell.attrib.get("r", "cell")
                    cell_type = cell.attrib.get("t", "")
                    value = "".join(cell.findtext("x:v", default="", namespaces=XML_NAMESPACES))
                    if cell_type == "s" and value.isdigit() and int(value) < len(shared_strings):
                        value = shared_strings[int(value)]
                    elif cell_type == "inlineStr":
                        value = "".join(cell.itertext())
                    if value:
                        cells.append(f"{cell_reference}: {value}")
                if not cells:
                    continue
                location = f"{path.name} — {sheet_name}, row {row_reference}"
                units.append(
                    TextUnit("xlsx", path.name, str(path), location, " | ".join(cells), (sheet_index, location))
                )
        return units


def extract_html_units(
    data: bytes,
    source_type: str,
    source_name: str,
    source_reference: str,
    location: str,
) -> list[TextUnit]:
    """Extract visible HTML text into heading-located search units."""
    parser = WebPageParser()
    parser.feed(data.decode("utf-8", errors="replace"))
    parser.close()
    units: list[TextUnit] = []
    for index, (heading, text) in enumerate(parser.sections):
        unit_text = f"{heading}\n{text}" if heading else text
        unit_location = f"{location} — {heading}" if heading else location
        units.append(
            TextUnit(
                source_type,
                source_name,
                source_reference,
                unit_location,
                unit_text,
                (index, unit_location),
            )
        )
    return units


def extract_local_file(path: Path) -> list[TextUnit]:
    """Extract searchable units from one supported local file."""
    suffix = path.suffix.casefold()
    if suffix == ".pdf":
        return extract_pdf_units(path.read_bytes(), path.name, str(path))
    if suffix == ".docx":
        return extract_docx_units(path)
    if suffix in {".xlsx", ".xlsm"}:
        return extract_xlsx_units(path)
    data = path.read_bytes()
    if suffix in {".html", ".htm"}:
        return extract_html_units(data, "html", path.name, str(path), path.name)
    text = data.decode("utf-8-sig")
    return split_text_units(text, "file", path.name, str(path))


def extract_web_source(url: str) -> list[TextUnit]:
    """Fetch one approved URL and extract HTML or PDF units."""
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "source-grounded-answers/1.0"},
        method="GET",
    )
    with urllib.request.urlopen(request, timeout=20) as response:
        data = response.read()
        content_type = response.headers.get_content_type().casefold()
        charset = response.headers.get_content_charset() or "utf-8"
    if content_type == "application/pdf" or urlparse(url).path.casefold().endswith(".pdf"):
        name = Path(unquote(urlparse(url).path)).name or url
        return extract_pdf_units(data, name, url, "web_pdf")

    parser = WebPageParser()
    parser.feed(data.decode(charset, errors="replace"))
    parser.close()
    title = parser.title or url
    units: list[TextUnit] = []
    for index, (heading, text) in enumerate(parser.sections):
        unit_text = f"{heading}\n{text}" if heading else text
        location = f"{title} — {heading} — {url}" if heading else f"{title} — {url}"
        units.append(
            TextUnit("website", title, url, location, unit_text, (index, location))
        )
    return units


def iter_local_paths(spec: SourceSpec) -> list[Path]:
    """Expand a local file or folder source deterministically."""
    path = Path(spec.value).expanduser()
    if path.is_file():
        return [path]
    if not path.is_dir():
        return []
    children: Iterable[Path] = path.rglob("*") if spec.recursive else path.iterdir()
    return sorted(
        (child for child in children if child.is_file() and child.suffix.casefold() in SUPPORTED_SUFFIXES),
        key=lambda child: str(child.resolve()),
    )


def collect_units(specs: Sequence[SourceSpec]) -> tuple[list[TextUnit], list[dict[str, str]]]:
    """Read approved sources and record inaccessible sources."""
    units: list[TextUnit] = []
    skipped: list[dict[str, str]] = []
    seen: set[str] = set()
    for spec in specs:
        if spec.kind == "web":
            key = spec.value
            if key in seen:
                continue
            seen.add(key)
            try:
                units.extend(extract_web_source(spec.value))
            except Exception as error:  # source failures must be reported, not hidden
                skipped.append({"source": spec.value, "reason": str(error) or type(error).__name__})
            continue

        source_path = Path(spec.value).expanduser()
        paths = iter_local_paths(spec)
        if not paths:
            skipped.append({"source": spec.value, "reason": "source does not exist or contains no supported files"})
            continue
        if source_path.is_file() and source_path.suffix.casefold() not in SUPPORTED_SUFFIXES:
            skipped.append({"source": spec.value, "reason": "unsupported file type"})
            continue
        for path in paths:
            key = str(path.resolve())
            if key in seen:
                continue
            seen.add(key)
            try:
                units.extend(extract_local_file(path))
            except Exception as error:  # source failures must be reported, not hidden
                skipped.append({"source": str(path), "reason": str(error) or type(error).__name__})
    return units, skipped


def query_terms(query: str) -> list[str]:
    """Return stable, useful search terms from a natural-language query."""
    tokens = [token.casefold() for token in WORD_PATTERN.findall(query)]
    meaningful = [token for token in tokens if token not in STOPWORDS and len(token) > 1]
    return meaningful or tokens


def normalized_words(text: str) -> str:
    """Normalize text only for deterministic matching, never for quotations."""
    return " ".join(token.casefold() for token in WORD_PATTERN.findall(text))


def exact_excerpt(text: str, first_position: int, max_chars: int) -> str:
    """Return a source-exact excerpt around the first matched term."""
    if len(text) <= max_chars:
        return text.strip()
    start = max(0, first_position - max_chars // 3)
    end = min(len(text), start + max_chars)
    while start > 0 and not text[start - 1].isspace():
        start -= 1
    while end < len(text) and not text[end].isspace():
        end += 1
    return text[start:end].strip()


def best_matching_excerpt(text: str, terms: Sequence[str], max_chars: int) -> str:
    """Choose a source-exact excerpt that covers the most distinct query terms."""
    if len(text) <= max_chars:
        return text.strip()
    candidates: list[tuple[int, int]] = []
    for term in terms:
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
        candidates.extend((match.start(), len(term)) for match in pattern.finditer(text))
    if not candidates:
        return exact_excerpt(text, 0, max_chars)

    best_excerpt = ""
    best_score = (-1, -1, 0)
    for position, specificity in candidates:
        excerpt = exact_excerpt(text, position, max_chars)
        covered = sum(
            1
            for term in terms
            if re.search(r"(?<!\w)" + re.escape(term) + r"(?!\w)", excerpt, re.IGNORECASE)
        )
        score = (covered, specificity, -position)
        if score > best_score:
            best_excerpt = excerpt
            best_score = score
    return best_excerpt


def rank_unit(unit: TextUnit, terms: Sequence[str], query: str, max_quote_chars: int) -> dict[str, object] | None:
    """Rank one unit and return a JSON-ready match when it contains evidence."""
    matched_terms: list[str] = []
    score = 0
    for term in terms:
        pattern = re.compile(r"(?<!\w)" + re.escape(term) + r"(?!\w)", re.IGNORECASE)
        match = pattern.search(unit.text)
        if match is None:
            continue
        matched_terms.append(term)
        score += 10 + len(pattern.findall(unit.text))
    if not matched_terms:
        return None
    normalized_query = normalized_words(query)
    normalized_text = normalized_words(unit.text)
    if normalized_query and normalized_query in normalized_text:
        score += 100
    quote = best_matching_excerpt(unit.text, matched_terms, max_quote_chars)
    return {
        "score": score,
        "source_type": unit.source_type,
        "source_name": unit.source_name,
        "source_reference": unit.source_reference,
        "location": unit.location,
        "matched_terms": matched_terms,
        "quote": quote,
    }


def search_units(
    units: Sequence[TextUnit],
    query: str,
    max_results: int,
    max_quote_chars: int,
) -> list[dict[str, object]]:
    """Return stable, ranked evidence candidates."""
    terms = query_terms(query)
    matches = [
        result
        for unit in units
        if (result := rank_unit(unit, terms, query, max_quote_chars)) is not None
    ]
    matches.sort(
        key=lambda result: (
            -int(result["score"]),
            str(result["source_type"]),
            str(result["source_reference"]),
            str(result["location"]),
        )
    )
    deduplicated: list[dict[str, object]] = []
    seen: set[tuple[str, str]] = set()
    for match in matches:
        identity = (str(match["location"]), str(match["quote"]))
        if identity in seen:
            continue
        seen.add(identity)
        deduplicated.append(match)
        if len(deduplicated) >= max_results:
            break
    for rank, match in enumerate(deduplicated, start=1):
        match["rank"] = rank
    return deduplicated


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--query", required=True, help="Natural-language question or search prompt")
    parser.add_argument("--upload", action="append", default=[], help="Path to a file supplied as a conversation upload")
    parser.add_argument(
        "--prompt-source",
        action="append",
        default=[],
        help="Local path or URL explicitly supplied in the current prompt",
    )
    parser.add_argument(
        "--inline-source-json",
        action="append",
        default=[],
        help='JSON object with "name" and "text" for source content pasted in the prompt',
    )
    parser.add_argument(
        "--web-content-file",
        action="append",
        default=[],
        help='JSON file with "url", "title", and "text" captured from a URL also passed with --prompt-source',
    )
    parser.add_argument(
        "--workspace-root",
        action="append",
        default=[],
        help="Workspace folder explicitly included as a source root",
    )
    parser.add_argument("--max-results", type=int, default=40)
    parser.add_argument("--max-quote-chars", type=int, default=900)
    return parser


def main() -> None:
    """Search approved sources and write deterministic JSON to stdout."""
    parser = build_parser()
    args = parser.parse_args()
    if args.max_results < 1 or args.max_quote_chars < 80:
        parser.error("--max-results must be positive and --max-quote-chars must be at least 80")

    specs: list[SourceSpec] = []
    inline_units: list[TextUnit] = []
    captured_web_units: list[TextUnit] = []
    captured_web_skipped: list[dict[str, str]] = []
    try:
        specs.extend(source_from_argument(value, "upload") for value in args.upload)
        specs.extend(source_from_argument(value, "prompt") for value in args.prompt_source)
        specs.extend(source_from_argument(value, "workspace") for value in args.workspace_root)
        for payload in args.inline_source_json:
            inline_units.extend(inline_source_units(payload))
    except (OSError, ValueError) as error:
        parser.error(str(error))
    authorized_web_urls = {
        spec.value for spec in specs if spec.kind == "web" and spec.provenance == "prompt"
    }
    for filename in args.web_content_file:
        try:
            captured_web_units.extend(
                web_content_file_units(Path(filename).expanduser(), authorized_web_urls)
            )
        except ValueError as error:
            captured_web_skipped.append({"source": filename, "reason": str(error)})
    if not specs and not inline_units and not args.web_content_file:
        parser.error(
            "provide at least one --upload, --prompt-source, --inline-source-json, "
            "--web-content-file, or --workspace-root"
        )

    units, skipped = collect_units(specs)
    units.extend(inline_units)
    captured_urls = {unit.source_reference for unit in captured_web_units}
    direct_urls = {unit.source_reference for unit in units}
    units.extend(unit for unit in captured_web_units if unit.source_reference not in direct_urls)
    skipped = [entry for entry in skipped if entry["source"] not in captured_urls]
    skipped.extend(captured_web_skipped)
    matches = search_units(units, args.query, args.max_results, args.max_quote_chars)
    searched = sorted({unit.source_reference for unit in units})
    payload: dict[str, object] = {
        "query": args.query,
        "sources_searched": searched,
        "matches": matches,
        "skipped_sources": skipped,
    }
    json.dump(payload, sys.stdout, ensure_ascii=False, sort_keys=True, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
