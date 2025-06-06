
# Fase 2 – Validazione e Task di Completamento/Rifattorizzazione

## 1. Logica Validata (Logic Validated)

| Modulo (Percorso)                                    | Stato validazione       | Note eventuali correzioni                              |
|-------------------------------------------------------|-------------------------|---------------------------------------------------------|
| template_builder/builder_core.py                      | Parzialmente validata   | Adjust export_to_ebay per usare placeholder immagini    |
| template_builder/widgets.py                           | Parzialmente validata   | Aggiungere bind_steps dopo drag&drop, disabilitare edit |
| template_builder/services/storage.py                  | Validata                | Nessuna modifica richiesta                              |
| template_builder/services/text.py                     | In attesa di validazione| Da verificare porting da legacy                           |
| template_builder/services/images.py                   | In attesa di validazione| Da verificare placeholder e gestione immagini mancanti   |
| template_builder/infrastructure/preview_engine.py      | Parzialmente validata   | Disabilitare modifica inline nel preview                  |
| template_builder/infrastructure/ui_utils.py            | Validata                | Nessuna modifica richiesta                              |
| template_builder/infrastructure/validators.py         | In attesa di validazione| Da completare con validazioni esperte                     |
| template_builder/step_image.py                         | In attesa di validazione| Verificare bind_steps/sort_steps/renumber_steps           |
| template_builder/filters.py                            | Validata                | Nessuna modifica richiesta                              |
| template_builder/assets.py                             | Validata                | Nessuna modifica richiesta                              |
| template_builder/model.py                              | Validata                | Nessuna modifica richiesta                              |
| template_builder/__main__.py                           | Validata                | Nessuna modifica richiesta                              |
| template_builder/export/…                              | In attesa di validazione| Verificare workflow di esportazione completa             |
| template_builder/templates/…                           | Validata                | Nessuna modifica richiesta                              |
| template_builder/legacy/…                              | Solo riferimento        | Non modificare                                            |

> **Legenda Stato validazione**  
> - **Validata**: comportamento già allineato con le intenzioni dell’utente.  
> - **Parzialmente validata**: necessita di piccole modifiche (indicate nelle note).  
> - **In attesa di validazione**: da esaminare con l’utente.  
> - **Solo riferimento**: codice legacy, non tocchi.

----

## 2. Task di Completamento/Rifattorizzazione

| Modulo (Percorso)                                       | Obiettivo                                                | Modifiche Necessarie                                                                              | Test Stub                            |
|---------------------------------------------------------|----------------------------------------------------------|--------------------------------------------------------------------------------------------------|--------------------------------------|
| builder_core.py                                         | Gestire placeholder per immagini mancanti                | Sostituire errore “immagine mancante” con `services.images.get_placeholder()` in export_to_ebay | `test_export_with_missing_images()`  |
| builder_core.py                                         | Validazione input pre‐preview                             | Aggiungere `infrastructure.validators.check(input)` prima di `build_preview()`                   | `test_preview_invalid_input_raises()`|
| widgets.py                                              | Bind steps dopo drag&drop                                  | Aggiungere listener su `<ButtonRelease-1>` per chiamare `bind_steps()` dopo spostamento riga     | `test_bind_steps_after_drag()`       |
| services/storage.py                                     | Completamento gestione errori                              | Verificare cartella esistenza e sollevare `StorageError` con messaggi chiari                       | `test_save_file_folder_missing()`    |
| services/text.py                                        | Completare formattazione avanzata                           | Portare funzioni da `legacy/template_builder_legacy.py` e aggiungere test proprietà              | `test_text_formatting_property()`    |
| services/images.py                                      | Gestione placeholder immagine                               | Implementare `get_placeholder()` e usarla quando mancano immagini                                | `test_get_placeholder_default()`     |
| infrastructure/preview_engine.py                        | Disabilitare modifica inline nel preview                    | Rimuovere o ignorare event listeners che permettono editing nel preview                          | `test_preview_read_only()`           |
| infrastructure/ui_utils.py                              | Verifica posizionamento widget                              | Controllare che helper non generino elementi fuori layout previsto                               | `test_ui_widget_positions()`         |
| infrastructure/validators.py                            | Aggiungere validazioni dei campi                              | Implementare funzioni `check_mandatory_fields()` ereditate dal legacy                            | `test_validators_mandatory()`        |
| step_image.py                                           | Allineamento bind/sort/renumber                               | Assicurarsi che `bind_steps()`, `sort_steps()`, `renumber_steps()` rispettino nuova logica       | `test_step_image_bind_sort_renum()`  |
| filters.py                                              | Verifica registrazione filtri Jinja2                           | Assicurarsi che tutti i filtri ereditati da legacy siano registrati                              | `test_filters_registration()`        |
| assets.py                                               | Verifica gestione asset                                      | Controllare che `collect_assets()` eviti duplicati e filtri correttti                              | `test_collect_assets_no_duplicates()`|
| model.py                                                | Verifica contratti dei dati                                 | Controllare che tutte le classi Pydantic/TypedDict abbiano i campi corretti                       | `test_model_schema_fields()`         |
| __main__.py                                             | Verifica entry point                                         | Controllare avvio corretto di `BuilderApp` senza errori                                           | `test_cli_runs_without_error()`      |
| export/…                                                | Implementare flow di esportazione completa                    | Verificare che il package ZIP contenga tutti i file HTML e immagini                              | `test_export_zip_contents()`         |
| templates/…                                             | Controllo template                                              | Assicurarsi che tutti i file HTML contengano i segnaposto corretti                                | `test_templates_placeholder()`       |

> **Note**  
> - Non si aggiungono moduli: tutte le modifiche si basano sui file esistenti.  
> - Non si eliminano file: ogni feature legacy va migrata nei moduli target.  
