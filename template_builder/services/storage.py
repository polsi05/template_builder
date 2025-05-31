"""template_builder.services.storage

Funzioni di persistenza *pure*.
Se **Jinja2** non è installato, il modulo resta importabile: la funzione
``export_html`` utilizzerà un semplice fallback per sostituire i placeholder
in stile {{ key }}; in futuro si potrà usare Jinja2 per funzionalità avanzate.
"""

import json
import os
import tempfile
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

__all__ = [
    "UndoRedoStack",
    "quick_save",
    "load_recipe",
    "export_html",
]

class UndoRedoStack:
    """
    Implementa uno stack per undo/redo di stati serializzabili (ad es. dict).
    """
    def __init__(self) -> None:
        self._history: List[Any] = []
        self._index: int = -1

    def push(self, state: Any) -> None:
        # Se push dopo undo, tronca la parte "futura"
        if self._index < len(self._history) - 1:
            self._history = self._history[: self._index + 1]
        # Aggiungi copia dello stato
        self._history.append(state)
        self._index = len(self._history) - 1

    def undo(self) -> Any:
        """
        Torna allo stato precedente, se possibile, altrimenti solleva IndexError.
        """
        if self._index <= 0:
            raise IndexError("Nessuno stato precedente.")
        self._index -= 1
        return self._history[self._index]

    def redo(self) -> Any:
        """
        Torna allo stato successivo, se possibile, altrimenti solleva IndexError.
        """
        if self._index >= len(self._history) - 1:
            raise IndexError("Nessuno stato successivo.")
        self._index += 1
        return self._history[self._index]

def quick_save(state: Dict[str, Any]) -> Path:
    """
    Salva lo stato (serializzato in JSON) in un file temporaneo e restituisce il Path.
    Il file creato ha estensione .json.
    """
    # Crea un file temporaneo con estensione .json
    fd, path_str = tempfile.mkstemp(suffix=".json")
    os.close(fd)
    path = Path(path_str)
    # Scrivi JSON
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f)
    return path

def load_recipe(path: Path) -> Dict[str, Any]:
    """
    Carica un file JSON da `path`; se il contenuto non è valido, ritorna {}.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except Exception:
        pass
    return {}

def _simple_render(template_str: str, ctx: Dict[str, Any]) -> str:
    """
    Sostituisce {{ key }} con str(ctx[key]) per ogni chiave in ctx.
    Utilizza regex per gestire spazi interni.
    """
    result = template_str
    for key, value in ctx.items():
        pattern = re.compile(r"\{\{\s*" + re.escape(str(key)) + r"\s*\}\}")
        result = pattern.sub(str(value), result)
    return result

def export_html(
    ctx: Dict[str, Any],
    template_path: Path | str,
    **env_kw: Any,
) -> str:
    """
    Renderizza HTML via Jinja2 se disponibile, altrimenti usa _simple_render.
    - ctx: dizionario di contesto.
    - template_path: percorso del file template.
    - env_kw: argomenti aggiuntivi (es. save_to), ignorati nel fallback.
    """
    # Lettura file template
    template_path = Path(template_path)
    try:
        tpl_str = template_path.read_text(encoding="utf-8")
    except Exception as e:
        raise RuntimeError(f"Impossibile leggere il template: {e}")

    try:
        # Proviamo ad usare Jinja2
        from jinja2 import Environment, FileSystemLoader, select_autoescape
        env = Environment(
            loader=FileSystemLoader(str(template_path.parent)),
            autoescape=select_autoescape(["html", "htm"]),
        )
        tpl = env.get_template(template_path.name)  # type: ignore[arg-type]
        html_str = tpl.render(**ctx)
    except ImportError:
        # Fallback semplice senza Jinja2
        html_str = _simple_render(tpl_str, ctx)

    save_to: Optional[Path] = env_kw.get("save_to")  # type: ignore[arg-type]
    if save_to:
        save_to_path = Path(save_to)
        save_to_path.write_text(html_str, encoding="utf-8")
    return html_str
