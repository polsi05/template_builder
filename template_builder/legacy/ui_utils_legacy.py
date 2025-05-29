# ui_utils.py - complete updated file with render_html added

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as _tk_messagebox
from typing import Callable, List

# Proteggiamo Style() dall’errore Tcl su tcl_platform(threaded)
try:
    from ttkbootstrap import Style
except ImportError:
    Style = None

# Proviamo a importare i dialog di ttkbootstrap per avere messagebox in tema
try:
    from ttkbootstrap.dialogs.dialogs import Messagebox as _TBMessagebox
    _HAS_TB_DIALOG = True
except (ImportError, tk.TclError):
    _HAS_TB_DIALOG = False


def styled_option_menu(master, variable, values, **kwargs):
    style = ttk.Style()
    if Style:
        Style('darkly')
    om = ttk.OptionMenu(master, variable, *(values or []), **kwargs)
    return om


def styled_spinbox(master, from_, to, textvariable, command=None, **kwargs):
    sb = tk.Spinbox(
        master,
        from_=from_,
        to=to,
        textvariable=textvariable,
        command=command,
        **kwargs
    )
    try:
        sb.config(wrap=True)
    except tk.TclError:
        pass
    return sb


def show_info(title: str, message: str):
    if _HAS_TB_DIALOG:
        _TBMessagebox.show_info(title=title, message=message)
    else:
        _tk_messagebox.showinfo(title, message)


def show_warning(title: str, message: str):
    if _HAS_TB_DIALOG:
        _TBMessagebox.show_warning(title=title, message=message)
    else:
        _tk_messagebox.showwarning(title, message)


def show_error(title: str, message: str):
    if _HAS_TB_DIALOG:
        _TBMessagebox.show_error(title=title, message=message)
    else:
        _tk_messagebox.showerror(title, message)


class StyledText(ttk.Frame):
    def __init__(self, master, **kwargs):
        super().__init__(master)
        self.text = tk.Text(self, **kwargs)
        self.vsb = ttk.Scrollbar(self, orient='vertical', command=self.text.yview)
        self.text.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side='right', fill='y')
        self.text.pack(side='left', fill='both', expand=True)

    def get(self, *args):
        return self.text.get(*args)

    def insert(self, *args):
        return self.text.insert(*args)

    def bind(self, *args, **kwargs):
        return self.text.bind(*args, **kwargs)

    def config(self, **kwargs):
        return self.text.config(**kwargs)

    def delete(self, *args):
        return self.text.delete(*args)


class PlaceholderEntry(ttk.Entry):
    def __init__(self, master, placeholder='', **kwargs):
        super().__init__(master, **kwargs)
        self.placeholder = placeholder
        self.default_fg = self.cget('foreground')
        self.bind('<FocusIn>', self._clear_placeholder)
        self.bind('<FocusOut>', self._add_placeholder)
        self._add_placeholder()

    def _clear_placeholder(self, event=None):
        if self.get() == self.placeholder:
            self.delete(0, 'end')
            self.config(foreground=self.default_fg)

    def _add_placeholder(self, event=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self.config(foreground='grey')
        else:
            self.config(foreground=self.default_fg)


# Utility per paste intelligente in PlaceholderMultiTextField
def smart_paste(raw: str) -> List[str]:
    if not raw:
        return []
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if len(lines) == 1 and ';' in lines[0]:
        return [s.strip() for s in lines[0].split(';') if s.strip()]
    return lines


class PlaceholderMultiTextField(StyledText):
    """
    Estende StyledText con placeholder che scompare al focus,
    mantiene smart-paste e on_change binding.
    """
    def __init__(self, master, placeholder: str, mode: str,
                 on_change: Callable[[], None], **kwargs):
        super().__init__(master, **kwargs)
        self.mode = mode
        self.on_change = on_change
        self.placeholder = placeholder
        self.default_fg = self.text.cget('foreground')

        # placeholder focus handlers
        self.text.bind('<FocusIn>', self._clear_placeholder, add='+')
        self.text.bind('<FocusOut>', self._add_placeholder, add='+')

        # smart-paste & change
        self.text.bind('<KeyRelease>', lambda e: self.on_change(), add='+')
        self.text.bind('<Control-v>', self._handle_paste, add='+')
        self.text.bind('<Command-v>', self._handle_paste, add='+')

        # inizializza placeholder
        self._add_placeholder()

    def _clear_placeholder(self, event=None):
        if self.text.get('1.0', 'end').strip() == self.placeholder:
            self.text.delete('1.0', 'end')
            self.text.config(foreground=self.default_fg)

    def _add_placeholder(self, event=None):
        if not self.text.get('1.0', 'end').strip():
            self.text.insert('1.0', self.placeholder)
            self.text.config(foreground='grey')
        else:
            self.text.config(foreground=self.default_fg)

    def _handle_paste(self, event):
        try:
            clip = self.text.clipboard_get()
        except tk.TclError:
            return 'break'
        # rimuove placeholder se presente
        if self.text.get('1.0', 'end').strip() == self.placeholder:
            self.text.delete('1.0', 'end')
        lines = smart_paste(clip)
        if not lines:
            return 'break'
        for i, ln in enumerate(lines):
            self.text.insert(tk.INSERT, ln)
            if i < len(lines) - 1:
                self.text.insert(tk.INSERT, '\n')
        self.on_change()
        return 'break'

    def render_html(self) -> str:
        """
        Restituisce il contenuto del widget per il rendering.
        """
        return self.text.get('1.0', 'end').rstrip()

