# tests/test_dnd_images.py
"""
Smoke-test head-less per il supporto Drag & Drop immagini (Issue #4).

* Il test ***non richiede*** display né la libreria `tkinterdnd2`.
* Verifica che il modulo si importi e che `HAS_DND` sia un boolean.
"""

import os
import importlib
import pytest

# Forza ambiente head-less
os.environ.pop("DISPLAY", None)

widgets = importlib.import_module("template_builder.widgets")


def test_has_dnd_flag() -> None:
    assert hasattr(widgets, "HAS_DND")
    assert isinstance(widgets.HAS_DND, bool)


@pytest.mark.skipif(not widgets.HAS_DND, reason="tkinterdnd2 non disponibile")
def test_split_dnd_event_data() -> None:
    """Parsing robusto di stringa DnD con spazi / brace."""
    split = widgets._split_dnd_event_data  # type: ignore[attr-defined]
    raw = r'{/path/with space/img 1.png} {/other/img2.jpg}'
    assert split(raw) == ["/path/with space/img 1.png", "/other/img2.jpg"]
