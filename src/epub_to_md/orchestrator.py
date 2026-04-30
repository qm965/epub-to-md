import re
from epub_to_md.epub_parser import parse_epub, Epub, TocEntry
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

    # Group TOC entries by chapter file
    toc_by_file: dict[str, list[TocEntry]] = {}
    for entry in epub.toc:
        file_part = entry.href.split("#")[0]
        toc_by_file.setdefault(file_part, []).append(entry)

    for i, chapter in enumerate(epub.chapters):
        # Resolve images
        if epub.images:
            sample_key = next(iter(epub.images))
            base_dir = sample_key.rsplit("/", 1)[0] if "/" in sample_key else ""
        else:
            base_dir = ""

        html = resolve_images(chapter.html_content, base_dir, epub.images)

        # Inject TOC headings for this chapter
        for entry in toc_by_file.get(chapter.href, []):
            heading_html = f"<h{entry.level + 1}>{entry.title}</h{entry.level + 1}>"
            html = _inject_heading(html, heading_html, entry)

        md = html_to_md(html)
        parts.append(md)

    return "\n".join(parts)


def _inject_heading(html: str, heading_html: str, entry: TocEntry) -> str:
    """Inject a heading tag into the HTML content."""
    anchor = entry.href.split("#")[1] if "#" in entry.href else None
    if anchor:
        pattern = rf'(<[^>]+\s+id="?{re.escape(anchor)}"?[^>]*>)'
        match = re.search(pattern, html)
        if match:
            return html[:match.start()] + heading_html + "\n" + html[match.start():]

    body_match = re.search(r'<body[^>]*>', html)
    if body_match:
        return html[:body_match.end()] + "\n" + heading_html + html[body_match.end():]

    return heading_html + "\n" + html
