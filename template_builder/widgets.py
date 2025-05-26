from __future__ import annotations
"""template_builder.widgets

Widget library con logica UI per Template Builder.
Contiene i seguenti componenti pubblici (esportati via ``__all__``):

* ``PlaceholderEntry``              – Entry con ghost‑placeholder grigio
* ``PlaceholderMultiTextField``   – Text multiriga con placeholder, smart‑paste e auto_format
* ``MultiTextField``              – alias legacy → ``PlaceholderMultiTextField``
* ``SortableImageRepeaterField``  – lista di immagini riordinabile con drag‑handle + validazione URL

Dipendenze minime:
* standard tkinter / ttk
* template_builder.services.text  → ``smart_paste`` e ``auto_format``
* template_builder.services.images → ``validate_url``
* template_builder.assets          → palette e costanti

Tutti gli import sono runtime‑safe: il modulo può essere importato in ambiente headless
per i test (non costruisce alcuna finestra se non istanziato).
"""

from typing import Callable, List, Optional
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from .assets import PALETTE, DEFAULT_COLS
from .services import text as text_service
from .services import images as image_service

__all__ = [
    "PlaceholderEntry",
    "PlaceholderMultiTextField",
    "MultiTextField",
    "SortableImageRepeaterField",
]


# ---------------------------------------------------------------------------
# Helper – style utilities
# ---------------------------------------------------------------------------

def _apply_border(widget: tk.Widget, ok: bool) -> None:
    """Colora il bordo del widget in base alla validazione."""
    widget.configure(  # type: ignore[arg-type]
        highlightthickness=1,
        highlightbackground=PALETTE["valid" if ok else "error"],
    )


# ---------------------------------------------------------------------------
# PlaceholderEntry
# ---------------------------------------------------------------------------

class PlaceholderEntry(ttk.Entry):
    """Entry che mostra un testo grigio (placeholder) quando è vuoto."""

    def __init__(self, master: tk.Misc, placeholder: str = "", **kw):
        super().__init__(master, **kw)
        self._placeholder = placeholder
        self._placeholder_on = False
        self._default_fg = self.cget("foreground") or "black"
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self._show_placeholder_if_needed()

    # ------------------------------------------------------------------ events

    def _on_focus_in(self, _):
        if self._placeholder_on:
            self.delete(0, tk.END)
            self.configure(foreground=self._default_fg)
            self._placeholder_on = False

    def _on_focus_out(self, _):
        self._show_placeholder_if_needed()

    # ------------------------------------------------------------------ helpers

    def _show_placeholder_if_needed(self):
        if not self.get():
            self.insert(0, self._placeholder)
            self.configure(foreground="grey")
            self._placeholder_on = True

    # ------------------------------------------------------------------ public

    def get_value(self) -> str:
        """Ritorna stringa effettiva senza placeholder."""
        val = self.get()
        return "" if self._placeholder_on else val


# ---------------------------------------------------------------------------
# PlaceholderMultiTextField
# ---------------------------------------------------------------------------

class PlaceholderMultiTextField(ttk.Frame):
    """Text multiriga + rendering HTML + smart‑paste.

    Args:
        mode: "ul" (default) → converte newline in <li>…<li>
              "p"           → newline in <p>
    """

    def __init__(self, master: tk.Misc, *, mode: str = "ul", placeholder: str = "", **kw):
        super().__init__(master, **kw)
        self.mode = mode
        self.text = tk.Text(self, wrap="word", height=6)
        self.text.pack(fill="both", expand=True)
        self._placeholder = placeholder
        self._placeholder_on = False

        self.text.bind("<FocusIn>", self._focus_in)
        self.text.bind("<FocusOut>", self._focus_out)
        self.text.bind("<Control-v>", self._smart_paste, add="+")
        # macOS Command+V
        self.text.bind("<Command-v>", self._smart_paste, add="+")

        self._show_placeholder_if_needed()

    # ------------------------------------------------------------------ events

    def _focus_in(self, _):
        if self._placeholder_on:
            self.text.delete("1.0", tk.END)
            self.text.configure(foreground="black")
            self._placeholder_on = False

    def _focus_out(self, _):
        self._show_placeholder_if_needed()

    def _smart_paste(self, event):  # noqa: D401 – returning "break" is Tk idiom
        """Override default paste: applica smart_paste()."""
        try:
            raw = self.clipboard_get()
        except tk.TclError:
            return "break"  # nothing to paste
        # convert ; or newline in list items
        lines = text_service.smart_paste(raw)
        self.text.insert(tk.INSERT, "\n".join(lines))
        return "break"

    # ------------------------------------------------------------------ helpers

    def _show_placeholder_if_needed(self):
        if not self.text.get("1.0", tk.END).strip():
            self.text.insert("1.0", self._placeholder)
            self.text.configure(foreground="grey")
            self._placeholder_on = True

    # ------------------------------------------------------------------ public

    def get_raw(self) -> str:
        """Testo grezzo senza placeholder."""
        data = self.text.get("1.0", tk.END).strip()
        return "" if self._placeholder_on else data

    def render_html(self) -> str:
        """Rende il contenuto in HTML secondo la modalità impostata."""
        raw = self.get_raw()
        return text_service.auto_format(raw, mode=self.mode)

# alias legacy compatibile
MultiTextField = PlaceholderMultiTextField


# ---------------------------------------------------------------------------
# SortableImageRepeaterField
# ---------------------------------------------------------------------------

class SortableImageRepeaterField(ttk.Frame):
    """Repeater lista immagini con validazione URL e riordino."""

    def __init__(self, master: tk.Misc, cols: int = DEFAULT_COLS, **kw):
        super().__init__(master, **kw)
        self.cols = cols
        self._rows: List[ttk.Frame] = []
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        btn_add = ttk.Button(self, text="+ Add", command=self._add_row)
        btn_add.pack(anchor="w")
        self._container = ttk.Frame(self)
        self._container.pack(fill="both", expand=True)

    def _add_row(self, url: str = ""):
        row_frame = ttk.Frame(self._container)
        entry = ttk.Entry(row_frame, width=60)
        entry.insert(0, url)
        entry.pack(side="left", fill="x", expand=True)
        btn_up = ttk.Button(row_frame, text="↑", width=2, command=lambda: self._move(row_frame, -1))
        btn_dn = ttk.Button(row_frame, text="↓", width=2, command=lambda: self._move(row_frame, +1))
        btn_del = ttk.Button(row_frame, text="✕", width=2, command=lambda: self._delete(row_frame))
        for b in (btn_up, btn_dn, btn_del):
            b.pack(side="left")
        # validate on focus out
        entry.bind("<FocusOut>", lambda e, ent=entry: self._validate(ent))
        self._rows.append(row_frame)
        row_frame.pack(fill="x", pady=2)

    # ------------------------------------------------------------------ actions

    def _move(self, row: ttk.Frame, delta: int):
        idx = self._rows.index(row)
        new_idx = max(0, min(len(self._rows) - 1, idx + delta))
        if new_idx == idx:
            return
        self._rows.pop(idx)
        self._rows.insert(new_idx, row)
        # re‑pack alla nuova posizione
        for r in self._rows:
            r.pack_forget()
            r.pack(fill="x", pady=2)

    def _delete(self, row: ttk.Frame):
        self._rows.remove(row)
        row.destroy()

    def _validate(self, entry: ttk.Entry):
        try:
            image_service.validate_url(entry.get().strip())
            _apply_border(entry, ok=True)
        except Exception:  # noqa: BLE001 – mostra solo bordo rosso
            _apply_border(entry, ok=False)

    # ------------------------------------------------------------------ public

    def get_urls(self) -> List[str]:
        return [row.winfo_children()[0].get().strip() for row in self._rows]
