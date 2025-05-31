from __future__ import annotations
import os
import tkinter as tk
from typing import Any, Callable, List, Sequence, Optional

# Servizi del package
from .services import text as text_service
from .services import images as image_service

# ───────────── Importazioni opzionali e setup head-less ─────────────
try:
    import tkinter as tk
    from tkinter import ttk, filedialog, TclError, Toplevel
except ImportError:
    # Fallback: definisce stub se Tkinter non disponibile (modalità head-less)
    tk = None
    import types
    # Dummy Tkinter components
    class DummyFrame:
        def __init__(self, *args, **kwargs): pass
        def pack(self, *args, **kwargs): pass
        def pack_forget(self, *args, **kwargs): pass
        def destroy(self, *args, **kwargs): pass
    class DummyButton:
        def __init__(self, *args, **kwargs): pass
        def pack(self, *args, **kwargs): pass
    class DummyCombobox:
        def __init__(self, *args, **kwargs): pass
    ttk = types.SimpleNamespace(Frame=DummyFrame, Button=DummyButton, Combobox=DummyCombobox)
    filedialog = types.SimpleNamespace(askopenfilename=lambda *args, **kwargs: "")
    class DummyTclError(Exception):
        pass
    TclError = DummyTclError
    Toplevel = None

# Drag & Drop opzionale
if tk:
    try:
        from tkinterdnd2 import DND_FILES  # type: ignore
        HAS_DND: bool = True
    except ImportError:
        DND_FILES = None  # type: ignore[assignment]
        HAS_DND = False
else:
    DND_FILES = None
    HAS_DND = False

# Tooltip opzionale
if tk:
    # Se Tkinter è disponibile, assumiamo che Toplevel sia importabile
    try:
        from tkinter import Toplevel as _TkTop  # verifica disponibilità
    except Exception:
        _TOOLTIP_AVAILABLE = False
    else:
        _TOOLTIP_AVAILABLE = True
else:
    _TOOLTIP_AVAILABLE = False
# Flag richiesto dai test per abilitazione tooltip
HAS_TOOLTIP: bool = _TOOLTIP_AVAILABLE

# ───────────── Classe Tooltip interna ────────────────────────────────
if tk and _TOOLTIP_AVAILABLE:
    class _Tooltip:
        def __init__(self, widget: tk.Misc, text: str) -> None:
            self.win = Toplevel(widget)  # finestra indipendente
            self.win.wm_overrideredirect(True)
            self.win.attributes("-topmost", True)
            label = tk.Label(self.win, text=text, bg="#ffffe0", relief="solid",
                              borderwidth=1, padx=4, pady=2)
            label.pack()
            x = widget.winfo_pointerx() + 20
            y = widget.winfo_pointery() + 10
            self.win.wm_geometry(f"+{x}+{y}")
        def hide(self) -> None:
            try:
                self.win.destroy()
            except Exception:
                pass
else:
    # Stub Tooltip per modalità head-less (non fa nulla)
    class _Tooltip:
        def __init__(self, widget: Any, text: str) -> None: pass
        def hide(self) -> None: pass

def _attach_tooltip(widget: tk.Misc, tip: str) -> None:
    """Associa un tooltip testuale al widget se disponibile."""
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
            tooltip = None
    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

# ───────────── Bordo colorato per validazione ───────────────────────
def _apply_border(widget: Any, ok: bool) -> None:
    """Applica un bordo verde (ok) o rosso (errore) al widget, se possibile."""
    color = "#4caf50" if ok else "#f44336"
    try:
        widget.configure(highlightthickness=1, highlightbackground=color)
    except Exception:
        # In modalità head-less o widget non Tk, semplicemente ignoriamo
        pass

# ───────────── Definizione dei Widget Placeholder ───────────────────
if tk:
    class PlaceholderEntry(tk.Entry):
        """Entry con testo segnaposto e metodi get_value(), render_html()."""
        def __init__(self, master: tk.Misc, placeholder: str = "", **kw: Any) -> None:
            super().__init__(master, **kw)
            self.placeholder = placeholder
            self.default_fg = self.cget("foreground") or "black"
            self._has_placeholder = False
            self.bind("<FocusIn>", self._clear_placeholder)
            self.bind("<FocusOut>", self._add_placeholder)
            self._add_placeholder()
            # Tooltip contestuale sul placeholder (se disponibile)
            _attach_tooltip(self, text_service.get_field_help(placeholder) or placeholder)
        def _add_placeholder(self, *_: Any) -> None:
            if not self.get():
                self.insert(0, self.placeholder)
                self.configure(foreground="grey")
                self._has_placeholder = True
        def _clear_placeholder(self, *_: Any) -> None:
            if self._has_placeholder:
                self.delete(0, tk.END)
                self.configure(foreground=self.default_fg)
                self._has_placeholder = False
        def get_value(self) -> str:
            """Ritorna il testo reale (stringa vuota se c'è ancora il placeholder)."""
            return "" if self._has_placeholder else self.get().strip()
        def render_html(self) -> str:
            """Formato testo per HTML (paragrafi)."""
            return text_service.auto_format(self.get_value(), mode="p")

    class PlaceholderSpinbox(tk.Spinbox):
        """Spinbox con testo segnaposto e metodo get_value()."""
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
            """Ritorna il valore reale (stringa vuota se c'è il placeholder)."""
            return "" if self._has_placeholder else self.get().strip()

    class PlaceholderMultiTextField(ttk.Frame):
        """
        Text multi-linea con placeholder, smart-paste e render_html().
        Signatura: (master, placeholder, mode, on_change)
        """
        def __init__(
            self, master: tk.Misc,
            placeholder: str,
            mode: str = "p",
            on_change: Optional[Callable[[], None]] = None,
            **kw: Any,
        ) -> None:
            super().__init__(master, **kw)
            self.placeholder = placeholder
            self.mode = mode
            self.on_change = on_change
            self._has_placeholder = False
            # Componenti interni: Text con scrollbar
            self.text = tk.Text(self, wrap="word", height=5)
            self.scroll = ttk.Scrollbar(self, command=self.text.yview)
            self.text.configure(yscrollcommand=self.scroll.set)
            self.text.pack(side="left", fill="both", expand=True)
            self.scroll.pack(side="right", fill="y")
            # Bind eventi per placeholder e modifica testo
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
            """Smart paste: incolla testo formattato su più linee."""
            try:
                raw = self.text.clipboard_get()
            except TclError:
                return "break"
            parts = text_service.smart_paste(raw)
            if parts:
                # Sostituisce tutto il testo con le parti incollate
                self.text.delete("1.0", tk.END)
                for line in parts:
                    self.text.insert(tk.END, line + "\n")
            return "break"
        def get_raw(self) -> str:
            """Ritorna il testo raw (stringa vuota se c'è placeholder)."""
            return "" if self._has_placeholder else self.text.get("1.0", tk.END).strip()
        def render_html(self) -> str:
            """Formatta il testo raw in HTML (<ul>/<p> in base a mode)."""
            return text_service.auto_format(self.get_raw(), mode=self.mode)

    # Alias per retrocompatibilità (nome legacy)
    MultiTextField = PlaceholderMultiTextField

    class SortableImageRepeaterField(ttk.Frame):
        """
        Gestisce una lista di URL di immagini con aggiunta/rimozione/riordino.
        - _add_row(src: str)
        - _move_row(delta: int)
        - _del_row(row)
        - get_urls() -> List[str]
        - Drag&Drop opzionale se HAS_DND True.
        """
        def __init__(self, master: tk.Misc, **kw: Any) -> None:
            super().__init__(master, **kw)
            self._rows: List[ttk.Frame] = []
            # Abilita Drop se supportato
            if HAS_DND and DND_FILES:
                try:
                    self.drop_target_register(DND_FILES)         # type: ignore
                    self.dnd_bind("<<Drop>>", self._on_drop)    # type: ignore
                except TclError:
                    pass
        def _on_drop(self, event):
            for p in _split_dnd_event_data(event.data):
                self._add_row(p)
        def _add_row(self, src: str = "") -> None:
            # Crea una riga con una Entry e tre pulsanti (su/giu/rimuovi)
            row = ttk.Frame(self)
            entry = PlaceholderEntry(row, placeholder=src)
            entry.insert(0, src)
            entry.pack(side="left", fill="x", expand=True, padx=2)
            ttk.Button(row, text="↑", width=2,
                       command=lambda r=row: self._move_row(r, -1)).pack(side="left")
            ttk.Button(row, text="↓", width=2,
                       command=lambda r=row: self._move_row(r, +1)).pack(side="left")
            ttk.Button(row, text="✕", width=2,
                       command=lambda r=row: self._del_row(r)).pack(side="left")
            entry.bind("<FocusOut>", lambda e, ent=entry: self._validate(ent), add="+")
            entry.bind("<KeyRelease>", lambda e, ent=entry: self._debounce_validate(ent), add="+")
            self._rows.append(row)
            row.pack(fill="x", pady=2)
        def _move_row(self, row: ttk.Frame, delta: int) -> None:
            idx = self._rows.index(row)
            new = idx + delta
            if 0 <= new < len(self._rows):
                # Scambia le righe
                self._rows[idx], self._rows[new] = self._rows[new], self._rows[idx]
                for r in self._rows:
                    r.pack_forget()
                    r.pack(fill="x", pady=2)
        def _del_row(self, row: ttk.Frame) -> None:
            row.destroy()
            self._rows.remove(row)
        def _validate(self, entry: tk.Entry) -> None:
            try:
                image_service.validate_url(entry.get().strip())
                _apply_border(entry, ok=True)
            except Exception:
                _apply_border(entry, ok=False)
        def _debounce_validate(self, entry: tk.Entry) -> None:
            # Delay di 300ms per evitare validazioni eccessive durante la digitazione
            if hasattr(entry, "_after_id"):
                entry.after_cancel(entry._after_id)
            entry._after_id = entry.after(300, lambda ent=entry: self._validate(ent))
        def get_urls(self) -> List[str]:
            """Ritorna la lista di URL (stringhe) correntemente inserite."""
            return [row.winfo_children()[0].get_value() for row in self._rows]
else:
    # Definizione di classi placeholder per ambiente head-less (Tkinter assente)
    class PlaceholderEntry:
        def __init__(self, *args, **kwargs): pass
        def insert(self, *args, **kwargs): pass
        def configure(self, *args, **kwargs): pass
        def bind(self, *args, **kwargs): pass
        def get(self) -> str: return ""
        def get_value(self) -> str: return ""
        def pack(self, *args, **kwargs): pass
    class PlaceholderSpinbox:
        def __init__(self, *args, **kwargs): pass
        def insert(self, *args, **kwargs): pass
        def delete(self, *args, **kwargs): pass
        def configure(self, *args, **kwargs): pass
        def bind(self, *args, **kwargs): pass
        def get(self) -> str: return ""
        def get_value(self) -> str: return ""
        def pack(self, *args, **kwargs): pass
    class PlaceholderMultiTextField:
        def __init__(self, *args, **kwargs): pass
        def get_raw(self) -> str: return ""
        def render_html(self) -> str: return ""
    # Alias MultiTextField
    MultiTextField = PlaceholderMultiTextField
    class SortableImageRepeaterField:
        def __init__(self, *args, **kwargs): pass
        def get_urls(self) -> List[str]: return []

# ─────────── Utility: parsing stringa DnD (percorsi) ────────────────
def _split_dnd_event_data(data: str | bytes | None) -> Sequence[str]:
    """Parsa la stringa evento DnD di tkinterdnd2 in lista di path."""
    if not data:
        return []
    if isinstance(data, bytes):
        data = data.decode()
    out, token = [], ""
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
