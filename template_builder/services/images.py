# template_builder/services/images.py

"""
template_builder.services.images

Funzioni **pure** derivate dal modulo *legacy* dedicate alla gestione
collegata alle immagini (placeholder, gallerie HTML, codifica Base64).

Tutte le routine sono state riscritte in forma test-friendly e senza
side-effects: nessun accesso al filesystem viene effettuato al momento
della definizione delle funzioni.
"""

from __future__ import annotations

import base64
import html
import io
import math
import mimetypes
import os
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Union

from ..assets import DEFAULT_COLS
from .text import smart_paste
from ..infrastructure.validators import validate_image_url as _legacy_validate

# Pillow è opzionale: se non è disponibile, le funzioni che ne fanno uso alzeranno RuntimeError.
try:
    from PIL import Image
except (ImportError, ModuleNotFoundError):
    Image = None  # type: ignore

__all__ = [
    "guess_grid",
    "generate_placeholders",
    "encode_file_to_data_uri",
    "paths_to_html_grid",
    "images_to_html",
    "smart_paste_images",
    "validate_url",
    "fetch_metadata",
]

# ---------------------------------------------------------------------------
# Calcolo automatizzato di righe×colonne
# ---------------------------------------------------------------------------
def guess_grid(n_images: int, *, cols: int = DEFAULT_COLS) -> Tuple[int, int]:
    """Calcola automaticamente (righe, colonne) per *n_images*.

    * `cols` definisce la larghezza massima; se *n_images* è minore, viene
      ridotto di conseguenza.
    * Restituisce sempre valori ≥1.
    """
    n_images = max(1, int(n_images))
    cols = max(1, int(cols))
    rows = math.ceil(n_images / cols)
    if n_images < cols:
        cols = n_images
    return rows, cols


# ---------------------------------------------------------------------------
# Generazione placeholder
# ---------------------------------------------------------------------------
def _placeholder(index: int) -> str:
    """Restituisce il placeholder Jinja2 `{{ IMG<index> }}`."""
    return f"{{{{ IMG{index} }}}}"


def generate_placeholders(n_images: int) -> List[str]:
    """Ritorna lista di placeholder: ['{{ IMG1 }}', '{{ IMG2 }}', …]."""
    n_images = max(1, int(n_images))
    return [_placeholder(i) for i in range(1, n_images + 1)]


# ---------------------------------------------------------------------------
# Conversione file→data URI
# ---------------------------------------------------------------------------
def encode_file_to_data_uri(path: Union[os.PathLike, str], *, mime: Optional[str] = None) -> str:
    """Converte un file immagine *path* in una Data URI (`data:image/...;base64,…`)."""
    # se l’utente non fornisce mime, determino via mimetypes
    mime_type, _ = mimetypes.guess_type(path)
    mime_type = mime or mime_type or "application/octet-stream"
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("ascii")
    return f"data:{mime_type};base64,{b64}"


# ---------------------------------------------------------------------------
# Costruzione griglia HTML
# ---------------------------------------------------------------------------
def paths_to_html_grid(
    paths: Optional[Sequence[Union[str, os.PathLike]]],
    cols: int = DEFAULT_COLS,
    inline: bool = False,
    alt_texts: Optional[Sequence[str]] = None,
) -> str:
    """
    Crea una tabella HTML con le immagini elencate in `paths`.
    Se `paths` è None o vuota, genera una griglia di placeholder.
    - `cols`: numero di colonne della tabella (default da DEFAULT_COLS)
    - `inline=True`: usa Data URI anziché link esterni
    - `alt_texts`: lista parallela di descrizioni ALT (altrimenti stringhe vuote)
    """
    # se non ci sono percorsi, generiamo griglia di placeholder
    if not paths:
        rows, cols = guess_grid(1, cols=cols)
        return images_to_html(rows, cols)

    total = len(paths)
    rows, _ = guess_grid(total, cols=cols)
    out: List[str] = ["<table>"]
    idx = 0
    for _ in range(rows):
        out.append("  <tr>")
        for c in range(cols):
            if idx >= total:
                out.append("    <td></td>")
            else:
                p = paths[idx]
                alt = (alt_texts[idx] if alt_texts and idx < len(alt_texts) else "")
                if inline:
                    src = encode_file_to_data_uri(p)
                else:
                    src = str(p)
                out.append(f'    <td><img src="{html.escape(src)}" alt="{html.escape(alt)}" style="max-width:100%;"></td>')
                idx += 1
        out.append("  </tr>")
    out.append("</table>")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# images_to_html: compatibilità monolitico
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
# smart_paste_images (alias di smart_paste testo)
# ---------------------------------------------------------------------------
def smart_paste_images(raw: Union[str, Sequence[str]]) -> List[str]:
    """Alias di smart_paste per liste di percorsi. Stessa logica di smart_paste."""
    return smart_paste(raw)


# ---------------------------------------------------------------------------
# validate_url
# ---------------------------------------------------------------------------
def validate_url(url: str) -> None:
    """Verifica validità di una URL; solleva TypeError o ValueError se non ok."""
    _legacy_validate(url)


# ---------------------------------------------------------------------------
# fetch_metadata
# ---------------------------------------------------------------------------
def fetch_metadata(path: Union[os.PathLike, str]) -> Dict[str, Union[int, str]]:
    """Restituisce un dizionario con {width, height, format} di un'immagine.

    Richiede PIL; altrimenti solleva RuntimeError.
    """
    if Image is None:
        raise RuntimeError("Pillow non è installato: impossibile estrarre metadata immagine.")
    with Image.open(path) as img:  # type: ignore[arg-type]
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format or "",
        }
