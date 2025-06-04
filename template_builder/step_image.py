from __future__ import annotations
from typing import List, Sequence
from .model import StepImage
import re

def sort_steps(steps: List[StepImage]) -> List[StepImage]:
    """Ordina in-place per attributo 'order' crescente e restituisce la lista"""
    if not isinstance(steps, list):
        raise TypeError("steps deve essere una lista di StepImage")
    for s in steps:
        if not isinstance(s, StepImage):
            raise ValueError("steps deve contenere solo oggetti StepImage")
    steps.sort(key=lambda s: s.order)
    return steps

def swap_steps(steps: List[StepImage], i: int, j: int) -> List[StepImage]:
    """Scambia due step (0-based) e restituisce la lista."""
    if not isinstance(steps, list):
        raise TypeError("steps deve essere una lista di StepImage")
    n = len(steps)
    if not (0 <= i < n and 0 <= j < n):
        raise ValueError("indici fuori range")
    steps[i], steps[j] = steps[j], steps[i]
    return steps

def renumber_steps(steps: List[StepImage]) -> List[StepImage]:
    """Riassegna order consecutivi (1..N) mantenendo l'ordine attuale."""
    if not isinstance(steps, list):
        raise TypeError("steps deve essere una lista di StepImage")
    for idx, step in enumerate(steps, start=1):
        step.order = idx
    return steps

def bind_steps(
    texts: Sequence[str],
    images: Sequence[str],
    alts: Sequence[str] | None = None,
) -> List[StepImage]:
    """
    Combina liste di testi, immagini e (eventualmente) alts in una lista di StepImage.
    Regole:
    - Viene creato un StepImage solo se esistono contemporaneamente:
      • testo (texts[i].strip() != "")
      • URL immagine (images[i] != "")
      • alt non vuoto (alts[i].strip() != "")
    - Se manca alt mentre esistono testo e URL immagine, solleva ValueError subito,
      con messaggio:
      "Errore: l'immagine in posizione {i+1} non ha l'attributo ALT. Inserisci un testo alternativo all'immagine."
    - Passi in cui testo.strip()=="" e images[i]=="" vengono ignorati senza errore.
    """
    steps: List[StepImage] = []
    max_len = max(len(texts), len(images))
    for i in range(max_len):
        t = texts[i] if i < len(texts) else ""
        img = images[i] if i < len(images) else ""
        alt = ""
        if alts is not None and i < len(alts):
            alt = alts[i]
        # Se né testo né immagine → salto
        if not t.strip() and not img:
            continue
        # Se c'è URL immagine, allora serve anche testo e alt
        if img:
            if not t.strip():
                # C'è immagine ma non c'è testo: non è passo ricetta valido → salto
                continue
            if not alt or not alt.strip():
                # Manca alt → errore
                position = i + 1
                raise ValueError(
                    f"Errore: l'immagine in posizione {position} non ha l'attributo ALT. "
                    "Inserisci un testo alternativo all'immagine."
                )
            # Altrimenti posso costruire lo StepImage
            step = StepImage(img=img, alt=alt.strip(), text=t, order=len(steps) + 1)
            steps.append(step)
        # Se non c'è URL immagine ma c'è testo, non genero nulla (solo immagine passo viene mostrata se c'è testo)
    return steps

def steps_to_html(steps: List[StepImage]) -> str:
    """
    Genera HTML per una lista di StepImage in <ol><li>... structure.
    Se step.img è non vuoto, include <img src="..." alt="...">.
    """
    lines: list[str] = []
    lines.append("<ol>")
    for step in steps:
        lines.append("  <li>")
        if step.img:
            escaped_alt = step.alt.replace('"', "&quot;")
            lines.append(f'    <img src="{step.img}" alt="{escaped_alt}">')
        for line in step.text.splitlines():
            lines.append(f"    {line}")
        lines.append("  </li>")
    lines.append("</ol>")
    return "\n".join(lines)