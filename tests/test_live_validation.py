"""
Smoke-test head-less per la *live validation* (Issue #5).

*Non* richiede display: testa solo le funzioni pure e i flag.
"""

import os
import importlib

# forza ambiente head-less
os.environ.pop("DISPLAY", None)

widgets = importlib.import_module("template_builder.widgets")


def test_apply_border_stub():
    """_apply_border deve agire senza sollevare eccezioni."""
    class Dummy:
        def configure(self, **kw):
            self.kw = kw

    w = Dummy()
    widgets._apply_border(w, ok=True)   # type: ignore[attr-defined]
    assert "highlightbackground" in w.kw
    widgets._apply_border(w, ok=False)  # type: ignore[attr-defined]
    assert "highlightbackground" in w.kw


def test_has_dnd_flag_still_bool():
    assert isinstance(widgets.HAS_DND, bool)
