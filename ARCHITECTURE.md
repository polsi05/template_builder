**ARCHITECTURE.md**

```markdown
# Architecture di Template Builder

Questa guida descrive in dettaglio la **struttura modulare** e le **dipendenze** interne del progetto, con riferimenti ai file sorgente e agli elementi chiave.

---

## Indice

1. [Panoramica ad Albero dei Moduli](#1-panoramica-ad-albero-dei-moduli)  
2. [Descrizione Modulo per Modulo](#2-descrizione-modulo-per-modulo)  
   - 2.1 [template_builder/__init__.py](#21-template_builderinitpy)  
   - 2.2 [template_builder/__main__.py](#22-template_buildermainpy)  
   - 2.3 [template_builder/assets.py](#23-template_builderassetspy)  
   - 2.4 [template_builder/filters.py](#24-template_builderfilterspy)  
   - 2.5 [template_builder/model.py](#25-template_buildermodelpy)  
   - 2.6 [template_builder/step_image.py](#26-template_builderstep_imagepy)  
   - 2.7 [template_builder/widgets.py](#27-template_builderwidgetspy)  
   - 2.8 [template_builder/services/\_\_init\_\_.py](#28-template_builderservicesinitpy)  
   - 2.9 [template_builder/services/text.py](#29-template_builderservicestextpy)  
   - 2.10 [template_builder/services/images.py](#210-template_builderservicesimagespy)  
   - 2.11 [template_builder/services/storage.py](#211-template_builderservicesstoragepy)  
   - 2.12 [template_builder/infrastructure/preview_engine.py](#212-template_builderinfrastructurepreview_enginepy)  
   - 2.13 [template_builder/infrastructure/ui_utils.py](#213-template_builderinfrastructureui_utilspy)  
   - 2.14 [template_builder/infrastructure/validators.py](#214-template_builderinfrastructurevalidatorspy)  
   - 2.15 [template_builder/templates/](#215-template_buildertemplates)  
   - 2.16 [tests/](#216-tests)  
3. [Flusso dei Dati (Call Graph ad Alto Livello)](#3-flusso-dei-dati-call-graph-ad-alto-livello)  
4. [Mappa delle Dipendenze (Import Map)](#4-mappa-delle-dipendenze-import-map)  
5. [Convenzioni di Nomenclatura](#5-convenzioni-di-nomenclatura)  

---

## 1. Panoramica ad Albero dei Moduli

```text
project-root/
├── README.md
├── ARCHITECTURE.md
├── CHANGELOG.md
├── LICENSE
├── pyproject.toml
├── pytest.ini
├── template_builder/
│   ├── __init__.py          # Espone TemplateBuilderApp e funzione main()
│   ├── __main__.py          # Entry-point CLI
│   ├── assets.py            # Costanti globali (regex, colori, cartella history)
│   ├── builder_core.py      # Controller principale (TemplateBuilderApp)
│   ├── filters.py           # Filtri Jinja2 (steps_bind stub)
│   ├── model.py             # Dataclass di dominio (Hero, StepImage, GalleryRow)
│   ├── step_image.py        # Funzioni helper per step-immagine (sort, swap, bind)
│   ├── widgets.py           # Widget Tkinter personalizzati
│   ├── services/
│   │   ├── __init__.py       # Re-export API di servizi
│   │   ├── images.py         # Servizi immagine (griglie, placeholder, Data-URI, smart-paste)
│   │   ├── text.py           # Servizi testo (smart-paste, auto-format, estrazione placeholder)
│   │   └── storage.py        # Persistenza JSON, migrazione v1→v2, export HTML, Undo/Redo
│   ├── infrastructure/
│   │   ├── __init__.py       # Inizializzatore infrastruttura (stub fallback)
│   │   ├── preview_engine.py # PreviewEngine: anteprima HTML (tkinterweb/ScrolledText)
│   │   ├── ui_utils.py       # Utility GUI (popup, centrare finestre, bind mousewheel)
│   │   └── validators.py     # Validatori campi (URL, email, date, non-vuoto)
│   └── templates/            # Template Jinja2 di esempio
└── tests/                    # Suite Pytest (test modelli, servizi, widget)
````

* **template\_builder/**: pacchetto principale contenente controller, widget, servizi e infrastruttura.
* **tests/**: suite di test (Pytest) per verificare modelli, servizi e widget in ambiente headless (usando `pytest-xvfb`).
* **docs/** (non mostrata nell’albero): conterrà documenti di supporto (CONTRIBUTING.md, BUILD\_AND\_TEST.md, RELEASE\_PROCESS.md, eventualmente altri).

---

## 2. Descrizione Modulo per Modulo

### 2.1 `template_builder/__init__.py`

* **Espone**:

  * `__version__ = "1.0.0"`
  * `TemplateBuilderApp`
  * `main()` (wrapper che istanzia `TemplateBuilderApp` e chiama `mainloop()`).
* **Finalità**: consentire il comando CLI `python -m template_builder` e l’importazione diretta di `TemplateBuilderApp`.

---

### 2.2 `template_builder/__main__.py`

* **Entry-point CLI**:

  ```python
  from .builder_core import TemplateBuilderApp

  if __name__ == "__main__":
      app = TemplateBuilderApp()
      if app.root:
          app.root.mainloop()
  ```
* **Finalità**: avviare l’applicazione con:

  ```
  python -m template_builder
  ```

---

### 2.3 `template_builder/assets.py`

* Import principali: `os`, `re`
* **Costanti globali**:

  * `PLACEHOLDER_RGX = re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")`
    (> Regex per estrarre segnaposto Jinja2 `{{TAG}}`.)
  * `URL_RGX = r"https?://[^\s]+"`
  * `DATE_RGX = r"\d{4}-\d{2}-\d{2}"`
  * `DEFAULT_COLS = 3`
  * `HISTORY_DIR = os.path.join(os.path.expanduser("~"), ".template_builder", "history")`
  * `PALETTE = { "bg": "#f0f0f0", "fg": "#000000", "accent": "#007acc", "error": "#ff4c4c", ... }`
  * `APP_NAME = "Template Builder"`
  * `VERSION = "1.0.0"`
* **Utilizzi**:

  * In `services/text.py`: estrazione placeholder con `PLACEHOLDER_RGX`.
  * In `services/images.py`: numero default colonne con `DEFAULT_COLS`.
  * In `widgets.py`: colore placeholder, border per validazioni (usando `PALETTE["accent"]`, `PALETTE["error"]`).

---

### 2.4 `template_builder/filters.py`

* **Registro filtri Jinja2**:

  ```python
  __all__ = ["steps_bind"]

  def steps_bind(env, raw: str) -> str:
      """
      Stub filter legacy: riceve il contesto Jinja (env) e restituisce inalterato raw.
      """
      return raw
  ```
* **Finalità**: mantenere compatibilità con template legacy che usano `{% filter steps_bind %}`.

---

### 2.5 `template_builder/model.py`

* Import principali: `dataclasses`, `html`

* **Dataclass `Hero`**:

  ```python
  @dataclass
  class Hero:
      title: str
      img: str
      alt: str
      intro: str

      def __post_init__(self):
          if self.img and not self.alt:
              raise ValueError("Se img non vuota, deve essere definito alt")

      def to_dict(self) -> dict:
          return {
              "TITLE": self.title,
              "HERO_IMAGE_SRC": self.img,
              "HERO_IMAGE_ALT": self.alt,
              "INTRO": self.intro
          }

      def fallback_html(self) -> str:
          esc_title = html.escape(self.title)
          esc_intro = html.escape(self.intro)
          return f"<h1>{esc_title}</h1><p>{esc_intro}</p>"

      @classmethod
      def from_dict(cls, data: dict):
          return Hero(
              title=data.get("TITLE", ""),
              img=data.get("HERO_IMAGE_SRC", ""),
              alt=data.get("HERO_IMAGE_ALT", ""),
              intro=data.get("INTRO", "")
          )
  ```

  * **Ruolo**: rappresenta la sezione “hero” del template (titolo, immagine, testo ALT, introduzione).
  * **Metodi**: validazione `alt`, serializzazione JSON (`to_dict()`), fallback HTML.

* **Dataclass `StepImage`**:

  ```python
  @dataclass
  class StepImage:
      img: str
      alt: str
      text: str
      order: int

      def __post_init__(self):
          if self.img and not self.alt:
              raise ValueError("Ogni immagine richiede un testo ALT.")

      def to_dict(self) -> dict:
          return {
              "IMG_SRC": self.img,
              "IMG_ALT": self.alt,
              "TEXT": self.text,
              "ORDER": self.order
          }

      @classmethod
      def from_dict(cls, data: dict):
          return StepImage(
              img=data.get("IMG_SRC", ""),
              alt=data.get("IMG_ALT", ""),
              text=data.get("TEXT", ""),
              order=data.get("ORDER", 0)
          )
  ```

  * **Ruolo**: modello per ogni passo “illustrato” (immagine, ALT, testo descrittivo, ordine).
  * **Metodi**: validazione `alt` se esiste immagine, serializzazione JSON.

* **Dataclass `GalleryRow`**:

  ```python
  @dataclass
  class GalleryRow:
      steps: List[StepImage]  # max 3 elementi

      def to_jinja_ctx(self) -> dict:
          return {
              "IMAGES_DESC": [step.text for step in self.steps],
              "IMAGES_SRC": [step.img for step in self.steps],
              "IMAGES_ALT": [step.alt for step in self.steps],
              "IMAGES_ORDER": [step.order for step in self.steps]
          }

      def fallback_html(self) -> str:
          # Genera tabella HTML con righe di immagini per fallback se Jinja non presente
          ...
  ```

  * **Ruolo**: rappresenta una riga di massimo 3 immagini (insieme di `StepImage`) per la galleria.
  * **Metodi**: generazione contesto Jinja (`to_jinja_ctx()`), fallback HTML semplice.

* **Costanti**: `__all__ = ["Hero", "StepImage", "GalleryRow"]`.

---

### 2.6 `template_builder/step_image.py`

* Import principali: `List` (typing), `StepImage` da `model.py`
* **Funzioni**:

  * `sort_steps(steps: List[StepImage]) -> List[StepImage]`
    Restituisce la lista ordinata secondo `step.order`.
  * `swap_steps(steps: List[StepImage], idx1: int, idx2: int) -> None`
    Scambia gli elementi agli indici `idx1` e `idx2` e aggiorna i rispettivi `order`.
  * `renumber_steps(steps: List[StepImage]) -> None`
    Riassegna `order` in sequenza da 1 a N.
  * `bind_steps(texts: List[str], images: List[str], alts: List[str]) -> List[StepImage]`

    * Legge tre liste parallele: testi, URL immagini, testi ALT.
    * Se `images[i] != ""` e `alts[i] == ""`, solleva `ValueError`.
    * Crea `StepImage(img=images[i], alt=alts[i], text=texts[i], order=i+1)` per ogni `i`.
  * `steps_to_html(steps: List[StepImage]) -> str`
    Genera un elenco numerato `<ol><li>…</li></ol>` contenente solo i testi dei passi (fallback testuale).
* **Costanti**: `__all__ = ["sort_steps", "swap_steps", "renumber_steps", "bind_steps", "steps_to_html"]`.

---

### 2.7 `template_builder/widgets.py`

* Import principali:
  `tkinter as tk`, `from tkinter import ttk`
  `from .services import text as text_service`
  `from .services import images as image_service`
  `from .infrastructure import ui_utils`
  `from .assets import PLACEHOLDER_RGX`
  `from typing import List`

* **Classi principali**:

  1. **`_Tooltip`** / **`TooltipMixin`**

     * Gestiscono finestre balloon on-hover per mostrare suggerimenti.
     * Usati da `PlaceholderEntry` e da `SortableImageRepeaterField` per tooltips contestuali (es. `text_service.get_field_help(key)`).

  2. **`PlaceholderEntry`**
     Estende `ttk.Entry` con:

     * Testo placeholder grigio (`PLACEHOLDER_COLOR = "#888888"`).
     * Metodi:

       * `get_value()`: restituisce stringa corrente senza placeholder.
       * `render_html()`: applica `text_service.auto_format()` per generare fallback HTML del campo.

  3. **`PlaceholderSpinbox`**
     Estende `ttk.Spinbox` con placeholder e binding a `update_preview()`.
     Viene usato per i selettori di colonne (`COLS_DESC`, `COLS_REC`).

  4. **`PlaceholderMultiTextField`** (alias `MultiTextField`)
     Basato su `tk.Text`, con:

     * Placeholder di testo,
     * Callback `on_change` (il controller lo passa come `update_preview`),
     * Supporto a `text_service.smart_paste()` su incolla (split su newline/`;`, rimozione righe vuote),
     * Metodi per generare fallback HTML (`render_html()`).

  5. **`SortableImageRepeaterField`**
     Componente avanzato per elenchi di righe immagine+ALT:

     * Ogni riga ha due `ttk.Entry` (URL immagine, ALT) e bottoni `+`, `–`, `↑`, `↓`.
     * Validazione live di ciascun URL con `image_service.validate_url()`: applica `_apply_border(widget, ok)` per colorare bordo in verde/rosso.
     * Supporta drag & drop di file se `tkinterdnd2` è installato (`HAS_DND = True`), altrimenti mostra pulsante “+ Add”.

* **Funzioni helper**:

  * `_apply_border(widget, ok: bool)`: colora bordo `widget` in verde se `ok=True`, rosso se `ok=False`.
  * `_split_dnd_event_data(data: str) -> List[str]`: parsing dati di drag & drop per estrarre percorsi di file.

* **Costanti**:

  * `HAS_DND` (flag booleano: `True` se `tkinterdnd2` è installato),
  * `HAS_TOOLTIP` (flag su supporto tooltip),
  * `PLACEHOLDER_COLOR = "#888888"`.

* **Ruolo**: forniscono tutti i widget interattivi della GUI, interfacciandosi con il controller (`builder_core.py`) tramite callback a `update_preview()` e raccogliendo i dati per il contesto Jinja.

---

### 2.8 `template_builder/services/__init__.py`

* **Re-export** di tutto ciò che si trova in `services/text.py`, `services/images.py`, `services/storage.py`.
  Definisce `__all__` opportuno per rendere disponibili funzioni e classi via:

  ```python
  from template_builder.services import quick_save, validate_url, smart_paste, ...
  ```
* **Finalità**: incapsulare i servizi in un unico namespace e semplificare gli import nel resto del progetto.

---

### 2.9 `template_builder/services/text.py`

* Import principali: `re`, `typing.List`, `typing.Set`, `html`
* **Funzioni**:

  * `smart_paste(raw: str) -> List[str]`

    * Suddivide `raw` su newline (`\n`) o punto e virgola (`;`); rimuove spazi iniziali/finali e righe vuote.
    * Ritorna lista di righe “pulite”.
  * `_split_lines(raw: str) -> List[str]` (helper interno a `smart_paste`).
  * `_format_line(line: str) -> str`

    * Format HTML leggero per una singola riga: gestisce markup `**bold**` e `*italic*`.
  * `auto_format(text: str, mode: str = "ul"|"p") -> str`

    * Se `mode="ul"`, avvolge ogni riga in `<li>…</li>` e incapsula in `<ul>`.
    * Se `mode="p"`, avvolge ogni riga in `<p>…</p>`.
  * `extract_placeholders(html_src: str) -> Set[str]`

    * Usa `assets.PLACEHOLDER_RGX` (`re.compile(r"\{\{\s*([A-Z0-9_]+)\s*\}\}")`) per individuare tutti i segnaposto `{{ TAG }}` in `html_src`.
  * `images_to_html(rows: int, cols: int) -> str`

    * Fallback HTML per una galleria di placeholder numerati se `Jinja2` non è installato.
  * `get_field_help(key: str) -> str`

    * Restituisce la stringa di help associata a `key` (es. `"TITLE"`, `"STEP1_IMG_ALT"`) pescata da `_HELP_DEFAULTS`.
* **Costanti**:

  * `_HELP_DEFAULTS`: dizionario mapping chiavi → stringhe di suggerimento (tooltip).
  * `BULLET_RGX`, `HTML_ALLOWED_TAGS`: definiscono regole base di escape per HTML.
* **Ruolo**: centralizzare tutte le funzioni di manipolazione e validazione del testo, indipendenti dalla GUI, per generare fallback HTML o estrarre segnaposto.

---

### 2.10 `template_builder/services/images.py`

* Import principali: `base64`, `os`, `requests` (per metadata da URL), `typing.List`,
  import lazy di `PIL.Image` (in `_ensure_pillow()`).
* **Funzioni**:

  1. `guess_grid(n_images: int, cols: int) -> Tuple[int,int]`

     * Data la quantità `n_images` e il numero desiderato di colonne `cols`, calcola il numero ottimale di righe e colonne per la griglia.
  2. `generate_placeholders(n_images: int) -> List[str]`

     * Restituisce lista di segnaposto Jinja: `["{{IMG1}}", "{{IMG2}}", …]`.
  3. `_ensure_pillow()`

     * Tenta di importare `PIL.Image`; se fallisce, imposta `Image = None` e `HAS_PIL = False`.
  4. `_img_to_bytes(path: str) -> bytes`

     * Apre localmente il file immagine e converte in bytes (usato se `Pillow` disponibile).
  5. `encode_file_to_data_uri(path: str) -> str`

     * Converte un file immagine locale in Data-URI base64 per inclusion inline nel markup HTML.
  6. `_make_img_tag(src: str, alt: str) -> str`

     * Genera un tag `<img src="…" alt="…">` con attributi width/height se disponibili (tramite `Pillow`).
  7. `paths_to_html_grid(paths: List[str], cols: int, inline: bool=False, alt_texts: List[str]=None) -> str`

     * Costruisce una `<table>` HTML di immagini:

       * Se `inline=True`, inserisce Data-URI (base64), altrimenti usa URL esterni.
       * Usa `alt_texts` per ciascun attributo `alt`.
       * Sfrutta `guess_grid()` per calcolare righe/colonne ottimali.
  8. `images_to_html(paths: List[str], cols: int, inline: bool=False, alt_texts: List[str]=None) -> str`

     * Alias per `paths_to_html_grid()`.
  9. `smart_paste_images(raw: str) -> List[str]`

     * Delegato a `text.smart_paste()`: suddivide `raw` su newline/`;`, rimuove righe vuote.
  10. `validate_url(url: str) -> bool`

      * Wrapper su `infrastructure.validators.validate_url(url)`.
  11. `fetch_metadata(path: str) -> Dict[str,int]`

      * Se `Pillow` installato, apre l’immagine con `PIL.Image` e restituisce `{"width": …, "height": …}`; altrimenti ritorna `{}`.
* **Costanti**:

  * `PLACEHOLDER_BASE_URL` (definita come base per placeholder online, ma non usata attualmente).
  * `MIME_TYPES`: mappa estensioni → MIME type.
  * `HAS_PIL`: flag booleano che indica se `Pillow` è disponibile.
* **Ruolo**: fornire tutte le funzioni “pure” per la gestione di immagini, indipendenti dalla GUI, testabili in isolamento.

---

### 2.11 `template_builder/services/storage.py`

* Import principali: `os`, `json`, `datetime`, `jinja2` (import lazy in `export_html`),
  `from ..step_image import bind_steps`.
* **Costanti**:

  * `SCHEMA_VERSION = 2`
  * `_BASE_DIR = os.path.expanduser("~/.template_builder")`
  * `_HISTORY_DIR = os.path.join(_BASE_DIR, "history")`
  * `AUTOSAVE_LIMIT = 50`
* **Classi**:

  1. **`UndoRedoStack`**

     * `push(state: Dict)`: aggiunge copia profonda di `state` allo stack.
     * `undo() -> Dict`: se possibile, estrae e restituisce snapshot precedente.
     * `redo() -> Dict`: se dopo un `undo()`, consente di ripristinare snapshot “rifatto”.
* **Funzioni**:

  1. `_timestamp() -> str`

     * Genera timestamp in formato `YYYYMMDD_HHMMSS`.
  2. `quick_save(state: Dict) -> pathlib.Path`

     * Salva `state` in JSON dentro `~/.template_builder/history/recipe_<timestamp>.json`.
     * Restituisce il path del file creato.
  3. `_migrate_v1_to_v2(old: Dict) -> Dict`

     * Se `old["SCHEMA_VERSION"] == 1`, ricostruisce i campi `STEPS` e `STEPn_IMG_ALT` combinando vecchi elenchi `"IMAGES_STEP"`, `"ALTS_STEP"`, `"TEXTS_STEP"` attraverso `step_image.bind_steps()`.
     * Imposta `SCHEMA_VERSION = 2`.
  4. `load_recipe(path: Union[str, pathlib.Path]) -> Dict`

     * Legge JSON da `path`; se `SCHEMA_VERSION < 2`, invoca `_migrate_v1_to_v2()` per garantire compatibilità con schema attuale.
     * Restituisce contesto JSON completo (con chiavi `STEPS`, `STEPn_IMG_ALT`, ecc.).
  5. `export_html(ctx: Dict, template_path: str, **env_kw) -> str`

     * Import lazy di `jinja2`; carica il template da `template_path`, lo renderizza con `ctx`, restituisce HTML come stringa.
     * Se `jinja2` mancante, solleva `ImportError`.
* **Ruolo**: gestire la persistenza su file (undo/redo, quick-save, load e migrazione v1→v2) e l’export finale in HTML attraverso Jinja2.

---

### 2.12 `template_builder/infrastructure/preview_engine.py`

* Import principali: `tkinter as tk`, `tkinter.scrolledtext.ScrolledText`, import lazy di `"tkinterweb.HtmlFrame"`.
* **Classe `PreviewEngine`**:

  ```python
  class PreviewEngine:
      def __init__(self, parent, width: int, height: int):
          """
          Tenta import di tkinterweb.HtmlFrame:
          - Se disponibile, crea HtmlFrame(parent, horizontal_scrollbar="auto").
          - Altrimenti, crea ScrolledText(parent).
          Imposta self._headless = not self._display_available().
          """
          ...
      def render(self, html: str) -> None:
          """
          Se non headless, aggiorna contenuto di HtmlFrame o ScrolledText con la stringa HTML.
          Altrimenti, no-op.
          """
          ...
      def collect_context(self) -> dict:
          """Stub per parity API; restituisce {}."""
          return {}
      def _display_available(self) -> bool:
          """Controlla se DISPLAY è settato (su Unix) o se istanziare un Tk() non fallisce."""
      def _safe(self, name: str):
          """Import dinamico in try/except per moduli opzionali (es. tkinterweb, cefpython3)."""
  ```
* **Ruolo**: fornire un unico “motore” di anteprima HTML che:

  * Utilizza `tkinterweb` se presente per un anteprima embedded a tutti gli effetti.
  * Altrimenti, si rifugia su un semplice `ScrolledText` per visualizzare HTML “grezzo” (headless fallback).

---

### 2.13 `template_builder/infrastructure/ui_utils.py`

* Import principali: `tkinter as tk`, `tkinter.messagebox`, `platform`
* **Funzioni**:

  * `show_info(msg: str) -> None`: popup informativo (`messagebox.showinfo`).
  * `show_error(msg: str) -> None`: popup errore (`messagebox.showerror`).
  * `show_warning(msg: str) -> None`: popup avviso (`messagebox.showwarning`).
  * `center_window(win: tk.Tk) -> None`: centra la finestra `win` sullo schermo.
  * `bind_mousewheel(widget: tk.Widget) -> None`: associa `<MouseWheel>`, `<Button-4>`, `<Button-5>` a `widget` per scroll cross-platform.
  * `ask_yes_no(msg: str) -> bool`: popup di conferma `Yes/No`.
* **Costanti**:

  * `KEY_CTRL = "Control"`, `KEY_CMD = "Command"`,
  * `OS_NAME = platform.system().lower()`.
* **Ruolo**: utility generali per la GUI, popup e binding di eventi.

---

### 2.14 `template_builder/infrastructure/validators.py`

* Import principali: `re`, `datetime`
* **Funzioni**:

  * `validate_url(url: str) -> bool`: verifica che `url` rispetti `URL_RGX = re.compile(r"https?://[^\s]+")`.
  * `validate_email(email: str) -> bool`: verifica che `email` rispetti `EMAIL_RGX = re.compile(r"[^@]+@[^@]+\.[^@]+")`.
  * `validate_date(date_str: str) -> bool`: tenta `datetime.strptime(date_str, "%Y-%m-%d")`; ritorna `True` se valido, altrimenti `False`.
  * `validate_nonempty(value: str) -> bool`: ritorna `len(value.strip()) > 0`.
* **Ruolo**: centralizzare le funzioni di validazione basi per campi (URL, email, date, non vuoto), usate da widget e servizi.

---

### 2.15 `template_builder/templates/`

* Cartella contenente circa 10 file HTML/Jinja2 di esempio, utilizzati sia da `builder_core.py` (anteprima) sia da `export_html()` (esportazione finale).
* **Esempi di template**:

  * `ebay_template_modern_dynamicv2.html`
  * `ebay_template_modern_full.html`
  * `template dinamico prova.html`
  * `template_ebay completo.html`
  * `template_completov2.html`
  * `template_ebay_+ricetta_con_foto.html`
  * `template_ebay+ricetta.html`
  * `template_final_ebay.html`
  * `template_segnaposto_prova.html`
* Ogni file contiene:

  * Sezioni `<head>` con CSS inline, `<body>`, commenti Jinja, e segnaposto come `{{ TITLE }}`, `{{ DESCRIPTION }}`, `{{ STEPS }}`, `{{ IMG1_SRC }}`, `{{ IMG1_ALT }}`, ecc.
* **Ruolo**: esempi di layout da utilizzare per anteprima e per esportazione definitiva.

---

### 2.16 `tests/`

* **Suite Pytest** per verificare:

  * **Modelli** (`model.py`, `step_image.py`)
  * **Servizi** (`services/text.py`, `services/images.py`, `services/storage.py`)

    * Esecuzione in headless (`pytest-xvfb`) per controllare funzioni di fallback (senza dipendenze GUI).
  * **Widget** (`widgets.py`, `preview_engine.py`, `ui_utils.py`, `validators.py`)

    * I test verificano binding, comportamenti di validazione, creazione/rimozione dinamica righe in `SortableImageRepeaterField`, ecc.
* **File di configurazione**:

  * `pytest.ini`: definisce marker specifici (es. `xfail`, `skipif`) e opzioni come `--maxfail=1 --disable-warnings -q`.
  * I layout headless vengono garantiti da `pytest-xvfb`.

---

## 3. Flusso dei Dati (Call Graph ad Alto Livello)

Nella seguente tabella, i principali chiamanti (caller) vengono confrontati con i callee (funzioni/metodi invocati):

| Chiamante                                    | Callee                                       | Finalità                                                             |
| -------------------------------------------- | -------------------------------------------- | -------------------------------------------------------------------- |
| **TemplateBuilderApp.\_collect()**           | `step_image.bind_steps(texts, images, alts)` | Genera lista `STEPS` a partire da testi, URL immagini e ALT.         |
| **TemplateBuilderApp.quick\_save()**         | `services.storage.quick_save(state)`         | Salva lo stato corrente in un file JSON con timestamp.               |
| **TemplateBuilderApp.load\_recipe(path)**    | `services.storage.load_recipe(path)`         | Carica e migra progetto (schema v1→v2) tramite `_migrate_v1_to_v2`.  |
| **TemplateBuilderApp.update\_preview()**     | `PreviewEngine.render(html)`                 | Richiede rendering HTML e aggiorna il riquadro anteprima.            |
| **SortableImageRepeaterField.\_validate()**  | `services.images.validate_url(url)`          | Evidenzia in tempo reale la validità di un URL immesso.              |
| **Ogni widget `<KeyRelease>`**               | `TemplateBuilderApp.update_preview()`        | Aggiorna live l’anteprima ad ogni modifica di testo/spinbox.         |
| **services.storage.\_migrate\_v1\_to\_v2()** | `step_image.bind_steps(texts, images, alts)` | Durante caricamento di JSON legacy v1, popola i nuovi campi `STEPS`. |
| **builder\_core (init UI)**                  | `ui_utils.bind_mousewheel(self.nb)`          | Applica binding di scroll alla `Notebook` (smart-scroll base).       |

---

## 4. Mappa delle Dipendenze (Import Map)

Di seguito una rappresentazione schematica di quali moduli importano quali altri moduli. L’asterisco (`✔︎`) indica un import diretto, mentre (`—`) indica nessun import.

| Modulo                  | assets.py | widgets.py | services.text.py | services.images.py | services.storage.py | step\_image.py | preview\_engine.py | ui\_utils.py | validators.py |
| ----------------------- | :-------: | :--------: | :--------------: | :----------------: | :-----------------: | :------------: | :----------------: | :----------: | :-----------: |
| **builder\_core.py**    |     ✔︎    |     ✔︎     |        ✔︎        |         ✔︎         |          ✔︎         |       ✔︎       |         ✔︎         |      ✔︎      |       ✔︎      |
| **model.py**            |     ✔︎    |      —     |         —        |          —         |          —          |       ✔︎       |          —         |       —      |       —       |
| **step\_image.py**      |     ✔︎    |      —     |         —        |          —         |          —          |        —       |          —         |       —      |       —       |
| **widgets.py**          |     ✔︎    |      —     |        ✔︎        |         ✔︎         |          —          |        —       |          —         |      ✔︎      |       —       |
| **services/text.py**    |     ✔︎    |      —     |         —        |          —         |          —          |        —       |          —         |       —      |       —       |
| **services/images.py**  |     ✔︎    |     ✔︎     |        ✔︎        |          —         |          —          |        —       |          —         |       —      |       —       |
| **services/storage.py** |     ✔︎    |      —     |         —        |          —         |          —          |       ✔︎       |          —         |       —      |       —       |
| **preview\_engine.py**  |     ✔︎    |      —     |         —        |          —         |          —          |        —       |          —         |       —      |       —       |
| **ui\_utils.py**        |     ✔︎    |      —     |         —        |          —         |          —          |        —       |          —         |       —      |       —       |
| **validators.py**       |     ✔︎    |      —     |         —        |          —         |          —          |        —       |          —         |       —      |       —       |

Legenda:

* **builder\_core.py** importa quasi tutti i moduli principali (widget, servizi, step\_image, preview\_engine, ui\_utils, assets, filters, validators).
* **widgets.py** si appoggia a `services.text`, `services.images`, `ui_utils`, `assets`.
* **services/storage.py** richiama `step_image.bind_steps` durante la migrazione.
* Gli altri moduli (model, step\_image, filters, templates) non richiedono import ciclici complessi.

---

## 5. Convenzioni di Nomenclatura

* **Classi**: PascalCase
  Es.: `TemplateBuilderApp`, `StepImage`, `PreviewEngine`.
* **Funzioni/Metodi**: snake\_case
  Es.: `quick_save`, `bind_steps`, `sort_steps`, `export_html`.
* **Costanti (Screaming Snake)**:
  Es.: `DEFAULT_COLS`, `PLACEHOLDER_RGX`, `SCHEMA_VERSION`.
* **Segnaposto Jinja2 / Chiavi di contesto**: UPPER\_SNAKE
  Es.: `TITLE`, `HERO_IMAGE_SRC`, `STEP3_IMG_ALT`.
* **Pacchetti/Moduli**: tutto minuscolo con underscore
  Es.: `services`, `infrastructure`, `step_image`.

---

*Fine di ARCHITECTURE.md*