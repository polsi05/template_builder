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
from typing import Dict, Iterable, List, Sequence, Tuple

from ..assets import DEFAULT_COLS
from .text import smart_paste

try:
    # Pillow è opzionale: se non è disponibile, le funzioni che ne fanno uso
    # alzeranno RuntimeError con messaggio esplicativo.
    from PIL import Image  # type: ignore
except ModuleNotFoundError:  # pragma: no cover – non in test env
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
    # minimizziamo righe mantenendo il numero di colonne richiesto (almeno 1)
    rows = math.ceil(n_images / cols)
    # se le immagini stanno tutte in meno colonne, riduciamo cols
    if n_images < cols:
        cols = n_images
    return rows, cols


def _placeholder(index: int) -> str:
    """Restituisce il placeholder Jinja2 `{{ IMG<index> }}`."""
    return f"{{{{ IMG{index} }}}}"


def generate_placeholders(n_images: int) -> List[str]:
    """Genera la sequenza di placeholder `{{ IMG1 }}`, `{{ IMG2 }}`, …

    Anche se `n_images=0`, restituisce almeno `["{{ IMG1 }}"]`.
    """
    # max(1, int(n_images)) garantisce che ci sia almeno un placeholder
    return [_placeholder(i) for i in range(1, max(1, int(n_images)) + 1)]


# ---------------------------------------------------------------------------
# Base64 helpers
# ---------------------------------------------------------------------------

def _ensure_pillow() -> None:  # pragma: no cover
    """Verifica che Pillow sia installato; altrimenti solleva RuntimeError."""
    if Image is None:
        raise RuntimeError(
            "Le funzioni di manipolazione immagini richiedono Pillow (pip install pillow)."
        )


def _img_to_bytes(img: "Image.Image", *, format: str | None = None) -> bytes:  # type: ignore
    """Converte un'istanza PIL.Image in bytes, con formato specificato o di default."""
    buf = io.BytesIO()
    img.save(buf, format=format or img.format or "PNG")
    return buf.getvalue()


def encode_file_to_data_uri(path: os.PathLike | str, *, mime: str | None = None) -> str:
    """Converte un file immagine *path* in una Data URI (`data:image/...;base64,...`).

    **Attenzione**: evitare l’uso con immagini di grandi dimensioni, specialmente
    in ambito e-mail.
    """
    path = os.fspath(path)
    if not mime:  # se non esplicitamente passato, proviamo a indovinarlo
        mime, _ = mimetypes.guess_type(path)
    mime = mime or "application/octet-stream"
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"


# ---------------------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------------------

def _make_img_tag(src: str, *, alt: str = "", style: str = "max-width:100%;") -> str:
    """Restituisce un tag `<img>` con attributi `src`, `alt` e `style`."""
    alt_escaped = html.escape(alt)
    return f"<img src=\"{src}\" alt=\"{alt_escaped}\" style=\"{style}\">"


def paths_to_html_grid(
    paths: Sequence[str | os.PathLike] | None,
    *,
    cols: int = DEFAULT_COLS,
    inline: bool = False,
    alt_texts: Sequence[str] | None = None,
) -> str:
    """Genera una *grid* HTML (`<table>`) riempiendola con le immagini *paths*.

    - Se `inline=True`, le immagini vengono incorporate come Data-URI.
    - In caso di `paths=None` (o lista vuota) viene generata la griglia di
      *placeholder* tramite `generate_placeholders`.
    - `alt_texts`, se fornito, è una lista parallela di stringhe usate come `alt`.
      I valori mancanti vengono integrati con stringhe vuote.
    """
    # *** caso fallback: niente paths reali, usiamo un solo placeholder
    if not paths:
        n_images = 1
        rows, cols_fallback = 1, 1
        placeholder_tags = [_make_img_tag(_placeholder(1))]
    else:
        n_images = len(paths)
        rows, cols_fallback = guess_grid(n_images, cols=cols)
        placeholder_tags: List[str] = []
        alts = list(alt_texts or [])
        # allunghiamo la lista degli alt se troppo corta
        alts.extend(["" for _ in range(n_images - len(alts))])

        for idx, (p, alt) in enumerate(zip(paths, alts), start=1):
            # costruiamo src: Data URI o percorso HTML-escaped
            if inline:
                src = encode_file_to_data_uri(p)
            else:
                src = html.escape(os.fspath(p))
            placeholder_tags.append(_make_img_tag(src, alt=alt))

    # Ora disponiamo i tag <img> (o placeholder) in tabella righe×colonne (row-major)
    out: List[str] = ["<table>"]
    num = 0
    for _ in range(rows):
        out.append("  <tr>")
        for _ in range(cols_fallback):
            if num < len(placeholder_tags):
                out.append(f"    <td>{placeholder_tags[num]}</td>")
            else:
                # se c’è spazio residuo, inseriamo placeholder Jinja2 standard
                # (utile nel caso di tabella non perfettamente allineata)
                out.append(f"    <td>{_make_img_tag(_placeholder(num + 1))}</td>")
            num += 1
        out.append("  </tr>")
    out.append("</table>")

    return "\n".join(out)


def images_to_html(rows: int, cols: int) -> str:
    """(Compatibilità) Genera una tabella HTML con placeholder `{{ IMGn }}`.

    Viene usata da test e in fallback, ma solitamente si preferisce
    `paths_to_html_grid` per le griglie reali.
    """
    r = max(1, int(rows))
    c = max(1, int(cols))
    out: List[str] = ["<table>"]
    num = 1
    for _ in range(r):
        out.append("  <tr>")
        for _ in range(c):
            out.append(f"    <td>{{{{ IMG{num} }}}}</td>")
            num += 1
        out.append("  </tr>")
    out.append("</table>")
    return "\n".join(out)


def smart_paste_images(raw: str | Sequence[str]) -> List[str]:
    """Estende `smart_paste()` per “incollare” liste di URL o stringhe multiple.

    Accetta:
      * stringa di testo (multilinea o con “;” che separa più URL)
      * lista/tupla di stringhe
    Ritorna:
      Lista di URL immagine (senza spazi iniziali/finali).
    """
    return smart_paste(raw)


# ---------------------------------------------------------------------------
# Legacy validator wrapper + metadata fetch
# ---------------------------------------------------------------------------

from ..infrastructure.validators import validate_image_url as _legacy_validate


def validate_url(url: str) -> None:
    """Valida l'URL o path immagine tramite il validator legacy.

    Se il validator solleva ValueError, lo propaga.
    """
    _legacy_validate(url)


def fetch_metadata(path: os.PathLike | str) -> Dict[str, int | str]:
    """Restituisce un dizionario con {width, height, format} di un'immagine.

    Richiede Pillow; altrimenti solleva RuntimeError.
    """
    _ensure_pillow()
    with Image.open(path) as img:  # type: ignore[arg-type]
        return {
            "width": img.width,
            "height": img.height,
            "format": img.format or "",
        }
