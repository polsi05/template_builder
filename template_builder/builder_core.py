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
        """Controlla quali segnaposto {{TAG}} del template sono coperti dallo stato.
        Restituisce una lista di stringhe del tipo "✅ TAG" o "❌ TAG", in ordine alfabetico.
        Se un tag termina con "_ALT" e la corrispondente chiave con "_SRC" esiste nello stato,
        lo consideriamo comunque presente (✅)."""
        # Ricava tutti i segnaposto dal template HTML corrente
        tags = extract_placeholders(self.template_src or "")
        # Lista di righe risultato
        lines: list[str] = []
        for tag in sorted(tags):
            if tag in self._state:
                # Il tag è direttamente presente nello stato
                lines.append(f"✅ {tag}")
            else:
                # Se termina in _ALT e il corrispondente _SRC è presente, consideralo presente
                if tag.endswith("_ALT"):
                    base = tag[: -len("_ALT")]
                    src_key = base + "_SRC"
                    if src_key in self._state:
                        lines.append(f"✅ {tag}")
                        continue
                # Altrimenti, manca
                lines.append(f"❌ {tag}")
        return lines

    # alias per compatibilità con demo CLI
    run = lambda self: None
    __call__ = run