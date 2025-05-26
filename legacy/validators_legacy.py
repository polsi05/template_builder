import requests
from io import BytesIO
from PIL import Image, UnidentifiedImageError

# Timeout di default per il download (in secondi)
REQUEST_TIMEOUT = 5

class ImageValidationError(Exception):
    """Eccezione sollevata quando l'URL non punta a un'immagine valida."""
    pass

def validate_image_url(url: str) -> bool:
    """
    Controlla che l'URL punti a un'immagine valida.
    - Scarica interamente i dati con timeout.
    - Tenta di aprirli come immagine PIL.
    """
    try:
        resp = requests.get(url, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = BytesIO(resp.content)
        # Provo a caricare l'immagine
        Image.open(data).verify()
    except requests.RequestException as e:
        raise ImageValidationError(f"Errore nel download: {e}")
    except (UnidentifiedImageError, Exception) as e:
        raise ImageValidationError(f"Non è un formato immagine valido: {e}")

    return True
