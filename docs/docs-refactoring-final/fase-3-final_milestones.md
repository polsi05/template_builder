
# Fase 3 – Pianificazione delle Milestone Progressive

Ogni milestone segue rigorosamente il workflow anti-rottura:
1. **CRT (Change Request Template):** definizione titolo, descrizione, moduli impattati, effetti collaterali, piano rollback.
2. **Stub di test:** creazione di almeno un test stub (unit/property/integration) per ogni funzionalità.
3. **Modifica del codice:** generazione del diff minimo necessario.
4. **Checks automatici:** pre-commit (ruff, black, mypy, bandit), CI (lint + test), hook grafo import.
5. **AI‐review:** commenti automatici su eventuali deviazioni.
6. **Canary Deploy (solo milestone finali).**

---

## Milestone 1 (M1): Aggiornamento di `builder_core.py`

- **CRT 3.1**
  - **Titolo:** `M1 · builder_core: Gestione immagini mancanti e validazione input`
  - **Descrizione:**
    - Sostituire errore “immagine mancante” con `services.images.get_placeholder()` in `export_to_ebay`.
    - Aggiungere chiamata a `infrastructure.validators.check(input)` prima di `build_preview()`.
  - **Moduli impattati:** `template_builder/builder_core.py`, `template_builder/services/images.py`, `template_builder/infrastructure/validators.py`
  - **Effetti collaterali previsti:**
    - Modifica flusso di `export_to_ebay`: se mancano immagini, ora usa placeholder.
    - Inserimento di validazione pre‐preview potrebbe generare errori di input bloccanti.
  - **Piano rollback:** Revert patch a commit precedente; rimuovere chiamata a `get_placeholder()` e `validators.check()`.

- **Test Stub 3.1**
  - `tests/test_builder_core/test_export_with_missing_images.py`
    ```python
    def test_export_with_missing_images(tmp_path):
        from template_builder.builder_core import BuilderApp
        # Setup input con immagine mancante
        input_data = {..., "images": []}
        app = BuilderApp(...)
        # Export non fallisce, restituisce ZIP contenente placeholder.jpg
        result = app.export_to_ebay(input_data)
        assert "placeholder.jpg" in result.list_files()
    ```
  - `tests/test_builder_core/test_preview_invalid_input.py`
    ```python
    import pytest
    from template_builder.builder_core import BuilderApp
    def test_preview_invalid_input_raises():
        bad_input = {..., "field_mandatory": None}
        app = BuilderApp(...)
        with pytest.raises(ValueError):
            app.build_preview(bad_input)
    ```

- **Modifiche Necessarie 3.1**
  - In `builder_core.py`:
    1. Importa `from template_builder.services.images import get_placeholder`
    2. Nel metodo `export_to_ebay`, sostituisci:
       ```python
       if image_missing:
           raise ExportError("Manca immagine")
       ```
       con
       ```python
       if image_missing:
           images_list.append(get_placeholder())
       ```
    3. Importa `from template_builder.infrastructure.validators import check`
    4. All’inizio di `build_preview`, aggiungi:
       ```python
       check(input_data)
       ```
  - Aggiungi in `services/images.py` la funzione:
    ```python
    def get_placeholder() -> bytes:
        # Restituisce i byte di un’immagine placeholder standard
        path = Path(__file__).parent / "assets" / "placeholder.png"
        return path.read_bytes()
    ```
  - In `infrastructure/validators.py`, definire:
    ```python
    def check(input_data: dict):
        if not input_data.get("required_field"):
            raise ValueError("Campo obbligatorio mancante")
    ```
- **Checks 3.1**
  - Esegui `pre-commit run --all-files`.
  - Esegui `pytest tests/test_builder_core/ -q`.
  - Esegui hook “grafo import”: nessun nuovo ciclo deve emergere.

- **Diff 3.1**
  - Restituire un patch Git minimo contenente solo le righe modificate.

---

## Milestone 2 (M2): Aggiornamento di `widgets.py`

- **CRT 3.2**
  - **Titolo:** `M2 · widgets: bind_steps dopo drag&drop`
  - **Descrizione:**
    - Aggiungere listener `<ButtonRelease-1>` per richiamare `bind_steps()` quando l’utente rilascia una riga.
    - Verificare che il tab Preview rimanga read‐only (nessuna modifica inline).
  - **Moduli impattati:** `template_builder/widgets.py`, `template_builder/step_image.py`
  - **Effetti collaterali:**
    - Eventuali modifiche al comportamento drag&drop; rischio di rallentamento UI.
  - **Piano rollback:** Revert patch in `widgets.py`.

- **Test Stub 3.2**
  - `tests/test_widgets/test_bind_steps_after_drag.py`
    ```python
    import pytest
    from template_builder.widgets import SortableImageRepeaterField
    from tkinter import Tk
    def test_bind_steps_after_drag(snapshot):
        root = Tk()
        field = SortableImageRepeaterField(root)
        # Simulazione di drag&drop
        field.add_row("img1.png")
        field.add_row("img2.png")
        field.simulate_drag(from_index=0, to_index=1)
        field.on_button_release(None)
        assert field.steps_sequence == ["img2.png", "img1.png"]
        root.destroy()
    ```

- **Modifiche Necessarie 3.2**
  - In `widgets.py`:
    ```python
    self.treeview.bind("<ButtonRelease-1>", lambda e: bind_steps(self.treeview))
    ```
    (dove `bind_steps` importa da `step_image`).
  - Controllare che non ci siano `<Key>` binding sul preview; se presenti, commentarli.

- **Checks 3.2**
  - `pre-commit run --all-files`
  - `pytest tests/test_widgets/ -q`
  - Hook grafo import.

- **Diff 3.2**
  - Patch con nuove righe di binding e rimozione eventuali binding inline.

---

## Milestone 3 (M3): Completamento di `services/text.py`

- **CRT 3.3**
  - **Titolo:** `M3 · services/text: Porting funzioni legacy e property test`
  - **Descrizione:**
    - Migrare funzioni di formattazione avanzata da `legacy/template_builder_legacy.py`.
    - Aggiungere almeno una property‐based test per la funzione più complessa (es. `smart_format()`).
  - **Moduli impattati:** `template_builder/services/text.py`, `legacy/template_builder_legacy.py`
  - **Effetti collaterali:**
    - Potenziali differenze di output su casi limite; occorre validare test.
  - **Piano rollback:** Revert patch in `services/text.py`.

- **Test Stub 3.3**
  - `tests/test_text/test_text_formatting_property.py`
    ```python
    from hypothesis import given, strategies as st
    from template_builder.services.text import smart_format
    @given(st.text(), st.text())
    def test_smart_format_idempotent(a, b):
        result1 = smart_format(a, b)
        result2 = smart_format(a, b)
        assert result1 == result2
    ```

- **Modifiche Necessarie 3.3**
  - Copiare `smart_format`, `sanitize_text`, ecc. da:
    ```python
    # legacy/template_builder_legacy.py
    def smart_format(text, pattern):
        ...
    ```
  - Sistemare eventuali import mancanti, aggiungere type hints, docstring.
  - Inserire `__all__ = [...]` con le funzioni pubbliche.

- **Checks 3.3**
  - `pre-commit run --all-files`
  - `pytest tests/test_text/ -q`
  - Hook grafo import.

- **Diff 3.3**
  - Mostrare patch con il corpo di `smart_format` e aggiunta di property test.

---

## Milestone 4 (M4): Completamento di `services/images.py`

- **CRT 3.4**
  - **Titolo:** `M4 · services/images: Placeholder e gestione immagini mancanti`
  - **Descrizione:**
    - Implementare `get_placeholder()` (restituisce dati immagine).
    - Adeguare funzioni di caricamento e ridimensionamento per usare placeholder quando l’immagine non esiste.
  - **Moduli impattati:** `template_builder/services/images.py`
  - **Effetti collaterali:**
    - Output immagine modificato potrebbe cambiare look&feel di preview.
  - **Piano rollback:** Revert patch in `services/images.py`.

- **Test Stub 3.4**
  - `tests/test_images/test_get_placeholder_default.py`
    ```python
    def test_get_placeholder_default():
        from template_builder.services.images import get_placeholder
        data = get_placeholder()
        assert isinstance(data, (bytes, bytearray))
        # Opzionale: validare dimensione minima
        assert len(data) > 0
    ```

- **Modifiche Necessarie 3.4**
  - Aggiungere:
    ```python
    def get_placeholder() -> bytes:
        path = Path(__file__).parent / "assets" / "placeholder.png"
        return path.read_bytes()
    ```
  - In funzione `load_image(path)`, sostituire:
    ```python
    if not path.exists():
        raise ImageError("File non trovato")
    ```
    con:
    ```python
    if not path.exists():
        return get_placeholder()
    ```

- **Checks 3.4**
  - Pre-commit + `pytest tests/test_images/`
  - Hook grafo import.

- **Diff 3.4**
  - Patch che mostra `get_placeholder()` e modifica di `load_image`.

---

## Milestone 5 (M5): Verifica `infrastructure/preview_engine.py`

- **CRT 3.5**
  - **Titolo:** `M5 · preview_engine: Render read-only e validazione segnaposto`
  - **Descrizione:**
    - Disabilitare qualsiasi binding che permetta editing inline dell’HTML preview.
    - Assicurarsi che i segnaposto Jinja2 ereditati siano gestiti correttamente.
  - **Moduli impattati:** `template_builder/infrastructure/preview_engine.py`, `template_builder/filters.py`
  - **Effetti collaterali:**
    - Preview non deve più essere editabile; utente deve usare moduli form dedicati.
  - **Piano rollback:** Ripristinare binding originali su click o focus.

- **Test Stub 3.5**
  - `tests/test_preview_engine/test_preview_read_only.py`
    ```python
    def test_preview_read_only():
        from template_builder.infrastructure.preview_engine import PreviewEngine
        engine = PreviewEngine()
        html = engine.render({'foo': 'bar'})
        # Simulare evento edit (tentativo di modifica): nessuna eccezione ma output invariato
        assert "contenteditable" not in html
    ```

- **Modifiche Necessarie 3.5**
  - Rimuovere o commentare righe del tipo:
    ```python
    element.setAttribute("contenteditable", "true")
    ```
  - Verificare che i filtri Jinja2 registrati (in `filters.py`) includano tutti quelli del legacy.

- **Checks 3.5**
  - Pre-commit + `pytest tests/test_preview_engine/`
  - Hook grafo import.

- **Diff 3.5**
  - Patch con rimozione binding e registrazione filtri.

---

## Milestone 6 (M6): Adeguamento `infrastructure/ui_utils.py` e `validators.py`

- **CRT 3.6**
  - **Titolo:** `M6 · ui_utils & validators: Controlli layout e campi obbligatori`
  - **Descrizione:**
    - Verificare che i metodi di `ui_utils` non producano widget fuori layout; aggiungere log/exception in caso di overflow.
    - In `validators.py`, implementare `check_mandatory_fields(data: dict)`.
  - **Moduli impattati:** `template_builder/infrastructure/ui_utils.py`, `template_builder/infrastructure/validators.py`
  - **Effetti collaterali:**
    - Layout possibili modifiche di padding/posizionamento.
  - **Piano rollback:** Rimuovere logica extra in `ui_utils`, `validators`.

- **Test Stub 3.6**
  - `tests/test_ui_utils/test_ui_widget_positions.py`
    ```python
    def test_ui_widget_positions():
        from template_builder.infrastructure.ui_utils import position_widget
        # Simulare creazione widget in finestra fittizia
        # Se esce da bordo, raise LayoutError
        ```
  - `tests/test_validators/test_validators_mandatory.py`
    ```python
    import pytest
    from template_builder.infrastructure.validators import check_mandatory_fields
    def test_validators_mandatory():
        data = {"name": "", "email": ""}
        with pytest.raises(ValueError):
            check_mandatory_fields(data)
    ```

- **Modifiche Necessarie 3.6**
  - In `ui_utils.py`, aggiungere controllo bounding:
    ```python
    if widget.x + widget.width > parent.width:
        raise LayoutError("Widget fuori layout")
    ```
  - In `validators.py`:
    ```python
    def check_mandatory_fields(data: dict):
        for field, value in data.items():
            if not value:
                raise ValueError(f"{field} è obbligatorio")
    ```

- **Checks 3.6**
  - Pre-commit + `pytest tests/test_ui_utils/` e `pytest tests/test_validators/`
  - Hook grafo import.

- **Diff 3.6**
  - Patch con il controllo di posizione e la funzione `check_mandatory_fields`.

---

## Milestone 7 (M7): Revisione di `step_image.py`

- **CRT 3.7**
  - **Titolo:** `M7 · step_image: Verifica bind/sort/renumber`
  - **Descrizione:**
    - Assicurarsi che `bind_steps()`, `sort_steps()`, `renumber_steps()` rispettino la nuova logica di sequenza immagine (coerenza tra filtri e storage).
  - **Moduli impattati:** `template_builder/step_image.py`, `template_builder/services/images.py`
  - **Effetti collaterali:**
    - Sequenza di immagini potrebbe cambiare leggermente nell’ordine se la logica di sort cambia.
  - **Piano rollback:** Revert patch in `step_image.py`.

- **Test Stub 3.7**
  - `tests/test_step_image/test_step_image_bind_sort_renum.py`
    ```python
    from template_builder.step_image import bind_steps, sort_steps, renumber_steps
    def test_step_image_bind_sort_renum():
        steps = [{"order":2, "src":"b.png"}, {"order":1,"src":"a.png"}]
        sorted_steps = sort_steps(steps)
        assert [s["src"] for s in sorted_steps] == ["a.png","b.png"]
        renumbered = renumber_steps(sorted_steps)
        assert [s["order"] for s in renumbered] == [1,2]
        bound = bind_steps(renumbered)
        assert isinstance(bound, list)
    ```

- **Modifiche Necessarie 3.7**
  - Assicurarsi che `sort_steps()` usi `key=lambda x: x["order"]`.
  - Verificare che `renumber_steps()` assegni numeri consecutivi a partire da 1.
  - Confermare che `bind_steps()` ritorni lista di dict con chiavi `order`, `src`, `alt`.
  - Non rimuovere funzioni esistenti; solo allineare la logica.

- **Checks 3.7**
  - Pre-commit + `pytest tests/test_step_image/`
  - Hook grafo import.

- **Diff 3.7**
  - Patch con la logica di sort/renum e binding.

---

## Milestone 8 (M8): Verifica di `filters.py` e `assets.py`

- **CRT 3.8**
  - **Titolo:** `M8 · filters & assets: Registrazione filtri e gestione duplicati`
  - **Descrizione:**
    - In `filters.py`, assicurarsi che tutti i filtri custom (ereditati) siano registrati per Jinja2.
    - In `assets.py`, verificare che `collect_assets()` eviti file duplicati e ignori file non rilevanti.
  - **Moduli impattati:** `template_builder/filters.py`, `template_builder/assets.py`
  - **Effetti collaterali:**
    - Potenziale modifica di nomi asset; potrebbe cambiare percorsi nei template.

- **Test Stub 3.8**
  - `tests/test_filters/test_filters_registration.py`
    ```python
    from jinja2 import Environment
    from template_builder.filters import register_filters
    def test_filters_registration():
        env = Environment()
        register_filters(env)
        assert "sanitize" in env.filters
    ```
  - `tests/test_assets/test_collect_assets_no_duplicates.py`
    ```python
    from template_builder.assets import collect_assets
    def test_collect_assets_no_duplicates(tmp_path):
        # Creare due file con nome identico in subfolder
        # Assicurarsi che collect_assets restituisca un solo percorso per nome
    ```

- **Modifiche Necessarie 3.8**
  - In `filters.py` aggiungere:
    ```python
    def register_filters(env):
        env.filters["sanitize"] = sanitize
        # aggiungere altri filtri ereditati
    ```
  - In `assets.py`:
    ```python
    seen = set()
    for f in all_files:
        if f.name not in seen:
            seen.add(f.name)
            result.append(f)
    ```

- **Checks 3.8**
  - Pre-commit + `pytest tests/test_filters/` e `pytest tests/test_assets/`
  - Hook grafo import.

- **Diff 3.8**
  - Patch che mostra la registrazione dei filtri e rimozione duplicati.

---

## Milestone 9 (M9): Test di integrazione e CI finale

- **CRT 3.9**
  - **Titolo:** `M9 · integration: Test full-stack + pipeline CI`
  - **Descrizione:**
    - Creare test di integrazione in `tests/integration/` per coprire flusso completo: 
      - `builder_core.build_preview()` → `preview_engine` → `services/storage`  
    - Aggiornare `.github/workflows/ci.yml`:
      - Step lint, test unit/property, test di integrazione, test di coverage.
      - Aggiungere `sbom` check e `osv-scanner`.

  - **Moduli impattati:** Tutto il progetto + file CI (`.github/workflows/ci.yml`).
  - **Effetti collaterali:**
    - Possibili fallimenti di integrazione richiedono fix preliminari.
  - **Piano rollback:** Rimuovere test di integrazione e ripristinare vecchia pipeline.

- **Test Stub 3.9**
  - `tests/integration/test_full_stack.py`
    ```python
    def test_full_stack_flow(tmp_path):
        from template_builder.builder_core import BuilderApp
        input_data = {..., "images": []}
        app = BuilderApp(...)
        html = app.build_preview(input_data)
        # Verifica placeholder e validazione
        assert "<img" in html
        zip_path = tmp_path / "out.zip"
        app.export_to_ebay(input_data, output=zip_path)
        assert zip_path.exists()
    ```

- **Modifiche Necessarie 3.9**
  - Aggiungere file `tests/integration/test_full_stack.py`.
  - Aggiornare `.github/workflows/ci.yml`:

    ```yaml
    jobs:
      lint-test:
        ...
        - run: pytest --maxfail=1 --disable-warnings -q
      integration-test:
        needs: lint-test
        steps:
          - uses: actions/checkout@v4
          - uses: actions/setup-python@v5
            with: {python-version: '3.12'}
          - run: pip install -e .[test]
          - run: pytest tests/integration/ -q
          - run: cyclonedx-py --output sbom.cdx.json
          - run: osv-scanner --file=requirements.txt
    ```

- **Checks 3.9**
  - CI GitHub Actions: job `lint-test` e `integration-test` verdi.
  - Coverage totale ≥ baseline + 1%.

- **Diff 3.9**
  - Patch per `ci.yml` e aggiunta test integration.

---

## Milestone 10 (M10): Tag di Release e Canary Deploy

- **CRT 3.10**
  - **Titolo:** `M10 · Release v1.0.0 e Canary Deploy`
  - **Descrizione:**
    - Taggare il commit corrente come `v1.0.0` (semver).
    - Generare `CHANGELOG.md` con `git-cliff`.
    - Eseguire “Canary Deploy” su container o ambiente di staging.
  - **Moduli impattati:** Nessuno, solo file di release e configurazione.
  - **Effetti collaterali:**
    - Possibili bug emersi in canary devono essere risolti con hotfix.
  - **Piano rollback:** Revert tag e rollback container alla versione precedente.

- **Test Stub 3.10**
  - Nessuno specifico: verificare che il release automatizzato non fallisca.

- **Modifiche Necessarie 3.10**
  - Aggiungere script `release.sh`:
    ```bash
    git tag v1.0.0
    git push --tags
    git-cliff --config .gitcliff.toml > CHANGELOG.md
    ./deploy_canary.sh
    ```
  - Configurare `deploy_canary.sh` per eseguire push del container su registry di staging.

- **Checks 3.10**
  - Verifica che `v1.0.0` esista nel repo.
  - Verifica che `CHANGELOG.md` includa le voci dalla milestone 1 a 9.
  - Verifica p95 latency canary con OpenTelemetry (< baseline + 20%).

- **Diff 3.10**
  - Patch che aggiunge `release.sh`, `deploy_canary.sh` e aggiornamenti `CHANGELOG.md`.

---

**Fine Fase 3 – Pianificazione Milestone**

Ogni milestone è ordinata e incrementale: partendo dal modulo centrale `builder_core`, prosegue con UI, servizi, infrastruttura, step_image, filtri, test di integrazione e termina con release. Tutti i task rispettano il workflow anti-rottura, iniziano con CRT, creano stub test, eseguono controlli automatici e generano patch minime.
