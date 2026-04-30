from bs4 import BeautifulSoup, Tag, NavigableString


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
            return ["  \\n"]
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
                    text = _inline_text(child)
                    parts.append(f"[{text}]({href})")
                case "img":
                    src = child.get("src", "")
                    alt = child.get("alt", "")
                    parts.append(f"![{alt}]({src})")
                case "code":
                    parts.append(f"`{child.get_text()}`")
                case "br":
                    parts.append("  \\n")
                case "sup":
                    parts.append(f"^{{ {_inline_text(child)} }}")
                case "sub":
                    parts.append(f"~{_inline_text(child)}~")
                case "span" | "u" | "s" | "del" | "ins" | "small" | "abbr":
                    parts.append(_inline_text(child))
                case _:
                    parts.append(_inline_text(child))
    return "".join(parts)
