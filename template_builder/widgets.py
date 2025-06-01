# template_builder/widgets.py

import tkinter as tk
from tkinter import ttk
from typing import Callable, List
from template_builder.services.text import get_field_help, auto_format, smart_paste

# Segnala se i tooltip sono supportati
HAS_TOOLTIP: bool = True

def _attach_tooltip(widget: tk.Widget, text: str):
    """
    Associa un attributo `tooltip_text` al widget,
    usato dai test per verificare la presenza del tooltip.
    """
    if HAS_TOOLTIP and text:
        setattr(widget, 'tooltip_text', text)

class PlaceholderEntry(ttk.Entry):
    """
    Entry con ghost-text (placeholder), tooltip contestuale e rendering HTML.
    """
    def __init__(self, master: tk.Misc, placeholder: str = "", **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.default_fg = self.cget("foreground") or "black"

        # ghost-text handlers
        self.bind("<FocusIn>", self._clear_placeholder, add="+")
        self.bind("<FocusOut>", self._add_placeholder, add="+")
        self._add_placeholder()

        # tooltip contestuale (test_placeholder_entry_and_spinbox) :contentReference[oaicite:1]{index=1}
        _attach_tooltip(self, get_field_help(placeholder))

    def _clear_placeholder(self, event=None):
        if self.get() == self.placeholder:
            self.delete(0, tk.END)
            self.config(foreground=self.default_fg)

    def _add_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(foreground="grey")
        else:
            self.config(foreground=self.default_fg)

    def get_value(self) -> str:
        """
        Restituisce il valore corrente, o "" se è ancora il placeholder
        (test_placeholder_entry_and_spinbox). :contentReference[oaicite:3]{index=3}
        """
        val = self.get()
        return "" if val == self.placeholder else val

    def render_html(self) -> str:
        """
        Render HTML via <p>…</p> (test_placeholder_entry_and_spinbox). :contentReference[oaicite:5]{index=5}
        """
        return auto_format(self.get_value(), mode="p")

class PlaceholderSpinbox(PlaceholderEntry):
    """
    Spinbox con ghost-text – eredita PlaceholderEntry,
    ridefinisce solo render_html per input numerico.
    """
    def __init__(self, master: tk.Misc, placeholder: str = "", **kwargs):
        super().__init__(master, placeholder=placeholder, **kwargs)

    def render_html(self) -> str:
        """
        Rende un <input type="number"> con il valore corrente
        (test_placeholder_entry_and_spinbox). :contentReference[oaicite:7]{index=7}
        """
        val = self.get_value()
        return f'<input type="number" value="{val}">'

class PlaceholderMultiTextField(ttk.Frame):
    """
    Campo multilinea con placeholder e smart-paste:
      - __init__(..., placeholder, mode, on_change)
      - get_raw(): testo puro o ""
      - render_html(): via auto_format(mode)
      - paste intelligente (test_placeholder_multi_text_field) :contentReference[oaicite:9]{index=9}
    """
    def __init__(self,
                 master: tk.Misc,
                 placeholder: str,
                 mode: str,
                 on_change: Callable[[], None],
                 **kwargs):
        super().__init__(master, **kwargs)
        self.text = tk.Text(self, height=6, wrap="word")
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.text.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.text.pack(side="left", fill="both", expand=True)

        self.placeholder = placeholder
        self.mode = mode
        self.on_change = on_change
        self.default_fg = self.text.cget("foreground") or "black"

        # ghost-text
        self.text.bind("<FocusIn>", self._clear_placeholder, add="+")
        self.text.bind("<FocusOut>", self._add_placeholder, add="+")
        # smart-paste e change
        self.text.bind("<KeyRelease>", lambda e: self.on_change(), add="+")
        self.text.bind("<Control-v>", self._handle_paste, add="+")
        self.text.bind("<Command-v>", self._handle_paste, add="+")
        # inizializza placeholder
        self._add_placeholder()

    def _clear_placeholder(self, event=None):
        content = self.text.get("1.0", "end").strip()
        if content == self.placeholder:
            self.text.delete("1.0", "end")
            self.text.config(foreground=self.default_fg)

    def _add_placeholder(self, event=None):
        content = self.text.get("1.0", "end").strip()
        if not content:
            self.text.insert("1.0", self.placeholder)
            self.text.config(foreground="grey")
        else:
            self.text.config(foreground=self.default_fg)

    def _handle_paste(self, event):
        try:
            clip = self.text.clipboard_get()
        except tk.TclError:
            return "break"
        # se ancora placeholder, lo rimuove
        if self.text.get("1.0", "end").strip() == self.placeholder:
            self.text.delete("1.0", "end")
        lines = smart_paste(clip)
        if not lines:
            return "break"
        for i, ln in enumerate(lines):
            self.text.insert(tk.INSERT, ln)
            if i < len(lines) - 1:
                self.text.insert(tk.INSERT, "\n")
        self.on_change()
        return "break"

    def get_raw(self) -> str:
        """
        Restituisce testo puro o "" se placeholder
        (test_placeholder_multi_text_field). :contentReference[oaicite:11]{index=11}
        """
        content = self.text.get("1.0", "end").strip()
        return "" if content == self.placeholder else content

    def render_html(self) -> str:
        """
        Render HTML via auto_format(self.get_raw(), mode)
        (test_placeholder_multi_text_field). :contentReference[oaicite:13]{index=13}
        """
        return auto_format(self.get_raw(), mode=self.mode)

class SortableImageRepeaterField(ttk.Frame):
    """
    Lista dinamica di URL immagine:
      - _add_row(src)
      - _move_row(frame, delta)
      - _del_row(frame)
      - get_urls()
      (test_sortable_image_repeater_field) :contentReference[oaicite:15]{index=15}
    """
    def __init__(self, master: tk.Misc, **kwargs):
        super().__init__(master, **kwargs)
        self._rows: List[tk.Frame] = []

    def _add_row(self, src: str = ""):
        row = tk.Frame(self)
        row.pack(fill="x", pady=1)
        entry = PlaceholderEntry(row, placeholder=src)
        entry.pack(side="left", padx=2)
        self._rows.append(row)

    def _move_row(self, row: tk.Frame, delta: int):
        idx = self._rows.index(row)
        new = idx + delta
        if 0 <= new < len(self._rows):
            self._rows.pop(idx)
            self._rows.insert(new, row)
            for r in self._rows:
                r.pack_forget()
                r.pack(fill="x", pady=1)

    def _del_row(self, row: tk.Frame):
        row.destroy()
        self._rows.remove(row)

    def get_urls(self) -> List[str]:
        """
        Restituisce la lista di valori attuali dalle entry
        (test_sortable_image_repeater_field). :contentReference[oaicite:17]{index=17}
        """
        urls: List[str] = []
        for row in self._rows:
            w = row.winfo_children()[0]
            if hasattr(w, "get_value"):
                urls.append(w.get_value())
            else:
                urls.append(w.get().strip())
        return urls
