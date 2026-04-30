"""Test with a realistic EPUB containing multiple chapter types."""
import zipfile
import io
from epub_to_md.orchestrator import convert


def _build_realistic_epub() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("mimetype", "application/epub+zip")
        zf.writestr("META-INF/container.xml", """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles>
</container>""")
        opf = """<?xml version="1.0"?>
<package xmlns="http://www.idpf.org/2007/opf" version="3.0">
  <metadata>
    <dc:title xmlns:dc="http://purl.org/dc/elements/1.1/">Realistic Test Book</dc:title>
    <dc:creator xmlns:dc="http://purl.org/dc/elements/1.1/">Real Author</dc:creator>
  </metadata>
  <manifest>
    <item id="ch1" href="chap1.xhtml" media-type="application/xhtml+xml"/>
    <item id="ch2" href="chap2.xhtml" media-type="application/xhtml+xml"/>
    <item id="img1" href="images/cover.png" media-type="image/png"/>
  </manifest>
  <spine>
    <itemref idref="ch1"/>
    <itemref idref="ch2"/>
  </spine>
</package>"""
        zf.writestr("OEBPS/content.opf", opf)
        zf.writestr("OEBPS/chap1.xhtml", """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 1</title></head>
<body>
<h1>Introduction</h1>
<p>This is the first chapter with an image: <img src="images/cover.png" alt="Cover"/></p>
<ul><li>Item <b>A</b></li><li>Item <i>B</i></li></ul>
</body>
</html>""")
        zf.writestr("OEBPS/chap2.xhtml", """<?xml version="1.0"?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head><title>Chapter 2</title></head>
<body>
<h2>Details</h2>
<p>Some <a href="http://example.com">link</a> here.</p>
<pre><code class="language-python">print("hello")</code></pre>
</body>
</html>""")
        zf.writestr("OEBPS/images/cover.png", b"fake_png_bytes_for_real_test")
    return buf.getvalue()


def test_realistic_epub_conversion():
    epub_data = _build_realistic_epub()
    result = convert(epub_data)

    # Metadata
    assert "title: Realistic Test Book" in result
    assert "creator: Real Author" in result

    # Chapter 1 content
    assert "# Introduction" in result
    assert "first chapter" in result
    assert "data:image/png;base64," in result  # image embedded

    # Chapter 2 content
    assert "## Details" in result
    assert "[link](http://example.com)" in result
    assert "```python" in result
    assert 'print("hello")' in result
