"""Book parsing — extract structure and content from PDF and EPUB files."""

import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml


def check_book_deps(fmt: str = "all") -> None:
    """Raise ImportError with install instructions if book deps are missing."""
    missing = []

    if fmt in ("all", "pdf"):
        try:
            import pymupdf  # noqa: F401
        except ImportError:
            missing.append("pymupdf")

    if fmt in ("all", "epub"):
        try:
            import ebooklib  # noqa: F401
        except ImportError:
            missing.append("ebooklib")
        try:
            import bs4  # noqa: F401
        except ImportError:
            missing.append("beautifulsoup4")

    if missing:
        raise ImportError(
            f"Book parsing requires: {', '.join(missing)}\n"
            f"Install with: pip install 'learning-os[book]'"
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_book(file_path: Path) -> Dict[str, Any]:
    """Parse a book and return structured data.

    Returns dict with keys: title, authors, format, original_file,
    total_pages (PDF only), chapters (list of {id, title, content, ...}).
    """
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        check_book_deps("pdf")
        return _parse_pdf(file_path)
    elif suffix == ".epub":
        check_book_deps("epub")
        return _parse_epub(file_path)
    else:
        raise ValueError(f"Unsupported format: {suffix} (expected .pdf or .epub)")


def write_book_output(
    parsed: Dict[str, Any], output_dir: Path
) -> Tuple[Path, List[Path]]:
    """Write parsed book data to disk.

    Creates:
      output_dir/book-outline.yaml
      output_dir/book-content/ch-NN-<id>.md

    Returns (outline_path, list_of_content_paths).
    """
    content_dir = output_dir / "book-content"
    content_dir.mkdir(parents=True, exist_ok=True)

    outline_chapters: List[Dict[str, Any]] = []
    content_paths: List[Path] = []

    for i, ch in enumerate(parsed["chapters"]):
        filename = f"ch-{i + 1:02d}-{ch['id']}.md"
        content_path = content_dir / filename

        md = f"# {ch['title']}\n\n{ch['content']}"
        content_path.write_text(md, encoding="utf-8")
        content_paths.append(content_path)

        entry: Dict[str, Any] = {
            "id": ch["id"],
            "title": ch["title"],
            "content_file": f"book-content/{filename}",
        }
        if "page_range" in ch:
            entry["page_range"] = ch["page_range"]
        outline_chapters.append(entry)

    outline: Dict[str, Any] = {
        "title": parsed["title"],
        "authors": parsed["authors"],
        "format": parsed["format"],
        "original_file": parsed["original_file"],
        "chapter_count": len(outline_chapters),
        "chapters": outline_chapters,
    }
    if parsed.get("total_pages"):
        outline["total_pages"] = parsed["total_pages"]

    outline_path = output_dir / "book-outline.yaml"
    outline_path.write_text(
        yaml.dump(
            outline,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        ),
        encoding="utf-8",
    )

    return outline_path, content_paths


# ---------------------------------------------------------------------------
# PDF parsing
# ---------------------------------------------------------------------------


def _parse_pdf(file_path: Path) -> Dict[str, Any]:
    import pymupdf

    doc = pymupdf.open(str(file_path))
    try:
        metadata = doc.metadata or {}
        title = (
            metadata.get("title", "").strip()
            or _title_from_filename(file_path)
        )
        author_str = metadata.get("author", "")
        authors = (
            [a.strip() for a in author_str.split(",") if a.strip()]
            if author_str
            else []
        )

        toc = doc.get_toc()  # [[level, title, page], ...]

        if toc:
            chapters = _pdf_chapters_from_toc(doc, toc)
        else:
            chapters = _pdf_chapters_heuristic(doc)

        total_pages = len(doc)
    finally:
        doc.close()

    if not chapters:
        raise RuntimeError(
            "Could not extract any chapters from the PDF. "
            "The file may be scanned/image-only or have no readable text."
        )

    return {
        "title": title,
        "authors": authors,
        "format": "pdf",
        "original_file": file_path.name,
        "total_pages": total_pages,
        "chapters": chapters,
    }


def _pdf_chapters_from_toc(doc, toc: list) -> List[Dict[str, Any]]:
    """Use the PDF's bookmark tree to split into chapters."""
    top_level = [(t, p) for lvl, t, p in toc if lvl == 1]

    if len(top_level) <= 1:
        # Level-1 is probably just the book title; try level ≤ 2
        top_level = [(t, p) for lvl, t, p in toc if lvl <= 2]

    if not top_level:
        return _pdf_chapters_heuristic(doc)

    num_pages = len(doc)
    chapters: List[Dict[str, Any]] = []

    for i, (title, start_page) in enumerate(top_level):
        end_page = (
            top_level[i + 1][1] - 1 if i + 1 < len(top_level) else num_pages
        )
        start_page = max(1, min(start_page, num_pages))
        end_page = max(start_page, min(end_page, num_pages))

        text_parts = []
        for pn in range(start_page - 1, end_page):  # 0-indexed
            text_parts.append(doc[pn].get_text())

        content = "\n\n".join(text_parts).strip()
        if not content:
            continue

        clean = _clean_title(title)
        chapters.append(
            {
                "id": _make_id(clean, i + 1),
                "title": clean,
                "content": content,
                "page_range": f"{start_page}-{end_page}",
            }
        )

    return chapters


_CHAPTER_RE = re.compile(
    r"^\s*(?:"
    r"chapter\s+\d+|"
    r"chapter\s+[ivxlc]+|"
    r"part\s+\d+|"
    r"part\s+[ivxlc]+|"
    r"section\s+\d+|"
    r"\d{1,3}\.\s+\S"
    r")",
    re.IGNORECASE,
)


def _pdf_chapters_heuristic(doc) -> List[Dict[str, Any]]:
    """Detect chapters by heading patterns when no bookmarks exist."""
    all_text: List[str] = []
    starts: List[Tuple[int, str]] = []

    for i in range(len(doc)):
        text = doc[i].get_text().strip()
        all_text.append(text)
        if text and _CHAPTER_RE.match(text):
            first_line = text.split("\n")[0].strip()
            starts.append((i, first_line))

    if not starts:
        return _pdf_pages_chunked(all_text)

    chapters: List[Dict[str, Any]] = []
    for i, (page_idx, heading) in enumerate(starts):
        end_idx = starts[i + 1][0] if i + 1 < len(starts) else len(doc)
        content = "\n\n".join(all_text[page_idx:end_idx]).strip()
        if not content:
            continue
        clean = _clean_title(heading)
        chapters.append(
            {
                "id": _make_id(clean, i + 1),
                "title": clean,
                "content": content,
                "page_range": f"{page_idx + 1}-{end_idx}",
            }
        )

    return chapters


def _pdf_pages_chunked(all_text: List[str]) -> List[Dict[str, Any]]:
    """Last-resort fallback: split into ~20-page chunks."""
    chunk_size = 20
    chapters: List[Dict[str, Any]] = []
    for start in range(0, len(all_text), chunk_size):
        end = min(start + chunk_size, len(all_text))
        content = "\n\n".join(all_text[start:end]).strip()
        if content:
            n = len(chapters) + 1
            chapters.append(
                {
                    "id": f"section-{n}",
                    "title": f"Section {n} (pages {start + 1}\u2013{end})",
                    "content": content,
                    "page_range": f"{start + 1}-{end}",
                }
            )
    return chapters


# ---------------------------------------------------------------------------
# EPUB parsing
# ---------------------------------------------------------------------------


def _parse_epub(file_path: Path) -> Dict[str, Any]:
    import ebooklib
    from ebooklib import epub

    book = epub.read_epub(str(file_path))

    raw_title = book.get_metadata("DC", "title")
    title = (
        raw_title[0][0]
        if raw_title
        else _title_from_filename(file_path)
    )

    raw_creator = book.get_metadata("DC", "creator")
    authors = [c[0] for c in raw_creator] if raw_creator else []

    spine_items = []
    for item_id, _ in book.spine:
        item = book.get_item_with_id(item_id)
        if item and item.get_type() == ebooklib.ITEM_DOCUMENT:
            spine_items.append(item)

    toc_entries = _flatten_epub_toc(book.toc)

    if toc_entries:
        chapters = _epub_chapters_from_toc(toc_entries, spine_items)
    else:
        chapters = _epub_chapters_from_spine(spine_items)

    if not chapters:
        raise RuntimeError(
            "Could not extract any chapters from the EPUB. "
            "The file may be DRM-protected or malformed."
        )

    return {
        "title": title,
        "authors": authors,
        "format": "epub",
        "original_file": file_path.name,
        "total_pages": None,
        "chapters": chapters,
    }


def _flatten_epub_toc(toc) -> List[Tuple[str, Optional[str]]]:
    """Flatten nested EPUB TOC into [(title, href), ...]."""
    entries: List[Tuple[str, Optional[str]]] = []
    for item in toc:
        if isinstance(item, tuple):
            section, children = item
            title = section.title if hasattr(section, "title") else str(section)
            href = getattr(section, "href", None)
            entries.append((title, href))
            entries.extend(_flatten_epub_toc(children))
        elif hasattr(item, "title"):
            entries.append((item.title, getattr(item, "href", None)))
    return entries


def _epub_chapters_from_toc(
    toc_entries: List[Tuple[str, Optional[str]]],
    spine_items: list,
) -> List[Dict[str, Any]]:
    """Map TOC entries to spine items and extract text."""
    chapters: List[Dict[str, Any]] = []
    seen_hrefs: set = set()

    for i, (title, href) in enumerate(toc_entries):
        if not title or not href:
            continue

        href_clean = href.split("#")[0]
        if href_clean in seen_hrefs:
            continue
        seen_hrefs.add(href_clean)

        for item in spine_items:
            item_name = item.get_name()
            if item_name == href_clean or item_name.endswith("/" + href_clean):
                html = item.get_content().decode("utf-8", errors="replace")
                content = _html_to_markdown(html)
                if not content.strip():
                    break
                clean = _clean_title(title)
                chapters.append(
                    {
                        "id": _make_id(clean, i + 1),
                        "title": clean,
                        "content": content,
                    }
                )
                break

    return chapters


def _epub_chapters_from_spine(spine_items: list) -> List[Dict[str, Any]]:
    """Fallback: treat each spine item as a chapter."""
    from bs4 import BeautifulSoup

    chapters: List[Dict[str, Any]] = []

    for i, item in enumerate(spine_items):
        html = item.get_content().decode("utf-8", errors="replace")
        content = _html_to_markdown(html)
        if not content.strip():
            continue

        soup = BeautifulSoup(html, "html.parser")
        heading = soup.find(["h1", "h2", "h3"])
        title = heading.get_text().strip() if heading else f"Section {i + 1}"

        clean = _clean_title(title)
        chapters.append(
            {
                "id": _make_id(clean, len(chapters) + 1),
                "title": clean,
                "content": content,
            }
        )

    return chapters


# ---------------------------------------------------------------------------
# HTML → Markdown (for EPUB)
# ---------------------------------------------------------------------------


def _html_to_markdown(html: str) -> str:
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "nav", "header", "footer"]):
        tag.decompose()

    root = soup.body if soup.body else soup
    lines: List[str] = []
    _walk(root, lines)

    text = "\n".join(lines)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _walk(elem, lines: list) -> None:
    from bs4 import NavigableString, Tag

    if isinstance(elem, NavigableString):
        text = str(elem).strip()
        if text:
            lines.append(text)
        return

    if not isinstance(elem, Tag):
        return

    tag = elem.name

    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        prefix = "#" * int(tag[1])
        lines.append(f"\n{prefix} {elem.get_text().strip()}\n")
    elif tag == "p":
        text = elem.get_text().strip()
        if text:
            lines.append(f"\n{text}\n")
    elif tag in ("ul", "ol"):
        lines.append("")
        for i, li in enumerate(elem.find_all("li", recursive=False)):
            marker = f"{i + 1}." if tag == "ol" else "-"
            lines.append(f"{marker} {li.get_text().strip()}")
        lines.append("")
    elif tag in ("pre", "code"):
        lines.append(f"\n```\n{elem.get_text()}\n```\n")
    elif tag == "blockquote":
        for line in elem.get_text().strip().split("\n"):
            lines.append(f"> {line}")
    elif tag == "br":
        lines.append("")
    elif tag in ("div", "section", "article", "main", "span", "body"):
        for child in elem.children:
            _walk(child, lines)
    else:
        text = elem.get_text().strip()
        if text:
            lines.append(text)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _title_from_filename(path: Path) -> str:
    return path.stem.replace("-", " ").replace("_", " ").title()


def _clean_title(title: str) -> str:
    title = title.strip()
    title = re.sub(r"^\d+\.\s*", "", title)
    title = re.sub(r"\s+", " ", title)
    return title


def _make_id(title: str, fallback_num: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    if not slug:
        slug = f"chapter-{fallback_num}"
    if len(slug) > 50:
        slug = slug[:50].rstrip("-")
    return slug
