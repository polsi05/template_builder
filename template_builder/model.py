# template_builder/model.py
"""
Definitive data-model layer (Batch 2).

Principi:
P1 – to_dict() restituisce solo dati, niente HTML.
P2 – fallback_html() usato solo se Jinja non è disponibile.
P3 – placeholders sempre {{ TAG }}.
P4 – il filtro steps_bind resta esterno.
P5 – strutture pensate per cicli Jinja (liste, tuple, dict).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from html import escape
from typing import List, Dict


# ────────────────────────────────────────────────
# HERO SECTION
# ────────────────────────────────────────────────
@dataclass
class Hero:
    title: str = ""
    img: str = ""
    intro: str = ""
    alt: str = ""  # alt obbligatorio se img è presente

    # ---------- Serialization ---------- #
    def to_dict(self) -> Dict[str, str]:
        return {
            "TITLE": self.title,
            "HERO_IMAGE_SRC": self.img,
            "HERO_IMAGE_ALT": self.alt,
            "INTRO": self.intro,
        }

    # ---------- Fallback HTML (solo preview senza Jinja) ---------- #
    def fallback_html(self) -> str:
        t = self.title or "{{ TITLE }}"
        i = self.intro or "{{ INTRO }}"
        src = self.img or "{{ HERO_IMAGE_SRC }}"
        alt = self.alt or "{{ HERO_IMAGE_ALT }}"
        return (
            f"<h1>{escape(t)}</h1>\n"
            f"<p>{escape(i)}</p>\n"
            f'<img src="{escape(src)}" alt="{escape(alt)}">'
        )


# ────────────────────────────────────────────────
# STEP IMAGE
# ────────────────────────────────────────────────
@dataclass
class StepImage:
    img: str = ""
    alt: str = ""
    text: str = ""
    order: int = 0  # 1-based in recipe steps / gallery rows

    def __post_init__(self) -> None:
        if self.img and not self.alt:
            raise ValueError("Alt text is required if image is provided")


# ────────────────────────────────────────────────
# GALLERY ROW  (max 3 images)
# ────────────────────────────────────────────────
@dataclass
class GalleryRow:
    images: List[StepImage] = field(default_factory=list)

    def __post_init__(self) -> None:
        if len(self.images) > 3:
            raise ValueError("GalleryRow can have at most 3 images")
        orders = [img.order for img in self.images]
        if len(orders) != len(set(orders)):
            raise ValueError("StepImage order must be unique within a GalleryRow")

    # ---------- Serialization for Jinja ---------- #
    def to_jinja_ctx(self) -> Dict[str, List[List[str]]]:
        sorted_imgs = sorted(self.images, key=lambda si: si.order)
        return {"IMAGES_DESC": [[si.img, si.alt] for si in sorted_imgs]}

    # (facoltativo) fallback_html se vuoi anteprima statica rapida
    def fallback_html(self) -> str:
        parts = []
        for si in sorted(self.images, key=lambda si: si.order):
            src = si.img or "{{ IMG_SRC }}"
            alt = si.alt or "{{ IMG_ALT }}"
            parts.append(f'<img src="{escape(src)}" alt="{escape(alt)}">')
        return "\n".join(parts)
