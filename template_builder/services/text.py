"""template_builder.services.text

Funzioni PURE legate alla manipolazione di testo.
Derivano dalla logica legacy ma sono state riscritte in
forma testabile, senza dipendenze su Tkinter o altri sottosistemi.
"""

from __future__ import annotations

import html
import re
from typing import List, Sequence, Set

from ..assets import PLACEHOLDER_RGX

__all__ = [
    "smart_paste",
    "auto_format",
    "extract_placeholders",
    "images_to_html",
    "get_field_help",
]

# ---------------------------------------------------------------------------
# split_lines
# ---------------------------------------------------------------------------
def _split_lines(raw: str) -> List[str]:
    """Divide una stringa incollata in linee pulite.

    • accetta separatori: newline (`\n`) e punto-e-virgola (`;`)
    • rimuove spazi iniziali/finali
    • filtra righe vuote
    """
    unified = raw.replace(";", "\n")
    return [ln.strip() for ln in unified.splitlines() if ln.strip()]

# ---------------------------------------------------------------------------
# smart_paste
# ---------------------------------------------------------------------------
def smart_paste(raw: str | Sequence[str]) -> List[str]:
    """Restituisce una lista di stringhe "pulite" da incollare.

    Accetta:
      * blocco di testo (multilinea o con `;`)
      * lista/tupla di stringhe (già suddivise)
    """
    if raw is None:
        return []
    if isinstance(raw, str):
        return _split_lines(raw)
    # presumiamo una sequenza di stringhe
    try:
        lines: List[str] = []
        for item in raw:
            lines.extend(_split_lines(str(item)))
        return lines
    except Exception:
        return []

# ---------------------------------------------------------------------------
# extract_placeholders
# ---------------------------------------------------------------------------
def extract_placeholders(html_src: str) -> Set[str]:
    """Estrae tutti i {{TAG}} da una stringa HTML."""
    return set(PLACEHOLDER_RGX.findall(html_src))

# ---------------------------------------------------------------------------
# auto_format
# ---------------------------------------------------------------------------
_RE_HAS_TAG = re.compile(r"<[^>]+>")

def auto_format(text: str, *, mode: str = "ul") -> str:
    """Converte testo *plain* in semplice markup HTML.

    - mode="ul": genera una lista <ul><li>… per ogni linea
    - mode="p" : genera un paragrafo <p>…</p> per ogni linea

    In modalità UL, se il testo contiene già tag HTML, viene restituito
    invariato. In modalità P, il testo viene sempre escapato e wrappato.
    """
    cleaned = text.strip()
    if not cleaned:
        return ""

    # modalità UL: se ci sono tag, non toccare
    if mode == "ul" and _RE_HAS_TAG.search(cleaned):
        return cleaned

    parts = smart_paste(cleaned)

    if mode == "ul":
        items = "".join(f"<li>{html.escape(p)}</li>" for p in parts)
        return f"<ul>{items}</ul>"

    if mode == "p":
        return "".join(f"<p>{html.escape(p)}</p>" for p in parts)

    # fallback generico
    return cleaned

def get_field_help(key: str) -> str:
    """Restituisce il testo di help per un campo (case‐insensitive)."""
    defaults = {
        "title":       "Titolo del prodotto",
        "description": "Descrizione del prodotto",
        # aggiungere qui altri help standard…
    }
    return defaults.get(key.strip().lower(), "")

# ---------------------------------------------------------------------------
# images_to_html
# ---------------------------------------------------------------------------
def images_to_html(rows: int, cols: int) -> str:
    """Genera una tabella HTML di placeholder per rows × cols immagini."""
    r = max(1, int(rows))
    c = max(1, int(cols))
    out: List[str] = ["<table>"]
    num = 1
    for _ in range(r):
        out.append("  <tr>")
        for _ in range(c):
            # ciascuna cella contiene un tag <img> con src = {{ IMGn }}
            out.append(f'    <td><img src="{{{{ IMG{num} }}}}" alt="" style="max-width:100%;"></td>')
            num += 1
        out.append("  </tr>")
    out.append("</table>")
    return "\n".join(out)
