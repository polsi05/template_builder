
**Contenuto**:
```markdown
# Architettura di Template Builder

Questa sezione descrive l’architettura modulare del progetto.

## 1. Core (controller)

- **builder_core.py**  
  - `TemplateBuilderApp`  
    - Gestisce lo stato (`_state: dict`).  
    - Implementa `undo()`/`redo()` con `UndoRedoStack`.  
    - `load_recipe(path)` carica un JSON e imposta `_state`.  
    - `audit_placeholders()` estrae tutti i placeholder `{{TAG}}` da `template_src` e indica quali sono presenti in `_state`.  
  - Non dipende direttamente da Tkinter se `enable_gui=False`.

## 2. Widget (GUI)

- **widgets.py**  
  - `PlaceholderEntry`, `PlaceholderSpinbox`  
    - Implementano ghost‐text, tooltip (`get_field_help()`), `get_value()`, `render_html()`.  
  - `PlaceholderMultiTextField`  
    - Campo `tk.Text` con placeholder e “smart paste” (utilizza `smart_paste()`).  
    - `get_raw()`, `render_html()`.  
  - `SortableImageRepeaterField`  
    - Lista di `PlaceholderEntry` per gestire una serie di URL immagine.  
    - `_add_row()`, `_move_row()`, `_del_row()`, `get_urls()`.

## 3. Servizi

### 3.1 Servizi Testo (`services/text.py`)

- `extract_placeholders(html_src: str) -> Set[str]`  
  - Estrae tutti i tag `{{TAG}}` da una stringa (usando la regex `PLACEHOLDER_RGX`).  
- `smart_paste(raw: str | Sequence[str]) -> List[str]`  
  - Divide il testo o lista di stringhe su `\n` e `;`, rimuove spazi e righe vuote.  
- `auto_format(text: str, mode: "ul" | "p") -> str`  
  - Mode `"ul"`: genera `<ul><li>…</li></ul>`, splittando su `\n` e `;`.  
  - Mode `"p"`: genera `<p>…</p>` per ogni linea.  
  - Escape di `<`/`>` con `html.escape()`.  
- `get_field_help(key: str) -> str`  
  - Fornisce una stringa di aiuto contestuale (es. “Titolo del prodotto”).  
- `images_to_html(rows: int, cols: int) -> str`  
  - Genera una tabella HTML di placeholder `{{ IMGn }}`.

### 3.2 Servizi Immagini (`services/images.py`)

- `guess_grid(n_images: int, cols: int) -> (rows, cols)`  
  - Calcola righe e colonne minimizzando il numero di righe.  
- `generate_placeholders(n_images: int) -> List[str]`  
  - Genera `["{{ IMG1 }}", …]`, almeno un elemento.  
- `encode_file_to_data_uri(path, mime=None) -> str`  
  - Converte un file immagine in `data:image/...;base64,...`.  
- `paths_to_html_grid(paths: Sequence[str]|None, cols: int, inline: bool, alt_texts: List[str]|None) -> str`  
  - Se `paths` vuoto, fallback con un solo placeholder.  
  - Altrimenti, usa `guess_grid` per dimensioni e posiziona `<img>` in tabella `<table><tr><td>…</td></tr></table>`.  
- `images_to_html(rows: int, cols: int) -> str`  
  - Compatibilità: tabella di placeholder `{{ IMGn }}`.  
- `smart_paste_images(raw: str | Sequence[str]) -> List[str]`  
  - Alias di `smart_paste`.  
- `validate_url(url: str) -> None`  
  - Usa il validator legacy per URL immagine.  
- `fetch_metadata(path: str) -> Dict[str, int|str]`  
  - Apre l’immagine con Pillow e restituisce `{ width, height, format }`.

### 3.3 Servizi Storage (`services/storage.py`)

- `UndoRedoStack`  
  - `_history: List[Any]`, `_index: int`  
  - `push(state)`, `undo()`, `redo()`.  
- `quick_save(state)`  
  - Serializza in JSON e salva in un file temporaneo (`.json`), ritorna il `Path`.  
- `load_recipe(path)`  
  - Carica un JSON da file; se non valido o non `dict`, restituisce `{}`.  
- `export_html(ctx: Dict, template_path: str|Path)`  
  - Legge il template da disco.  
  - Tenta di importare Jinja2:  
    - Se ha successo, usa Jinja2 per il rendering.  
    - Altrimenti, fallback `_simple_render`:  
      - Sostituisce ogni `{{ key }}` con `str(ctx[key])`.  
  - Se `save_to` in `env_kw` è impostato, salva anche su file.

## 4. Infrastruttura (`infrastructure/`)

- **ui_utils.py**  
  - `show_info(msg: str)`  
    - Stub: stampa `"[info] {msg}\n"` su stdout.  
- **preview_engine.py**  
  - `PreviewEngine(html: str = "")`  
    - `render_source() -> str` restituisce l’HTML in memoria.

## 5. Modulo Filtro (`filters.py`)

- `steps_bind(ctx, raw)`  
  - Stub: ritorna esattamente `raw` grazie al decorator fittizio `@pass_context`.

## 6. Modello Dati (`model.py`)

- `Hero(url: str = "", alt: str = "")`  
- `StepImage(url: str = "", alt: str = "", order: int = 0)`  
- `GalleryRow(urls: List[str] = None)`

Questa struttura garantisce modularità, testabilità e facilità di manutenzione.

---

## 4. Mapping Legacy (opzionale)

Se hai un file di mapping verso il codice legacy (per esempio situato in `project-root/legacy/mapping_template_builder_legacy.csv`), aggiornalo in questo modo:

```csv
legacy_function,new_module,new_function
template_builder_legacy.extract_placeholders,services/text.py,extract_placeholders
template_builder_legacy.smart_paste,services/text.py,smart_paste
template_builder_legacy.auto_format,services/text.py,auto_format
template_builder_legacy.images_to_html,services/text.py,images_to_html
template_builder_legacy.validate_image,services/images.py,validate_url
template_builder_legacy.fetch_metadata,services/images.py,fetch_metadata
template_builder_legacy.undo_redo,services/storage.py,UndoRedoStack
template_builder_legacy.load_recipe,services/storage.py,load_recipe
template_builder_legacy.export_html,services/storage.py,export_html
template_builder_legacy.show_info,infrastructure/ui_utils.py,show_info
template_builder_legacy.PreviewEngine,infrastructure/preview_engine.py,PreviewEngine
