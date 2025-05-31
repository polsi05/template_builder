"""template_builder.services.text

Funzioni PURE legate alla manipolazione di testo.
Derivano dalla logica legacy ma sono state riscritte in
forma testabile, senza dipendenze su Tkinter o altri sottosistemi.
"""

from __future__ import annotations

import html
import re
from typing import List, Sequence, Set, Union

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
def smart_paste(raw: Union[str, Sequence[str]]) -> List[str]:
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
    return set(match.group(1) for match in PLACEHOLDER_RGX.finditer(html_src))


# ---------------------------------------------------------------------------
# auto_format
# ---------------------------------------------------------------------------
_RE_HAS_TAG = re.compile(r"<[^>]+>")

def auto_format(text: str, *, mode: str = "ul") -> str:
    """Converte testo *plain* in semplice markup HTML.

    - mode="ul": genera una lista <ul><li>… per ogni linea (split anche su `;`)
    - mode="p" : genera un paragrafo <p>…</p> per ogni linea (split anche su `;`)

    In modalità UL, se il testo contiene già tag HTML, viene restituito invariato.
    """
    # Controllo presenza di tag HTML solo in UL
    if mode == "ul" and _RE_HAS_TAG.search(text):
        return text

    # Utilizzo smart_paste per splittare su newline e su `;`
    lines = smart_paste(text)

    if not lines:
        return ""

    if mode == "ul":
        # Genero <ul><li>…</li>…</ul> (tutto in un'unica riga, senza newline)
        items = "".join(f"<li>{html.escape(ln)}</li>" for ln in lines)
        return f"<ul>{items}</ul>"

    # mode == "p": per ogni linea un <p>…</p>, concatenati senza newline
    paragraphs = "".join(f"<p>{html.escape(ln)}</p>" for ln in lines)
    return paragraphs


# ---------------------------------------------------------------------------
# images_to_html (compatibilità monolitico)
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
            out.append(f'    <td><img src="{{{{ IMG{num} }}}}" alt="" style="max-width:100%;"></td>')
            num += 1
        out.append("  </tr>")
    out.append("</table>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# get_field_help (case-insensitive lookup)
# ---------------------------------------------------------------------------
_FIELD_HELP: dict[str, str] = {
    "title": "Titolo del prodotto (massimo 60 caratteri)",
    "description": "Descrizione lunga (vale 500 caratteri max), supporta invio a capo.",
}


def get_field_help(key: str) -> str:
    """Restituisce una stringa di aiuto per una chiave di campo (case-insensitive)."""
    return _FIELD_HELP.get(key.lower(), "")
