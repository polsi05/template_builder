from dataclasses import dataclass
from typing import List

@dataclass
class Hero:
    url: str = ""
    alt: str = ""

@dataclass
class StepImage:
    url: str = ""
    alt: str = ""
    order: int = 0

@dataclass
class GalleryRow:
    urls: List[str] = None  # type: ignore
