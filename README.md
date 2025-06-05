# Template Builder 🖌️

Toolkit GUI in Python per creare template HTML e email marketing. Offre un'interfaccia moderna basata su Tkinter con **anteprima live**, supporto undo/redo e gestione automatica delle immagini.

## Funzionalità principali

| Funzione                                | Extra req.                     | Fallback |
|-----------------------------------------|--------------------------------|---------|
| Anteprima HTML integrata (`PreviewEngine`) | `tkinterweb` per rendering web | testo a scorrimento |
| Undo/Redo tramite scorciatoie           | —                              | — |
| Drag & Drop immagini su ogni campo URL  | `tkinterdnd2` + `tkdnd`        | pulsanti “Add” |
| Validazione URL immagini in tempo reale | —                              | bordi disattivati |
| Tooltip contestuali on‑hover            | —                              | nessuno |

## Installazione

Richiede Python ≥3.9.

```bash
# installazione base (Tkinter già incluso nei pacchetti standard)
pip install template_builder

# componenti opzionali: drag&drop e web preview
pip install "template_builder[dnd,webpreview]"
```
Per contribuire al progetto è consigliato clonare il repository ed eseguire:

```bash
pip install -e .[test]  # installa in modalità editable con dipendenze test
```

## Quick start

```python
from template_builder.builder_core import TemplateBuilderApp

app = TemplateBuilderApp()
if app.root:  # avvia solo se è disponibile un display grafico
    app.root.mainloop()
```

## Struttura del repository

Un esempio di anteprima è visibile in `docs/img/overview.png`.

- `template_builder/builder_core.py` – controller principale dell'applicazione.
- `template_builder/widgets.py` – widget Tk personalizzati (placeholder, repeater immagini…).
- `template_builder/services/` – moduli **puri** per testo, immagini e storage.
- `template_builder/infrastructure/` – wrapper (per ora semplici stub) dei moduli legacy.
- `template_builder/model.py` e `step_image.py` – dataclass e helper per le immagini passo‑passo.
- `template_builder/filters.py` – filtri Jinja2 opzionali.
- `templates/` – template HTML di esempio utilizzati dalla GUI.
- `tests/` – suite Pytest completa.

Per eseguire i test:
```bash
pytest -q
```
## License
Questo progetto è distribuito con licenza MIT.
