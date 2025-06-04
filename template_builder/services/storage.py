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
    "SCHEMA_VERSION",
]

# ---------------------------------------------------------------------------
# Costanti percorso cartelle
# ---------------------------------------------------------------------------

_BASE_DIR = Path.home() / ".template_builder"
SCHEMA_VERSION = 2                    # ← ora è definita correttamente come nome pubblico
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


def _migrate_v1_to_v2(old: Dict[str, Any]) -> Dict[str, Any]:
    """Porta un JSON v1 al nuovo schema v2 (aggiunge STEPS e ALT)."""
    from template_builder.step_image import bind_steps  # richiede che step_image.py sia già corretto

    # Raccogli testo da STEP1…STEP9 (se esistono), altrimenti stringa vuota
    texts: List[str] = [old.get(f"STEP{i}", "") for i in range(1, 10)]
    images: List[str] = old.get("IMAGES_STEP", [])

    # bind_steps con due argomenti (alts=None di default)
    steps_objs = bind_steps(texts, images)
    # Aggiungo chiave "STEPS" con lista di dict serializzabili
    old["STEPS"] = [s.to_dict() for s in steps_objs]
    # Aggiungo placeholder STEPn_IMG_ALT basandomi su ogni StepImage.alt
    for s in steps_objs:
        old[f"STEP{s.order}_IMG_ALT"] = s.alt
    # Se era un file v1, manteniamo anche la chiave "__migrated_from_v1"
    old["__migrated_from_v1"] = True
    return old


def load_recipe(path: os.PathLike | str) -> Dict[str, Any]:
    """
    Carica un file JSON di “ricetta” e restituisce il contesto Python.
    - Se il JSON contiene la chiave "schema" uguale a SCHEMA_VERSION, 
      restituisce data["data"] (schema v2).
    - Se il JSON contiene {"created": ..., "schema": <qualcosa>}, ma lo schema
      non corrisponde a SCHEMA_VERSION, solleva ValueError.
    - Se il JSON contiene {"created": ..., "data": {...}} senza "schema",
      considera v1 legacy: chiama _migrate_v1_to_v2(data) e restituisce il contesto migrato.
    - Se è un dict senza chiave “schema” né "data" (batch-1 puro), chiama
      _migrate_v1_to_v2(data_puro) e restituisce il contesto migrato.
    - Altrimenti solleva ValueError.
    """
    path = Path(path)
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)

    if not isinstance(data, dict):
        raise ValueError("Recipe JSON must be an object at top-level")

    # Caso v2: presenza di "schema" uguale a SCHEMA_VERSION
    if data.get("schema") == SCHEMA_VERSION:
        # restituisco direttamente il dict "data"
        return data["data"]

    # Caso un file con "created" e "data" (file v1 di quick_save precedente)
    if "data" in data:
        return _migrate_v1_to_v2(data["data"])

    # Caso batch-1 puro: semplicemente dict di placeholder (es. STEP1, IMAGES_STEP, ecc.)
    return _migrate_v1_to_v2(data)


def quick_save(state: Dict[str, Any]) -> Path:
    """
    Salva lo stato corrente in un file JSON all’interno di ~/.template_builder/history/.
    Il payload è:
      {
        "created": <timestamp>,
        "schema":  SCHEMA_VERSION,
        "data":    <state>
      }
    Restituisce il Path completo del file creato.
    """
    _HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    target = _HISTORY_DIR / f"recipe_{_timestamp()}.json"
    payload = {
        "created": _timestamp(),
        "schema":  SCHEMA_VERSION,
        "data":    state,
    }
    with target.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)
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
    # Registrazione del filtro custom steps_bind, se presente
    try:
        from template_builder import filters as _filters  # noqa: F401
        env.filters["steps_bind"] = getattr(_filters, "steps_bind", lambda ctx, x: x)
    except Exception:
        pass
    tpl = env.get_template(template_path.name)  # type: ignore[arg-type]
    html_str = tpl.render(**ctx)

    save_to: Path | None = env_kw.get("save_to")  # type: ignore[arg-type]
    if save_to:
        save_to = Path(save_to)
        save_to.write_text(html_str, encoding="utf-8")
    return html_str
