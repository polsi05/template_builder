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
]

# ---------------------------------------------------------------------------
# smart_paste
# ---------------------------------------------------------------------------

def _split_lines(raw: str) -> List[str]:
    """Divide una stringa incollata in linee pulite.

    • accetta separatori: newline (``\n``) e punto‑e‑virgola (``;``)  
    • rimuove spazi iniziali/finali  
    • filtra righe vuote
    """
    # sostituiamo i ; con newline per uniformare
    unified = raw.replace(";", "\n")
    return [ln.strip() for ln in unified.splitlines() if ln.strip()]


def smart_paste(raw: str | Sequence[str]) -> List[str]:
    """Restituisce una lista di stringhe "pulite" da incollare.

    Accetta:
      * blocco di testo (multilinea o con ";")
      * lista/tupla di stringhe (già suddivise)
    """
    if isinstance(raw, str):
        return _split_lines(raw)
    # se è già una sequenza, normalizza singoli elementi
    result: List[str] = []
    for item in raw:
        result.extend(_split_lines(str(item)))
    return result


# ---------------------------------------------------------------------------
# auto_format
# ---------------------------------------------------------------------------

_RE_HAS_TAG = re.compile(r"<[^>]+>")


def _wrap_ul(lines: List[str]) -> str:
    if not lines:
        return ""
    li = "".join(f"<li>{html.escape(line)}</li>" for line in lines)
    return f"<ul>{li}</ul>"


def _wrap_p(lines: List[str]) -> str:
    return "".join(f"<p>{html.escape(line)}</p>" for line in lines)


def auto_format(text: str, *, mode: str = "ul") -> str:
    """Converte testo *plain* in semplice markup HTML.

    - **mode="ul"** (default)  → newline ⇒ ``<li>`` dentro un ``<ul>``
    - **mode="p"**            → newline ⇒ ``<p>`` … ``</p>``

    Se il testo contiene già tag HTML (``<`` … ``>``) viene restituito
    invariato per non duplicare la formattazione.
    """
    cleaned = text.strip()
    if not cleaned:
        return ""

    # Se troviamo già tag, non tocchiamo la stringa
    if _RE_HAS_TAG.search(cleaned):
        return cleaned

    lines = [ln.strip() for ln in cleaned.splitlines() if ln.strip()]

    if mode == "p":
        return _wrap_p(lines)
    # default "ul"
    return _wrap_ul(lines)


# ---------------------------------------------------------------------------
# extract_placeholders
# ---------------------------------------------------------------------------

def extract_placeholders(html_src: str) -> Set[str]:
    """Estrae l'insieme dei placeholder Jinja2 ``{{ TAG }}`` da una stringa HTML."""
    return {m.group(1) for m in PLACEHOLDER_RGX.finditer(html_src)}


# ---------------------------------------------------------------------------
# images_to_html
# ---------------------------------------------------------------------------

_IMG_TMPL = "<img src=\"{{ IMG{index} }}\" alt=\"\" style=\"max-width:100%;\">"


def images_to_html(rows: int, cols: int) -> str:
    """Genera una griglia HTML placeholder per *rows × cols* immagini.

    Restituisce una tabella <table> semplice usata come fallback per gallerie
    descrizione/ricetta quando non c'è markup personalizzato.
    I segnaposto saranno ``{{ IMG1 }}``, ``{{ IMG2 }}``, … numerati in row-major.
    """
    rows = max(1, int(rows))
    cols = max(1, int(cols))
    out: List[str] = ["<table>"]
    counter = 1
    for _ in range(rows):
        out.append("  <tr>")
        for _ in range(cols):
            out.append("    <td>" + _IMG_TMPL.format(index=counter) + "</td>")
            counter += 1
        out.append("  </tr>")
    out.append("</table>")
    return "\n".join(out)
