"""PreviewEngine stub – sufficiente per import."""

class PreviewEngine:  # pragma: no cover
    """
    Questa classe è un semplice stub per il motore di visualizzazione HTML.
    In futuro potrà basarsi su tkinterweb; per ora rende disponibile solo:
      - __init__(html: str)
      - render_source() → restituisce la stringa HTML in memoria
    """
    def __init__(self, html: str = "") -> None:
        self.html = html

    def render_source(self) -> str:
        """
        Restituisce il contenuto HTML corrente.
        """
        return self.html
