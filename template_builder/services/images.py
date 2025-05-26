"""Wrapper validazione immagini – STUB."""
from ..infrastructure.validators import validate_image_url as _legacy_validate

def validate_url(url: str):
    return _legacy_validate(url)

def fetch_metadata(url: str) -> dict:  # pragma: no cover
    """Stub placeholder – restituisce info minima."""
    return {"url": url, "width": None, "height": None}
