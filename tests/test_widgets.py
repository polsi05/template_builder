# tests/test_widgets.py
import os
import sys
import pytest

# Import Tkinter in modo sicuro: in ambienti head-less o dove la libreria manca
# l'import potrebbe fallire.
try:
    import tkinter as tk
    from tkinter import TclError
except ImportError:        # Tkinter non installato
    tk = None              # type: ignore
    TclError = RuntimeError  # placeholder

# True se abbiamo sia Tkinter importato con successo sia un display disponibile
HAS_DISPLAY = (
    tk is not None
    and not (sys.platform.startswith("linux") and os.environ.get("DISPLAY", "") == "")
)

from template_builder.widgets import (   # import dopo aver definito HAS_DISPLAY
    PlaceholderEntry,
    PlaceholderSpinbox,
    PlaceholderMultiTextField,
    SortableImageRepeaterField,
)


# ---------- Fixture radice Tk ---------- #
@pytest.fixture
def root():
    """Istanzia Tk solo se il display è disponibile; altrimenti salta i test."""
    if not HAS_DISPLAY:
        pytest.skip("Tkinter/Display non disponibile in questo ambiente")
    try:
        root = tk.Tk()
    except TclError:
        pytest.skip("Tcl non disponibile in questo ambiente")
    yield root
    root.destroy()


# ---------- Test: PlaceholderEntry + PlaceholderSpinbox ---------- #
@pytest.mark.skipif(not HAS_DISPLAY, reason="Display non disponibile")
def test_placeholder_entry_and_spinbox(root):
    entry = PlaceholderEntry(root, placeholder="Enter name")
    # Placeholder presente all'avvio
    assert entry.get_value() == ""
    entry._clear_placeholder()
    entry.insert(0, "Alice")
    assert entry.get_value() == "Alice"
    html = entry.render_html()
    assert "<p>" in html and "Alice" in html

    spin = PlaceholderSpinbox(root, placeholder="0")
    assert spin.get_value() == ""
    spin._clear_placeholder()
    spin.insert(0, "5")
    assert spin.get_value() == "5"


# ---------- Test: PlaceholderMultiTextField ---------- #
@pytest.mark.skipif(not HAS_DISPLAY, reason="Display non disponibile")
def test_placeholder_multi_text_field(root):
    mtf = PlaceholderMultiTextField(root, "Placeholder text", mode="ul", on_change=None)
    assert mtf.get_raw() == ""
    mtf._clear_placeholder(None)
    mtf.text.insert("1.0", "Line1\nLine2")
    raw_text = mtf.get_raw()
    assert "Line1" in raw_text and "Line2" in raw_text
    html = mtf.render_html()
    assert "<ul>" in html and "</ul>" in html


# ---------- Test: SortableImageRepeaterField ---------- #
@pytest.mark.skipif(not HAS_DISPLAY, reason="Display non disponibile")
def test_sortable_image_repeater_field(root):
    s = SortableImageRepeaterField(root)
    s._add_row("url1")
    s._add_row("url2")

    # Simuliamo l'inserimento di percorsi reali
    for i, frame in enumerate(s._rows):
        entry = frame.winfo_children()[0]
        entry._clear_placeholder()
        entry.delete(0, tk.END)
        entry.insert(0, f"path{i+1}")

    assert s.get_urls() == ["path1", "path2"]

    # Sposta la seconda riga in cima
    s._move_row(s._rows[1], -1)
    assert s.get_urls() == ["path2", "path1"]

    # Cancella la prima riga
    s._del_row(s._rows[0])
    assert s.get_urls() == ["path1"]
