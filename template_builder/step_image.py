from __future__ import annotations

from html import unescape
from typing import List, Sequence

from .model import StepImage

# ---------------------------------------------------------------------------
# UTILITÀ “LOW-LEVEL” PER LA GESTIONE DELL’ORDINE DEGLI STEP
# ---------------------------------------------------------------------------

def sort_steps(steps: List[StepImage]) -> List[StepImage]:
    """Ordina in-place per attributo `order` crescente e restituisce la lista."""
    if not isinstance(steps, list):
        raise TypeError("steps deve essere una lista di StepImage")
    for s in steps:
        if not isinstance(s, StepImage):
            raise ValueError("steps deve contenere solo oggetti StepImage")
    steps.sort(key=lambda s: s.order)
    return steps

def swap_steps(steps: List[StepImage], i: int, j: int) -> List[StepImage]:
    """Scambia due step (indici 0-based) e restituisce la lista."""
    if not isinstance(steps, list):
        raise TypeError("steps deve essere una lista di StepImage")
    n = len(steps)
    if not (0 <= i < n and 0 <= j < n):
        raise ValueError("indici fuori range")
    steps[i], steps[j] = steps[j], steps[i]
    return steps

def renumber_steps(steps: List[StepImage]) -> List[StepImage]:
    """Riassegna `order` consecutivi (1..N) mantenendo l'ordine attuale."""
    if not isinstance(steps, list):
        raise TypeError("steps deve essere una lista di StepImage")
    for idx, step in enumerate(steps, start=1):
        step.order = idx
    return steps

# ---------------------------------------------------------------------------
# NUOVA LOGICA: gestione ALT obbligatori
# ---------------------------------------------------------------------------

def _strip_html(text: str) -> str:
    """Rimuove markup HTML elementare e spazi/escape."""
    return (
        unescape(text)
        .strip()
        .removeprefix("<p>")
        .removesuffix("</p>")
        .strip()
    )

def bind_steps(
    texts: Sequence[str],
    images: Sequence[str],
    alts: Sequence[str] | None = None,
) -> List[StepImage]:
    """
    Combina *testi*, *immagini* e – opzionalmente – *alt* in una lista di `StepImage`.

    ```
    Compatibilità all'indietro:
    --------------------------------
    - Se *alts* **non** è fornito, il comportamento resta quello originario:
      l'alt viene derivato dal testo (con fallback ``"Step {n}"``).

    Nuova logica con *alts* espliciti:
    ----------------------------------
    - Se *alts* è passato, si applicano queste regole **per ciascuna posizione** *i*:
        • se esiste *images[i]* (URL non vuoto) allora **è obbligatorio**
          che l'alt corrispondente sia ``alts[i].strip() != ""`` – in caso
          contrario viene sollevato ``ValueError`` con messaggio:
              "Errore: l'immagine in posizione {i+1} non ha l'attributo ALT. …"
        • il testo può essere vuoto; se lo è, l'alt esplicito è comunque usato.
    - Slot dove *testo*, *immagine* **e** *alt* (se presente) sono tutti vuoti
      vengono ignorati (non generano StepImage).

    Restituisce una lista ordinata con ``order`` progressivo (1-based).
    """
    max_len = max(len(texts), len(images), len(alts or []))
    steps: list[StepImage] = []

    for i in range(max_len):
        text = texts[i] if i < len(texts) else ""
        img = images[i] if i < len(images) else ""
        # alt esplicito se fornito
        if alts is not None and i < len(alts):
            alt = alts[i].strip()
        else:
            # derivato dal testo
            alt = _strip_html(text) or (f"Step {i+1}" if img else "")

        # Salta slot completamente vuoto
        if not text.strip() and not img:
            continue

        # Validazioni ALT obbligatorio se c'è immagine
        if img and not alt:
            raise ValueError(
                f"Errore: l'immagine in posizione {i+1} non ha l'attributo ALT. "
                "Inserisci un testo alternativo all'immagine."
            )

        steps.append(
            StepImage(
                img=img,
                alt=alt,
                text=text,
                order=len(steps) + 1,
            )
        )

    return steps

def steps_to_html(steps: List[StepImage]) -> str:
    """
    Genera HTML in una struttura `<ol><li>`.

    ```
    Viene usato principalmente nei test per ispezionare rapidamente il risultato
    senza passare dal motore Jinja.
    """
    lines: list[str] = ["<ol>"]
    for step in sort_steps(steps):  # garantiamo l'ordine
        lines.append("  <li>")
        if step.img:
            escaped_alt = step.alt.replace('"', "&quot;")
            lines.append(f'    <img src="{step.img}" alt="{escaped_alt}">')
        for line in step.text.splitlines():
            lines.append(f"    {line}")
        lines.append("  </li>")
    lines.append("</ol>")
    return "\n".join(lines)

# Esportiamo solo le API ufficiali

__all__ = [
    "sort_steps",
    "swap_steps",
    "renumber_steps",
    "bind_steps",
    "steps_to_html",
]
