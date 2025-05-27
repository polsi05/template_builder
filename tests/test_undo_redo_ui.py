# tests/test_undo_redo_ui.py
"""
Head-less smoke-test per l’integrazione Undo/Redo UI.
Verifica che le API non alzino eccezioni in assenza di display.
"""

import os
import importlib

# Simula un ambiente CI senza display
os.environ.pop("DISPLAY", None)

core = importlib.import_module("template_builder.builder_core")
TemplateBuilderApp = core.TemplateBuilderApp


def test_undo_redo_headless() -> None:
    app = TemplateBuilderApp(enable_gui=False)

    # Carica un paio di stati fittizi nello stack
    app._state = {"TITLE": "First"}
    app._undo.push(app._state.copy())
    app._state = {"TITLE": "Second"}
    app._undo.push(app._state.copy())

    # Le chiamate non devono sollevare
    app.edit_undo()
    app.edit_redo()
