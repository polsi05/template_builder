"""Costanti di stile, regex placeholder, palette colori – STUB."""
import re

# Regex per estrarre {{ TAG }} con tag costituito da lettere maiuscole, numeri e underscore.
PLACEHOLDER_RGX = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")

# Numero di colonne di default per le griglie immagine
DEFAULT_COLS = 3

# Palette colori utilizzata in UI (stub)
PALETTE = {
    "error": "#e74c3c",
    "valid": "#2ecc71",
    "bg": "#f9f9f9",
}
