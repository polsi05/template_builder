# template_builder/step_image.py
"""
Helper puri per la gestione di StepImage:
  • sort_steps
  • swap_steps
  • renumber_steps
Mantengono P1-P5 e sono 100 % test-friendly.
"""
from __future__ import annotations

from typing import List
from .model import StepImage  # usa il dataclass già definito
import re
from html import unescape
# ────────────────────────────────────────────────────────────────
def _ensure_list(steps):
    if not isinstance(steps, list):
        raise TypeError("steps must be a list")
    for s in steps:
        if not isinstance(s, StepImage):
            raise ValueError("steps list must contain StepImage items")

# ----------------------------------------------------------------
def sort_steps(steps: List[StepImage]) -> List[StepImage]:
    """Ordina in-place per `order` ASC e ritorna la lista."""
    _ensure_list(steps)
    steps.sort(key=lambda s: s.order)
    return steps

# ----------------------------------------------------------------
def swap_steps(steps: List[StepImage], i: int, j: int) -> List[StepImage]:
    """Scambia elementi *i* e *j* (0-based)."""
    _ensure_list(steps)
    n = len(steps)
    if i == j:
        return steps
    if not (0 <= i < n and 0 <= j < n):
        raise ValueError("swap indices out of range")
    steps[i], steps[j] = steps[j], steps[i]
    return steps

# ----------------------------------------------------------------
def renumber_steps(steps: List[StepImage]) -> List[StepImage]:
    """Riassegna order consecutivi (1…N) mantenendo l’ordine attuale."""
    _ensure_list(steps)
    for idx, step in enumerate(steps, start=1):
        step.order = idx
    return steps

def _strip_html(text: str) -> str:
    return re.sub("<[^<]+?>", "", unescape(text or "")).strip()

def bind_steps(texts: list[str], images: list[str]) -> list[StepImage]:
    """Combina liste testo / immagini in StepImage con alt derivato."""
    max_len = max(len(texts), len(images))
    steps: list[StepImage] = []
    for i in range(max_len):
        t = texts[i]  if i < len(texts)  else ""
        img = images[i] if i < len(images) else ""
        alt = _strip_html(t) or (f"Step {i+1}" if img else "")
        # se sia testo che img mancano ⇒ salta
        if not t.strip() and not img:
            continue
        steps.append(StepImage(img=img, alt=alt, text=t, order=i+1))
    return steps