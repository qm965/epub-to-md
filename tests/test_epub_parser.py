import zipfile
import io
from pathlib import Path
from epub_to_md.epub_parser import parse_epub


def test_parse_epub_returns_metadata_and_chapters():
    """Minimal valid EPUB with one chapter."""
    epub_bytes = _build_minimal_epub(
        title="Test Book",
        creator="Test Author",
        chapters=[("chap1.xhtml", "<p>Hello</p>")],
    )
    result = parse_epub(epub_bytes)
    assert result.metadata.title == "Test Book"
    assert result.metadata.creator == "Test Author"
    assert len(result.chapters) == 1
    assert "Hello" in result.chapters[0].html_content


def test_parse_epub_extracts_images():
    """EPUB with an image should extract it."""
    epub_bytes = _build_epub_with_image("cover.png", b"fake_png_bytes")
    result = parse_epub(epub_bytes)
    assert len(result.images) > 0
    assert any("cover.png" in k for k in result.images)


def _build_minimal_epub(title: str, creator: str, chapters: list[tuple[str, str]]) -> bytes:
    """Build a minimal valid EPUB in memory for testing."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr("META-INF/container.xml", """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""")
        manifest_items = ""
        spine_refs = ""
        for i, (href, _) in enumerate(chapters):
            manifest_items += f'<item id="chap{i}" href="{href}" media-type="application/xhtml+xml"/>\n'
            spine_refs += f'<itemref idref="chap{i}"/>\n'
        opf = f"""<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata>
    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">{title}</dc:title>
    <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">{creator}</dc:creator>
  </metadata>
  <manifest>
    {manifest_items}
  </manifest>
  <spine>
    {spine_refs}
  </spine>
</package>"""
        zf.writestr("OEBPS/content.opf", opf)
        for href, body_content in chapters:
            xhtml = f"""<?xml version="1.0" encoding="utf-8"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter</title></head>
<body>{body_content}</body>
</html>"""
            zf.writestr(f"OEBPS/{href}", xhtml)
    return buf.getvalue()


def _build_epub_with_image(image_name: str, image_data: bytes) -> bytes:
    """Build a minimal EPUB containing an image file."""
    chapters = [("chap1.xhtml", "<p>Text with image</p>")]
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr("META-INF/container.xml", """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
  </rootfiles>
</container>""")
        opf = f"""<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata>
    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Test</dc:title>
    <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Author</dc:creator>
  </metadata>
  <manifest>
    <item id="chap0" href="chap1.xhtml" media-type="application/xhtml+xml"/>
    <item id="img0" href="{image_name}" media-type="image/png"/>
  </manifest>
  <spine>
    <itemref idref="chap0"/>
  </spine>
</package>"""
        zf.writestr("OEBPS/content.opf", opf)
        zf.writestr("OEBPS/chap1.xhtml", """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml"><body><p>Hello</p></body></html>""")
        zf.writestr(f"OEBPS/{image_name}", image_data)
    return buf.getvalue()
