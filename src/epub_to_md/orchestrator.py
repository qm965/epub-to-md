from epub_to_md.epub_parser import parse_epub, Epub
from epub_to_md.converter import html_to_md
from epub_to_md.image_resolver import resolve_images


def convert(epub_data: bytes) -> str:
    """Convert EPUB bytes to a complete Markdown string."""
    epub = parse_epub(epub_data)
    return _epub_to_md(epub)


def _epub_to_md(epub: Epub) -> str:
    """Convert parsed Epub to complete Markdown document."""
    parts: list[str] = []

    # YAML frontmatter
    parts.append("---")
    if epub.metadata.title:
        parts.append(f"title: {epub.metadata.title}")
    if epub.metadata.creator:
        parts.append(f"creator: {epub.metadata.creator}")
    parts.append("source: epub")
    parts.append("---")
    parts.append("")

    # Convert each chapter
    for i, chapter in enumerate(epub.chapters):
        # Resolve images with base dir from the first image key
        if epub.images:
            sample_key = next(iter(epub.images))
            base_dir = sample_key.rsplit("/", 1)[0] if "/" in sample_key else ""
        else:
            base_dir = ""
        html = resolve_images(chapter.html_content, base_dir, epub.images)

        md = html_to_md(html)
        parts.append(md)

    return "\n".join(parts)
