# template_builder/builder_core.py
"""
Refactored core controller for Template Builder 3.x — **Undo/Redo UI enabled**

Changes
-------
* Edit → Undo / Redo menu collegato alla `UndoRedoStack`.
* Alias pubblici `edit_undo` / `edit_redo` (shortcut-friendly).
* Dopo ogni undo/redo i widget (se presenti) e la preview vengono
  aggiornati via `_apply_state_to_widgets()` e `update_preview()`.
* Rimane importabile in ambiente head-less (CI).

"""

from __future__ import annotations

import importlib
import os
import sys
import types
from typing import Any, Dict, List, Tuple, Optional

# ───────────────────────────── optional imports (fallback → stub)
def _safe(name: str) -> types.ModuleType:
    try:
        return importlib.import_module(name)
    except Exception:                               # pragma: no cover
        return types.ModuleType(f"_stub_{name.replace('.', '_')}")

_tk          = _safe("tkinter")
_ttk         = _safe("tkinter.ttk")
_widgets_mod = _safe("template_builder.widgets")
_services    = _safe("template_builder.services.storage")
_preview_mod = _safe("template_builder.infrastructure.preview_engine")
_ui_utils    = _safe("template_builder.infrastructure.ui_utils")

PlaceholderEntry          = getattr(_widgets_mod, "PlaceholderEntry", object)
PlaceholderMultiTextField = getattr(_widgets_mod, "PlaceholderMultiTextField", object)
UndoRedoStack             = getattr(_services, "UndoRedoStack", lambda: None)
quick_save_fn             = getattr(_services, "quick_save",   lambda *_: None)
load_recipe_fn            = getattr(_services, "load_recipe", lambda *_: {})
PreviewEngine             = getattr(_preview_mod, "PreviewEngine", None)
bind_mousewheel           = getattr(_ui_utils, "bind_mousewheel", lambda widget: None)

tk  = _tk  if hasattr(_tk,  "Tk")   else None
ttk = _ttk if hasattr(_ttk, "Frame") else None       # type: ignore[assignment]

# ──────────────────────────────────────────────── main class
class TemplateBuilderApp:
    """Modern, modular controller for Template Builder."""

    _SHORTCUTS: List[Tuple[str, str]] = [
        ("<Control-s>", "quick_save"),
        ("<Control-z>", "edit_undo"),
        ("<Control-y>", "edit_redo"),
        ("<Command-s>", "quick_save"),   # macOS ⌘
        ("<Command-z>", "edit_undo"),
        ("<Command-y>", "edit_redo"),
    ]

    # ---------------------------------------------------- init
    def __init__(self, *, enable_gui: bool | None = None) -> None:
        self.enable_gui = self._display_available() if enable_gui is None else enable_gui
        self.root = tk.Tk() if self.enable_gui and tk else None
        self._undo = UndoRedoStack()
        self._state: Dict[str, Any] = {}

        if self.root:
            self._build_ui()
            self._build_menu()
            self._bind_global_shortcuts()

    # ---------------------------------------------------- public API
    def quick_save(self, *_: Any) -> None:
        quick_save_fn(self._state)

    # ---- Undo / Redo — alias “friendly” per menu e shortcut
    def edit_undo(self, *_: Any) -> None:  # noqa: D401
        """Alias di :py:meth:`undo` (scorciatoie/UI)."""
        self.undo()

    def edit_redo(self, *_: Any) -> None:  # noqa: D401
        """Alias di :py:meth:`redo` (scorciatoie/UI)."""
        self.redo()

    def undo(self, *_: Any) -> None:
        new = self._undo.undo()
        if new is not None:
            self._state = new
            self._apply_state_to_widgets()
            self.update_preview()

    def redo(self, *_: Any) -> None:
        new = self._undo.redo()
        if new is not None:
            self._state = new
            self._apply_state_to_widgets()
            self.update_preview()

    def load_recipe(self, path: os.PathLike | str) -> None:
        """Importa un file ricetta; ignora errori in head-less."""
        try:
            self._state = load_recipe_fn(path)
            self._undo.push(self._state)
            self._apply_state_to_widgets()
            self.update_preview()
        except (FileNotFoundError, OSError, ValueError, TypeError):
            self._state = {}

    def update_preview(self) -> None:
        """Aggiorna il pannello di anteprima (NOP se head-less)."""
        if hasattr(self, "_preview") and self._preview:
            html = self._render_html()
            if html:
                self._preview.render(html)        # type: ignore[attr-defined]

    # ---------------------------------------------------- internals
    @staticmethod
    def _display_available() -> bool:
        # Tratta macOS (darwin) come una piattaforma GUI nativa
        if sys.platform.startswith("win") or sys.platform == "darwin":
            return True
        return bool(os.environ.get("DISPLAY"))

    # -------------- GUI helpers
    def _build_ui(self) -> None:
        """Costruisce i widget principali (notebook, preview…)."""
        assert self.root is not None and ttk                  # type: ignore[truthy-bool]
        self.root.title("Template Builder 3")
        self.root.geometry("1200x780")

        nb = ttk.Notebook(self.root)                          # type: ignore[arg-type]
        nb.pack(fill="both", expand=True)

        # Abilita smart-scroll sul notebook
        bind_mousewheel(nb)

        content = ttk.Frame(nb)                               # type: ignore[arg-type]
        nb.add(content, text="Content")

        PlaceholderEntry(content, placeholder="Title").pack(fill="x", padx=4, pady=4)
        desc_field = PlaceholderMultiTextField(content, placeholder="Description…")
        desc_field.pack(fill="both", expand=True, padx=4, pady=4)

        # Abilita smart-scroll sul campo di testo della descrizione
        bind_mousewheel(desc_field)

        if PreviewEngine:
            # Istanzia la PreviewEngine senza init_frame() finale
            self._preview = PreviewEngine(nb)  # type: ignore[call-arg]

            # Aggiunge il tab Preview solo se il frame esiste e senza crashare
            frame = None
            try:
                frame = getattr(self._preview, "frame", None)
                if frame:
                    nb.add(frame, text="Preview")
            except Exception:
                # ignora eventuali errori Tcl durante nb.add
                pass
        if frame:
            # Abilita smart-scroll sul tab preview
            bind_mousewheel(frame)
        # Abilita lo scroll fluido sul notebook e sulle sezioni scrollabili
        bind_mousewheel(nb)
        bind_mousewheel(desc_field)
        if frame:
            bind_mousewheel(frame)

    def _build_menu(self) -> None:
        """Aggiunge il menu *Edit* con Undo / Redo (solo GUI)."""
        if not self.enable_gui or not self.root or not tk:
            return

        menubar = tk.Menu(self.root)                          # type: ignore[attr-defined]
        edit = tk.Menu(menubar, tearoff=False)
        edit.add_command(label="Undo", accelerator="Ctrl+Z", command=self.edit_undo)
        edit.add_command(label="Redo", accelerator="Ctrl+Y", command=self.edit_redo)
        menubar.add_cascade(label="Edit", menu=edit)

        self.root.config(menu=menubar)
        self._menu_edit = edit

    def _bind_global_shortcuts(self) -> None:
        if not self.root:
            return
        for seq, handler in self._SHORTCUTS:
            cb = getattr(self, handler, None)
            if callable(cb):
                self.root.bind_all(seq, cb, add="+")

    # -------------- widget/state sync (stub, estendibile)
    def _apply_state_to_widgets(self) -> None:
        """Aggiorna i campi GUI dallo stato; no-op se head-less."""
        if not self.enable_gui or not self.root:
            return
        # TODO: mappatura TITLE/BODY → campi widget

    # -------------- HTML helpers
    def _render_html(self) -> str | None:
        text_mod = _safe("template_builder.services.text")
        auto_format = getattr(text_mod, "auto_format", None)
        title = self._state.get("TITLE", "")
        body = self._state.get("BODY", "")
        if auto_format:
            body = auto_format(body)
        return f"<h1>{title}</h1>\n{body}" if (title or body) else None

    # ---------------------------------------------------- dunder
    def __repr__(self) -> str:  # pragma: no cover
        return f"<TemplateBuilderApp gui={self.enable_gui!r} state={len(self._state)} keys>"


# --------------------------------------------------------- CLI demo
def _demo() -> None:  # pragma: no cover
    app = TemplateBuilderApp()
    if app.root:
        app.root.mainloop()


if __name__ == "__main__":  # pragma: no cover
    _demo()
