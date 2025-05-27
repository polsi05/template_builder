# template_builder/builder_core.py
"""
Refactored core controller for Template Builder 3 .x.

Highlights
----------
* Drop-in replacement of the old ``BuilderApp`` (monolith) renamed
  **TemplateBuilderApp**.
* No import from ``legacy/*`` – uses the new sliced package:
    ``template_builder.widgets`` and ``template_builder.services``.
* Safe to import in **head-less** environments: set ``enable_gui=False`` or
  run with no $DISPLAY (CI).
* Public API kept minimal but compatible:
    - ``quick_save()``
    - ``load_recipe(path)``
    - ``update_preview()``
    - ``undo()`` / ``redo()``
"""

from __future__ import annotations

import importlib
import os
import sys
import types
from pathlib import Path
from typing import Any, Dict, List, Tuple

# ────────────────────────────────────────────────────────────────
# Optional runtime-safe imports (become dummy modules on failure)
# ----------------------------------------------------------------
def _safe(name: str) -> types.ModuleType:
    try:
        return importlib.import_module(name)
    except Exception:
        return types.ModuleType(f"_stub_{name.replace('.', '_')}")

_tk          = _safe("tkinter")
_ttk         = _safe("tkinter.ttk")
_widgets_mod = _safe("template_builder.widgets")
_services    = _safe("template_builder.services.storage")
_preview_mod = _safe("template_builder.infrastructure.preview_engine")

PlaceholderEntry             = getattr(_widgets_mod, "PlaceholderEntry", object)
PlaceholderMultiTextField    = getattr(_widgets_mod, "PlaceholderMultiTextField", object)
UndoRedoStack                = getattr(_services, "UndoRedoStack", lambda: None)
quick_save_fn                = getattr(_services, "quick_save", lambda *_: None)
load_recipe_fn               = getattr(_services, "load_recipe", lambda *_: {})
PreviewEngine                = getattr(_preview_mod, "PreviewEngine", None)

tk  = _tk if hasattr(_tk, "Tk") else None
ttk = _ttk if hasattr(_ttk, "Frame") else None  # type: ignore[assignment]


# ────────────────────────────────────────────────────────────────
# Main class
# ----------------------------------------------------------------
class TemplateBuilderApp:
    """Modern, modular controller for Template Builder."""

    _SHORTCUTS: List[Tuple[str, str]] = [
        ("<Control-s>", "quick_save"),
        ("<Control-z>", "undo"),
        ("<Control-y>", "redo"),
        ("<Command-s>", "quick_save"),  # macOS ⌘
        ("<Command-z>", "undo"),
        ("<Command-y>", "redo"),
    ]

    # ------------------------------------------------------------------ init
    def __init__(self, *, enable_gui: bool | None = None) -> None:
        self.enable_gui = self._display_available() if enable_gui is None else enable_gui
        self.root = tk.Tk() if self.enable_gui and tk else None
        self._undo = UndoRedoStack()
        self._state: Dict[str, Any] = {}

        # GUI scaffolding
        if self.root:
            self._build_ui()
            self._bind_global_shortcuts()

    # ------------------------------------------------------------------ public API
    def quick_save(self, *_: Any) -> None:
        """Persist current state to history folder."""
        quick_save_fn(self._state)

    def load_recipe(self, path: os.PathLike | str) -> None:
        """
        Carica un file JSON di “ricetta”.

        Se il percorso non esiste o il contenuto è corrotto, lo stato
        viene azzerato senza propagare l’eccezione—così i test head-less
        (e la GUI) non si interrompono.
        """
        try:
            self._state = load_recipe_fn(path)
            self._undo.push(self._state)           # traccia lo snapshot
        except (FileNotFoundError, OSError, ValueError, TypeError):
            self._state = {}

    def undo(self, *_: Any) -> None:            # key-binding friendly
        new = self._undo.undo()
        if new is not None:
            self._state = new

    def redo(self, *_: Any) -> None:            # key-binding friendly
        new = self._undo.redo()
        if new is not None:
            self._state = new

    def update_preview(self) -> None:
        """Render live preview (NOP when head-less)."""
        if hasattr(self, "_preview") and self._preview:
            html = self._render_html()
            if html:
                self._preview.render(html)      # type: ignore[attr-defined]

    # ------------------------------------------------------------------ internals
    def _display_available(self) -> bool:
        if sys.platform.startswith("win"):
            return True
        return bool(os.environ.get("DISPLAY"))

    # ----------------------------------------------- GUI (only when enabled)
    def _build_ui(self) -> None:
        assert self.root is not None and ttk      # type: ignore[truthy-bool]
        self.root.title("Template Builder 3")
        self.root.geometry("1200x780")

        # notebook tabs
        nb = ttk.Notebook(self.root)             # type: ignore[arg-type]
        nb.pack(fill="both", expand=True)

        # example “Content” tab with placeholder widgets
        frame_content = ttk.Frame(nb)            # type: ignore[arg-type]
        nb.add(frame_content, text="Content")

        PlaceholderEntry(frame_content, placeholder="Title").pack(fill="x", padx=4, pady=4)
        PlaceholderMultiTextField(frame_content, placeholder="Description…").pack(
            fill="both", expand=True, padx=4, pady=4
        )

        # preview
        if PreviewEngine:
            self._preview = PreviewEngine(nb)    # type: ignore[call-arg]
            nb.add(self._preview.frame, text="Preview")  # type: ignore[attr-defined]

    def _bind_global_shortcuts(self) -> None:
        if not self.root:
            return
        for seq, handler in self._SHORTCUTS:
            cb = getattr(self, handler, None)
            if cb:
                self.root.bind_all(seq, cb, add="+")

    # ----------------------------------------------- HTML helpers
    def _render_html(self) -> str | None:
        """Naïve placeholder → HTML render via services.text.auto_format."""
        text_mod = _safe("template_builder.services.text")
        auto_format = getattr(text_mod, "auto_format", None)
        title = self._state.get("TITLE", "")
        body = self._state.get("BODY", "")
        if auto_format:
            body = auto_format(body)
        return f"<h1>{title}</h1>\n{body}" if (title or body) else None

    # ------------------------------------------------------------------ dunder
    def __repr__(self) -> str:  # pragma: no cover
        return f"<TemplateBuilderApp gui={self.enable_gui!r} state={len(self._state)} keys>"

# ────────────────────────────────────────────────────────────────
# CLI demo
# ----------------------------------------------------------------
def _demo() -> None:  # pragma: no cover
    app = TemplateBuilderApp()
    if app.root:
        app.root.mainloop()

if __name__ == "__main__":  # pragma: no cover
    _demo()
