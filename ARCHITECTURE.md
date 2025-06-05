# Architettura del Template Builder -- vediamo se funziona

Questo documento descrive la struttura modulare del progetto, il flusso dei dati e i pattern di progettazione adottati.

## 1. Panoramica Modulare

Il progetto è organizzato in diversi moduli, ognuno con responsabilità chiaramente separate:

1. **template_builder/builder_core.py**  
   - Logica di business principale.  
   - orchestrazione tra interfaccia grafica (GUI) e modello di dominio (`StepImage`, `ProjectData`).  
   - Raccolta e validazione dei dati di input dall’utente (testi step, URL immagini, ALT).  
   - Funzionalità di esportazione e salvataggio.

2. **template_builder/step_image.py**  
   - Definizione di funzioni per la gestione dei “passaggi illustrati” (StepImage).  
   - `sort_steps`, `swap_steps`, `renumber_steps` per ordinare e manipolare liste di `StepImage`.  
   - `bind_steps(texts, images, alts=None)`: combinazione di testi, URL e ALT per generare oggetti `StepImage` con validazione rigorosa.  
   - `steps_to_html(steps)`: helper per generare HTML semplice di verifica (lista ordinata di passi con immagini).

3. **template_builder/model.py**  
   - Definizione del dataclass `StepImage`.  
   - `__post_init__` per validare che, se è presente un’immagine (`img`), esista anche un testo alternativo (`alt`).  
   - Metodo `to_dict()` per serializzare in dizionario Python.

4. **template_builder/widgets.py**  
   - Contiene tutti i widget personalizzati basati su Tkinter/ttk.  
   - In particolare, `SortableImageRepeaterField`: widget che consente di aggiungere, rimuovere, ordinare e validare righe di URL immagine + ALT.  
   - `LiveValidationEntry`, `PlaceholderField`, `TextField`, ecc. (non modificati in F6‐F7).

5. **template_builder/services/**  
   - `images.py`: servizi relativi alle immagini, in particolare `validate_url(url: str) -> bool` e `download_image(url: str) -> bytes`.  
   - `storage.py`: salvataggio/lettura del progetto (JSON), migrazione v1→v2 usando `bind_steps` per popolare `STEPS` e `STEP{n}_IMG_ALT`.  
   - `text.py`: funzioni di manipolazione testo (rimozione tag HTML, conversione Markdown, sostituzione segnaposto).

6. **template_builder/infrastructure/**  
   - `preview_engine.py`: anteprima del template in una finestra Tkinter usando Jinja2.  
   - `ui_utils.py`: utility generiche per la UI (centratura finestre, popup di errore, tooltip).  
   - `validators.py`: funzioni di validazione generali (date, email, numeri).

7. **template_builder/legacy/**  
   - Backup del codice precedente: versioni obsolete di `builder_core`, `preview_engine`, `ui_utils`, `validators`.  
   - Non vengono più utilizzate, ma conservate a mo’ di riferimento.

8. **template_builder/templates/**  
   - Contiene tutti i template Jinja/HTML di esempio, destinati all’esportazione o all’anteprima.

9. **tests/**  
   - Contiene l’intera suite di test pytest/unittest, coprendo tanto il codice di business (model, step_image, services) quanto i widget GUI e l’integrazione Jinja.

---

## 2. Flusso dei Dati

1. **Input Utente (GUI) – Tab “Ricetta”**  
   - L’utente popola i campi di testo per ogni passaggio (es. STEP1, STEP2, …).  
   - Al salvataggio o in tempo reale, il sistema crea segnaposto di tipo “immagine_step_{n}” nel tab “Immagini”.

2. **Tab “Immagini” – Inserimento URL + ALT**  
   - Ogni “riga” del widget `SortableImageRepeaterField` corrisponde a un URL immagine + testo alternativo (ALT).  
   - Il widget effettua validazione live:  
     - Se l’URL è valido (regex base) e l’ALT non è vuoto → bordo verde.  
     - Altrimenti → bordo rosso.  
   - Permette di aggiungere o rimuovere righe, oltre a spostarle su/giù per modificare l’ordine.

3. **Raccolta Dati – Metodo `_collect()` in `builder_core.py`**  
   - Recupera:  
     - I testi dei passi (`data.get("STEP{i}")` per i=1..9).  
     - L’elenco degli URL immagine (`data.get("IMAGES_STEP")`).  
     - L’elenco degli ALT immagine (`data.get("ALTS_STEP")`).  
   - Chiama `bind_steps(texts, images, alts)` se `alts` esiste, altrimenti `bind_steps(texts, images)`.  
   - `bind_steps` genera una lista di oggetti `StepImage(img, alt, text, order)`, eseguendo validazione:  
     - Se per una posizione i `img` non è vuoto e `alt` è vuoto → solleva `ValueError`.  
     - Se né `img` né `text` sono forniti → ignora lo slot.  
   - Converte ogni `StepImage` in dict e popola:  
     ```python
     data["STEPS"] = [s.to_dict() for s in steps]
     for s in steps:
         data[f"STEP{s.order}_IMG_ALT"] = s.alt
     ```
   - Ritorna il dizionario `data` pronto per l’esportazione o l’anteprima.

4. **Esportazione/Anteprima**  
   - Il dizionario `data` viene passato a:  
     - Il modulo di esportazione JSON (`services/storage.py`) per il salvataggio su file.  
     - Il motore di anteprima Jinja (`infrastructure/preview_engine.py`) per generare HTML e mostrarlo in una finestra.

5. **Migrazione della Struttura Dati (v1→v2)**  
   - Nel caso si carichi un progetto creato con versione precedente, il metodo `_migrate_v1_to_v2()` di `services/storage.py` estrae campi legacy:  
     - `STEP{i}`, `IMAGES_STEP_V1`, `ALTS_STEP`.  
   - Li passa a `bind_steps` per ottenere il nuovo formato `STEPS` + `STEP{i}_IMG_ALT`.

---

## 3. Pattern di Progettazione

1. **Modello‐Vista‐Controller (MVC) semplificato**  
   - **Modello**: `template_builder/model.py` (StepImage, eventuali altri dataclass).  
   - **Vista (GUI)**: `template_builder/widgets.py` + `builder_core.run_app()` che fa partire la finestra principale.  
   - **Controller/Business Logic**: `template_builder/builder_core.py`, `step_image.py`, `services/`, `infrastructure/`.

2. **Separazione dei Servizi**  
   - Il codice relativo alla validazione e manipolazione delle immagini è isolato in `services/images.py`.  
   - Le funzionalità di salvataggio/caricamento JSON sono in `services/storage.py`.  
   - I template HTML statici sono in `templates/`.

3. **Forward Compatibility – Legacy Folder**  
   - Tutte le versioni precedenti del codice restano in `template_builder/legacy/`, così da poter recuperare rapidamente comportamenti obsoleti senza intasare il codice corrente.

4. **Utilizzo Esteso dei Test**  
   - Suite di test che copre:  
     - Modello (validazione StepImage).  
     - Funzioni helper (`_strip_html`, filtri, servizi testo).  
     - Binding e validazione (bind_steps, step_image_helpers).  
     - Integrazione Jinja.  
     - Test GUI (widgets) con supporto headless (xvfb) e fallback in caso di assenza di Tk/Ttk.  
     - Test di migrazione (storage).

---

## 4. Dipendenze Esterne

- **Python ≥ 3.10** (compatibilità estesa fino a 3.12).  
- **Tkinter/Ttk** (per GUI).  
  - Su GitHub Actions, viene installato via `apt-get install python3-tk xvfb`.  
  - I test GUI vengono eseguiti con `xvfb-run` per evitare schermate effettive.  
- **Jinja2** (per rendering dei template).  
- **Markdown** (per eventuali conversioni da Markdown a HTML in `services/text.py`).  
- **Requests** (utilizzato solo per `download_image`, non coperto dai test).  

---

## 5. Risorse di Supporto

- **tests/**:  
  - Oltre ai test di unità, la cartella contiene test di integrazione e regressione completi.  
  - I test GUI saltano correttamente in assenza di display, grazie a `self.skipTest("Tkinter/Display non disponibile")`.  
- **docs/CHANGELOG.md**:  
  - Storia delle versioni e note di rilascio (vede in dettaglio F6‐F7).  

---

## 6. Conclusioni

Questa panoramica completa dell’architettura illustra come i diversi moduli cooperino per offrire:  
- un’interfaccia grafica per inserire testi e immagini con validazione live;  
- un motore di binding e validazione dei dati (bind_steps);  
- un sistema di esportazione JSON e anteprima Jinja;  
- test di qualità del codice (unitari, di integrazione, GUI) con supporto headless.  

Ogni sezione del codice è documentata e coperta da test, e il repository è pronto per essere esteso alle fasi successive della roadmap (ad esempio, alert al momento del salvataggio se mancano ALT, integrazione con servizi cloud, ecc.).

