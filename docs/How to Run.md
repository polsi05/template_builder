## How to Run

### Da CLI

```bash
python -m template_builder
```

Questo comando avvia `TemplateBuilderApp` se è disponibile un display GUI.

### Da codice Python

```python
from template_builder.builder_core import TemplateBuilderApp

app = TemplateBuilderApp()
if app.root:
    app.root.mainloop()
```

---

## Funzionalità Principali

* **Anteprima Live**
  Visualizza in tempo reale il rendering del template HTML generato dal contesto Jinja2. Se `tkinterweb` è installato, usa un `HtmlFrame`; altrimenti, un semplice `ScrolledText` come fallback.

* **Undo/Redo**
  Gestione completa delle modifiche tramite `UndoRedoStack`. Scorciatoie da tastiera:

  * *Windows/Linux*: Ctrl + Z (Undo), Ctrl + Y (Redo)
  * *macOS*: Cmd + Z (Undo), Shift + Z (Redo)

* **Gestione Immagini**

  * **Drag & Drop** (se `tkinterdnd2` installato) o pulsante “+ Add” per aggiungere URL di immagini.
  * **Validazione live** di URL immagini: bordo verde se valido, rosso se non valido.
  * Se `Pillow` installato, `fetch_metadata()` estrae larghezza/altezza immagine.
  * Generazione HTML di griglie con `images_to_html()`.

* **Widget Avanzati**

  * `PlaceholderEntry`, `PlaceholderSpinbox`, `PlaceholderMultiTextField`: campi con testo “ghost” (placeholder) e validazione live.
  * `SortableImageRepeaterField`: lista dinamica di URL immagini + ALT, con pulsanti di aggiunta/rimozione e spostamento righe.

* **Migrazione Dati**
  Caricamento di progetti legacy v1 (chiavi `"Step1"`, `"IMAGES_STEP"`, `"ALTS_STEP"`) → nuovo schema v2 (chiavi `"STEPS"`, `"STEPn_IMG_ALT"`) tramite `_migrate_v1_to_v2()` in `services/storage.py`.

* **Audit Segnaposti**
  Menu **Edit → Audit Segnaposti (F11)**: estrae tutti i segnaposto `{{TAG}}` dal template e li confronta con chiavi contesto interne, mostrando elenco “FOUND vs MISSING”.

* **Selettore Colonne**
  Nella tab “Images”, due spinbox per definire numero di colonne (`COLS_DESC`, `COLS_REC`) con binding a `update_preview()`.

* **Tipografia e Formattazione**

  * `smart_paste()`: normalizza input multi-linea / separato da `;`.
  * `auto_format()`: converte testo plain in `<ul>`, `<li>`, `<p>`.
  * `extract_placeholders()`: estrae segnaposto Jinja2.

---

## Dipendenze

Le dipendenze obbligatorie e opzionali sono elencate in `requirements.txt` (vedi sezione dedicata).

* **Obbligatori (runtime)**

  * `Jinja2>=3.0`
  * `Pillow>=8.0`
  * Python 3.10+ (con modulo Tkinter incluso)

* **Opzionali**

  * `tkinterdnd2>=0.3`  (facilita il drag & drop di immagini)
  * `tkinterweb>=0.4`   (consente anteprima HTML embedded)
  * `ttkbootstrap>=0.5` (per applicare il tema “darkly” – se presente)

* **Per sviluppo / test / headless**

  * `pytest>=6.0`
  * `pytest-xvfb>=0.3`  (abilita test GUI in ambiente headless)
  * `flake8>=3.9`
  * `black>=22.0`
  * `coverage>=5.5`

---

## Esempio di Utilizzo

1. **Avvia l’app**

   ```bash
   python -m template_builder
   ```

2. **Crea un nuovo progetto o carica uno esistente**

   * Tab **Hero**: inserisci titolo, URL immagine hero e testo ALT.
   * Tab **Description**: digita il testo; usa `auto_format` per elenchi puntati.
   * Tab **Recipe**: incolla nomi dei passaggi separati da `;` o newline; usa “Add Image” per ciascun URL immagine del passo (o trascina se `tkinterdnd2` installato).
   * Tab **Images**: configura numero colonne (`COLS_DESC`, `COLS_REC`).
   * Menu **Edit → Audit Segnaposti** per verificare placeholder mancanti o in eccesso.
   * Menu **File → Save** o `Ctrl+S` per salvare in `~/.template_builder/history/`.
   * Menu **File → Export HTML** per generare il file HTML finale (richiede `Jinja2`).

3. **Esempio rapido (codice)**

   ```python
   from template_builder.builder_core import TemplateBuilderApp

   app = TemplateBuilderApp()
   if app.root:
       app.root.mainloop()
   ```
