import base64
import re
from pathlib import Path


def resolve_images(html: str, base_dir: str, images: dict[str, bytes]) -> str:
    """Replace <img src> references with base64 data URIs.

    Tries multiple path resolutions since EPUB internal paths vary.
    """
    def _replace(match: re.Match) -> str:
        tag = match.group(0)
        src_match = re.search(r'src="([^"]*)"', tag)
        alt_match = re.search(r'alt="([^"]*)"', tag)
        if not src_match:
            return tag
        src = src_match.group(1)
        alt = alt_match.group(1) if alt_match else ""

        # Try exact match, then with base_dir prefix, then various path resolutions
        candidates = [src]
        if base_dir:
            candidates.append(f"{base_dir}/{src}")
            parts = base_dir.split("/")
            for i in range(len(parts) - 1, 0, -1):
                candidates.append(f"{'/'.join(parts[:i])}/{src}")

        image_data = None
        matched_key = None
        for candidate in candidates:
            if candidate in images:
                image_data = images[candidate]
                matched_key = candidate
                break

        if image_data is None:
            src_filename = Path(src).name
            for key, data in images.items():
                if Path(key).name == src_filename:
                    image_data = data
                    matched_key = key
                    break

        if image_data is None:
            return tag

        mime = _get_mime_type(matched_key or src)
        b64 = base64.b64encode(image_data).decode("ascii")
        return f'<img src="data:{mime};base64,{b64}" alt="{alt}"/>'

    return re.sub(r'<img[^>]*>', _replace, html)


def _get_mime_type(filename: str) -> str:
    ext = Path(filename).suffix.lower()
    return {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".svg": "image/svg+xml",
        ".webp": "image/webp",
    }.get(ext, "application/octet-stream")
