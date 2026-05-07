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
    href: str  # original href from manifest
    html_content: str


@dataclass
class TocEntry:
    title: str
    href: str
    level: int  # 0-based: 0 = h1, 1 = h2, etc.


@dataclass
class Epub:
    metadata: Metadata
    chapters: list[Chapter]
    images: dict[str, bytes] = field(default_factory=dict)
    toc: list[TocEntry] = field(default_factory=list)


def parse_epub(data: bytes) -> Epub:
    """Parse EPUB bytes into structured Epub object."""
    try:
        with zipfile.ZipFile(BytesIO(data)) as zf:
            container = zf.read("META-INF/container.xml").decode("utf-8")
            opf_path = _extract_opf_path(container)
            opf = zf.read(opf_path).decode("utf-8")
            metadata = _extract_metadata(opf)
            chapter_files, ncx_href, nav_href = _extract_chapter_files(opf)
            base_dir = opf_path.rsplit("/", 1)[0] if "/" in opf_path else ""

            chapters: list[Chapter] = []
            for chap_id, href in chapter_files:
                chap_path = f"{base_dir}/{href}" if base_dir else href
                html = zf.read(chap_path).decode("utf-8")
                chapters.append(Chapter(id=chap_id, href=href, html_content=html))

            images: dict[str, bytes] = {}
            for name in zf.namelist():
                if _is_image_file(name):
                    images[name] = zf.read(name)

            # Parse TOC from NCX or Nav
            toc: list[TocEntry] = []
            if ncx_href:
                ncx_path = f"{base_dir}/{ncx_href}" if base_dir else ncx_href
                try:
                    ncx_content = zf.read(ncx_path).decode("utf-8")
                    toc = _parse_ncx(ncx_content)
                except KeyError:
                    pass
            if not toc and nav_href:
                nav_path = f"{base_dir}/{nav_href}" if base_dir else nav_href
                try:
                    nav_content = zf.read(nav_path).decode("utf-8")
                    toc = _parse_nav(nav_content)
                except KeyError:
                    pass

        return Epub(metadata=metadata, chapters=chapters, images=images, toc=toc)
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

    # Try standard dc:creator first
    creator = ""
    creator_match = re.search(r'<dc:creator[^>]*>(.*?)</dc:creator>', opf_xml, re.DOTALL)
    if creator_match:
        creator = creator_match.group(1).strip()

    # Fallback: EPUB 3 self-closing dc:creator with file-as meta refinement
    if not creator:
        for meta_match in re.finditer(r'<meta\s[^>]*>([^<]*)</meta>', opf_xml):
            meta_tag = meta_match.group(0)
            if 'property="file-as"' in meta_tag:
                refines_match = re.search(r'refines="#([^"]+)"', meta_tag)
                content = meta_match.group(1).strip()
                if refines_match and content:
                    creator = content
                    break

    return Metadata(title=title, creator=creator)


def _extract_chapter_files(opf_xml: str) -> tuple[list[tuple[str, str]], str | None, str | None]:
    """Extract (id, href) pairs from OPF spine/manifest.
    Returns (chapters, ncx_href, nav_href)."""
    import re
    spine_refs = re.findall(r'<itemref[^>]+idref="([^"]+)"', opf_xml)

    item_map: dict[str, str] = {}
    ncx_href: str | None = None
    nav_href: str | None = None

    for match in re.finditer(r'<item\s[^>]*?(?:/>|</item>)', opf_xml):
        item_tag = match.group(0)
        id_match = re.search(r'id="([^"]+)"', item_tag)
        href_match = re.search(r'href="([^"]+)"', item_tag)
        if id_match and href_match:
            item_id = id_match.group(1)
            href = href_match.group(1)
            if 'media-type="application/x-dtbncx+xml"' in item_tag:
                ncx_href = href
            elif 'properties="nav"' in item_tag:
                nav_href = href
            if href.endswith(".xhtml") or href.endswith(".html") or href.endswith(".htm"):
                item_map[item_id] = href

    result = []
    for ref in spine_refs:
        if ref in item_map:
            result.append((ref, item_map[ref]))
    return result, ncx_href, nav_href


def _is_image_file(name: str) -> bool:
    return any(name.lower().endswith(ext) for ext in (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp"))


def _parse_ncx(ncx_xml: str) -> list[TocEntry]:
    """Parse NCX (EPUB 2) table of contents using BeautifulSoup."""
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(ncx_xml, "xml")
    entries: list[TocEntry] = []

    def _walk(parent_tag, level: int = 0) -> None:
        for nav_point in parent_tag.find_all("navPoint", recursive=False):
            label = nav_point.find("text")
            content = nav_point.find("content")
            if label and content:
                title = label.get_text(strip=True)
                src = content.get("src", "")
                if title:
                    entries.append(TocEntry(title=title, href=src, level=level))
            _walk(nav_point, level + 1)

    nav_map = soup.find("navMap")
    if nav_map:
        _walk(nav_map)

    return entries


def _parse_nav(nav_html: str) -> list[TocEntry]:
    """Parse EPUB 3 Nav document table of contents using BeautifulSoup."""
    import warnings
    from bs4 import BeautifulSoup, XMLParsedAsHTMLWarning
    warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)
    soup = BeautifulSoup(nav_html, "lxml")
    entries: list[TocEntry] = []

    # Find the toc nav — look for nav with epub:type="toc"
    toc_nav = None
    for nav in soup.find_all("nav"):
        if nav.get("epub:type") == "toc":
            toc_nav = nav
            break

    if toc_nav is None:
        return entries

    def _walk_ol(ol_tag, level: int = 0) -> None:
        for li in ol_tag.find_all("li", recursive=False):
            a = li.find("a")
            if a:
                href = a.get("href", "")
                title = a.get_text(strip=True)
                if title:
                    entries.append(TocEntry(title=title, href=href, level=level))
            nested_ol = li.find("ol")
            if nested_ol:
                _walk_ol(nested_ol, level + 1)

    first_ol = toc_nav.find("ol")
    if first_ol:
        _walk_ol(first_ol)

    return entries
