"""Tests for book parsing helpers and the add-book CLI command."""

import zipfile
from pathlib import Path

import pytest
import yaml

from learning_os.book_parser import _clean_title, _make_id, _html_to_markdown


# ---------------------------------------------------------------------------
# Pure helper tests
# ---------------------------------------------------------------------------


class TestCleanTitle:
    def test_strips_leading_number(self):
        assert _clean_title("1. Introduction") == "Introduction"

    def test_strips_whitespace(self):
        assert _clean_title("  Chapter Title  ") == "Chapter Title"

    def test_collapses_inner_whitespace(self):
        assert _clean_title("A   Long    Title") == "A Long Title"

    def test_preserves_title_without_number(self):
        assert _clean_title("Conclusion") == "Conclusion"


class TestMakeId:
    def test_basic_slug(self):
        assert _make_id("Data Types & Variables", 1) == "data-types-variables"

    def test_empty_title_uses_fallback(self):
        assert _make_id("", 5) == "chapter-5"

    def test_truncates_long_slugs(self):
        long_title = "A " * 50  # generates a slug longer than 50 chars
        result = _make_id(long_title, 1)
        assert len(result) <= 50

    def test_strips_special_chars(self):
        assert _make_id("Hello, World! (2nd Edition)", 1) == "hello-world-2nd-edition"

    def test_no_trailing_hyphens_after_truncation(self):
        result = _make_id("A " * 50, 1)
        assert not result.endswith("-")


# ---------------------------------------------------------------------------
# HTML → Markdown tests
# ---------------------------------------------------------------------------


class TestHtmlToMarkdown:
    def _wrap(self, html):
        """Wrap HTML fragment in a body tag so BeautifulSoup parses it correctly."""
        return f"<body>{html}</body>"

    def test_headings(self):
        md = _html_to_markdown(self._wrap("<h1>Title</h1><h2>Subtitle</h2>"))
        assert "# Title" in md
        assert "## Subtitle" in md

    def test_paragraphs(self):
        md = _html_to_markdown(self._wrap("<p>First paragraph.</p><p>Second paragraph.</p>"))
        assert "First paragraph." in md
        assert "Second paragraph." in md

    def test_unordered_list(self):
        md = _html_to_markdown(self._wrap("<ul><li>Alpha</li><li>Beta</li></ul>"))
        assert "- Alpha" in md
        assert "- Beta" in md

    def test_ordered_list(self):
        md = _html_to_markdown(self._wrap("<ol><li>First</li><li>Second</li></ol>"))
        assert "1. First" in md
        assert "2. Second" in md

    def test_code_block(self):
        md = _html_to_markdown(self._wrap("<pre><code>x = 1</code></pre>"))
        assert "```" in md
        assert "x = 1" in md

    def test_strips_script_and_style(self):
        md = _html_to_markdown("<body><script>alert(1)</script><style>.x{}</style><p>Visible</p></body>")
        assert "alert" not in md
        assert "Visible" in md

    def test_empty_html_returns_empty(self):
        assert _html_to_markdown("") == ""


# ---------------------------------------------------------------------------
# add-book CLI smoke test (synthetic EPUB)
# ---------------------------------------------------------------------------


def _make_minimal_epub(path: Path) -> None:
    """Build a minimal valid EPUB file for testing.

    An EPUB is a zip with:
      mimetype
      META-INF/container.xml  → points to content.opf
      content.opf             → metadata + spine
      toc.ncx                 → table of contents
      chapter1.xhtml          → actual content
    """
    mimetype = "application/epub+zip"

    container_xml = (
        '<?xml version="1.0"?>'
        '<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
        "<rootfiles>"
        '<rootfile full-path="content.opf" media-type="application/oebps-package+xml"/>'
        "</rootfiles>"
        "</container>"
    )

    content_opf = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<package xmlns="http://www.idpf.org/2007/opf" version="2.0" unique-identifier="uid">'
        "<metadata>"
        '<dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Test Book</dc:title>'
        '<dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Test Author</dc:creator>'
        '<dc:identifier xmlns:dc="http://purl.org/dc/elements/1.1/" id="uid">test-123</dc:identifier>'
        '<dc:language xmlns:dc="http://purl.org/dc/elements/1.1/">en</dc:language>'
        "</metadata>"
        "<manifest>"
        '<item id="ch1" href="chapter1.xhtml" media-type="application/xhtml+xml"/>'
        '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>'
        "</manifest>"
        '<spine toc="ncx">'
        '<itemref idref="ch1"/>'
        "</spine>"
        "</package>"
    )

    toc_ncx = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
        "<head/>"
        "<docTitle><text>Test Book</text></docTitle>"
        "<navMap>"
        '<navPoint id="ch1" playOrder="1">'
        "<navLabel><text>Chapter One</text></navLabel>"
        '<content src="chapter1.xhtml"/>'
        "</navPoint>"
        "</navMap>"
        "</ncx>"
    )

    chapter1 = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<html xmlns="http://www.w3.org/1999/xhtml">'
        "<head><title>Chapter One</title></head>"
        "<body>"
        "<h1>Chapter One</h1>"
        "<p>This is the first chapter of the test book.</p>"
        "<p>It covers important concepts.</p>"
        "</body>"
        "</html>"
    )

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        # mimetype must be first and stored (not compressed)
        zf.writestr("mimetype", mimetype, compress_type=zipfile.ZIP_STORED)
        zf.writestr("META-INF/container.xml", container_xml)
        zf.writestr("content.opf", content_opf)
        zf.writestr("toc.ncx", toc_ncx)
        zf.writestr("chapter1.xhtml", chapter1)


@pytest.fixture
def epub_file(tmp_path):
    """Create a minimal test EPUB."""
    path = tmp_path / "test-book.epub"
    _make_minimal_epub(path)
    return path


def _has_book_deps():
    try:
        import ebooklib  # noqa: F401
        import bs4  # noqa: F401
        return True
    except ImportError:
        return False


@pytest.mark.skipif(not _has_book_deps(), reason="book deps not installed")
class TestAddBookCLI:
    def test_add_book_creates_output(self, tmp_path, epub_file):
        from click.testing import CliRunner
        from learning_os.cli import main

        workspace = tmp_path / "workspace"
        workspace.mkdir()

        runner = CliRunner()
        result = runner.invoke(
            main, ["add-book", str(epub_file), "--dir", str(workspace)]
        )

        assert result.exit_code == 0, result.output
        assert "Book ready" in result.output

        book_dir = workspace / "books" / "test-book"
        assert book_dir.is_dir()
        assert (book_dir / "book-outline.yaml").exists()
        assert (book_dir / "book-content").is_dir()
        assert (book_dir / "test-book.epub").exists()

        # Verify outline is valid YAML with expected structure
        outline = yaml.safe_load(
            (book_dir / "book-outline.yaml").read_text(encoding="utf-8")
        )
        assert outline["title"] == "Test Book"
        assert outline["format"] == "epub"
        assert len(outline["chapters"]) >= 1

        # Verify at least one content file was written
        content_files = list((book_dir / "book-content").glob("*.md"))
        assert len(content_files) >= 1

    def test_add_book_rejects_unsupported_format(self, tmp_path):
        from click.testing import CliRunner
        from learning_os.cli import main

        bad_file = tmp_path / "notes.txt"
        bad_file.write_text("hello")

        runner = CliRunner()
        result = runner.invoke(main, ["add-book", str(bad_file)])
        assert result.exit_code != 0
        assert "Unsupported format" in result.output


@pytest.mark.skipif(not _has_book_deps(), reason="book deps not installed")
class TestParseBook:
    def test_parse_epub_returns_expected_structure(self, epub_file):
        from learning_os.book_parser import parse_book

        result = parse_book(epub_file)

        assert result["title"] == "Test Book"
        assert result["authors"] == ["Test Author"]
        assert result["format"] == "epub"
        assert len(result["chapters"]) >= 1
        assert "content" in result["chapters"][0]

    def test_write_book_output(self, tmp_path, epub_file):
        from learning_os.book_parser import parse_book, write_book_output

        parsed = parse_book(epub_file)
        output_dir = tmp_path / "output"
        outline_path, content_paths = write_book_output(parsed, output_dir)

        assert outline_path.exists()
        assert len(content_paths) >= 1
        for cp in content_paths:
            assert cp.exists()
            text = cp.read_text(encoding="utf-8")
            assert text.startswith("# ")
