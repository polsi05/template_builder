import os
import json
import tkinter as tk
from template_builder.services.storage import UndoRedoStack, quick_save, load_recipe as _load_recipe
from template_builder.services.text import extract_placeholders
from template_builder.infrastructure.ui_utils import show_info


class TemplateBuilderApp:
    """Controller principale: GUI opzionale, stato, undo/redo, load, auditing."""
    def __init__(self, enable_gui: bool = True) -> None:
        self.enable_gui = bool(enable_gui)
        # Stato interno e undo/redo
        self._state: dict = {}
        self._undo = UndoRedoStack()

        if self.enable_gui and self._display_available():
            # Inizializzazione GUI solo se richiesto e DISPLAY presente
            self._root = tk.Tk()
            self._root.title("Template Builder")
            # Tema dark se disponibile
            try:
                from ttkbootstrap import Style
                Style('darkly')
            except Exception:
                pass
            # (eventuali build_ui, menu, demo, mainloop)
        else:
            self._root = None

    def __repr__(self) -> str:
        return f"<TemplateBuilderApp enable_gui={self.enable_gui}>"

    @staticmethod
    def _display_available() -> bool:
        disp = os.environ.get("DISPLAY", "")
        return bool(disp)

    def undo(self) -> None:
        """Torna allo stato precedente."""
        try:
            self._state = self._undo.undo()
        except IndexError:
            pass

    def redo(self) -> None:
        """Ritorna allo stato successivo."""
        try:
            self._state = self._undo.redo()
        except IndexError:
            pass

    def quick_save(self) -> None:
        """Snapshot di _state su disco."""
        quick_save(self._state)

    def load_recipe(self, path: str) -> None:
        """Carica JSON da file; su errore resetta a {}."""
        try:
            data = _load_recipe(path)
            if isinstance(data, dict):
                self._state = data
            else:
                self._state = {}
        except Exception:
            self._state = {}

    def audit_placeholders(self) -> list[str]:
        """
        Estrae {{TAG}} da template_src e segnala tramite dialog le differenze
        rispetto a _state.
        """
        tpl = getattr(self, "template_src", "")
        found = extract_placeholders(tpl)
        lines = []
        for tag in found:
            mark = "✅" if tag in self._state else "❌"
            lines.append(f"{mark} {tag}")
        show_info("\n".join(lines))
        return lines

    # alias per compatibilità con demo CLI
    run = lambda self: None
    __call__ = run