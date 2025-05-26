"""Legacy image-url validator – stub sempre valido."""
class ImageValidationError(Exception):
    ...

def validate_image_url(url: str) -> None:  # pragma: no cover
    """Accetta sempre, verrà sostituito da logica legacy."""
    if not url:
        raise ImageValidationError("URL vuoto")
