"""PreviewEngine stub – sufficiente per import."""
class PreviewEngine:  # pragma: no cover
    def __init__(self, html: str = "") -> None:
        self.html = html

    def render_source(self) -> str:
        return self.html
