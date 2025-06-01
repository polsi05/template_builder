from dataclasses import dataclass
from typing import List

@dataclass
class Hero:
    """
    Esempio di dataclass per un'immagine “eroica”:
      - url: stringa, default ""
      - alt: stringa di testo alternativo, default ""
    """
    url: str = ""
    alt: str = ""

@dataclass
class StepImage:
    """
    Dataclass per un’immagine di un “passo” (step) in una procedura:
      - url: stringa, default ""
      - alt: stringa, default ""
      - order: intero (ordine), default 0
    """
    url: str = ""
    alt: str = ""
    order: int = 0

@dataclass
class GalleryRow:
    """
    Rappresenta un’intera riga di galleria di immagini:
      - urls: lista di stringhe (URL), default None (vuoto)
    """
    urls: List[str] = None  # type: ignore
