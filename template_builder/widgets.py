"""
Widget library per Template Builder.
Mantiene compatibilità con i test originali e integra le estensioni F6/F7:
  - PlaceholderEntry, PlaceholderSpinbox, PlaceholderMultiTextField (alias MultiTextField)
  - SortableImageRepeaterField con supporto ALT
  - HAS_TOOLTIP per test_tooltips.py
"""

from __future__ import annotations
import os
import tkinter as tk
from tkinter import ttk, TclError
from typing import Any, Callable, List, Optional

from .services import text as text_service
from .services import images as image_service

# ──────────────── Drag & Drop opzionale ─────────────────────────
try:
    import tkinterdnd2 as dndlib
    HAS_DND = True
    DND_FILES = dndlib.DND_FILES
except ImportError:
    HAS_DND = False
    DND_FILES = None


def _split_dnd_event_data(data: str) -> list[str]:
    out: list[str] = []
    token = ""
    in_brace = False
    for ch in data:
        if ch == "{":
            in_brace, token = True, ""
        elif ch == "}":
            in_brace = False
            out.append(token)
            token = ""
        elif ch == " " and not in_brace:
            if token:
                out.append(token)
                token = ""
        else:
            token += ch
    if token:
        out.append(token)
    return [os.path.expanduser(p) for p in out]

# ──────────────── Tooltip opzionale ──────────────────────────────
try:
    from .infrastructure.ui_utils import _Tooltip
    _TOOLTIP_AVAILABLE = True
except ImportError:
    _TOOLTIP_AVAILABLE = False

# Export del flag HAS_TOOLTIP per i test
HAS_TOOLTIP = _TOOLTIP_AVAILABLE

def _attach_tooltip(widget: tk.Misc, tip: str) -> None:
    if not _TOOLTIP_AVAILABLE or not tip:
        return
    tooltip: Optional[_Tooltip] = None
    def on_enter(evt):
        nonlocal tooltip
        tooltip = _Tooltip(widget, tip)
    def on_leave(evt):
        nonlocal tooltip
        if tooltip:
            tooltip.hide()
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# ──────────────── Border helper ──────────────────────────────────
def _apply_border(widget: tk.Widget, ok: bool) -> None:
    color = "#4caf50" if ok else "#f44336"
    try:
        widget.configure(highlightthickness=1, highlightbackground=color)
    except TclError:
        pass

# ──────────────── PlaceholderEntry ────────────────────────────────
class PlaceholderEntry(tk.Entry):
    """Entry con ghost-text e metodi get_value() e render_html()"""
    def __init__(self, master: tk.Misc, placeholder: str = "", **kw: Any) -> None:
        super().__init__(master, **kw)
        self.placeholder = placeholder
        self.default_fg = self.cget("foreground") or "black"
        self._has_placeholder = False
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _add_placeholder(self, *_: Any) -> None:
        if not self.get():
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self.configure(foreground="grey")
            self._has_placeholder = True

    def _clear_placeholder(self, *_: Any) -> None:
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.configure(foreground=self.default_fg)
            self._has_placeholder = False

    def get_value(self) -> str:
        """Ritorna testo reale o stringa vuota se placeholder"""
        return "" if self._has_placeholder else self.get().strip()

    def render_html(self) -> str:
        """Restituisce HTML in <p> del contenuto (usa auto_format)"""
        return text_service.auto_format(self.get_value(), mode="p")

# ──────────────── PlaceholderSpinbox ─────────────────────────────
class PlaceholderSpinbox(tk.Spinbox):
    """Spinbox con ghost-text e get_value()"""
    def __init__(self, master: tk.Misc, placeholder: str = "", **kw: Any) -> None:
        super().__init__(master, **kw)
        self.placeholder = placeholder
        self.default_fg = self.cget("foreground") or "black"
        self._has_placeholder = False
        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self._add_placeholder()

    def _add_placeholder(self, *_: Any) -> None:
        if not self.get():
            self.delete(0, tk.END)
            self.insert(0, self.placeholder)
            self.configure(foreground="grey")
            self._has_placeholder = True

    def _clear_placeholder(self, *_: Any) -> None:
        if self._has_placeholder:
            self.delete(0, tk.END)
            self.configure(foreground=self.default_fg)
            self._has_placeholder = False

    def get_value(self) -> str:
        """Ritorna valore reale o stringa vuota se placeholder"""
        return "" if self._has_placeholder else self.get().strip()

# ──────────────── PlaceholderMultiTextField ──────────────────────
class PlaceholderMultiTextField(ttk.Frame):
    """
    Campo testo multilinea con placeholder, smart-paste e auto-format.
    I test originali si aspettano:
      - metodo get_raw() che restituisce "" se placeholder è attivo, altrimenti tutto il contenuto
      - metodo render_html() per l’output in HTML
      - get_value() per il testo effettivo (vuoto se placeholder)
    """
    def __init__(
        self,
        master: tk.Misc,
        placeholder: str = "",
        mode: str = "p",
        on_change: Callable[[], None] | None = None,
        **kw: Any,
    ) -> None:
        super().__init__(master, **kw)
        self.placeholder = placeholder
        self.mode = mode
        self.on_change = on_change
        self._has_placeholder = False
        self.text = tk.Text(self, wrap="word", height=5)
        self.scroll = ttk.Scrollbar(self, command=self.text.yview)
        self.text.configure(yscrollcommand=self.scroll.set)
        self.text.pack(side="left", fill="both", expand=True)
        self.scroll.pack(side="right", fill="y")
        self.text.bind("<FocusIn>", self._clear_placeholder, add="+")
        self.text.bind("<FocusOut>", self._add_placeholder, add="+")
        self.text.bind("<KeyRelease>", lambda e: self.on_change() if self.on_change else None, add="+")
        self.text.bind("<Control-v>", self._on_paste, add="+")
        self.text.bind("<Command-v>", self._on_paste, add="+")
        self._add_placeholder()

    def _add_placeholder(self, *_: Any) -> None:
        if not self.text.get("1.0", tk.END).strip():
            self.text.insert("1.0", self.placeholder)
            self.text.configure(foreground="grey")
            self._has_placeholder = True

    def _clear_placeholder(self, *_: Any) -> None:
        if self._has_placeholder:
            self.text.delete("1.0", tk.END)
            self.text.configure(foreground="black")
            self._has_placeholder = False

    def _on_paste(self, event: tk.Event) -> str:
        try:
            content = self.text.selection_get(selection="CLIPBOARD")
        except TclError:
            return ""
        parts = text_service.smart_paste(content)
        if parts:
            self.text.delete("1.0", tk.END)
            joined = "\n".join(parts)
            html_formatted = text_service.auto_format(joined, mode=self.mode)
            self.text.insert("1.0", html_formatted)
            if self.on_change:
                self.on_change()
            return "break"
        return ""

    def get_raw(self) -> str:
        """
        Metodo richiesto dai test originali (test_widgets.py):
        restituisce "" se placeholder è attivo, altrimenti tutto il contenuto
        """
        return "" if self._has_placeholder else self.text.get("1.0", tk.END)

    def get_value(self) -> str:
        """Ritorna testo effettivo o stringa vuota se placeholder"""
        return "" if self._has_placeholder else self.text.get("1.0", tk.END).strip()

    def render_html(self) -> str:
        """Formatta il contenuto in HTML (usa auto_format)"""
        return text_service.auto_format(self.get_value(), mode=self.mode)

# Alias per retrocompatibilità
MultiTextField = PlaceholderMultiTextField

# ──────────────── Classe Row per _rows ───────────────────────────
class Row:
    """
    Contenitore per ogni riga di SortableImageRepeaterField.
    Supporta:
      - row.frame: Frame effettivo
      - row.entry_src: PlaceholderEntry per URL
      - row.entry_alt: PlaceholderEntry per ALT
    Inoltre implementa winfo_children() delegando al frame,
    __iter__ per unpacking, e __getitem__ per index.
    """
    def __init__(self, frame: tk.Frame, entry_src: PlaceholderEntry, entry_alt: PlaceholderEntry):
        self.frame = frame
        self.entry_src = entry_src
        self.entry_alt = entry_alt

    def winfo_children(self):
        return self.frame.winfo_children()

    def __iter__(self):
        return iter((self.frame, self.entry_src, self.entry_alt))

    def __getitem__(self, idx: int):
        return (self.frame, self.entry_src, self.entry_alt)[idx]

# ──────────────── SortableImageRepeaterField ────────────────────
class SortableImageRepeaterField(ttk.Frame):
    """
    Gestisce una lista ordinabile di righe, ciascuna con due Entry: URL immagine e ALT text.
    Ora _rows contiene istanze di Row.
    Espone:
      - get_urls() -> List[str]
      - get_alts() -> List[str]
      - validazione: se URL e ALT validi, bordi verdi, altrimenti rossi
    """
    def __init__(self, master: tk.Misc, **kw: Any) -> None:
        super().__init__(master, **kw)
        self._rows: List[Row] = []
        self.enable_alt = True  # Feature toggle per ALT
        if HAS_DND and DND_FILES:
            try:
                self.drop_target_register(DND_FILES)  # type: ignore[attr-defined]
                self.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]
            except TclError:
                pass

    def _on_drop(self, event: Any) -> None:
        for p in _split_dnd_event_data(event.data):
            self._add_row(p, "")

    def _add_row(self, src: str = "", alt: str = "") -> None:
        """
        Aggiunge una riga:
          - un Frame contenente due Entry (URL e ALT) e tre bottoni ↑, ↓, ✕
        """
        row_frame = ttk.Frame(self)
        entry_src = PlaceholderEntry(row_frame, placeholder=src)
        if src:
            entry_src._has_placeholder = False
            entry_src.delete(0, tk.END)
            entry_src.insert(0, src)
        entry_src.pack(side="left", fill="x", expand=True, padx=2)

        entry_alt = PlaceholderEntry(row_frame, placeholder=alt)
        if alt:
            entry_alt._has_placeholder = False
            entry_alt.delete(0, tk.END)
            entry_alt.insert(0, alt)
        entry_alt.pack(side="left", fill="x", expand=True, padx=2)

        btn_up = ttk.Button(row_frame, text="↑", width=2, command=lambda r=row_frame: self._move_row(r, -1))
        btn_up.pack(side="left")
        btn_down = ttk.Button(row_frame, text="↓", width=2, command=lambda r=row_frame: self._move_row(r, +1))
        btn_down.pack(side="left")
        btn_del = ttk.Button(row_frame, text="✕", width=2, command=lambda r=row_frame: self._del_row(r))
        btn_del.pack(side="left")

        entry_src.bind(
            "<FocusOut>",
            lambda e, es=entry_src, ea=entry_alt: self._validate(es, ea),
            add="+"
        )
        entry_alt.bind(
            "<FocusOut>",
            lambda e, es=entry_src, ea=entry_alt: self._validate(es, ea),
            add="+"
        )

        row_frame.pack(fill="x", pady=2)
        self._rows.append(Row(row_frame, entry_src, entry_alt))

    def _move_row(self, row_frame_or_row: tk.Frame | Row, direction: int) -> None:
        """
        Sposta la riga di `direction` (-1 su su, +1 giù).
        Accetta sia Row sia Frame.
        """
        # Se passo un'istanza di Row, ricavo il frame interno
        if isinstance(row_frame_or_row, Row):
            target_frame = row_frame_or_row.frame
        else:
            target_frame = row_frame_or_row
        idx = None
        for i, row in enumerate(self._rows):
            if row.frame is target_frame:
                idx = i
                break
        if idx is None:
            return
        new_idx = idx + direction
        if new_idx < 0 or new_idx >= len(self._rows):
            return
        self._rows[idx], self._rows[new_idx] = self._rows[new_idx], self._rows[idx]
        for row in self._rows:
            row.frame.pack_forget()
        for row in self._rows:
            row.frame.pack(fill="x", pady=2)

    def _del_row(self, row_frame_or_row: tk.Frame | Row) -> None:
        """
        Rimuove la riga (e il Frame corrispondente) da self._rows.
        Accetta sia Row sia Frame.
        """
        if isinstance(row_frame_or_row, Row):
            target_frame = row_frame_or_row.frame
        else:
            target_frame = row_frame_or_row
        idx = None
        for i, row in enumerate(self._rows):
            if row.frame is target_frame:
                idx = i
                break
        if idx is None:
            return
        row = self._rows[idx]
        row.frame.destroy()
        del self._rows[idx]

    def _validate(self, entry_src: PlaceholderEntry, entry_alt: PlaceholderEntry) -> None:
        url = entry_src.get_value()
        alt_val = entry_alt.get_value()
        ok = True
        if url:
            try:
                image_service.validate_url(url)
            except Exception:
                ok = False
            if not alt_val:
                ok = False
        _apply_border(entry_src, ok)
        _apply_border(entry_alt, ok)

    def get_urls(self) -> List[str]:
        return [row.entry_src.get_value() for row in self._rows]

    def get_alts(self) -> List[str]:
        return [row.entry_alt.get_value() for row in self._rows]