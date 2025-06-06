**CHANGELOG.md**

```markdown
# Changelog

Tutte le modifiche di Template Builder sono elencate per versione in ordine decrescente. Ogni sezione riporta le novità più rilevanti, aggregate per commit e per file coinvolti.

---

## [1.0.0] – 2025-06-06

- **Nuovi moduli e dataclass**  
  - Aggiunta dataclass `Hero` (gestione sezione hero con titolo, immagine, ALT, introduzione).  
  - Aggiunta dataclass `GalleryRow` (gestione riga galleria max 3 immagini).  
  - Introdotto `StepImage` per i passi illustrati (immagine + testo + ALT + ordine).  

- **Anteprima avanzata**  
  - Implementato `PreviewEngine` che usa `tkinterweb.HtmlFrame` se presente, altrimenti fallback `ScrolledText`.  
  - Anteprima live con binding su quasi tutti i campi (testo, spinbox, repeater immagini).  

- **Undo/Redo completamente integrato**  
  - Classe `UndoRedoStack` in `services/storage.py`: snapshot dello stato JSON.  
  - Scorciatoie da tastiera:  
    - Windows/Linux: Ctrl + Z (Undo), Ctrl + Y (Redo)  
    - macOS: Cmd + Z (Undo), Shift + Z (Redo)

- **Drag & Drop immagini**  
  - `SortableImageRepeaterField` supporta drag & drop tramite `tkinterdnd2` (fallback pulsante “+ Add”).  

- **Validazione live**  
  - Campi URL/ALT evidenziati con bordo verde se `validate_url(url) == True`, rosso altrimenti.  

- **Tooltips contestuali**  
  - Funzionalità `TooltipMixin` su campi placeholder e repeater immagini basata su `text.get_field_help(key)`.  

- **Persistenza JSON con migrazione autom.**  
  - `quick_save(state)` salva lo stato in `~/.template_builder/history/recipe_<timestamp>.json`.  
  - `load_recipe(path)` esegue migrazione v1→v2 tramite `_migrate_v1_to_v2()` (ricostruisce campi `STEPS`, `STEPn_IMG_ALT`).  

- **Esportazione HTML con Jinja2 lazy import**  
  - `export_html(ctx, template_path)` in `services/storage.py`:  
    - Se `jinja2` non installato, solleva `ImportError`.  
    - Altrimenti, genera HTML definitivo dal template.  

- **Rifattorizzazione e rimozione stub legacy**  
  - Separazione netta tra servizi (`images.py`, `text.py`, `storage.py`) e GUI (`widgets.py`, `builder_core.py`).  
  - Eliminazione progressiva delle cartelle e file monolitici legacy.  

---

## [0.1.0]

- **Correzioni legacy e bugfix**  
  - Risolti bug storici in anteprima HTML per template complessi; regressioni su undo/redo; problemi con drag & drop immagini; placeholder non persistenti; tooltip mancanti.  
  - `services/storage.py`: metodi di migrazione automatica `_migrate_v1_to_v2()` e gestione compatibilità con progetti v1.  
  - Introduzione menu **Edit → Audit Segnaposti (F11)**: estrazione segnaposto via `text.extract_placeholders()`, confronto con chiavi contesto, output in dialogo.  

- **Prime basi di test e CI**  
  - Configurati GitHub Actions per eseguire `pip install` e `pytest -q` in headless (Xvfb).  
  - Aggiunte prime suite Pytest per modelli e servizi.  

---

## [0.0.1]

- **Skeleton & Core**  
  - Creazione struttura di base del package (`builder_core.py`, `widgets.py`, `services/`, `infrastructure/`, `model.py`, `filters.py`, `assets.py`).  
  - Definizione di `pyproject.toml` e configurazione iniziale di `setup.py` per gioco minimale del package.  
  - Garantita importabilità in test headless (`xvfb`) senza crash.  

- **Test headless**  
  - Aggiunti file di configurazione `pytest.ini`.  
  - Definiti primi test su `infrastructure/validators.py` e `services/text.py`.

- **CI iniziale**  
  - GitHub Actions `ci.yml` per `pip install .[test]` e `pytest`.  
  - Tag `v0.0.1` creato a fine fase A.  

---

*Fine di CHANGELOG.md*
````

---


