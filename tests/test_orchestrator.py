from epub_to_md.orchestrator import convert
from tests.test_epub_parser import _build_minimal_epub


def test_convert_produces_markdown():
    epub_bytes = _build_minimal_epub(
        title="My Book",
        creator="Me",
        chapters=[("chap1.xhtml", "<h1>Chapter 1</h1><p>Hello world</p>")],
    )
    result = convert(epub_bytes)
    assert result.startswith("---")  # YAML frontmatter
    assert "title: My Book" in result
    assert "creator: Me" in result
    assert "---" in result
    assert "# Chapter 1" in result
    assert "Hello world" in result


def test_convert_empty_epub():
    epub_bytes = _build_minimal_epub(
        title="Empty", creator="Nobody", chapters=[]
    )
    result = convert(epub_bytes)
    assert "title: Empty" in result
