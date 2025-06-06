**ROADMAP.md**

````markdown
# ROADMAP per lo Sviluppatore C

Questo documento definisce le attività necessarie per completare il progetto **Template Builder**, con particolare attenzione al refactoring, ai test, alla CI/CD, al packaging, al rilascio e alla risoluzione delle feature legacy (F9–F18). Ogni sezione identifica obiettivi concreti, priorità e dipendenze tra task.

---

## 1. Completamento Feature Legacy (F9–F18)

### F9 – Smart-Scroll Notebook
- **Stato attuale**:  
  - Binding `ui_utils.bind_mousewheel(self.nb)` attivo solo a livello di `Notebook`, non sui Canvas interni.  
- **Obiettivo**:  
  - Applicare binding `bind_mousewheel()` a ogni widget scrollabile (Canvas) all’interno di ciascuna Tab.  
  - Garantire scroll fluido verticale orizzontale su Linux, macOS e Windows, intercettando `<MouseWheel>`, `<Button-4>`, `<Button-5>`.  
- **Attività**:  
  1. Individuare in `builder_core.py` la creazione dei Canvas interni e applicare `ui_utils.bind_mousewheel(canvas_widget)`.  
  2. Aggiungere test automatici in `tests/test_smart_scroll.py` per verificare che lo scroll sia effettivamente reindirizzato anche all’interno dei singoli Canvas.  

### F10 – UI Polish / Tema Scuro (Dark-Bootstrap)
- **Stato attuale**:  
  - Tentativo di `from ttkbootstrap import Style; Style('darkly')` in avvio, ma se `ttkbootstrap` non installato non succede nulla.  
  - Mancano stili centralizzati e tema di fallback “chiaro”.  
- **Obiettivo**:  
  - Integrare un tema “darkly” completo se `ttkbootstrap` è disponibile; altrimenti, definire un tema di default chiaro con colori centralizzati in `assets.PALETTE`.  
  - Uniformare margini, padding, bordi, font, dimensioni degli elementi UI.  
- **Attività**:  
  1. Creare modulo interno `infrastructure/theme.py` che gestisca il caricamento dinamico di `ttkbootstrap.Style('darkly')` e, se non presente, applichi funzioni di styling custom su widget base (usando `PALETTE`).  
  2. Aggiungere opzione via menu (es. **View → Theme → Dark/Light**) per consentire switch runtime del tema.  
  3. Aggiornare widget (`widgets.py`) per usare parametri di colore e stile definiti in `PALETTE`, evitando hard-coding.  
  4. Scrivere test per verificare che, in assenza di `ttkbootstrap`, la UI rimanga coerente in “light mode”.

### F11 – Diff-Validator Segnaposto (Audit Automatica)
- **Stato attuale**:  
  - Metodo `audit_placeholders()` in `builder_core.py` mostra in dialogo l’elenco “FOUND vs MISSING”, ma non colora i widget né viene eseguito automaticamente al caricamento di un nuovo template.  
- **Obiettivo**:  
  - Integrare audit automatico durante `load_recipe()` e `reload_template()`: segnalare nei widget (campo testo, repeater immagini) i placeholder mancanti (bordo giallo) o eccessivi (bordo rosso).  
  - Mantenere comunque la possibilità di audit manuale via menu **Edit → Audit Segnaposti**.  
- **Attività**:  
  1. Modificare `builder_core.load_recipe()` e `builder_core.reload_template()` per richiamare internamente `audit_placeholders()` e applicare stili di evidenziazione sui widget:  
     - Bordi gialli su campi mancanti (tag nel template non coperto da contesto).  
     - Bordi rossi su chiavi contesto non usate nel template.  
  2. Aggiungere metodi in `widgets.py` (o in `ui_utils.py`) come `highlight_widget(widget, color)` per semplificare l’applicazione di stili visivi di errore/warning.  
  3. Scrivere test in `tests/test_audit_placeholders.py` per verificare che, dopo `load_recipe()` di un template “incoerente”, i widget corretti siano colorati appropriatamente.

### F12 – Auto-Preview on Change (Completo)
- **Stato attuale**:  
  - `PlaceholderMultiTextField` e spinbox colonne hanno binding a `update_preview()`.  
  - I campi URL/ALT di Hero e Step attuali sono `tk.Entry` semplici SENZA callback, pertanto non triggerano anteprima live.  
- **Obiettivo**:  
  - Estendere binding a tutti gli `Entry` che raccolgono URL immagine e testo ALT (Hero, Step), in modo che ogni modifica in tali campi chiami `update_preview()`.  
- **Attività**:  
  1. In `widgets.py`, creare classe `PlaceholderEntryWithCallback` estesa da `PlaceholderEntry` (o modificare `PlaceholderEntry`) per accettare parametro `on_change` (funzione) e bindare `<KeyRelease>` all’evento `on_change`.  
  2. In `builder_core._build_ui()`, sostituire tutti i campi `Entry` per URL/ALT di Hero e Step con questa nuova classe e passare `update_preview`.  
  3. Aggiornare test in `tests/test_auto_preview.py` per verificare che una modifica in un campo URL attivi immediatamente `update_preview()` (mockare il metodo e controllare chiamata).

### F16 – Column Layout Selector (Spinbox COLS_DESC / COLS_REC)
- **Stato attuale**:  
  - Già completamente migrato.  
  - `builder_core.py`: spinbox per `self.cols_desc` e `self.cols_rec` con `from_=1 to=4` e `command=self.update_preview()` in tab “Images”.  
  - In `_collect()`, i valori vengono letti e inseriti nel contesto Jinja (`COLS_DESC`, `COLS_REC`).  
- **Verifica**:  
  - Controllare che i template Jinja in `templates/` effettivamente usino `COLS_DESC`/`COLS_REC` per disporre le immagini nella griglia corretta.  
  - Se necessario, aggiungere esempi in `templates/` per dimostrare layout a 1, 2, 3 o 4 colonne.

### F18 – Motore di Rendering Modulare (TkinterWeb / CEF / Browser Esterno)
- **Stato attuale**:  
  - `PreviewEngine` supporta solo `tkinterweb.HtmlFrame` o `ScrolledText` come fallback.  
  - Non esiste scelta esplicita tra back-end (CEF, browser esterno) dall’utente.  
- **Obiettivo**:  
  - Ampliare `PreviewEngine` per includere supporto a:  
    1. **CEF (Chromium Embedded Framework)**: se `cefpython3` installato, permettere rendering in CEF (in finestra separata o in widget dedicato).  
    2. **Browser esterno**: se selezionato, salvare HTML in file temporaneo e aprire con `webbrowser.open()`.
  - Offrire opzione via menu **View → Preview Engine → [Embedded HtmlFrame / CEF / External Browser]**.  
- **Attività**:  
  1. In `infrastructure/preview_engine.py`, aggiungere metodi:  
     - `_init_cef()`: prova `import cefpython3`, inizializza minimo CEF per rendering HTML (off-screen).  
     - `_open_in_browser(html_str)`: salva temporaneamente `template_preview.html` e chiama `webbrowser.open()`.  
  2. In `builder_core._build_menu()`, aggiungere sottomenu **Preview Engine** con le tre opzioni (Embedded, CEF, Browser Esterno).  
  3. Memorizzare scelta di back-end in configurazione (es. in `~/.template_builder/config.json`) per renderizzare di conseguenza.  
  4. Aggiornare test in `tests/test_preview_engine.py` per verificare fallback se `cefpython3` non presente o se scelta “Browser Esterno” avvia correttamente `webbrowser.open()` (usare mocking).

---

## 2. Refactoring del Codice

### 2.1 Rimozione Cartella Legacy
- **Finalità**: eliminare la directory `template_builder/legacy/`, che contiene codice monolitico non più referenziato.  
- **Attività**:
  1. Verificare che nessun import punti a `template_builder/legacy/`.  
  2. Spostare eventuali frammenti di codice utile da `legacy/` verso moduli aggiornati (solo se strettamente necessario).  
  3. Eliminare fisicamente la cartella e aggiornare `.gitignore`/`pyproject.toml` se necessario.  
  4. Aggiornare documentazione (`README.md`, `ARCHITECTURE.md`) per rimuovere ogni riferimento a `legacy/`.

### 2.2 Miglioramento Naming e Struttura Package
- **Finalità**: uniformare i nomi di file e classi, aderire a PEP8 e best practice di packaging.  
- **Attività**:  
  1. Controllare `builder_core.py`, `widgets.py`, `services` per uniformare nomi di funzioni e parametri.  
  2. Verificare PEP8 con `flake8`; correggere errori di style, linee troppo lunghe, nomi variabili non descrittivi.  
  3. Riorganizzare eventuali helper in moduli dedicati (`infrastructure/theme.py`, `infrastructure/constants.py`) se è il caso.  
  4. Aggiornare `pyproject.toml` e `setup.py` in base a eventuali spostamenti di moduli.  

---

## 3. Test & CI/CD

### 3.1 Estensione Copertura Test
- **Obiettivo**: portare la copertura di test al 100% sui moduli business e almeno 90% sui componenti GUI (headless).  
- **Attività**:  
  1. Aggiungere test mancanti per:  
     - `services/images.py` (griglie, Data-URI, fallback senza `Pillow`)  
     - `services/text.py` (markup bold/italic, estrazione placeholder, fallback HTML)  
     - `services/storage.py` (migrazione v1→v2, undo/redo, export HTML senza Jinja2)  
     - `widgets.py` (aggiunta/rimozione righe in `SortableImageRepeaterField`, validazione URL, tooltips, placeholder); utilizzare `pytest-xvfb` per testare comportamenti in headless.  
     - `preview_engine.py` (fallback a `ScrolledText`, rendering base, gestione di scelta back-end).  
     - `ui_utils.py` (popup `show_info`, `show_error`, centratura finestra; in test headless verificare che non fallisca).  
  2. Creare cartella `tests/gui/` per test che richiedono Xvfb (marcatore `@pytest.mark.xvfb`).  
  3. Configurare acquisizione di screenshot temporanei (opzionale) su test GUI per debugging.  
  4. Garantire che i test falliscano se la copertura scende al di sotto di soglia prestabilita (es. 90% GUI, 100% business).  

### 3.2 Integrazione Linting / Formattazione
- **Obiettivo**: uniformare stile codice e prevenire errori di formattazione.  
- **Attività**:  
  1. Inserire `flake8` e `black` come job nel workflow CI (`.github/workflows/ci.yml`).  
  2. Definire in `pytest.ini` o in file `.flake8` le regole di style (max line length = 100, ignorare E203/W503, ecc.).  
  3. Integrare step di pre-commit (opzionale) con `pre-commit` per bloccare commit non formattati correttamente.  

### 3.3 Pipeline CI/CD (GitHub Actions)
- **Obiettivo**: definire un workflow completo di CI/CD su GitHub per build, lint, test, report coverage e release automatico.  
- **Attività**:
  1. **`ci.yml`** (trigger su `push` / `pull_request` a `main` e a branch `release/*`):
     - Step 1: checkout codice
     - Step 2: setup Python 3.10
     - Step 3: installare dipendenze core e dev (`pip install .[test]`)
     - Step 4: eseguire `flake8`  
     - Step 5: eseguire `black --check .`
     - Step 6: far girare test con `pytest -q --maxfail=1 --disable-warnings`
     - Step 7: generare report coverage (`coverage run -m pytest` + `coverage xml`)
     - Step 8: pubblicare report coverage (con `codecov` o GitHub Codecov Action).  
  2. **`release.yml`** (trigger su tag `v*.*.*`):
     - Step 1: checkout codice  
     - Step 2: setup Python 3.10  
     - Step 3: installare dipendenze: `pip install .[test]`  
     - Step 4: eseguire test rapidi (smoke test)  
     - Step 5: build wheel e sdist:  
       ```bash
       python -m build
       ```  
     - Step 6: pubblicare su PyPI (usando `pypa/gh-action-pypi-publish@release`)  
     - Step 7: aggiornare automaticamente il `CHANGELOG.md` con label `chore: release vX.Y.Z`.  

---

## 4. Packaging & Rilascio

### 4.1 Aggiornamento `pyproject.toml` / `setup.py`
- **Obiettivo**: completare i metadata e configurare entry points CLI, extras, licenze.  
- **Attività**:  
  1. In `pyproject.toml` (PEP 621), specificare campi:  
     - `name = "template_builder"`  
     - `version = "1.0.0"`  
     - `description`, `authors`, `license = "MIT"`, `readme = "README.md"`, `homepage` (repo GitHub), `keywords`  
     - `[project.optional-dependencies]`:  
       ```toml
       dnd = ["tkinterdnd2>=0.3"]
       webpreview = ["tkinterweb>=0.4"]
       theme = ["ttkbootstrap>=0.5"]
       test = ["pytest>=6.0", "pytest-xvfb>=0.3", "flake8>=3.9", "black>=22.0", "coverage>=5.5"]
       ```
     - `entry-points = { "console_scripts" = ["template-builder = template_builder.__main__:main"] }`.
  2. Rimuovere eventuali duplicazioni in `setup.py` (se presente) e assicurarsi che punti a `pyproject.toml` per la configurazione.  

### 4.2 Definizione del Comando CLI
- **Obiettivo**: esporre comodo comando `template-builder` da terminale.  
- **Attività**:  
  1. In `__main__.py`, definire `def main():` che instanzia `TemplateBuilderApp()` e chiama `mainloop()`.  
  2. Mappare `entry-points` (in `pyproject.toml`) a `template_builder.__main__:main`.  
  3. Verificare che, dopo `pip install template_builder`, il comando `template-builder` sia disponibile nel PATH.  

### 4.3 Creazione del pacchetto e release PyPI
- **Obiettivo**: distribuire su PyPI la versione stabile.  
- **Attività**:  
  1. Eseguire `python -m build` e verificare che generi correttamente `.whl` e `.tar.gz`.  
  2. Testare installazione da PyPI in un nuovo virtual environment:
     ```bash
     pip install template_builder==1.0.0
     python -m template_builder
     ```
  3. Configurare action GitHub `release.yml` per push automatico su PyPI al tag `vX.Y.Z` (usando secret `PYPI_API_TOKEN`).  
  4. Aggiornare il `CHANGELOG.md` con la sezione della nuova release e pubbicarlo su GitHub.  

---

## 5. Documentazione

### 5.1 Aggiornamento dei Documenti Chiave
- **README.md**  
  - Verificare che la sezione “How to Install / How to Run” rimanga aggiornata.  
  - Includere screenshot (opzionale) o GIF brevi per mostrare funzionalità principali (anteprima live, drag & drop).  
  - Verificare che l’elenco moduli rifletta la struttura corrente (rimuovere eventuali riferimenti obsoleti).

- **ARCHITECTURE.md**  
  - Assicurarsi che essa contenga i dettagli di ogni modulo (come da questa roadmap), import map e call-graph sempre aggiornati.  
  - Aggiungere diagramma ad alto livello (controller → servizi → widget → anteprima) se possibile (file `.png` o `.svg` in `docs/`).

- **CHANGELOG.md**  
  - Ogni volta che viene creata una nuova versione (tag Git), aggiornare immediatamente con sezioni puntuali per:
    - Nuovi moduli / classi.  
    - Bugfix critici.  
    - Feature aggiunte.  
    - Migrazioni di schema.  

- **docs/legacy_issues.md**  
  - Rimuovere tutte le feature già completate (F16, F12 parziali se completate).  
  - Segnalare ancora aperte: F9, F10, F11, F18 (con link a issue sul tracker GitHub).  
  - Inserire riferimenti ai file sorgenti (ad es. `builder_core.py`, `widgets.py`, `infrastructure/preview_engine.py`) dove parti di queste feature sono già parzialmente implementate.

- **docs/CONTRIBUTING.md**  
  - Linee guida per contribuire:  
    - Stile di codice (PEP8, `black`, `flake8`).  
    - Convenzioni di commit (tipo “feat:”, “fix:”, “chore:”).  
    - Procedura per inviare pull request (frok, branch dedicato, descrizione, referenze issue).  
    - Come aggiungere nuovi test (posizionamento, naming file, fixture comuni).  

- **docs/BUILD_AND_TEST.md**  
  - Istruzioni dettagliate per eseguire test (headless con `pytest-xvfb`),  
  - Come usare `flake8` e `black`,  
  - Come generare report coverage (`coverage run -m pytest`, `coverage html`).  

- **docs/RELEASE_PROCESS.md**  
  - Passo-per-passo per creare una nuova release:  
    1. Verificare che tutti i test e lint passino su `main`.  
    2. Aggiornare `CHANGELOG.md` e `pyproject.toml` con la nuova versione.  
    3. Creare branch di release (es. `release/1.1.0`).  
    4. Aprire PR verso `main` e ottenere approval.  
    5. Effettuare merge, taggare: `git tag v1.1.0` → `git push --tags`.  
    6. GitHub Actions pubblicherà su PyPI.  
    7. Verificare su PyPI che il pacchetto sia disponibile.  

---

## 6. Ulteriori Feature e Manutenzione

1. **Internazionalizzazione (i18n)**  
   - Valutare integrazione di `gettext` per tradurre stringhe UI.  
   - Creare file `.pot`/`.po` per inglese e italiano (almeno).  
   - Aggiungere selettore lingua in menu **Settings → Language**.

2. **Supporto ad Altri Template**  
   - Abilità di importare template Jinja2 personalizzati da utente; aggiungere file di esempio in `templates/`.  
   - Definire convenzioni per placeholder (nomi chiavi, fallback HTML).

3. **Connettori Esterni**  
   - Possibilità di collegarsi a servizi di invio email (SMTP, SendGrid, MailChimp) per inviare direttamente dal client.  
   - Definire modulo `services/connectors.py` con interfacce astratte e implementazioni concrete.

4. **Plugin System / API Pubblica**  
   - Esporre API Python per creare estensioni (es. plugin per generazione PDF del template).  
   - Strutturare un sistema di plugin che consenta di caricare moduli esterni.

5. **Rilascio di Versione Mobile**  
   - Valutare progetto alternativo su Kivy o PySide per rendere l’app multiplatform su Android e iOS (a lungo termine).

---

*Fine di ROADMAP.md*