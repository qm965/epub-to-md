from epub_to_md.image_resolver import resolve_images, _get_mime_type
from epub_to_md.epub_parser import Epub, Metadata, Chapter


def test_resolve_images_replaces_src_with_base64():
    epub = Epub(
        metadata=Metadata(title="T", creator="A"),
        chapters=[Chapter(id="c1", html_content='<img src="images/pic.png"/>')],
        images={"OEBPS/images/pic.png": b"fake_png_bytes"},
    )
    html = epub.chapters[0].html_content
    result = resolve_images(html, "OEBPS/", epub.images)
    assert "data:image/png;base64," in result
    assert "fake_png_bytes" not in result


def test_resolve_images_handles_jpg():
    epub = Epub(
        metadata=Metadata(title="T", creator="A"),
        chapters=[Chapter(id="c1", html_content='<img src="images/photo.jpg"/>')],
        images={"OEBPS/images/photo.jpg": b"fake_jpeg_bytes"},
    )
    result = resolve_images(epub.chapters[0].html_content, "OEBPS/", epub.images)
    assert "data:image/jpeg;base64," in result


def test_resolve_images_nonexistent_image():
    """If image file not found in EPUB, leave the original src."""
    epub = Epub(
        metadata=Metadata(title="T", creator="A"),
        chapters=[Chapter(id="c1", html_content='<img src="missing.png"/>')],
        images={},
    )
    result = resolve_images(epub.chapters[0].html_content, "OEBPS/", epub.images)
    assert "missing.png" in result
    assert "data:" not in result


def test_get_mime_type():
    assert _get_mime_type("img.png") == "image/png"
    assert _get_mime_type("img.jpg") == "image/jpeg"
    assert _get_mime_type("img.jpeg") == "image/jpeg"
    assert _get_mime_type("img.gif") == "image/gif"
    assert _get_mime_type("img.svg") == "image/svg+xml"
    assert _get_mime_type("img.webp") == "image/webp"
    assert _get_mime_type("unknown.xyz") == "application/octet-stream"
