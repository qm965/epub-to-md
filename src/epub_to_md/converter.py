import warnings
from bs4 import BeautifulSoup, Tag, NavigableString, XMLParsedAsHTMLWarning

warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


def html_to_md(html: str) -> str:
    """Convert XHTML string to Markdown string."""
    soup = BeautifulSoup(html, "lxml")
    body = soup.find("body")
    if body is None:
        return ""
    lines = _convert_node(body, 0)
    return "\n".join(lines)


def _convert_node(node: Tag | NavigableString, indent: int) -> list[str]:
    """Recursively convert a BeautifulSoup node to Markdown lines."""
    if isinstance(node, NavigableString):
        text = str(node).strip()
        return [text] if text else []

    tag = node.name  # type: ignore[union-attr]
    children = list(node.children)  # type: ignore[union-attr]

    match tag:
        # Block-level elements
        case "h1":
            return [f"# {_inline_text(node)}", ""]
        case "h2":
            return [f"## {_inline_text(node)}", ""]
        case "h3":
            return [f"### {_inline_text(node)}", ""]
        case "h4":
            return [f"#### {_inline_text(node)}", ""]
        case "h5":
            return [f"##### {_inline_text(node)}", ""]
        case "h6":
            return [f"###### {_inline_text(node)}", ""]
        case "p":
            text = _inline_text(node)
            return [f"{text}", ""] if text else [""]
        case "br":
            return ["", ""]
        case "hr":
            return ["---", ""]
        case "blockquote":
            inner = _convert_children(node, indent)
            return [f"> {line}" if line else ">" for line in inner] + [""]
        case "ul":
            return _convert_list(node, indent, ordered=False)
        case "ol":
            return _convert_list(node, indent, ordered=True)
        case "li":
            return _convert_children(node, indent)
        case "table":
            return _convert_table(node)
        case "pre":
            return _convert_pre(node)
        case "img":
            src = node.get("src", "")
            alt = node.get("alt", "")
            return [f"![{alt}]({src})", ""]
        case "div" | "body" | "section" | "article" | "main" | "header" | "footer" | "nav":
            return _convert_children(node, indent) + [""]
        case _:
            return _convert_children(node, indent)


def _convert_children(node: Tag, indent: int) -> list[str]:
    """Convert child nodes and flatten the result."""
    lines: list[str] = []
    for child in node.children:
        lines.extend(_convert_node(child, indent))
    return lines


def _convert_list(node: Tag, indent: int, ordered: bool) -> list[str]:
    """Convert ul/ol to Markdown list."""
    lines: list[str] = []
    for i, li in enumerate(node.find_all("li", recursive=False)):
        prefix = f"{'  ' * indent}{f'{i+1}.' if ordered else '-'} "
        inner = _convert_node(li, indent + 1)
        if inner:
            first = inner[0]
            rest = inner[1:]
            lines.append(f"{prefix}{first}")
            lines.extend(f"{'  ' * (indent + 1)}{line}" for line in rest if line)
    lines.append("")
    return lines


def _convert_pre(node: Tag) -> list[str]:
    """Convert <pre><code> block to fenced code."""
    code = node.find("code")
    if code:
        lang = code.get("class", [])
        lang_str = ""
        for c in lang:
            if c.startswith("language-"):
                lang_str = c.removeprefix("language-")
                break
        text = code.get_text()
    else:
        lang_str = ""
        text = node.get_text()
    text = text.strip("\n")
    return [f"```{lang_str}", text, "```", ""]


def _convert_table(node: Tag) -> list[str]:
    """Convert HTML table to GitHub-flavored Markdown."""
    lines: list[str] = []
    rows = node.find_all("tr")
    if not rows:
        return [""]

    max_cols = 0
    for row in rows:
        cells = row.find_all(["th", "td"])
        max_cols = max(max_cols, len(cells))

    if max_cols == 0:
        return [""]

    header_row = rows[0]
    headers = header_row.find_all(["th", "td"])
    header_texts = [_inline_text(h).strip() for h in headers]
    while len(header_texts) < max_cols:
        header_texts.append("")

    lines.append("| " + " | ".join(header_texts) + " |")
    lines.append("| " + " | ".join(["---"] * max_cols) + " |")

    for row in rows[1:]:
        cells = row.find_all(["th", "td"])
        cell_texts = [_inline_text(c).strip() for c in cells]
        while len(cell_texts) < max_cols:
            cell_texts.append("")
        lines.append("| " + " | ".join(cell_texts) + " |")

    lines.append("")
    return lines


def _convert_math(math_node: Tag) -> str:
    """Simple MathML-to-LaTeX conversion."""
    def _math_text(node: Tag | NavigableString) -> str:
        if isinstance(node, NavigableString):
            return str(node)
        tag = node.name
        match tag:
            case "mi" | "mn" | "mo" | "mtext":
                return node.get_text()
            case "msup":
                base_elem = node.find(["mi", "mn", "mo"])
                base = _math_text(base_elem) if base_elem else ""
                children_text = ""
                for child in node.children:
                    if isinstance(child, Tag) and child is not base_elem:
                        children_text += _math_text(child)
                exp = children_text or node.get_text().replace(base, "", 1) if base else node.get_text()
                return f"{base}^{{{exp}}}"
            case "msub":
                base_elem = node.find(["mi", "mn", "mo"])
                base = _math_text(base_elem) if base_elem else ""
                children_text = ""
                for child in node.children:
                    if isinstance(child, Tag) and child is not base_elem:
                        children_text += _math_text(child)
                sub = children_text or node.get_text().replace(base, "", 1) if base else node.get_text()
                return f"{base}_{{{sub}}}"
            case "math":
                return "".join(_math_text(child) for child in node.children)
            case "mrow":
                return "".join(_math_text(child) for child in node.children)
            case _:
                return node.get_text()
    return _math_text(math_node) if isinstance(math_node, Tag) else str(math_node)


def _inline_text(node: Tag) -> str:
    """Convert inline elements to Markdown, returning a single string."""
    parts: list[str] = []
    for child in node.children:
        if isinstance(child, NavigableString):
            text = str(child)
            parts.append(text)
        elif isinstance(child, Tag):
            tag = child.name
            match tag:
                case "b" | "strong":
                    parts.append(f"**{_inline_text(child)}**")
                case "i" | "em":
                    parts.append(f"*{_inline_text(child)}*")
                case "a":
                    href = child.get("href", "")
                    text = _inline_text(child).strip()
                    # Detect footnote links — render as clean [fnN]
                    if (child.get("epub:type") == "noteref"
                            or "noteref" in (child.get("class", "") or "")
                            or "footnote" in href.lower()
                            or "fn" in href.lower()):
                        parts.append(f"[{text}]")
                    # Strip cross-chapter links (page refs like chapter001.xhtml#pg11)
                    elif ".xhtml" in href.lower() or ".html" in href.lower():
                        parts.append(text)
                    else:
                        parts.append(f"[{text}]({href})")
                case "img":
                    src = child.get("src", "")
                    alt = child.get("alt", "")
                    parts.append(f"![{alt}]({src})")
                case "code":
                    parts.append(f"`{child.get_text()}`")
                case "br":
                    parts.append("  \n")
                case "math":
                    parts.append(_convert_math(child))
                case "sup":
                    inner = _inline_text(child).strip()
                    # Clean sup wrapping for footnote links
                    if inner.startswith("[") and inner.endswith("]"):
                        parts.append(inner)
                    else:
                        parts.append(f"^{{ {inner} }}")
                case "sub":
                    parts.append(f"~{_inline_text(child)}~")
                case "span" | "u" | "s" | "del" | "ins" | "small" | "abbr":
                    parts.append(_inline_text(child))
                case _:
                    parts.append(_inline_text(child))
    return "".join(parts)
