# template_builder/infrastructure/preview_engine.py
"""
HTML preview pane for **Template Builder**.

Goals
-----
* Drop-in replacement of the legacy ``PreviewEngine`` class.
* Works even when:
    - the optional dependency **tkinterweb** is **missing**;
    - the process runs **head-less** (no X-server / $DISPLAY) – typically on CI.
* Presents a unified API expected by ``builder_core.TemplateBuilderApp``:
    - ``frame`` attribute (Tk container or ``None`` in head-less);
    - ``render(html: str)`` to refresh the view;
    - ``collect_context() -> dict`` stub for future context extraction.

The module never raises on import: every risky import is wrapped in
a fallback stub so that **tests can import it safely with no display**.
"""

from __future__ import annotations

import importlib
import os
import sys
import types
from typing import Any, Dict, Optional

# ----------------------------------------------------------------------------- helpers
def _safe(name: str) -> types.ModuleType:
    """Import *name* or return an empty stub module."""
    try:
        return importlib.import_module(name)
    except Exception:          # pragma: no cover (any failure becomes stub)
        return types.ModuleType(f"_stub_{name.replace('.', '_')}")

def _display_available() -> bool:
    """True if a graphical display is detected (Linux/macOS)."""
    if sys.platform.startswith("win"):
        return True        # Tk works in the current session on Windows
    return bool(os.environ.get("DISPLAY"))

# ----------------------------------------------------------------------------- optional imports
_tk   = _safe("tkinter")
_tkw  = _safe("tkinterweb")          # Third-party HTML widget (optional)
_tksc = _safe("tkinter.scrolledtext")

tk = _tk if hasattr(_tk, "Frame") else None          # type: ignore[assignment]
ScrollableText = getattr(_tksc, "ScrolledText", None)
HtmlFrame      = getattr(_tkw, "HtmlFrame", None)    # provided by tkinterweb

# ----------------------------------------------------------------------------- main class
class PreviewEngine:
    """
    Minimal HTML preview pane.

    Parameters
    ----------
    parent:
        Tk container (e.g. a ``ttk.Notebook``) or *None* when head-less.
    enable_gui:
        Force GUI on/off.  *None* (default) → auto-detect via display env.
    """

    def __init__(self, parent: Optional[Any] = None, *, enable_gui: bool | None = None) -> None:
        self.enable_gui: bool = _display_available() if enable_gui is None else enable_gui
        self.frame: Optional[Any] = None   # Tk container or None

        if self.enable_gui and tk and parent:
            self._build_gui(parent)
        else:
            # head-less – keep API but do nothing
            self._viewer: Optional[Any] = None

    # ------------------------------------------------------------------ public API
    def render(self, html: str) -> None:
        """
        Render *html* in the embedded widget.

        When running head-less or without an HTML widget available, the
        method becomes a safe no-op.
        """
        if not self.enable_gui or not self._viewer:
            return

        try:
            if HtmlFrame and isinstance(self._viewer, HtmlFrame):           # tkinterweb
                self._viewer.set_content(html)
            elif ScrollableText and isinstance(self._viewer, ScrollableText):
                # Plain fallback: dump HTML in a readonly scrolled text.
                self._viewer.config(state="normal")
                self._viewer.delete("1.0", "end")
                self._viewer.insert("1.0", html)
                self._viewer.config(state="disabled")
        except Exception:   # pragma: no cover – never crash the host app
            pass

    # Stub, kept for API parity with legacy code and builder_core
    def collect_context(self) -> Dict[str, Any]:
        """Return extra context extracted from the preview (currently empty)."""
        return {}

    # ------------------------------------------------------------------ internals
    def _build_gui(self, parent: Any) -> None:
        """Instantiate the appropriate viewer widget."""
        self.frame = tk.Frame(parent)    # type: ignore[arg-type]
        self.frame.pack(fill="both", expand=True)

        if HtmlFrame:
            viewer = HtmlFrame(self.frame)               # type: ignore[call-arg]
            viewer.pack(fill="both", expand=True)
            self._viewer = viewer
        elif ScrollableText:
            viewer = ScrollableText(self.frame)
            viewer.pack(fill="both", expand=True)
            viewer.config(state="disabled")
            self._viewer = viewer
        else:
            # Ultimate fallback: empty Frame, no viewer
            self._viewer = None
