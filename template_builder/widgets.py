# template_builder/widgets.py
"""
Widget library per Template Builder – **Drag & Drop immagini integrato**.

Componenti pubblici
-------------------
* ``PlaceholderEntry``
* ``PlaceholderMultiTextField`` / ``MultiTextField``
* ``SortableImageRepeaterField``
* **``HAS_DND``** → ``True`` se la libreria *tkinterdnd2* è importabile.

Novità
------
* Rilevamento automatico della presenza di **tkinterdnd2**::
      from template_builder.widgets import HAS_DND
  Il valore è *True* solo se l'import e l'inizializzazione hanno successo.
* ``SortableImageRepeaterField`` accetta ora il **drag-and-drop** di file
  immagine/URL:
  - quando *tkinterdnd2* è disponibile il contenitore
    ``self._container`` riceve l'evento ``<<Drop>>`` e chiama ``_on_drop``;
  - in assenza di *tkinterdnd2* il widget continua a funzionare con i
    pulsanti “↑ ↓ ✕”.

L’intero modulo rimane importabile in **ambiente head-less**: nessun widget
viene instanziato a livello di modulo e l’assenza di display non solleva.
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# --------------------------------------------------------------------------- optional DnD
try:  # pragma: no cover – la CI non installa tkinterdnd2
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
    HAS_DND: bool = True
except Exception:  # noqa: BLE001
    DND_FILES = None  # type: ignore[assignment]
    TkinterDnD = None  # type: ignore[assignment]
    HAS_DND = False

# --------------------------------------------------------------------------- app-local imports
from .assets import PALETTE, DEFAULT_COLS
from .services import text as text_service
from .services import images as image_service

__all__ = [
    "HAS_DND",
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
    """Text multiriga + rendering HTML + smart-paste."""

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
        self.text.bind("<Command-v>", self._smart_paste, add="+")  # macOS

        self._show_placeholder_if_needed()

    # ------------------------------------------------------------------ events

    def _focus_in(self, _):
        if self._placeholder_on:
            self.text.delete("1.0", tk.END)
            self.text.configure(foreground="black")
            self._placeholder_on = False

    def _focus_out(self, _):
        self._show_placeholder_if_needed()

    def _smart_paste(self, event):  # noqa: D401 – Tk pattern
        try:
            raw = self.clipboard_get()
        except tk.TclError:
            return "break"
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
        data = self.text.get("1.0", tk.END).strip()
        return "" if self._placeholder_on else data

    def render_html(self) -> str:
        return text_service.auto_format(self.get_raw(), mode=self.mode)


# alias legacy compat
MultiTextField = PlaceholderMultiTextField

# ---------------------------------------------------------------------------
# SortableImageRepeaterField – con Drag & Drop
# ---------------------------------------------------------------------------


class SortableImageRepeaterField(ttk.Frame):
    """Repeater lista immagini con validazione URL, riordino e Drag-&-Drop."""

    def __init__(self, master: tk.Misc, cols: int = DEFAULT_COLS, **kw):
        super().__init__(master, **kw)
        self.cols = cols
        self._rows: List[ttk.Frame] = []
        self._build_ui()

    # ------------------------------------------------------------------ UI

    def _build_ui(self):
        btn_add = ttk.Button(self, text="+ Add", command=self._on_add_click)
        btn_add.pack(anchor="w")
        self._container = ttk.Frame(self)
        self._container.pack(fill="both", expand=True)

        # Registrazione DnD solo se libreria presente
        if HAS_DND and DND_FILES:
            self._container.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
            self._container.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]

    # ------------------------------------------------------------------ events / actions

    # bottoncino "+"
    def _on_add_click(self):
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp"), ("All", "*.*")]
        )
        if path:
            self._add_row(path)

    # drag-and-drop da Finder/Explorer
    def _on_drop(self, event):  # type: ignore[no-self-use]
        paths = _split_dnd_event_data(event.data)
        for p in paths:
            self._add_row(p)

    def _add_row(self, url: str = ""):
        row_frame = ttk.Frame(self._container)
        entry = ttk.Entry(row_frame, width=60)
        entry.insert(0, url)
        entry.pack(side="left", fill="x", expand=True)
        ttk.Button(
            row_frame, text="↑", width=2, command=lambda: self._move(row_frame, -1)
        ).pack(side="left")
        ttk.Button(
            row_frame, text="↓", width=2, command=lambda: self._move(row_frame, +1)
        ).pack(side="left")
        ttk.Button(
            row_frame, text="✕", width=2, command=lambda: self._delete(row_frame)
        ).pack(side="left")
        entry.bind("<FocusOut>", lambda e, ent=entry: self._validate(ent))
        self._rows.append(row_frame)
        row_frame.pack(fill="x", pady=2)

    def _move(self, row: ttk.Frame, delta: int):
        idx = self._rows.index(row)
        new_idx = max(0, min(len(self._rows) - 1, idx + delta))
        if new_idx == idx:
            return
        self._rows.pop(idx)
        self._rows.insert(new_idx, row)
        for r in self._rows:
            r.pack_forget()
            r.pack(fill="x", pady=2)

    def _delete(self, row: ttk.Frame):
        self._rows.remove(row)
        row.destroy()

    # ------------------------------------------------------------------ validators

    def _validate(self, entry: ttk.Entry):
        try:
            image_service.validate_url(entry.get().strip())
            _apply_border(entry, ok=True)
        except Exception:  # noqa: BLE001 – bordo rosso su qualunque fail
            _apply_border(entry, ok=False)

    # ------------------------------------------------------------------ public API

    def get_urls(self) -> List[str]:
        return [row.winfo_children()[0].get().strip() for row in self._rows]


# ---------------------------------------------------------------------------
# Utility per parsing stringhe DnD
# ---------------------------------------------------------------------------


def _split_dnd_event_data(data: str | bytes | None) -> Sequence[str]:
    """Converte la stringa grezza di ``<<Drop>>`` in una lista path/URL."""
    if not data:
        return []
    if isinstance(data, bytes):  # sul vecchio Tcl arriva bytes
        data = data.decode()
    # Gestisce path con spazi racchiusi da {}
    out: List[str] = []
    token: str = ""
    in_brace = False
    for char in data:
        if char == "{":
            in_brace = True
            token = ""
        elif char == "}":
            in_brace = False
            out.append(token)
            token = ""
        elif char == " " and not in_brace:
            if token:
                out.append(token)
                token = ""
        else:
            token += char
    if token:
        out.append(token)
    return [os.path.expanduser(p) for p in out]
