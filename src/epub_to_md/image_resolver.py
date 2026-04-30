import base64
import re
from pathlib import Path


def resolve_images(html: str, base_dir: str, images: dict[str, bytes]) -> str:
    """Replace <img src> references with base64 data URIs.

    Tries multiple path resolutions since EPUB internal paths vary.
    """
    def _replace(match: re.Match) -> str:
        src = match.group(1)
        alt = match.group(2) or ""

        # Try exact match, then with base_dir prefix, then various path resolutions
        candidates = [src]
        if base_dir:
            candidates.append(f"{base_dir}/{src}")
            # Also try parent dir without last component
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

        # Fuzzy match: search by filename only
        if image_data is None:
            src_filename = Path(src).name
            for key, data in images.items():
                if Path(key).name == src_filename:
                    image_data = data
                    matched_key = key
                    break

        if image_data is None:
            # Image not found — leave src as-is
            return match.group(0)

        mime = _get_mime_type(matched_key or src)
        b64 = base64.b64encode(image_data).decode("ascii")
        return f'<img src="data:{mime};base64,{b64}" alt="{alt}"/>'

    return re.sub(
        r'<img\s+src="([^"]*)"(?:\s+alt="([^"]*)")?\s*/?>',
        _replace,
        html,
    )


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
