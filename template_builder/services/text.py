"""Funzioni testo (smart_paste, auto_format, ecc.) – STUB."""
from typing import List

def smart_paste(raw: str) -> List[str]:
    return [line.strip() for line in raw.splitlines() if line.strip()]

def auto_format(text: str, mode: str = "ul") -> str:
    return text

def extract_placeholders(html: str):
    from ..assets import PLACEHOLDER_RGX  # lazy import
    return set(m.group(1) for m in PLACEHOLDER_RGX.finditer(html))

def images_to_html(rows: int, cols: int):
    return "<!-- TODO: gallery -->"
