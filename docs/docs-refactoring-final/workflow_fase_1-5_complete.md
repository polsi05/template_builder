
# Roadmap Completa del Workflow – TEMPLATE_BUILDER

---

## 📜 FASI DEL CICLO DI LAVORO – TEMPLATE\_BUILDER (11 fasi)

| Fase                                  | Descrizione                                                                   | Output atteso                                                                                                             | Dipendenze         |
| ------------------------------------- | ----------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------- | ------------------ |
| **F0 – Validazione Preliminare dei File Originali** | Lettura umana‐assistita di ogni file: traduzione in linguaggio semplice, esempi di flusso condizionale, simulazioni AI–utente per confermare che **ciascun file rispecchi la logica voluta dall’utente** | - Per ogni file/classe/funzione: descrizione in linguaggio quotidiano con “se…, allora…, altrimenti…”<br>- Simulazione Q&A (esempi reali con dati fittizi), incluso handling di un riscontro “negativo” per mostrare come la logica viene adeguata<br>- Report di conferma finale su coerenza o eventuali discrepanze da risolvere | ZIP progetto + PDF |
| **F1 – Init & Scansione**             | Parsing automatico del repo e della documentazione; estrazione di grafo import, contratti e SBOM    | `dep_graph.json`, `contracts.md`, `sbom.cdx.json`, `baseline_tests.txt`                                                   | F0                 |
| **F2 – BuilderCore stabilizzazione**  | Rifattorizzazione di `template_builder/builder_core.py` con interfacce solide e test associati       | Modulo `builder_core.py` con interfaccia chiara, test al 100 %, nessun import circolare, CRT approvato                       | F1                 |
| **F3 – Refactor `widgets.py`**        | Separazione della logica widget dal layer UI; introduzione di un test per `Entry/StepEditor`         | `widgets.py` aggiornato, test stub in `tests/test_widgets/`, coverage > baseline, lint zero                                    | F2                 |
| **F4 – `step_image` compliance**      | Allineamento di `bind_steps()`, `sort_steps()`, `renumber_steps()` secondo la nuova logica; stub di fallback HTML | `step_image.py` modulare, docstring in stile Google, test property-based in `tests/test_step_image/`                         | F2                 |
| **F5 – `services/text.py` + `utils`** | Migrazione delle funzioni legacy di formattazione (`smart_paste`, `interpolate_alt`), parsing Jinja, docstring + test | `text.py` completo, property‐test in `tests/test_text/`, typing completo, CRT firmato                                       | F2                 |
| **F6 – `services/storage.py`**        | Standardizzazione delle operazioni di I/O file (read/write/delete/list); inserimento fallback locale/cloud    | `storage.py` aggiornato, test isolati in `tests/test_storage_service/`, mock S3/fakefs                                       | F5                 |
| **F7 – `infrastructure/preview_engine.py` rendering engine**  | Composizione del motore di rendering preview (static + Jinja2); disabilitazione modifiche inline; test        | `preview_engine.py` aggiornato, fallback HTML corretto, test in `tests/test_preview_engine/`                                  | F4, F6             |
| **F8 – Test di integrazione**         | Implementazione di `tests/integration/test_full_stack.py` che copre il flusso completo Builder→Preview→Save   | Test di integrazione verdi, marker `@pytest.mark.slow`, coverage 100 % integrazione                                        | F2–F7              |
| **F9 – GUI smoke layer (opzionale)**  | Se presente GUI: test con `pytest-qt` per crash e import                       | Test smoke + avvio GUI su Xvfb, crash = 0 in `tests/test_gui_smoke/`                                                        | opzionale          |
| **F10 – CI + AI‐review finale**        | Aggiornare pipeline CI (`.github/workflows/ci.yml`) con check lint/type/test e integrazione `gpt-review-bot` | File `.github/workflows/ci.yml` completo, badge coverage, trigger AI-review                                                 | Tutte              |
| **F11 – Release v1.0.0**              | Taggare la versione semantica, generare `CHANGELOG.md` con `git-cliff`, eseguire Canary Deploy finale      | Tag `v1.0.0`, `CHANGELOG.md` aggiornato, Canary stabile in staging                                                           | F2–F10             |

---

## 🔐 GARANZIE ANTI‐ROTTURA PER OGNI FASE

- ✅ **CRT completato:** ogni modifica (anche logica/studio preliminare) inizia con un Change Request Template approvato.  
- ✅ **Test stub creato:** almeno un test stub (unit o property) per ogni feature o file validato.  
- ✅ **Pre‐commit (ruff, mypy, black, bandit) tutti verdi:** nessuna commit prosegue senza superare i check locali.  
- ✅ **`dep_graph.json` aggiornato e nessun nuovo ciclo:** controllo automatico import.  
- ✅ **Coverage ≥ baseline (nessun decremento > 1 %):** con test unitari e di integrazione inclusi.  
- ✅ **Latenza canary (p95) non degradata > +20 %:** monitoring in staging.  
- ✅ **Docstring e contratti aggiornati (`contracts.md`):** ogni funzione/class deve avere docstring chiaro.  
- ✅ **README e `CHANGELOG.md` aggiornati con `git-cliff`:** corrispondenza tra commit e note di rilascio.  

---

## F0 – Validazione Preliminare dei File Originali

**Obiettivo:**  
Prima di toccare qualunque riga di codice, l’AI deve leggere **ogni file** (controller, widget, servizi, infrastruttura, modelli) e tradurre la logica in linguaggio quotidiano, esplicitando flussi condizionali (“se … allora … altrimenti …”) e ponendosi come interlocutore con l’utente. In pratica, si costruisce un “contratto verbale” che l’utente conferma prima di procedere.

### 0.1. Descrizione della Fase

1.  **Per ciascun file** (ad esempio, `services/storage.py`, `widgets.py`, `step_image.py`, ecc.), l’AI:

    *   Legge il sorgente completo.

    *   Genera due forme di descrizione:

        *   **Frase “tecnica” semplificata:** una stringa breve che riassume il compito della funzione o classe, con cenni a “se … allora … altrimenti …”.

        *   **Descrizione in linguaggio comune, passo‐per‐passo:** elenca esattamente cosa succede in modo colloquiale, come nell’esempio di `save_file` o `load_file`.

2.  **Simulazione di Q&A**

    *   Dopo ogni descrizione di file/classe/funzione, l’AI include **due** esempi di dialogo (con dati fittizi), in forma sintetica:

        1.  **Utente conferma** (“nulla osta”): la logica è corretta, si procede al file successivo.

        2.  **Risposta “negativa” simulata**: evidenza discrepanze, l’utente chiede di modificare qualche dettaglio, e l’AI mostra il modo in cui adeguerà la descrizione/implementazione.

3.  **Output Atteso di F0**

    *   Un file Markdown (`F0_validation.md`) contenente la descrizione completa (tecnica + colloquiale) di ogni file/classe/funzione, seguita da due brevi dialoghi simulati.

    *   Un elenco finale di “file confermati” e “file da rivedere” (se l’utente ha segnalato discrepanze).

4.  **Vincoli di F0**

    *   **Nessuna modifica al codice vero**: solo lettura e descrizione verbale.

    *   **Verifica dall’utente per ogni descrizione**: la fase procede file per file, avanzando solo se l’utente conferma.

    *   **Nessuna aggiunta/rimozione di file**: non si propone mai di eliminare o creare moduli, si limita a tradurre la logica esistente.


---

### 0.2. Esempio Dettagliato di Descrizione per `services/storage.py`

> **File: `template_builder/services/storage.py`**

#### 0.2.1. Import e contesto generale

*   **Frase “tecnica” semplificata**:

    > “Questo file importa funzioni di binding per gli step (`step_image.bind_steps`), moduli JSON e Jinja2 – usati per migrare, salvare e caricare lo stato, oltre a esportare HTML.”

*   **Descrizione in linguaggio di uso comune, passo‐per‐passo**:

    1.  **Quando serve salvare lo stato corrente del progetto** (ad esempio dopo aver modificato i campi in UI), viene chiamata la funzione `quick_save(state: Dict) -> Path`:

        *   Controlla il percorso `~/.template_builder/history`;

        *   Genera un nome `recipe_<timestamp>.json`;

        *   Converte il `state` (un dizionario) in JSON e lo scrive in quel file;

        *   Restituisce il percorso completo del file salvato.

        *   **Se** la cartella di history non esiste, la crea poi salva (fallisce solo se permessi negati).

        *   **Altrimenti**, salva direttamente.

    2.  **Quando serve caricare un progetto già esistente** (ad es. l’utente clicca “File → Load”): si invoca `load_recipe(path: Union[str, Path]) -> Dict`:

        *   **Se** il file JSON non esiste → solleva subito `FileNotFoundError`, l’UI intercetta e mostra un alert;

        *   **Se** esiste, lo legge con `json.load()`.

        *   Verifica `old["SCHEMA_VERSION"]`:

            *   **Se** è 1 → chiama `_migrate_v1_to_v2(old)` per adattare i vecchi campi (es. da `"IMAGES_STEP"` a una lista di `StepImage`, usando `step_image.bind_steps()` internamente); aggiorna la versione a 2 e restituisce il nuovo dict.

            *   **Altrimenti** restituisce direttamente il dizionario letto.

        *   **Se** succede un errore di parsing JSON → rilancia `ValueError` con descrizione.

    3.  **Quando serve esportare un template in HTML** (es. “File → Export HTML”): si chiama `export_html(ctx: Dict, template_path: str, **env_kw) -> str`:

        *   **Se** Jinja2 non è installato → solleva `ImportError`; l’UI cattura e suggerisce di installare “`pip install jinja2`”.

        *   **Altrimenti**, carica `template_path` (un file Jinja2 con segnaposto come `{{ TITLE }}`, `{{ STEPn_IMG_ALT }}`, ecc.), chiama `jinja2.Environment(loader=FileSystemLoader(...))` e `render(ctx)` per produrre la stringa HTML.

        *   Restituisce l’HTML renderizzato.

        *   **Se** il template contiene errori di sintassi Jinja2 → rilancia `TemplateSyntaxError`, l’UI mostra popup.

    4.  **Classe `UndoRedoStack`** (gestione dello stack di undo/redo):

        *   Ha un attributo privato `_stack: List[Dict]` e `_position: int`.

        *   `push(state: Dict)`: aggiunge una copia profonda (`deepcopy`) di `state` alla lista; aggiorna `_position`.

        *   `undo() -> Dict`:

            *   **Se** `_position > 0`: decrementa `_position`, restituisce `_stack[_position]`;

            *   **Altrimenti**: restituisce l’ultimo stato e non decrementa oltre (è già al limite).

        *   `redo() -> Dict`:

            *   **Se** `_position < len(_stack) - 1`: incrementa `_position`, restituisce `_stack[_position]`;

            *   **Altrimenti**: restituisce l’ultimo (non fa nulla).

    5.  **Funzioni helper interne**:

        *   `_timestamp() -> str`: costruisce stringa `YYYYMMDD_HHMMSS`;

        *   `_migrate_v1_to_v2(old: Dict) -> Dict`:

            *   Controlla se `old["SCHEMA_VERSION"] == 1`;

            *   Legge `old["IMAGES_STEP"]`, `old["ALTS_STEP"]`, `old["TEXTS_STEP"]`;

            *   Chiama `bind_steps(texts, images, alts)` per ottenere lista di `StepImage` con `order` corretto;

            *   Costruisce `"STEPS": [ StepImage(...).to_dict(), … ]`;

            *   Restituisce un nuovo dict con `SCHEMA_VERSION = 2`.


---

#### 0.2.2. Simulazione Q&A per `services/storage.py`

**Esempio 1 – Utente conferma (nulla osta)**

> **AI (bot):** “Ho descritto la funzione `save_file` in ‘ottimo linguaggio colloquiale’, spiegando come gestisce la cartella, l’apertura in modalità carr... (continua)...
