# preview_engine.py

import tkinter as tk
from tkinter import ttk
import webbrowser
import tempfile
from ui_utils import StyledText, show_error

# Proviamo a importare HtmlFrame da tkinterweb
try:
    from tkinterweb import HtmlFrame
except ImportError:
    HtmlFrame = None

# Proviamo a importare CEF
try:
    from cefpython3 import cefpython as cef
except ImportError:
    cef = None

class RendererBackend:
    """Base per i motori di rendering."""
    def __init__(self, parent_frame: tk.Frame):
        self.parent_frame = parent_frame

    def setup(self): raise NotImplementedError
    def load(self, html: str): raise NotImplementedError
    def dispose(self): pass

class TkWebRenderer(RendererBackend):
    """Rendering inline con tkinterweb.HtmlFrame."""
    def __init__(self, parent_frame: tk.Frame):
        super().__init__(parent_frame)
        self.html_frame = None

    def setup(self):
        if not HtmlFrame:
            raise RuntimeError("tkinterweb non disponibile")
        self.html_frame = HtmlFrame(self.parent_frame, horizontal_scrollbar="auto")
        self.html_frame.pack(fill="both", expand=True)

    def load(self, html: str):
        self.html_frame.load_html(html)

    def dispose(self):
        if self.html_frame:
            self.html_frame.destroy()
            self.html_frame = None

class CefRenderer(RendererBackend):
    """Rendering con CEF embeddato in Tk."""
    _initialized = False

    def __init__(self, parent_frame: tk.Frame):
        super().__init__(parent_frame)
        self.browser = None

    def setup(self):
        if not cef:
            raise RuntimeError("cefpython3 non disponibile")
        if not CefRenderer._initialized:
            cef.Initialize()
            CefRenderer._initialized = True

        self.parent_frame.update_idletasks()
        handle = self.parent_frame.winfo_id()
        width = self.parent_frame.winfo_width()
        height = self.parent_frame.winfo_height()

        window_info = cef.WindowInfo()
        window_info.SetAsChild(handle, [0, 0, width, height])
        self.browser = cef.CreateBrowserSync(window_info, url="about:blank")
        self.parent_frame.bind("<Configure>", self._on_configure)

    def _on_configure(self, event):
        if self.browser:
            self.browser.SetBounds(0, 0, event.width, event.height)

    def load(self, html: str):
        if self.browser:
            html_full = html
            low = html_full.lstrip().lower()
            if not (low.startswith('<!doctype') or '<html' in low):
                html_full = (
                    "<!DOCTYPE html>"
                    "<html><head><meta charset='utf-8'></head><body>" +
                    html_full +
                    "</body></html>"
                )
            self.browser.GetMainFrame().LoadString(html_full, "about:blank")

    def dispose(self):
        if self.browser:
            self.browser.CloseBrowser(True)
            self.browser = None
        if CefRenderer._initialized:
            cef.Shutdown()
            CefRenderer._initialized = False

class ExternalRenderer(RendererBackend):
    """Fallback: salva HTML in temp file e apre il browser esterno."""
    def __init__(self, parent_frame):
        super().__init__(parent_frame)
        self.button = None
        self._html = ""

    def setup(self):
        self.button = ttk.Button(
            self.parent_frame,
            text="Apri anteprima nel browser",
            command=self._open_in_browser
        )
        self.button.pack(padx=10, pady=10)

    def load(self, html: str):
        self._html = html

    def _open_in_browser(self):
        try:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
            tmp.write(self._html.encode("utf-8"))
            tmp.close()
            webbrowser.open_new_tab(f"file://{tmp.name}")
        except Exception as e:
            show_error("Errore apertura browser", str(e))

    def dispose(self):
        if self.button:
            self.button.destroy()
            self.button = None

class PreviewEngine:
    """
    Gestisce il container di anteprima in due tab
    (HTML Source & Web Preview) e instrada render().
    """
    def __init__(self, parent: tk.Widget):
        self.parent = parent
        self.container = None
        self.source_text = None
        self.renderer = None

    def init_frame(self) -> ttk.Notebook:
        try:
            self.parent.tk.call('set', 'tcl_platform(threaded)', '0')
        except tk.TclError:
            pass

        nb = ttk.Notebook(self.parent)

        tab_src = ttk.Frame(nb)
        self.source_text = StyledText(tab_src, wrap="none")
        self.source_text.pack(fill="both", expand=True)
        self.source_text.config(state="disabled")
        nb.add(tab_src, text="HTML Source")

        tab_web = ttk.Frame(nb)
        nb.add(tab_web, text="Web Preview")

        backend = ("tkinterweb" if HtmlFrame else "cef" if cef else "external")
        try:
            if backend == "tkinterweb":
                self.renderer = TkWebRenderer(tab_web)
            elif backend == "cef":
                self.renderer = CefRenderer(tab_web)
            else:
                self.renderer = ExternalRenderer(tab_web)
            self.renderer.setup()
        except Exception as e:
            msg = str(e)
            if "stubs mechanism" not in msg:
                show_error("Errore configurazione anteprima", msg)
            self.renderer = ExternalRenderer(tab_web)
            self.renderer.setup()

        self.container = nb
        return nb

    def render(self, html: str):
        low = html.lstrip().lower()
        html_full = html
        if not (low.startswith('<!doctype') or '<html' in low):
            html_full = (
                "<!DOCTYPE html>"
                "<html><head><meta charset='utf-8'></head><body>" +
                html_full +
                "</body></html>"
            )
        if self.source_text:
            self.source_text.config(state="normal")
            self.source_text.delete("1.0", "end")
            self.source_text.insert("1.0", html_full)
            self.source_text.config(state="disabled")
        try:
            if self.renderer:
                self.renderer.load(html_full)
        except Exception as e:
            show_error("Errore rendering web", str(e))

    def dispose(self):
        if self.renderer:
            self.renderer.dispose()
        if self.container:
            self.container.destroy()
