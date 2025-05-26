"""
Custom widget collection – STUB.
Contiene placeholder delle classi chiave mappate dal legacy.
"""
from tkinter import ttk

__all__ = [
    "PlaceholderEntry",
    "PlaceholderMultiTextField",
    "MultiTextField",
    "SortableImageRepeaterField",
]

class PlaceholderEntry(ttk.Entry):
    pass

class PlaceholderMultiTextField(ttk.Frame):
    def render_html(self) -> str:  # pragma: no cover
        return ""

MultiTextField = PlaceholderMultiTextField  # alias legacy

class SortableImageRepeaterField(ttk.Frame):
    pass
