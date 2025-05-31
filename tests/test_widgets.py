import pytest
import tkinter as tk
from template_builder.widgets import (
    PlaceholderEntry,
    PlaceholderSpinbox,
    PlaceholderMultiTextField,
    SortableImageRepeaterField,
)

@pytest.fixture
def root():
    root = tk.Tk()
    yield root
    root.destroy()

def test_placeholder_entry_and_spinbox(root):
    entry = PlaceholderEntry(root, placeholder="Enter name")
    # All'inizio il placeholder è presente
    assert entry.get_value() == ""
    entry._clear_placeholder()
    entry.insert(0, "Alice")
    assert entry.get_value() == "Alice"
    result = entry.render_html()
    assert "<p>" in result and "Alice" in result

    spin = PlaceholderSpinbox(root, placeholder="0")
    assert spin.get_value() == ""
    spin._clear_placeholder()
    spin.insert(0, "5")
    assert spin.get_value() == "5"

def test_placeholder_multi_text_field(root):
    mtf = PlaceholderMultiTextField(root, "Placeholder text", mode="ul", on_change=None)
    # Inizialmente segnaposto presente => testo grezzo vuoto
    assert mtf.get_raw() == ""
    mtf._clear_placeholder(None)
    mtf.text.insert("1.0", "Line1\nLine2")
    raw_text = mtf.get_raw()
    assert "Line1" in raw_text and "Line2" in raw_text
    html = mtf.render_html()
    assert "<ul>" in html and "</ul>" in html

def test_sortable_image_repeater_field(root):
    s = SortableImageRepeaterField(root)
    s._add_row("url1")
    s._add_row("url2")
    # Per semplicità, impostiamo manualmente i valori reali
    for i, frame in enumerate(s._rows):
        entry = frame.winfo_children()[0]
        entry._clear_placeholder()
        entry.delete(0, tk.END)
        entry.insert(0, f"path{i+1}")
    urls = s.get_urls()
    assert urls == ["path1", "path2"]
    # Sposta seconda riga in cima
    s._move_row(s._rows[1], -1)
    urls_moved = s.get_urls()
    assert urls_moved == ["path2", "path1"]
    # Cancella la prima riga
    s._del_row(s._rows[0])
    urls_del = s.get_urls()
    assert urls_del == ["path1"]
