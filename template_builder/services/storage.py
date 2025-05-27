from __future__ import annotations
"""template_builder.services.storage

Funzioni di persistenza *pure*.
Se **Jinja2** non è installato, il modulo resta importabile: la funzione
``export_html`` solleverà RuntimeError sul primo utilizzo (comportamento
lazy‑import) ma gli altri helper continueranno a funzionare – questo rende
il pacchetto installabile senza dipendenze pesanti.
"""

import json
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

# ---------------------------------------------------------------------------
# Tentativo opzionale di import Jinja2
# ---------------------------------------------------------------------------

try:  # pragma: no cover – la CI non installa jinja2
    from jinja2 import Environment, FileSystemLoader, select_autoescape  # type: ignore
except ModuleNotFoundError:  # fallback leggero
    Environment = FileSystemLoader = select_autoescape = None  # type: ignore[misc,assignment]

__all__ = [
    "load_recipe",
    "quick_save",
    "export_html",
    "UndoRedoStack",
]

# ---------------------------------------------------------------------------
# Costanti percorso cartelle
# ---------------------------------------------------------------------------

_BASE_DIR = Path.home() / ".template_builder"
_HISTORY_DIR = _BASE_DIR / "history"
_HISTORY_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Undo / Redo stack
# ---------------------------------------------------------------------------

class UndoRedoStack:
    """Stack con indice corrente."""

    def __init__(self) -> None:
        self._stack: List[Dict[str, Any]] = []
        self._idx: int = -1

    def push(self, state: Dict[str, Any]) -> None:
        if self._idx < len(self._stack) - 1:
            self._stack = self._stack[: self._idx + 1]
        self._stack.append(json.loads(json.dumps(state)))
        self._idx += 1

    def undo(self) -> Optional[Dict[str, Any]]:
        if self._idx > 0:
            self._idx -= 1
            return json.loads(json.dumps(self._stack[self._idx]))
        return None

    def redo(self) -> Optional[Dict[str, Any]]:
        if self._idx < len(self._stack) - 1:
            self._idx += 1
            return json.loads(json.dumps(self._stack[self._idx]))
        return None

# ---------------------------------------------------------------------------
# File helpers
# ---------------------------------------------------------------------------

def _timestamp() -> str:
    return time.strftime("%Y%m%d-%H%M%S")


def load_recipe(path: os.PathLike | str) -> Dict[str, Any]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError("Recipe JSON must be an object at top-level")
    return data


def quick_save(state: Dict[str, Any]) -> Path:
    _HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    target = _HISTORY_DIR / f"recipe_{_timestamp()}.json"
    with target.open("w", encoding="utf-8") as fh:
        json.dump(state, fh, ensure_ascii=False, indent=2)
    return target

# ---------------------------------------------------------------------------
# HTML export (lazy import)
# ---------------------------------------------------------------------------

def _ensure_jinja2() -> None:
    if Environment is None:  # pragma: no cover
        raise RuntimeError(
            "export_html() richiede Jinja2 – installa con `pip install jinja2`."
        )


def export_html(ctx: Dict[str, Any], template_path: os.PathLike, **env_kw) -> str:
    """Renderizza html via Jinja2 se disponibile, altrimenti solleva errore."""
    _ensure_jinja2()
    template_path = Path(template_path)
    env = Environment(
        loader=FileSystemLoader(str(template_path.parent)),
        autoescape=select_autoescape(["html", "htm"]),
    )
    tpl = env.get_template(template_path.name)  # type: ignore[arg-type]
    html_str = tpl.render(**ctx)

    save_to: Path | None = env_kw.get("save_to")  # type: ignore[arg-type]
    if save_to:
        save_to = Path(save_to)
        save_to.write_text(html_str, encoding="utf-8")
    return html_str
