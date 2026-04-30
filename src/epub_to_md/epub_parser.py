import zipfile
from dataclasses import dataclass, field
from io import BytesIO

from epub_to_md.exceptions import InvalidEpubError


@dataclass
class Metadata:
    title: str = ""
    creator: str = ""


@dataclass
class Chapter:
    id: str
    html_content: str


@dataclass
class Epub:
    metadata: Metadata
    chapters: list[Chapter]
    images: dict[str, bytes] = field(default_factory=dict)


def parse_epub(data: bytes) -> Epub:
    """Parse EPUB bytes into structured Epub object."""
    try:
        with zipfile.ZipFile(BytesIO(data)) as zf:
            container = zf.read("META-INF/container.xml").decode("utf-8")
            opf_path = _extract_opf_path(container)
            opf = zf.read(opf_path).decode("utf-8")
            metadata = _extract_metadata(opf)
            chapter_files = _extract_chapter_files(opf)
            base_dir = opf_path.rsplit("/", 1)[0] if "/" in opf_path else ""

            chapters: list[Chapter] = []
            for chap_id, href in chapter_files:
                chap_path = f"{base_dir}/{href}" if base_dir else href
                html = zf.read(chap_path).decode("utf-8")
                chapters.append(Chapter(id=chap_id, html_content=html))

            images: dict[str, bytes] = {}
            for name in zf.namelist():
                if _is_image_file(name):
                    images[name] = zf.read(name)

        return Epub(metadata=metadata, chapters=chapters, images=images)
    except zipfile.BadZipFile:
        raise InvalidEpubError("File is not a valid ZIP/EPUB file")
    except KeyError as e:
        raise InvalidEpubError(f"Missing required file in EPUB: {e}")


def _extract_opf_path(container_xml: str) -> str:
    import re
    match = re.search(r'full-path="([^"]+)"', container_xml)
    if not match:
        raise ValueError("Cannot find OPF path in container.xml")
    return match.group(1)


def _extract_metadata(opf_xml: str) -> Metadata:
    import re
    title_match = re.search(r'<dc:title[^>]*>(.*?)</dc:title>', opf_xml, re.DOTALL)
    title = title_match.group(1).strip() if title_match else ""

    # Try standard dc:creator first, then file-as refinement (EPUB 3 self-closing form)
    creator = ""
    creator_match = re.search(r'<dc:creator[^>]*>(.*?)</dc:creator>', opf_xml, re.DOTALL)
    if creator_match:
        creator = creator_match.group(1).strip()
    if not creator:
        file_as_match = re.search(
            r'<meta\s+property="file-as"[^>]*refines="#([^"]+)"[^>]*>([^<]+)</meta>',
            opf_xml,
        )
        if file_as_match:
            creator = file_as_match.group(2).strip()

    return Metadata(title=title, creator=creator)


def _extract_chapter_files(opf_xml: str) -> list[tuple[str, str]]:
    import re
    spine_refs = re.findall(r'<itemref[^>]+idref="([^"]+)"', opf_xml)

    # Match all <item .../> elements regardless of attribute order
    item_map: dict[str, str] = {}
    for match in re.finditer(r'<item\s[^>]*/>', opf_xml):
        item_tag = match.group(0)
        id_match = re.search(r'id="([^"]+)"', item_tag)
        href_match = re.search(r'href="([^"]+)"', item_tag)
        if id_match and href_match:
            item_id = id_match.group(1)
            href = href_match.group(1)
            if href.endswith(".xhtml") or href.endswith(".html"):
                # Resolve relative paths
                item_map[item_id] = href

    result = []
    for ref in spine_refs:
        if ref in item_map:
            result.append((ref, item_map[ref]))
    return result


def _is_image_file(name: str) -> bool:
    return any(name.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"))
