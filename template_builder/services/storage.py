from __future__ import annotations
"""template_builder.services.storage

Funzioni di persistenza *pure*.
Se **Jinja2** non è installato, il modulo resta importabile: la funzione
``export_html`` solleverà RuntimeError sul primo utilizzo (comportamento
lazy-import) ma gli altri helper continueranno a funzionare – questo rende
il pacchetto installabile senza dipendenze pesanti.
"""

import json
import os
import time
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
        # se push su uno stato intermedio, elimino tutti i successivi
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
# export_html: render Jinja2 o fallback semplice
# ---------------------------------------------------------------------------
def _ensure_jinja2() -> None:
    try:
        import jinja2  # type: ignore
    except ImportError:
        raise RuntimeError("Jinja2 non installato: impossibile esportare in HTML.")


def export_html(ctx: Dict[str, Any], template_path: Union[str, Path], **env_kw: Any) -> str:
    """Renderizza html via Jinja2 se disponibile, altrimenti solleva errore."""
    from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore

    _ensure_jinja2()
    template_path = Path(template_path)
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "htm"]),
    )
    tpl = env.get_template(template_path.name)  # type: ignore[arg-type]
    html_str = tpl.render(**ctx)

    save_to: Optional[Path] = env_kw.get("save_to")  # type: ignore[arg-type]
    if save_to:
        save_to = Path(save_to)
        save_to.write_text(html_str, encoding="utf-8")
    return html_str
