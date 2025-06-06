# Template Builder

    **Template Builder** è un toolkit GUI in Python 3.10+ per creare agevolmente **template HTML** (ad es. campagne email) con anteprima live, gestione immagini intuitiva, undo/redo e altro.

---

## Struttura del Progetto

    ```text
    template_builder/
    ├─ __init__.py          # Espone TemplateBuilderApp e funzione main()
    ├─ __main__.py          # Entry-point CLI: avvia l'app
    ├─ assets.py            # Costanti globali (regex segnaposto, colori, cartella di history)
    ├─ builder_core.py      # Controller principale (TemplateBuilderApp)
    ├─ filters.py           # Filtri Jinja2 (stub `steps_bind`)
    ├─ model.py             # Dataclass di dominio: Hero, StepImage, GalleryRow
    ├─ step_image.py        # Funzioni helper per “step-immagine”
    ├─ widgets.py           # Widget Tkinter personalizzati (placeholder, repeater immagini, tooltip)
    ├─ services/            # Servizi “puri” (senza GUI)
    │  ├─ __init__.py       # Re-export API di servizi
    │  ├─ images.py         # Gestione immagini: griglie, placeholder, Data-URI, smart-paste
    │  ├─ text.py           # Manipolazione testo: smart-paste, auto-format, estrazione placeholder
    │  └─ storage.py        # Persistenza JSON, migrazione v1→v2, export HTML, Undo/Redo
    ├─ infrastructure/      # Wrapper e utilità (preview HTML, GUI utils, validator)
    │  ├─ __init__.py
    │  ├─ preview_engine.py # `PreviewEngine`: anteprima HTML con `tkinterweb` o fallback
    │  ├─ ui_utils.py       # Utility GUI generali (popup, centrare finestre, bind mousewheel)
    │  └─ validators.py     # Validatori campi (URL, email, date, non-vuoto)
    ├─ templates/           # Template Jinja2 di esempio per preview/esportazione
    └─ legacy/              # Codice monolitico legacy (solo a scopo di riferimento)

    tests/                   # Suite Pytest per moduli business, widget, servizi

### struttura ad albero della cartella project-root/

    ├── ARCHITECTURE.md
    ├── CHANGELOG.md
    ├── docs
    │   ├── DEV_PLAN_B2.md
    │   ├── IMPACT_MATRIX_B2.md
    │   ├── INTEGRATION_GUIDE_B2.md
    │   ├── legacy_issues.md
    │   ├── MODULE_PROPOSAL_GalleryRow.md
    │   ├── PRECAUTION_CHECKLIST_B2.md
    │   └── project-files.txt
    ├── legacy
    │   ├── __pycache__
    │   │   ├── template_builder.cpython-313.pyc
    │   │   ├── test_placeholders_legacy.cpython-313-pytest-8.3.5.pyc
    │   │   ├── test_placeholders.cpython-313-pytest-8.3.5.pyc
    │   │   └── ui_utils.cpython-313.pyc
    │   ├── mapping_template_builder_legacy.csv
    │   ├── preview_engine_legacy.py
    │   ├── template_builder_legacy.py
    │   ├── test_placeholders_legacy.py
    │   ├── ui_utils_legacy.py
    │   └── validators_legacy.py
    ├── path
    ├── project-files.txt
    ├── pyproject.toml
    ├── pytest.ini
    ├── README.md
    ├── scripts
    │   └── legacy_coverage_check.py
    ├── template_builder
    │   ├── __init__.py
    │   ├── __main__.py
    │   ├── __pycache__
    │   │   ├── __init__.cpython-313.pyc
    │   │   ├── __main__.cpython-313.pyc
    │   │   ├── assets.cpython-313.pyc
    │   │   ├── builder_core.cpython-313.pyc
    │   │   ├── filters.cpython-313.pyc
    │   │   ├── model.cpython-313.pyc
    │   │   ├── step_image.cpython-313.pyc
    │   │   └── widgets.cpython-313.pyc
    │   ├── assets.py
    │   ├── builder_core.py
    │   ├── data
    │   ├── export
    │   ├── filters.py
    │   ├── infrastructure
    │   │   ├── __init__.py
    │   │   ├── __pycache__
    │   │   │   ├── __init__.cpython-313.pyc
    │   │   │   ├── preview_engine.cpython-313.pyc
    │   │   │   ├── ui_utils.cpython-313.pyc
    │   │   │   └── validators.cpython-313.pyc
    │   │   ├── init.py
    │   │   ├── preview_engine.py
    │   │   ├── ui_utils.py
    │   │   └── validators.py
    │   ├── legacy
    │   │   ├── __init__.py
    │   │   ├── __pycache__
    │   │   │   ├── __init__.cpython-313.pyc
    │   │   │   └── template_builder_legacy.cpython-313.pyc
    │   │   ├── preview_engine_legacy.py
    │   │   ├── template_builder_legacy.py
    │   │   ├── ui_utils_legacy.py
    │   │   └── validators_legacy.py
    │   ├── model.py
    │   ├── services
    │   │   ├── __init__.py
    │   │   ├── __pycache__
    │   │   │   ├── __init__.cpython-313.pyc
    │   │   │   ├── images.cpython-313.pyc
    │   │   │   ├── step_image.cpython-313.pyc
    │   │   │   ├── storage.cpython-313.pyc
    │   │   │   └── text.cpython-313.pyc
    │   │   ├── images.py
    │   │   ├── storage.py
    │   │   └── text.py
    │   ├── step_image.py
    │   ├── templates
    │   │   ├── ebay_template_modern_dynamicv2.html
    │   │   ├── ebay_template_modern_full.html
    │   │   ├── template dinamico prova.html
    │   │   ├── template ebay completo.html
    │   │   ├── template_completov2.html
    │   │   ├── template_ebay_+ricetta_con_foto.html
    │   │   ├── template_ebay+ricetta.html
    │   │   ├── template_final_ebay.html
    │   │   └── template_segnaposto_prova.html
    │   └── widgets.py
    ├── template_builder.egg-info
    │   ├── dependency_links.txt
    │   ├── PKG-INFO
    │   ├── requires.txt
    │   ├── SOURCES.txt
    │   └── top_level.txt
    └── tests
        ├── __pycache__
        │   ├── test_assets.cpython-313-pytest-8.3.5.pyc
        │   ├── test_audit_placeholders.cpython-313-pytest-8.3.5.pyc
        │   ├── test_builder_core_collect.cpython-313-pytest-8.3.5.pyc
        │   ├── test_builder_core_images.cpython-313-pytest-8.3.5.pyc
        │   ├── test_builder_core.cpython-313-pytest-8.3.5.pyc
        │   ├── test_builder_import.cpython-313-pytest-8.3.5.pyc
        │   ├── test_cli.cpython-313-pytest-8.3.5.pyc
        │   ├── test_dnd_images.cpython-313-pytest-8.3.5.pyc
        │   ├── test_filters.cpython-313-pytest-8.3.5.pyc
        │   ├── test_images_service.cpython-313-pytest-8.3.5.pyc
        │   ├── test_images.cpython-313-pytest-8.3.5.pyc
        │   ├── test_jinja_integration.cpython-313-pytest-8.3.5.pyc
        │   ├── test_live_validation.cpython-313-pytest-8.3.5.pyc
        │   ├── test_model.cpython-313-pytest-8.3.5.pyc
        │   ├── test_placeholders_audit.cpython-313-pytest-8.3.5.pyc
        │   ├── test_placeholders.cpython-313-pytest-8.3.5.pyc
        │   ├── test_preview_engine_import.cpython-313-pytest-8.3.5.pyc
        │   ├── test_preview_engine.cpython-313-pytest-8.3.5.pyc
        │   ├── test_regression.cpython-313-pytest-8.3.5.pyc
        │   ├── test_smart_scroll.cpython-313-pytest-8.3.5.pyc
        │   ├── test_step_image_bind_alts.cpython-313-pytest-8.3.5.pyc
        │   ├── test_step_image_helpers.cpython-313-pytest-8.3.5.pyc
        │   ├── test_step_image.cpython-313-pytest-8.3.5.pyc
        │   ├── test_storage_migration.cpython-313-pytest-8.3.5.pyc
        │   ├── test_storage_service.cpython-313-pytest-8.3.5.pyc
        │   ├── test_text_service.cpython-313-pytest-8.3.5.pyc
        │   ├── test_text.cpython-313-pytest-8.3.5.pyc
        │   ├── test_tooltips.cpython-313-pytest-8.3.5.pyc
        │   ├── test_ui_utils.cpython-313-pytest-8.3.5.pyc
        │   ├── test_undo_redo_ui.cpython-313-pytest-8.3.5.pyc
        │   ├── test_widgets_alt.cpython-313-pytest-8.3.5.pyc
        │   ├── test_widgets_full.cpython-313-pytest-8.3.5.pyc
        │   └── test_widgets.cpython-313-pytest-8.3.5.pyc
        ├── test_audit_placeholders.py
        ├── test_builder_core_collect.py
        ├── test_builder_import.py
        ├── test_dnd_images.py
        ├── test_images_service.py
        ├── test_live_validation.py
        ├── test_model.py
        ├── test_placeholders.py
        ├── test_preview_engine.py
        ├── test_regression.py
        ├── test_smart_scroll.py
        ├── test_step_image_bind_alts.py
        ├── test_step_image_helpers.py
        ├── test_step_image.py
        ├── test_storage_migration.py
        ├── test_storage_service.py
        ├── test_text_service.py
        ├── test_tooltips.py
        ├── test_undo_redo_ui.py
        ├── test_widgets_alt.py
        └── test_widgets.py

    20 directories, 133 files