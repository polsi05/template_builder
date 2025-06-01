from __future__ import annotations
"""template_builder.services.storage

Funzioni di persistenza *pure*.
Se Jinja2 non è installato, `export_html` utilizza un semplice fallback
che sostituisce i segnaposto {{ key }} con i valori del contesto.
"""

import json
import os
import time
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

__all__ = [
    "UndoRedoStack",
    "quick_save",
    "load_recipe",
    "export_html",
]

# ---------------------------------------------------------------------------
# CLASSE per undo/redo
# ---------------------------------------------------------------------------
class UndoRedoStack:
    """Stack per gestire storicizzazione (undo/redo) di stati immutabili."""

    def __init__(self) -> None:
        self._history: List[Any] = []
        self._index: int = -1

    def push(self, state: Any) -> None:
        """Aggiunge uno stato alla cronologia e taglia eventuali redo futuri."""
        if self._index < len(self._history) - 1:
            self._history = self._history[: self._index + 1]
        self._history.append(state)
        self._index = len(self._history) - 1

    def undo(self) -> Any:
        """Torna allo stato precedente; se non esiste, restituisce l’ultimo conosciuto."""
        if self._index <= 0:
            return self._history[0] if self._history else {}
        self._index -= 1
        return self._history[self._index]

    def redo(self) -> Any:
        """Torna allo stato successivo; se non esiste, restituisce l’ultimo conosciuto."""
        if self._index >= len(self._history) - 1:
            return self._history[self._index] if self._history else {}
        self._index += 1
        return self._history[self._index]


# ---------------------------------------------------------------------------
# quick_save: salva JSON temporaneo
# ---------------------------------------------------------------------------
def quick_save(state: Dict[str, Any]) -> Path:
    """Serializza lo stato in JSON e lo salva in un file temporaneo."""
    directory = Path(os.path.expanduser("~")) / ".template_builder" / "history"
    directory.mkdir(parents=True, exist_ok=True)
    ts = int(time.time())
    fname = directory / f"history_{ts}.json"
    with open(fname, "w", encoding="utf-8") as fh:
        fh.write(json.dumps(state))
    return fname


# ---------------------------------------------------------------------------
# load_recipe: carica un dict da file JSON
# ---------------------------------------------------------------------------
def load_recipe(path: Union[os.PathLike, str]) -> Dict[str, Any]:
    """Carica da file JSON; se non valido o non ritorna dict, restituisce {}."""
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        if isinstance(data, dict):
            return data
        return {}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Funzione di rendering semplice (fallback quando Jinja2 non è disponibile)
# ---------------------------------------------------------------------------
_PLACEHOLDER_PATTERN = re.compile(r"\{\{\s*(\w+)\s*\}\}")

def _simple_render(template_content: str, ctx: Dict[str, Any]) -> str:
    """
    Sostituisce ogni occorrenza di {{ key }} con str(ctx[key]) se esiste,
    altrimenti lascia il placeholder invariato.
    """
    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        if key in ctx:
            return str(ctx[key])
        return match.group(0)  # lascio invariato se mancante
    return _PLACEHOLDER_PATTERN.sub(_replace, template_content)


# ---------------------------------------------------------------------------
# export_html: render Jinja2 o fallback semplice
# ---------------------------------------------------------------------------
def export_html(ctx: Dict[str, Any], template_path: Union[str, Path], **env_kw: Any) -> str:
    """Renderizza HTML da un template:
    
    - Se Jinja2 è disponibile, lo usa per il rendering completo.
    - Altrimenti, viene usato un semplice fallback (_simple_render) che
      sostituisce solo i placeholders {{ key }} con i valori dal contesto.

    L'argomento opzionale 'save_to' in env_kw può essere passato come
    percorso per salvare l'HTML generato su file.
    """
    template_path = Path(template_path)
    # 1) Provo a usare Jinja2
    try:
        from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore
        env = Environment(
            loader=FileSystemLoader(str(template_path.parent)),
            autoescape=select_autoescape(["html", "htm"]),
        )
        tpl = env.get_template(template_path.name)  # type: ignore[arg-type]
        html_str = tpl.render(**ctx)
    except (ImportError, ModuleNotFoundError):
        # Fallback: leggero, sostituzione placeholder
        try:
            content = template_path.read_text(encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Impossibile leggere il template: {e}")
        html_str = _simple_render(content, ctx)

    # 2) Se è stato passato 'save_to', salvo anche su file
    save_to: Optional[Path] = env_kw.get("save_to")  # type: ignore[arg-type]
    if save_to:
        try:
            dest = Path(save_to)
            dest.write_text(html_str, encoding="utf-8")
        except Exception as e:
            raise RuntimeError(f"Errore scrittura su file '{save_to}': {e}")
    return html_str
