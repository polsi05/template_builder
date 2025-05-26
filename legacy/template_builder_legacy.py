from __future__ import annotations
"""
Template Builder 2.3 – core module completo
Con:
- ghost‐placeholder uniforme su tutti i campi immagine e testuali
- move/up/down e delete in ImageRepeaterField
- validazione URL che ignora i placeholder
- supporto a PreviewEngine, quick‐save, smart‐paste, multi‐text formatting, etc.
- Preview tab con sottoviste “HTML Source” e “Web Preview”
"""
import re
import json
import time
import math
from pathlib import Path
from typing import Callable, Dict, List, Tuple, Union

import json

import tkinter as tk
# ---------- PATCH: filtro steps_bind -------------------------------
import jinja2, re
try:
    from jinja2 import pass_context
except ImportError:
    from jinja2 import contextfilter as pass_context  # Jinja 2.x fallback

# ---------- PATCH DEFINITIVO : filtro steps_bind -------------------
import jinja2, re

# decorator compatibile con Jinja 3.x e 2.11
try:
    from jinja2 import pass_context          # Jinja ≥ 3
except ImportError:
    from jinja2 import contextfilter as pass_context  # Jinja 2.11 fallback


@pass_context
def steps_bind(ctx, raw):
    """
    Converte RECIPE_STEPS_TEXT (multilinea) in lista di dict
    e abbina, in ordine, le foto presenti in IMAGES_STEP.

    • IMAGES_STEP può contenere tuple  (src, alt)
      oppure dict   {"src": "...", "alt": "..."}
    • Se mancano foto, lo step mostra solo testo.
    """

    # --- 1. TESTO -> lista -------------------------------------------------
    if not raw:
        lines = []
    else:
        raw = raw.strip()
        # rimuovi eventuali apici singoli/doppi prodotti dal replace letterale
        if raw[:1] in {"'", '"'} and raw[-1:] == raw[:1]:
            raw = raw[1:-1]
        lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]

    # --- 2. FOTO STEP ------------------------------------------------------
    step_imgs = ctx.get("IMAGES_STEP", [])  # lista di tuple OPPURE dict
    import sys, pprint
    pprint.pprint(step_imgs, stream=sys.stderr)

    steps = []
    for i, txt in enumerate(lines):
        src = alt = ""

        if i < len(step_imgs):
            item = step_imgs[i]

            # caso tuple/list -> (src, alt)
            if isinstance(item, (list, tuple)):
                src = item[0]
                alt = item[1] if len(item) > 1 else ""

            # caso dict -> {"src": "...", "alt": "..."}
            elif isinstance(item, dict):
                src = item.get("src", "")
                alt = item.get("alt", "")

        steps.append({"text": txt, "img": src, "alt": alt})

    return steps


# registra il filtro nel dizionario globale
jinja2.defaults.DEFAULT_FILTERS['steps_bind'] = steps_bind
# ---------- END PATCH -----------------------------------------------------

# filtro new-line → <br>  (compatibile con eBay)
import jinja2
jinja2.defaults.DEFAULT_FILTERS['nl2br'] = lambda v: '<br>'.join(x.strip() for x in (v or '').splitlines())

from tkinter import ttk
from jinja2 import Template

from validators import validate_image_url, ImageValidationError
from ui_utils import (
    styled_option_menu,
    styled_spinbox,
    show_info,
    show_warning,
    show_error,
    StyledText,
    PlaceholderEntry,
    PlaceholderMultiTextField,
)

try:
    from preview_engine import PreviewEngine
except ImportError:
    PreviewEngine = None

# -------------------------------------------------------------------
BASE_DIR        = Path(__file__).resolve().parent
TEMPLATE_FOLDER = BASE_DIR / "templates"
EXPORT_FOLDER   = BASE_DIR / "export"
HISTORY_FOLDER  = BASE_DIR / ".history"
for p in (TEMPLATE_FOLDER, EXPORT_FOLDER, HISTORY_FOLDER):
    p.mkdir(exist_ok=True)

# -------------------------------------------------------------------
PLACEHOLDER_REGEX = re.compile(r"\{\{\s*([A-Za-z0-9_-]+)\s*\}\}")

def extract_placeholders(html: str) -> List[str]:
    return sorted(set(PLACEHOLDER_REGEX.findall(html)))

def smart_paste(raw: str) -> List[str]:
    if not raw:
        return []
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    if len(lines) == 1 and ';' in lines[0]:
        return [s.strip() for s in lines[0].split(';') if s.strip()]
    return lines

def auto_format(text: str, mode: str) -> str:
    if not text:
        return ''
    if '<' in text:
        return text
    lines = [ln.strip() for ln in text.splitlines() if ln.strip()]
    if not lines:
        return ''
    if mode == 'ul':
        items = '\n'.join(f'<li>{ln}</li>' for ln in lines)
        return f'<ul>\n{items}\n</ul>'
    if mode == 'p':
        return '\n'.join(f'<p>{ln}</p>' for ln in lines)
    return text

def images_to_html(rows: List[Tuple[str, str]], cols: int) -> str:
    """Render immagini in righe di `cols` colonne; avanzamento centrato."""
    if not rows:
        return ''
    html_lines: List[str] = []
    per = max(1, cols)
    width_pct = int(100 / per) - 1
    for i in range(0, len(rows), per):
        chunk = rows[i:i+per]
        if len(chunk) == per:
            html_lines.append('<div class="img-row">')
            for src, alt in chunk:
                if src:
                    html_lines.append(
                        f"<img src='{src}' alt='{alt}' "
                        f"style='width:{width_pct}%;margin:0.5%;display:inline-block;'>"
                    )
            html_lines.append('</div>')
        else:
            html_lines.append('<div class="img-row single">')
            for src, alt in chunk:
                if src:
                    html_lines.append(
                        f"<img src='{src}' alt='{alt}' "
                        f"style='display:block;margin:0 auto;width:auto;max-width:90%;'>"
                    )
            html_lines.append('</div>')
    return '\n'.join(html_lines)

# -------------------------------------------------------------------
class MultiTextField(tk.Text):
    """
    Multi-line area:
      mode='ul'  → newline → <ul><li>..</li>
      mode='p'   → newline → <p>..</p>
    """
    def __init__(self, master, mode: str, on_change: Callable[[], None], **kwargs):
        super().__init__(master, height=6, width=72, fg="black", **kwargs)
        self.mode = mode
        self.on_change = on_change
        self.configure(insertbackground="black", wrap="word")
        self.text.bind('<KeyRelease>', lambda e: self.on_change(), add='+')
        self.text.bind('<Control-v>', self._handle_paste, add='+')
        self.text.bind('<Command-v>', self._handle_paste, add='+')

    def _handle_paste(self, event):
        try:
            clip = self.text.clipboard_get()
        except tk.TclError:
            return 'break'
        lines = smart_paste(clip)
        if not lines:
            return 'break'
        for i, ln in enumerate(lines):
            self.text.insert(tk.INSERT, ln)
            if i < len(lines) - 1:
                self.text.insert(tk.INSERT, '\n')
        self.on_change()
        return 'break'

    def render_html(self)->str:
        txt=self.get("1.0","end").strip()
        if not txt: return ""
        lines=[ln.strip() for ln in txt.splitlines() if ln.strip()]
        if self.mode=="ul":
            return "<ul>\n" + "\n".join(f"<li>{ln}</li>" for ln in lines) + "\n</ul>"
        if self.mode=="p":
            return "\n".join(f"<p>{ln}</p>" for ln in lines)

class ImageRepeaterField(tk.Frame):
    """
    Ripetitore URL+ALT con:
    - ghost-placeholder uniforme
    - move up/down e delete per ogni riga
    - validazione URL che ignora i placeholder
    """
    def __init__(self, master, on_change: Callable[[], None], **kwargs):
        super().__init__(master, **kwargs)
        self.on_change = on_change
        self.rows: List[tk.Frame] = []
        hdr = tk.Frame(self)
        hdr.pack(fill='x', pady=(0,4))
        ttk.Label(hdr, text='URL', width=50, anchor='w').pack(side='left', padx=2)
        ttk.Label(hdr, text='Alt', width=30, anchor='w').pack(side='left', padx=6)
        ttk.Button(hdr, text='➕ Aggiungi', command=lambda: (self.add_row(), self.on_change())).pack(side='right')

    def _mk_ph_entry(self, master, value: str, width: int, hint: str) -> PlaceholderEntry:
        ph = value or hint
        return PlaceholderEntry(master, placeholder=ph, width=width)

    def add_row(self, src: str = '', alt: str = ''):
        row = tk.Frame(self); row.pack(fill='x', pady=1)
        e_url = self._mk_ph_entry(row, src, width=50, hint="URL immagine")
        e_url.pack(side='left', padx=2)
        e_url.bind('<Control-v>', lambda e, ent=e_url: self._smart_paste_urls(e, ent), add='+')
        e_url.bind('<Command-v>', lambda e, ent=e_url: self._smart_paste_urls(e, ent), add='+')
        e_url.bind('<FocusOut>', lambda e, ent=e_url: self._validate_and_notify(ent), add='+')
        e_alt = self._mk_ph_entry(row, alt, width=30, hint="Testo alternativo")
        e_alt.pack(side='left', padx=6)
        e_alt.bind('<FocusOut>', lambda e, ent=e_alt: self._validate_and_notify(ent), add='+')
        btn_up = ttk.Button(row, text='👆', width=2, command=lambda r=row: (self._move(r, -1), self.on_change()))
        btn_down = ttk.Button(row, text='👇', width=2, command=lambda r=row: (self._move(r, +1), self.on_change()))
        btn_del = ttk.Button(row, text='❌', width=2, command=lambda r=row: (self._del(r), self.on_change()))
        for btn in (btn_up, btn_down, btn_del):
            btn.pack(side='left', padx=2)
        self.rows.append(row)
        self._validate_and_notify(e_url)

    def _smart_paste_urls(self, event, entry):
        try:
            clip = entry.clipboard_get()
        except tk.TclError:
            return 'break'
        urls = smart_paste(clip)
        if not urls:
            return 'break'
        entry.delete(0, 'end'); entry.insert(0, urls[0])
        for u in urls[1:]:
            self.add_row(src=u)
        self.on_change()
        return 'break'

    def _validate_and_notify(self, entry):
        url = entry.get().strip(); ph = entry.placeholder
        if not url or url == ph or PLACEHOLDER_REGEX.fullmatch(url):
            entry.configure(background='white')
        else:
            try:
                validate_image_url(url)
                entry.configure(background='white')
            except ImageValidationError as e:
                entry.configure(background='#ffcccc')
                show_warning('URL immagine non valida', str(e))
        if entry.get().strip() == ph:
            entry.configure(foreground='grey')
        else:
            entry.configure(foreground=entry.default_fg)
        return self.on_change()

    def _del(self, row: tk.Frame):
        row.destroy(); self.rows.remove(row)

    def _move(self, row: tk.Frame, delta: int):
        idx = self.rows.index(row); new = idx + delta
        if 0 <= new < len(self.rows):
            self.rows.pop(idx); self.rows.insert(new, row)
            for r in self.rows:
                r.pack_forget(); r.pack(fill='x', pady=1)

    def get_rows(self) -> List[Tuple[str, str]]:
        return [(r.winfo_children()[0].get().strip(), r.winfo_children()[1].get().strip())
                for r in self.rows]

# -------------------------------------------------------------------
class BuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Template Builder 2.3')
        self.geometry('1200x780')
        self.configure(bg='#222')

        self.cols_desc = tk.IntVar(value=2)
        self.cols_rec  = tk.IntVar(value=1)
        self.fields: Dict[str, Union[MultiTextField, PlaceholderMultiTextField]] = {}
        self.img_desc:  ImageRepeaterField | None = None
        self.img_rec:   ImageRepeaterField | None = None
        self.img_other: ImageRepeaterField | None = None
        self.preview_engine = None

        try:
            from ttkbootstrap import Style
            Style('darkly')
        except Exception:
            pass

        self.bind_all('<Control-s>', self._quick_save)
        self.bind_all('<Command-s>', self._quick_save)

        self.nb = ttk.Notebook(self); self.nb.pack(fill='both', expand=True, padx=8, pady=6)
        self.nb.bind('<<NotebookTabChanged>>', self._on_tab_change)
        for seq in ('<MouseWheel>','<Button-4>','<Button-5>'):
            self.bind_all(seq, self._on_mousewheel, add='+')

        top = ttk.Frame(self, padding=(8,4)); top.pack(fill='x')
        ttk.Label(top, text='Template:').pack(side='left')
        self.template_var = tk.StringVar()
        self.cbo = styled_option_menu(top, self.template_var, []); self.cbo.pack(side='left', padx=6)
        ttk.Button(top, text='💾 Salva', command=self._quick_save).pack(side='right')

        status = ttk.Frame(self); status.pack(fill='x', side='bottom')
        self.status = ttk.Label(status, text='Ready', anchor='w'); self.status.pack(side='left', fill='x', expand=True, padx=4)
        ttk.Button(status, text='Dettagli', command=self._toggle_details).pack(side='right', padx=4)
        self.detail_frame = ttk.Frame(self)
        self.detail_label = ttk.Label(self.detail_frame, text='', anchor='w', justify='left', wraplength=1000)

        self._load_templates()

    def _on_tab_change(self, event):
        sel = self.nb.tab(self.nb.select(), 'text')
        if sel == 'Preview' and not self.preview_engine:
            show_warning('Anteprima', 'PreviewEngine non disponibile')

    def _toggle_details(self):
        if self.detail_frame.winfo_ismapped():
            self.detail_frame.pack_forget()
        else:
            self.detail_frame.pack(fill='x'); self.detail_label.pack(fill='x', padx=8, pady=2)

    def _on_mousewheel(self, event):
        try:
            frame = self.nb.nametowidget(self.nb.select())
        except Exception:
            return
        def find_canvas(w):
            if isinstance(w, tk.Canvas):
                return w
            for c in w.winfo_children():
                f = find_canvas(c)
                if f:
                    return f
            return None
        canvas = find_canvas(frame)
        if not canvas:
            return
        if hasattr(event, 'delta'):
            delta = -int(math.copysign(1, event.delta))
        elif event.num == 4:
            delta = -1
        elif event.num == 5:
            delta = 1
        else:
            return
        canvas.yview_scroll(delta, 'units')

    def _make_scrollable(self, frame: ttk.Frame) -> ttk.Frame:
        wrapper = ttk.Frame(frame); wrapper.pack(fill='both', expand=True)
        canvas = tk.Canvas(wrapper, highlightthickness=0)
        vsb = ttk.Scrollbar(wrapper, orient='vertical', command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side='right', fill='y'); canvas.pack(side='left', fill='both', expand=True)
        inner = ttk.Frame(canvas)
        canvas.create_window((0,0), window=inner, anchor='nw')
        inner.bind('<Configure>', lambda e, c=canvas: c.configure(scrollregion=c.bbox('all')))
        return inner

    def _load_templates(self):
        files = sorted(p.name for p in TEMPLATE_FOLDER.glob('*.html'))
        menu = self.cbo['menu']; menu.delete(0, 'end')
        for f in files:
            menu.add_command(label=f, command=lambda v=f: self.template_var.set(v))
        if files:
            self.template_var.trace_add('write', lambda *_: self.reload_template())
            self.template_var.set(files[0])

    def reload_template(self):
        # --- Reset tabs e stato interno ---
        for tid in list(self.nb.tabs()):
            self.nb.forget(tid)
        self.fields.clear()
        self.img_desc = self.img_rec = self.img_other = None
        self.preview_engine = None

        # --- Carica template ---
        tpl_path = TEMPLATE_FOLDER / self.template_var.get()
        if not tpl_path.exists():
            show_error('Errore', f"Template '{tpl_path.name}' non trovato")
            return
        self.template_src = tpl_path.read_text(encoding='utf-8')
        placeholders = extract_placeholders(self.template_src)

        # --- Classifica gruppi immagini ---
        img_grps = {
            grp for grp in (k[:-4] for k in placeholders if k.endswith('_SRC'))
            if f"{grp}_ALT" in placeholders
        }
        desc_groups  = sorted(g for g in img_grps if 'DESC' in g.upper())
        rec_groups   = sorted(g for g in img_grps if any(r in g.upper() for r in ('REC','RECIPE')))
        other_groups = sorted(img_grps - set(desc_groups) - set(rec_groups))

        # --- Crea tab Product/Recipe/Other/Images ---
        prod = self._make_scrollable(self._add_tab('Product'))
        rec  = self._make_scrollable(self._add_tab('Recipe'))
        oth  = self._make_scrollable(self._add_tab('Other'))
        img_tab = self._make_scrollable(self._add_tab('Images'))

        # --- Campi testuali per placeholder non immagine ---
        img_keys = {k[:-4] for k in placeholders if k.endswith('_SRC')}
        for key in placeholders:
            if key in img_keys or key.endswith('_ALT') or key.endswith('_SRC'):
                continue
            if key.startswith(('TITLE','PROD')) or 'DESC' in key:
                parent, mode = prod, 'p'
            elif key.startswith(('RECIPE','STEP','TIME','INGREDIENT')):
                parent, mode = rec, 'ul'
            else:
                parent, mode = oth, 'p'
            ttk.Label(parent, text=key).pack(anchor='w', padx=6, pady=2)
            fld = PlaceholderMultiTextField(
                parent,
                placeholder=f"{{{{{key}}}}}",
                mode=mode,
                on_change=self.update_preview
            )
            fld.pack(fill='x', padx=6)
            self.fields[key] = fld
        
        # --- Hero Image (singola) ------------------------------------------
        lf_h = ttk.LabelFrame(img_tab, text='Hero Image')
        lf_h.pack(fill='x', padx=6, pady=4)

        e_hero_src = PlaceholderEntry(lf_h, placeholder='URL immagine hero')
        e_hero_src.pack(fill='x', padx=6, pady=2)

        e_hero_alt = PlaceholderEntry(lf_h, placeholder='Testo alternativo hero')
        e_hero_alt.pack(fill='x', padx=6, pady=2)

        # ⬇️  AGGIUNGI QUESTO (alias render_html -> get)
        for w in (e_hero_src, e_hero_alt):
            w.render_html = w.get
        # --------------------------------------------------------------

        # registra nei campi così _collect() li include
        self.fields['HERO_IMAGE_SRC'] = e_hero_src
        self.fields['HERO_IMAGE_ALT'] = e_hero_alt

        # --- Ripetitori immagini ---
        # Description
        lf_d = ttk.LabelFrame(img_tab, text='Description Images')
        lf_d.pack(fill='x', padx=6, pady=4)
        self.img_desc = ImageRepeaterField(lf_d, self.update_preview)
        self.img_desc.pack(fill='x', padx=6)
        for grp in desc_groups:
            self.img_desc.add_row(src=f"{{{{{grp}_SRC}}}}", alt=f"{{{{{grp}_ALT}}}}")
        # Recipe
        lf_r = ttk.LabelFrame(img_tab, text='Recipe Images')
        lf_r.pack(fill='x', padx=6, pady=4)
        self.img_rec = ImageRepeaterField(lf_r, self.update_preview)
        self.img_rec.pack(fill='x', padx=6)
        for grp in rec_groups:
            self.img_rec.add_row(src=f"{{{{{grp}_SRC}}}}", alt=f"{{{{{grp}_ALT}}}}")
        
        # --- Step Images ---------------------------------------------------
        lf_s = ttk.LabelFrame(img_tab, text='Step Images')
        lf_s.pack(fill='x', padx=6, pady=4)

        self.img_step = ImageRepeaterField(lf_s, self.update_preview)
        self.img_step.pack(fill='x', padx=6)

        # segnaposto automatici (max 4 foto step – aumenta se ti serve)
        for n in range(1, 4):
            self.img_step.add_row(src=f"{{{{STEP{n}_IMG_SRC}}}}",
                                alt=f"{{{{STEP{n}_IMG_ALT}}}}")

        # --- Controlli colonne immagini ---
        ctrl = ttk.Frame(img_tab)
        ctrl.pack(fill='x', pady=6)
        ttk.Label(ctrl, text='Colonne Descrizione:').pack(side='left', padx=(0,4))
        styled_spinbox(ctrl, from_=1, to=4,
                       textvariable=self.cols_desc,
                       command=self.update_preview,
                       width=3).pack(side='left')
        ttk.Label(ctrl, text='  Colonne Ricetta:').pack(side='left', padx=(12,4))
        styled_spinbox(ctrl, from_=1, to=4,
                       textvariable=self.cols_rec,
                       command=self.update_preview,
                       width=3).pack(side='left')

        # --- Preview tab: delegate completamente a PreviewEngine ---
        prev = self._add_tab('Preview')
        if PreviewEngine:
            self.preview_engine = PreviewEngine(prev)
            frame = self.preview_engine.init_frame()
            frame.pack(fill='both', expand=True)
        else:
            # fallback minimale: testo di avviso se non c'è motore di anteprima
            txt = StyledText(prev, wrap='none')
            txt.insert('1.0', '<PreviewEngine non disponibile>')
            txt.pack(fill='both', expand=True)

        # --- Audit dei placeholder ---
        audit_lines: List[str] = []
        for ph in placeholders:
            grp = ph.rsplit('_',1)[0]
            handled = (
                ph in self.fields
                or grp in desc_groups
                or grp in rec_groups
                or (self.img_other and grp in other_groups)
            )
            symbol = '✅' if handled else '❌'
            audit_lines.append(f"{symbol} {ph}")
        show_info(
            'Verifica segnaposti',
            f"Audit segnaposti per '{self.template_var.get()}':\n"
            + "\n".join(audit_lines)
        )

        # --- Rendi invisibili i dettagli e mostra la preview iniziale ---
        self.detail_frame.pack_forget()
        self.update_preview()


    def _add_tab(self, title: str) -> ttk.Frame:
        f = ttk.Frame(self.nb)
        self.nb.add(f, text=title)
        return f

    def _collect(self) -> Dict[str, Union[str,List]]:
        data: Dict[str, Union[str,List]] = {}
        for k,w in self.fields.items():
            data[k] = w.render_html()
        desc = self.img_desc.get_rows() if self.img_desc else []
        rec  = self.img_rec.get_rows()  if self.img_rec  else []
        data['IMAGES_DESC']      = desc
        data['IMAGES_REC']       = rec
        step  = self.img_step.get_rows() if hasattr(self, 'img_step') else []
        data['IMAGES_STEP']      = step
        data['COLS_DESC']        = self.cols_desc.get()
        data['COLS_REC']         = self.cols_rec.get()
        data['IMAGES_DESC_HTML'] = images_to_html(desc, self.cols_desc.get())
        data['IMAGES_REC_HTML']  = images_to_html(rec,  self.cols_rec.get())
        return data

    def update_preview(self):
        ctx = self._collect()
        raw = Template(self.template_src).render(**ctx)
        low = raw.lstrip().lower()
        html = (raw
                if low.startswith('<!doctype') or '<html' in low
                else '<!DOCTYPE html><html><head><meta charset="utf-8"></head><body>'
                     + raw + '</body></html>')
        # aggiorno HTML Source
        try:
            self.html_text.text.delete('1.0', 'end')
            self.html_text.text.insert('1.0', html)
        except AttributeError:
            pass
        # status/details
        missing = extract_placeholders(html)
        empty   = [k for k,w in self.fields.items() if not w.render_html().strip()]
        if missing or empty:
            parts: List[str] = []
            if missing:
                parts.append(f"Segnaposti mancanti: {', '.join(missing)}")
            if empty:
                parts.append(f"Campi vuoti: {', '.join(empty)}")
            self.status.config(text='')
            self.detail_label.config(text='\n'.join(parts))
            if not self.detail_frame.winfo_ismapped():
                self.detail_frame.pack(fill='x'); self.detail_label.pack(fill='x', padx=8, pady=2)
        else:
            self.status.config(text='Tutti i segnaposti popolati ✓', foreground='#5cb85c')
            self.detail_frame.pack_forget()
        # render web preview
        if self.preview_engine:
            self.preview_engine.render(html)

    def _quick_save(self, event=None):
        ctx = self._collect()
        raw = Template(self.template_src).render(**ctx)
        missing = extract_placeholders(raw)
        empty   = [k for k,w in self.fields.items() if not w.render_html().strip()]
        if missing or empty:
            msgs: List[str] = []
            if missing: msgs.append(f"Segnaposti mancanti: {', '.join(missing)}")
            if empty:   msgs.append(f"Campi vuoti: {', '.join(empty)}")
            show_warning('Non posso salvare', '\n'.join(msgs))
            return
        base      = self.template_var.get().rsplit('.',1)[0]
        ts        = time.strftime('%Y%m%d-%H%M%S')
        html_path = EXPORT_FOLDER / f"{base}_{ts}.html"
        json_path = HISTORY_FOLDER / f"{base}_{ts}.json"
        html_path.write_text(html, encoding='utf-8')
        json_path.write_text(json.dumps(ctx, ensure_ascii=False, indent=2), encoding='utf-8')
        show_info('Salvato', f'Export salvato: {html_path.name}')

if __name__ == '__main__':
    BuilderApp().mainloop()
