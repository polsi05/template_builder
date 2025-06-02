from __future__ import annotations

import importlib
import os
import sys
import types
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

# Optional safe imports for GUI modules and services
def _safe(name: str) -> types.ModuleType:
    try:
        return importlib.import_module(name)
    except Exception:
        return types.ModuleType(f"_stub_{name.replace('.', '_')}")

_tk          = _safe("tkinter")
_ttk         = _safe("tkinter.ttk")
_widgets_mod = _safe("template_builder.widgets")
_services    = _safe("template_builder.services.storage")
_stepimg_mod = _safe("template_builder.step_image")      # ⇦ NUOVO
_preview_mod = _safe("template_builder.infrastructure.preview_engine")
_ui_utils    = _safe("template_builder.infrastructure.ui_utils")

tk  = _tk  if hasattr(_tk, "Tk")   else None
ttk = _ttk if hasattr(_ttk, "Frame") else None
PlaceholderEntry          = getattr(_widgets_mod, "PlaceholderEntry", object)
PlaceholderMultiTextField = getattr(_widgets_mod, "PlaceholderMultiTextField", object)
PlaceholderSpinbox        = getattr(_widgets_mod, "PlaceholderSpinbox", object)
SortableImageRepeaterField= getattr(_widgets_mod, "SortableImageRepeaterField", object)
UndoRedoStack             = getattr(_services, "UndoRedoStack", lambda: None)
quick_save_fn             = getattr(_services, "quick_save",   lambda *_: None)
load_recipe_fn            = getattr(_services, "load_recipe",  lambda *_: {})
export_html_fn            = getattr(_services, "export_html",  None)
PreviewEngine             = getattr(_preview_mod, "PreviewEngine", None)
bind_mousewheel           = getattr(_ui_utils, "bind_mousewheel", lambda w: None)
show_info    = getattr(_ui_utils, "show_info",    lambda *a, **k: None)
show_warning = getattr(_ui_utils, "show_warning", lambda *a, **k: None)
show_error   = getattr(_ui_utils, "show_error",   lambda *a, **k: None)
styled_option_menu = getattr(_ui_utils, "styled_option_menu", None)
styled_spinbox     = getattr(_ui_utils, "styled_spinbox", None)
StyledText         = getattr(_ui_utils, "StyledText", None)
bind_steps_fn = getattr(_stepimg_mod, "bind_steps", None)   # ⇦ NUOVO

# Directories for templates and exports (ensure existence)
_BASE_DIR        = Path(__file__).resolve().parent
TEMPLATE_FOLDER  = _BASE_DIR / "templates"
EXPORT_FOLDER    = _BASE_DIR / "export"
for p in (TEMPLATE_FOLDER, EXPORT_FOLDER):
    try:
        p.mkdir(exist_ok=True, parents=True)
    except Exception:
        pass

# Import text service for placeholder parsing and formatting
_text_mod = _safe("template_builder.services.text")
extract_placeholders_fn = getattr(_text_mod, "extract_placeholders", lambda src: set())
smart_paste_fn          = getattr(_text_mod, "smart_paste", lambda raw: [raw] if isinstance(raw, str) else [str(x) for x in raw])

class TemplateBuilderApp:
    """Modern, modular controller for Template Builder."""
    _SHORTCUTS: List[Tuple[str, str]] = [
        ("<Control-s>", "quick_save"),
        ("<Control-z>", "edit_undo"),
        ("<Control-y>", "edit_redo"),
        ("<Command-s>", "quick_save"),   # macOS
        ("<Command-z>", "edit_undo"),
        ("<Command-y>", "edit_redo"),
    ]

    def __init__(self, *, enable_gui: bool | None = None) -> None:
        self.enable_gui = self._display_available() if enable_gui is None else enable_gui
        self.root = tk.Tk() if self.enable_gui and tk else None
        self._undo = UndoRedoStack()
        self._state: Dict[str, Any] = {}
        # Dynamic fields and image lists
        self.fields: Dict[str, Any] = {}
        self.img_desc = self.img_rec = self.img_step = self.img_other = None
        self.preview_engine = None
        # Image columns variables
        self.cols_desc = None
        self.cols_rec = None

        if self.root:
            # Apply dark theme if available
            try:
                from ttkbootstrap import Style
                Style('darkly')
            except Exception:
                pass
            # Build UI components
            self._build_ui()
            self._build_menu()
            self._bind_global_shortcuts()
            # Load templates and auto-select first
            self._load_templates()

    def quick_save(self, *_: Any) -> None:
        """Save current state to history (JSON)."""
        quick_save_fn(self._state)

    def edit_undo(self, *_: Any) -> None:
        """Alias for undo (for menu/shortcuts)."""
        self.undo()

    def edit_redo(self, *_: Any) -> None:
        """Alias for redo (for menu/shortcuts)."""
        self.redo()

    def undo(self, *_: Any) -> None:
        new_state = self._undo.undo()
        if new_state is not None:
            self._state = new_state
            self._apply_state_to_widgets()
            self.update_preview()

    def redo(self, *_: Any) -> None:
        new_state = self._undo.redo()
        if new_state is not None:
            self._state = new_state
            self._apply_state_to_widgets()
            self.update_preview()

    def load_recipe(self, path: os.PathLike | str) -> None:
        """Load a saved recipe (JSON state file)."""
        try:
            self._state = load_recipe_fn(path)
            self._undo.push(self._state)
            self._apply_state_to_widgets()
            self.update_preview()
        except (FileNotFoundError, OSError, ValueError, TypeError):
            self._state = {}

    def update_preview(self) -> None:
        """Render current state into preview (no-op if head-less)."""
        if hasattr(self, "preview_engine") and self.preview_engine:
            html: Optional[str] = None
            # Use Jinja engine if available and template loaded
            if export_html_fn and getattr(self, "template_path", None):
                try:
                    html = export_html_fn(self._collect(), self.template_path)
                except Exception:
                    html = None
            if html is None:
                # Fallback to simple Title+Body HTML (or placeholder if none)
                html = self._render_html() or "<!-- Preview not available -->"
            self.preview_engine.render(html)

    def audit_placeholders(self) -> List[str]:
        """Audit segnaposti sul template grezzo e mostra i risultati."""
        # estrai segnaposti dal template sorgente
        placeholders = set()
        if getattr(self, "template_src", None):
            placeholders = set(extract_placeholders_fn(self.template_src))

        # individua i gruppi immagini (gruppi con SRC+ALT)
        img_grps = {
            ph[:-4]
            for ph in placeholders
            if ph.endswith("_SRC") and f"{ph[:-4]}_ALT" in placeholders
        }

        # suddividi i gruppi nelle categorie (solo per compatibilità futura)
        desc_groups  = {g for g in img_grps if "DESC"   in g.upper()}
        rec_groups   = {g for g in img_grps if "REC"    in g.upper()}
        other_groups = img_grps - desc_groups - rec_groups

        state_keys = set(self._state.keys())
        audit_lines: List[str] = []
        for ph in sorted(placeholders):
            grp = ph.rsplit("_", 1)[0]
            # ph esplicito o gruppo (SRC/ALT) considerato coperto
            handled = (
                ph in state_keys
                or grp in desc_groups
                or grp in rec_groups
                or grp in other_groups
            )
            symbol = "✅" if handled else "❌"
            audit_lines.append(f"{symbol} {ph}")

        if self.enable_gui and self.root:
            msg = f"Audit placeholder per '{self.template_var.get()}':\n" + "\n".join(audit_lines)
            show_info("Verifica segnaposti", msg)

        return audit_lines

    @staticmethod
    def _display_available() -> bool:
        # Treat Windows/macOS as always GUI-available; on Linux require $DISPLAY
        if sys.platform.startswith("win") or sys.platform == "darwin":
            return True
        return bool(os.environ.get("DISPLAY"))

    def _build_ui(self) -> None:
        """Construct main UI layout (notebook, controls, preview tab)."""
        assert self.root is not None and ttk
        self.root.title("Template Builder 3")
        self.root.geometry("1200x780")
        # Notebook for tabs
        self.nb = ttk.Notebook(self.root)
        self.nb.pack(fill="both", expand=True)
        bind_mousewheel(self.nb)
        # Top bar for template selection and save
        top = ttk.Frame(self.root); top.pack(fill="x", padx=8, pady=(4, 0))
        ttk.Label(top, text="Template:").pack(side="left")
        self.template_var = getattr(_tk, "StringVar", lambda *a, **k: None)()
        if callable(styled_option_menu):
            self.cbo = styled_option_menu(top, self.template_var, [])
        else:
            try:
                self.cbo = _tk.OptionMenu(top, self.template_var, "")
            except Exception:
                self.cbo = ttk.Combobox(top, textvariable=self.template_var, values=[])
        try:
            self.cbo.pack(side="left", padx=6)
        except Exception:
            pass
        ttk.Button(top, text="💾 Salva", command=self.quick_save).pack(side="right")
        # Status bar and detail toggle
        status_bar = ttk.Frame(self.root); status_bar.pack(fill="x", side="bottom")
        self.status = ttk.Label(status_bar, text="Ready", anchor="w")
        self.status.pack(side="left", fill="x", expand=True, padx=4)
        ttk.Button(status_bar, text="Dettagli", command=self._toggle_details).pack(side="right", padx=4)
        self.detail_frame = ttk.Frame(self.root)
        self.detail_label = ttk.Label(self.detail_frame, text="", anchor="w", justify="left", wraplength=1000)

    def _build_menu(self) -> None:
        """Add Edit menu with Undo/Redo (GUI only)."""
        if not self.enable_gui or not self.root or not tk:
            return
        menubar = tk.Menu(self.root)
        edit_menu = tk.Menu(menubar, tearoff=False)
        edit_menu.add_command(label="Undo", accelerator="Ctrl+Z", command=self.edit_undo)
        edit_menu.add_command(label="Redo", accelerator="Ctrl+Y", command=self.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Audit Segnaposti", accelerator="F11",
                              command=self.audit_placeholders)
        self.root.bind_all("<F11>", lambda e: self.audit_placeholders(), add="+")
        menubar.add_cascade(label="Edit", menu=edit_menu)
        self.root.config(menu=menubar)
        self._menu_edit = edit_menu

    def _bind_global_shortcuts(self) -> None:
        if not self.root:
            return
        for seq, handler in self._SHORTCUTS:
            cb = getattr(self, handler, None)
            if callable(cb):
                self.root.bind_all(seq, cb, add="+")

    def _load_templates(self) -> None:
        """Populate template dropdown and load the first template."""
        if not hasattr(self, "template_var"):
            return
        try:
            files = sorted(p.name for p in TEMPLATE_FOLDER.glob("*.html"))
        except Exception:
            files = []
        # Update dropdown/combobox options
        try:
            menu_widget = self.cbo["menu"]
        except Exception:
            menu_widget = None
        if menu_widget:
            menu_widget.delete(0, "end")
            for f in files:
                menu_widget.add_command(label=f, command=lambda v=f: self.template_var.set(v))
        else:
            if hasattr(self.cbo, "configure"):
                try:
                    self.cbo.configure(values=files)
                except Exception:
                    pass
        if files:
            # Reload template on selection change
            try:
                self.template_var.trace_add("write", lambda *_: self.reload_template())
            except Exception:
                try:  # fallback for older tkinter
                    self.template_var.trace("w", lambda *_: self.reload_template())
                except Exception:
                    pass
            self.template_var.set(files[0])
        else:
            self.status.config(text="Nessun template trovato", foreground="#d9534f")
    def reload_template(self) -> None:
        """Load the selected template file and rebuild UI fields."""
        # Clear existing tabs and state
        for tab_id in list(self.nb.tabs()):
            self.nb.forget(tab_id)
        self.fields.clear()
        self.img_desc = self.img_rec = self.img_step = self.img_other = None
        self.preview_engine = None

        template_name = self.template_var.get()
        if not template_name:
            return
        tpl_path = TEMPLATE_FOLDER / template_name
        if not tpl_path.exists():
            show_error("Errore", f"Template '{template_name}' non trovato")
            return
        self.template_path = tpl_path
        try:
            template_src = tpl_path.read_text(encoding="utf-8")
        except Exception as e:
            show_error("Errore", f"Impossibile leggere il template: {e}")
            return
        placeholders = extract_placeholders_fn(template_src)
        if not isinstance(placeholders, set):
            placeholders = set(placeholders)

        # Identify image placeholder groups (with both _SRC and _ALT)
        img_groups = {
            tag[:-4] for tag in placeholders
            if tag.endswith("_SRC") and f"{tag[:-4]}_ALT" in placeholders
        }
        desc_groups = sorted(g for g in img_groups if "DESC" in g.upper())
        rec_groups  = sorted(g for g in img_groups if any(r in g.upper() for r in ("REC", "RECIPE")))
        other_groups= sorted(set(img_groups) - set(desc_groups) - set(rec_groups))

        # Create tabs for fields
        prod_tab   = self._make_scrollable(self._add_tab("Product"))
        recipe_tab = self._make_scrollable(self._add_tab("Recipe"))
        other_tab  = self._make_scrollable(self._add_tab("Other"))
        images_tab = self._make_scrollable(self._add_tab("Images"))

        # Create input fields for each non-image placeholder
        for key in sorted(placeholders):
            if key.endswith("_SRC") or key.endswith("_ALT") or key in self.fields:
                continue
            if key.startswith(("TITLE", "PROD")) or "DESC" in key.upper():
                parent, mode = prod_tab, "p"
            elif key.startswith(("RECIPE", "STEP", "TIME", "INGREDIENT")):
                parent, mode = recipe_tab, "ul"
            else:
                parent, mode = other_tab, "p"
            ttk.Label(parent, text=key).pack(anchor="w", padx=6, pady=2)
            fld = (PlaceholderMultiTextField(parent, placeholder=f"{{{{{key}}}}}", mode=mode, on_change=self.update_preview)
                   if PlaceholderMultiTextField is not object else ttk.Entry(parent))
            fld.pack(fill="x", padx=6, pady=(0, 4))
            self.fields[key] = fld

        # Hero image (single)
        lf_hero = ttk.LabelFrame(images_tab, text="Hero Image")
        lf_hero.pack(fill="x", padx=6, pady=4)
        e_hero_src = (PlaceholderEntry(lf_hero, placeholder="URL immagine hero")
                      if PlaceholderEntry is not object else ttk.Entry(lf_hero))
        e_hero_src.pack(fill="x", padx=6, pady=2)
        e_hero_alt = (PlaceholderEntry(lf_hero, placeholder="Testo alternativo hero")
                      if PlaceholderEntry is not object else ttk.Entry(lf_hero))
        e_hero_alt.pack(fill="x", padx=6, pady=2)
        for w in (e_hero_src, e_hero_alt):
            if not hasattr(w, "render_html"):
                w.render_html = lambda w=w: w.get().strip()
        self.fields["HERO_IMAGE_SRC"] = e_hero_src
        self.fields["HERO_IMAGE_ALT"] = e_hero_alt

        # Image repeater fields
        lf_desc = ttk.LabelFrame(images_tab, text="Description Images")
        lf_desc.pack(fill="x", padx=6, pady=4)
        self.img_desc = SortableImageRepeaterField(lf_desc) if SortableImageRepeaterField is not object else ttk.Frame(lf_desc)
        self.img_desc.pack(fill="x", padx=6, pady=(0, 4))
        for grp in desc_groups:
            try:
                add = getattr(self.img_desc, "_add_row", None)
                if callable(add):
                    add(f"{{{{{grp}_SRC}}}}")
            except Exception:
                pass

        lf_rec = ttk.LabelFrame(images_tab, text="Recipe Images")
        lf_rec.pack(fill="x", padx=6, pady=4)
        self.img_rec = SortableImageRepeaterField(lf_rec) if SortableImageRepeaterField is not object else ttk.Frame(lf_rec)
        self.img_rec.pack(fill="x", padx=6, pady=(0, 4))
        for grp in rec_groups:
            try:
                add = getattr(self.img_rec, "_add_row", None)
                if callable(add):
                    add(f"{{{{{grp}_SRC}}}}")
            except Exception:
                pass

        lf_step = ttk.LabelFrame(images_tab, text="Step Images")
        lf_step.pack(fill="x", padx=6, pady=4)
        self.img_step = SortableImageRepeaterField(lf_step) if SortableImageRepeaterField is not object else ttk.Frame(lf_step)
        self.img_step.pack(fill="x", padx=6, pady=(0, 4))
        for n in range(1, 4):
            try:
                add = getattr(self.img_step, "_add_row", None)
                if callable(add):
                    add(f"{{{{STEP{n}_IMG_SRC}}}}")
            except Exception:
                pass

        if other_groups:
            lf_other = ttk.LabelFrame(images_tab, text="Other Images")
            lf_other.pack(fill="x", padx=6, pady=4)
            self.img_other = SortableImageRepeaterField(lf_other) if SortableImageRepeaterField is not object else ttk.Frame(lf_other)
            self.img_other.pack(fill="x", padx=6, pady=(0, 4))
            for grp in other_groups:
                try:
                    add = getattr(self.img_other, "_add_row", None)
                    if callable(add):
                        add(f"{{{{{grp}_SRC}}}}")
                except Exception:
                    pass

        # Image columns controls
        ctrl = ttk.Frame(images_tab); ctrl.pack(fill="x", pady=6)
        ttk.Label(ctrl, text="Colonne Descrizione:").pack(side="left", padx=(0, 4))
        self.cols_desc = getattr(_tk, "IntVar", lambda **kw: type("IVar", (), {"get": (lambda self=0: 1), "set": (lambda *a, **k: None)}))()
        try: self.cols_desc.set(2)
        except Exception: pass
        spin_d = (styled_spinbox(ctrl, from_=1, to=4, textvariable=self.cols_desc, command=self.update_preview, width=3)
                  if callable(styled_spinbox) else ttk.Spinbox(ctrl, from_=1, to=4, textvariable=self.cols_desc, width=3))
        spin_d.pack(side="left")
        ttk.Label(ctrl, text="  Colonne Ricetta:").pack(side="left", padx=(12, 4))
        self.cols_rec = getattr(_tk, "IntVar", lambda **kw: type("IVar", (), {"get": (lambda self=0: 1), "set": (lambda *a, **k: None)}))()
        try: self.cols_rec.set(1)
        except Exception: pass
        spin_r = (styled_spinbox(ctrl, from_=1, to=4, textvariable=self.cols_rec, command=self.update_preview, width=3)
                  if callable(styled_spinbox) else ttk.Spinbox(ctrl, from_=1, to=4, textvariable=self.cols_rec, width=3))
        spin_r.pack(side="left")

        # Preview tab with live preview
        prev_frame = self._add_tab("Preview")
        if PreviewEngine:
            self.preview_engine = PreviewEngine(prev_frame)
            try:
                frame = getattr(self.preview_engine, "frame", None)
                if frame:
                    frame.pack(fill="both", expand=True)
            except Exception:
                pass
        if not self.preview_engine or not getattr(self.preview_engine, "frame", None):
            # Fallback text if no preview engine
            txt = StyledText(prev_frame, wrap="none") if StyledText else None
            if txt:
                txt.insert("1.0", "<Preview non disponibile>")
                txt.pack(fill="both", expand=True)

        # Initial preview update
        self.detail_frame.pack_forget()
        self.update_preview()

    def _add_tab(self, title: str) -> Any:
        frame = ttk.Frame(self.nb)
        self.nb.add(frame, text=title)
        return frame

    def _make_scrollable(self, frame: Any) -> Any:
        wrapper = ttk.Frame(frame); wrapper.pack(fill="both", expand=True)
        canvas = _tk.Canvas(wrapper, highlightthickness=0) if tk else None
        vsb = ttk.Scrollbar(wrapper, orient="vertical", command=canvas.yview) if ttk else None
        if canvas and vsb:
            canvas.configure(yscrollcommand=vsb.set)
            vsb.pack(side="right", fill="y"); canvas.pack(side="left", fill="both", expand=True)
            inner = ttk.Frame(canvas)
            canvas.create_window((0, 0), window=inner, anchor="nw")
            inner.bind("<Configure>", lambda e, c=canvas: c.configure(scrollregion=c.bbox("all")))
            return inner
        return frame

    def _toggle_details(self) -> None:
        if self.detail_frame.winfo_ismapped():
            self.detail_frame.pack_forget()
        else:
            self.detail_frame.pack(fill="x")
            self.detail_label.pack(fill="x", padx=8, pady=2)

    def _apply_state_to_widgets(self) -> None:
        """Sync GUI fields from internal state (no-op if head-less)."""
        if not self.enable_gui or not self.root:
            return
        for key, widget in self.fields.items():
            val = self._state.get(key, "")
            try:
                current = (widget.get_value() if hasattr(widget, "get_value") else
                           widget.get_raw()   if hasattr(widget, "get_raw") else
                           widget.get().strip())
            except Exception:
                current = ""
            if val is None:
                val = ""
            if isinstance(val, list):
                # Skip list types (images, etc.)
                continue
            if val and val != current:
                try:
                    if hasattr(widget, "text"):  # multi-line text widget
                        widget.text.delete("1.0", _tk.END)
                        widget.text.insert("1.0", str(val))
                    else:
                        widget.delete(0, _tk.END)
                        widget.insert(0, str(val))
                except Exception:
                    pass

    def _collect(self) -> Dict[str, Any]:
        """Collect current inputs into context dict."""
        data: Dict[str, Any] = {}
        # Text fields
        for k, w in self.fields.items():
            try:
                if hasattr(w, "render_html"):
                    data[k] = w.render_html()
                elif hasattr(w, "get_value"):
                    data[k] = w.get_value()
                elif hasattr(w, "get_raw"):
                    data[k] = w.get_raw()
                else:
                    data[k] = w.get().strip()
            except Exception:
                data[k] = ""
        # Image lists and columns
        data["IMAGES_DESC"] = (self.img_desc.get_urls()
                               if self.img_desc and hasattr(self.img_desc, "get_urls") else [])
        data["IMAGES_REC"]  = (self.img_rec.get_urls()
                               if self.img_rec and hasattr(self.img_rec, "get_urls") else [])
        data["IMAGES_STEP"] = (self.img_step.get_urls()
                               if self.img_step and hasattr(self.img_step, "get_urls") else [])
        data["COLS_DESC"]   = int(self.cols_desc.get()) if self.cols_desc else 1
        data["COLS_REC"]    = int(self.cols_rec.get()) if self.cols_rec else 1

        # ───────── StepImage binding & ALT placeholder ─────────
        try:
            from template_builder.step_image import bind_steps
            txts = [data.get(f"STEP{i}", "") for i in range(1, 10)]
            steps = bind_steps(txts, data["IMAGES_STEP"])
            data["STEPS"] = [s.to_dict() for s in steps]
            for s in steps:
                data[f"STEP{s.order}_IMG_ALT"] = s.alt
        except Exception:
            # se modulo mancante, ignora (modalità headless)
            pass
        # ───────── StepImage binding & ALT placeholder (Batch-2 F5) ─────────
        if callable(bind_steps_fn):
            try:
                txts  = [self._state.get(f"STEP{i}", "") for i in range(1, 10)]
                images = data["IMAGES_STEP"] or list(self._state.get("IMAGES_STEP", []))
                steps  = bind_steps_fn(txts, images)
                # Serializza in dict (JSON-safe)
                data["STEPS"] = [s.to_dict() for s in steps]
                # Propaga ALT per placeholder legacy
                for s in steps:
                    data[f"STEP{s.order}_IMG_ALT"] = s.alt
            except Exception:
                data["STEPS"] = []
        else:
            data["STEPS"] = []
        # ────────────────────────────────────────────────────────────────────        
        return data

    def _render_html(self) -> Optional[str]:
        """Simple fallback HTML using TITLE/BODY (if present)."""
        title = str(self._state.get("TITLE", "") or "")
        body  = str(self._state.get("BODY", "") or "")
        return f"<h1>{title}</h1>\n{body}" if (title or body) else None

    def __repr__(self) -> str:
        return f"<TemplateBuilderApp gui={self.enable_gui!r} state={len(self._state)} keys>"
    # --------------------------------------------------------- CLI demo
    def _demo() -> None:  # pragma: no cover
        app = TemplateBuilderApp()
        if app.root:
            app.root.mainloop()


    if __name__ == "__main__":  # pragma: no cover
        _demo()
