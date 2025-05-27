# template_builder/widgets.py
"""
Widget library for Template Builder.

🆕  Novità (Issue #5: *Live-Validation*)
---------------------------------------
* Bordo **verde** su campi validi, **rosso** su campi non validi **mentre l'utente digita**.
* Debounce di 300 ms per evitare flicker.
* Funziona in tandem con il Drag & Drop immagini (Issue #4).
* Importabile e testabile in head-less/CI: nessuna finestra viene creata a
  livello di modulo.

Espone:
    - HAS_DND
    - PlaceholderEntry
    - PlaceholderMultiTextField (alias MultiTextField)
    - SortableImageRepeaterField
"""

from __future__ import annotations

from typing import Callable, List, Optional, Sequence
import os
import tkinter as tk
from tkinter import ttk, filedialog, TclError

# ──────────────────────────────────────────────────────────────  opzionale DnD
try:  # pragma: no cover  – la CI non installa tkinterdnd2
    from tkinterdnd2 import DND_FILES, TkinterDnD  # type: ignore
    HAS_DND: bool = True
except Exception:  # noqa: BLE001
    DND_FILES = None  # type: ignore[assignment]
    TkinterDnD = None  # type: ignore[assignment]
    HAS_DND = False

# ──────────────────────────────────────────────────────────────  assets & services
try:
    from .assets import PALETTE  # type: ignore
except Exception:  # stub fallback se docs incompleti
    PALETTE = {"valid": "#4caf50", "error": "#f44336"}

from .services import text as text_service
from .services import images as image_service

__all__ = [
    "HAS_DND",
    "HAS_TOOLTIP",
    "PlaceholderEntry",
    "PlaceholderMultiTextField",
    "MultiTextField",
    "SortableImageRepeaterField",
]

_DEBOUNCE_MS = 300  # intervallo per la validazione live

# ──────────────────────────────────────────────────────────────  Tooltip support
try:  # un semplice import tkinter non crea finestre: sicuro anche in CI
    import tkinter as _tk                                    # type: ignore
    from tkinter import Toplevel as _Toplevel                # type: ignore

    def _tooltip_available() -> bool:
        """True se teoricamente potremmo creare un Toplevel (display permettendo)."""
        # Non chiamiamo Tk() (creerebbe la finestra e fallirebbe in head-less):
        # ci limitiamo a verificare che i simboli esistano.
        return hasattr(_tk, "Misc") and hasattr(_tk, "Toplevel")

    HAS_TOOLTIP: bool = _tooltip_available()

    class _Tooltip:
        """Piccolo balloon che segue il puntatore; distrutto su <Leave>."""

        def __init__(self, widget: "_tk.Misc", text: str) -> None:  # type: ignore[name-defined]
            self.win = _Toplevel(widget)
            self.win.wm_overrideredirect(True)
            self.win.attributes("-topmost", True)  # prima di tutto
            lbl = _tk.Label(
                self.win,
                text=text,
                justify="left",
                bg="#ffffe0",
                relief="solid",
                borderwidth=1,
                padx=4,
                pady=2,
            )
            lbl.pack()
            # posizioniamo accanto al mouse
            x = widget.winfo_pointerx() + 20
            y = widget.winfo_pointery() + 10
            self.win.wm_geometry(f"+{x}+{y}")

        def hide(self):
            if self.win:
                self.win.destroy()
                self.win = None

    def _attach_tooltip(widget: "_tk.Misc", tip: str) -> None:  # type: ignore[name-defined]
        """Bind <Enter>/<Leave> per visualizzare un tooltip stringa *tip*."""
        if not (HAS_TOOLTIP and tip):
            return

        tooltip: "_Tooltip" | None = None                      # noqa: PYI024

        def _enter(_ev):  # noqa: D401
            nonlocal tooltip
            tooltip = _Tooltip(widget, tip)

        def _leave(_ev):  # noqa: D401
            nonlocal tooltip
            if tooltip:
                tooltip.hide()
                tooltip = None

        widget.bind("<Enter>", _enter)
        widget.bind("<Leave>", _leave)

except Exception:  # pragma: no cover – qualsiasi errore ⇒ nessun tooltip
    HAS_TOOLTIP = False

    def _attach_tooltip(*_a, **_kw):  # type: ignore[empty-body]
        """Stub che non fa nulla quando i tooltip non sono disponibili."""
        return

# ──────────────────────────────────────────────────────────────  helpers UI


def _apply_border(widget: tk.Widget, *, ok: bool) -> None:
    """Colora il bordo del widget; ignora ambienti che non supportano l'opzione."""
    try:
        widget.configure(  # type: ignore[arg-type]
            highlightthickness=1,
            highlightbackground=PALETTE.get("valid" if ok else "error", "green" if ok else "red"),
        )
    except TclError:  # opzione non supportata sul widget (es. vecchio ttk)
        pass


# ──────────────────────────────────────────────────────────────  PlaceholderEntry


class PlaceholderEntry(tk.Entry):
    """Entry con placeholder grigio e validazione live."""

    def __init__(self, master: tk.Misc, placeholder: str = "", **kw):
        super().__init__(master, **kw)
        self._placeholder = placeholder
        self._placeholder_on = False
        self._default_fg = self.cget("foreground") or "black"
        self._after_id: Optional[str] = None

        # Bind
        self.bind("<FocusIn>", self._on_focus_in)
        self.bind("<FocusOut>", self._on_focus_out)
        self.bind("<KeyRelease>", self._schedule_validation)

        self._show_placeholder_if_needed()
        # Tooltip sul widget Entry
        _attach_tooltip(self, text_service.get_field_help(placeholder) or placeholder)
        
    # ------------------------------------------------ events
    def _on_focus_in(self, _):
        if self._placeholder_on:
            self.delete(0, tk.END)
            self.configure(foreground=self._default_fg)
            self._placeholder_on = False

    def _on_focus_out(self, _):
        self._show_placeholder_if_needed()

    def _schedule_validation(self, _):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(_DEBOUNCE_MS, self._validate)

    # ------------------------------------------------ helpers
    def _show_placeholder_if_needed(self):
        if not self.get():
            self.insert(0, self._placeholder)
            self.configure(foreground="grey")
            self._placeholder_on = True

    def _validate(self):
        _apply_border(self, ok=bool(self.get_value().strip()))

    # ------------------------------------------------ public
    def get_value(self) -> str:
        return "" if self._placeholder_on else self.get().strip()


# ──────────────────────────────────────────────────────────────  PlaceholderMultiTextField

class PlaceholderMultiTextField(ttk.Frame):
    """Text multiriga con placeholder, smart-paste e validazione live."""

    def __init__(self, master: tk.Misc, *, mode: str = "ul", placeholder: str = "", **kw):
        super().__init__(master, **kw)
        self.mode = mode
        self.text = tk.Text(self, wrap="word", height=6)
        self.text.pack(fill="both", expand=True)

        self._placeholder = placeholder
        self._placeholder_on = False
        self._after_id: Optional[str] = None

        # Bind
        self.text.bind("<FocusIn>", self._focus_in)
        self.text.bind("<FocusOut>", self._focus_out)
        self.text.bind("<Control-v>", self._smart_paste, add="+")
        self.text.bind("<Command-v>", self._smart_paste, add="+")  # macOS
        self.text.bind("<KeyRelease>", self._schedule_validation, add="+")

        self._show_placeholder_if_needed()

    # ------------------------------------------------ events
    def _focus_in(self, _):
        if self._placeholder_on:
            self.text.delete("1.0", tk.END)
            self.text.configure(foreground="black")
            self._placeholder_on = False

    def _focus_out(self, _):
        self._show_placeholder_if_needed()

    def _schedule_validation(self, _):
        if self._after_id:
            self.after_cancel(self._after_id)
        self._after_id = self.after(_DEBOUNCE_MS, self._validate)

    def _smart_paste(self, event):  # noqa: D401 – Tk pattern
        try:
            raw = self.clipboard_get()
        except tk.TclError:
            return "break"
        lines = text_service.smart_paste(raw)
        self.text.insert(tk.INSERT, "\n".join(lines))
        return "break"

    # ------------------------------------------------ helpers
    def _show_placeholder_if_needed(self):
        if not self.text.get("1.0", tk.END).strip():
            self.text.insert("1.0", self._placeholder)
            self.text.configure(foreground="grey")
            self._placeholder_on = True

    def _validate(self):
        _apply_border(self.text, ok=bool(self.get_raw()))

    # ------------------------------------------------ public
    def get_raw(self) -> str:
        return "" if self._placeholder_on else self.text.get("1.0", tk.END).strip()

    def render_html(self) -> str:
        return text_service.auto_format(self.get_raw(), mode=self.mode)


# alias legacy compat
MultiTextField = PlaceholderMultiTextField

# ──────────────────────────────────────────────────────────────  SortableImageRepeaterField

class SortableImageRepeaterField(ttk.Frame):
    """
    Lista di URL immagini con riordino, cancellazione e Drag & Drop.

    Ogni riga è un Entry *live-validated* tramite `image_service.validate_url`.
    """

    def __init__(self, master: tk.Misc, cols: int = 3, **kw):
        super().__init__(master, **kw)
        self.cols = cols
        self._rows: List[ttk.Frame] = []
        self._build_ui()

    # ------------------------------------------------ UI
    def _build_ui(self):
        global HAS_DND                # ← ora è prima di qualunque uso

        btn_add = ttk.Button(self, text="+ Add", command=self._on_add_click)
        btn_add.pack(anchor="w")
        self._container = ttk.Frame(self)
        self._container.pack(fill="both", expand=True)

        if HAS_DND and DND_FILES:
            try:
                self._container.drop_target_register(DND_FILES)      # type: ignore[attr-defined]
                self._container.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]
            except TclError:          # libreria tkdnd mancante → disabilita DnD
                HAS_DND = False

    # ------------------------------------------------ events / actions
    def _on_add_click(self):
        path = filedialog.askopenfilename(
            title="Select image",
            filetypes=[("Images", "*.png *.jpg *.jpeg *.gif *.webp"), ("All", "*.*")]
        )
        if path:
            self._add_row(path)

    def _on_drop(self, event):  # type: ignore[no-self-use]
        for p in _split_dnd_event_data(event.data):
            self._add_row(p)

    def _add_row(self, url: str = ""):
        row = ttk.Frame(self._container)
        entry = tk.Entry(row, width=60)  # tk.Entry per compatibilità highlight
        entry.insert(0, url)
        entry.pack(side="left", fill="x", expand=True)

        ttk.Button(row, text="↑", width=2, command=lambda: self._move(row, -1)).pack(side="left")
        ttk.Button(row, text="↓", width=2, command=lambda: self._move(row, +1)).pack(side="left")
        ttk.Button(row, text="✕", width=2, command=lambda: self._delete(row)).pack(side="left")

        entry.bind("<FocusOut>", lambda e, ent=entry: self._validate(ent))
        entry.bind("<KeyRelease>", lambda e, ent=entry: self._debounce_validate(ent))
        _attach_tooltip(
            entry,
            text_service.get_field_help("IMG_URL")  # chiave standard per URL immagini
            or "URL o percorso immagine supportato",
        )   
        self._rows.append(row)
        row.pack(fill="x", pady=2)

    # ------------------ riordino / cancellazione
    def _move(self, row: ttk.Frame, delta: int):
        idx = self._rows.index(row)
        new = max(0, min(len(self._rows) - 1, idx + delta))
        if new == idx:
            return
        self._rows.pop(idx)
        self._rows.insert(new, row)
        for r in self._rows:
            r.pack_forget()
            r.pack(fill="x", pady=2)

    def _delete(self, row: ttk.Frame):
        self._rows.remove(row)
        row.destroy()

    # ------------------ validazione
    def _validate(self, entry: tk.Entry):
        try:
            image_service.validate_url(entry.get().strip())
            _apply_border(entry, ok=True)
        except Exception:  # noqa: BLE001
            _apply_border(entry, ok=False)

    def _debounce_validate(self, entry: tk.Entry):
        if hasattr(entry, "_after_id") and entry._after_id:  # type: ignore[attr-defined]
            entry.after_cancel(entry._after_id)              # type: ignore[attr-defined]
        entry._after_id = entry.after(_DEBOUNCE_MS, lambda e=entry: self._validate(e))  # type: ignore[attr-defined]

    # ------------------ public API
    def get_urls(self) -> List[str]:
        return [row.winfo_children()[0].get().strip() for row in self._rows]


# ──────────────────────────────────────────────────────────────  utility DnD

def _split_dnd_event_data(data: str | bytes | None) -> Sequence[str]:
    """Parsa la stringa grezza di ``<<Drop>>`` in lista di path/url."""
    if not data:
        return []
    if isinstance(data, bytes):
        data = data.decode()
    out, token, in_brace = [], "", False
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
