"""Costanti di stile, regex placeholder, palette colori – STUB."""
import re

PLACEHOLDER_RGX = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")
DEFAULT_COLS = 4
PALETTE = {
    "error": "#e74c3c",
    "valid": "#2ecc71",
    "bg": "#f9f9f9",
}
