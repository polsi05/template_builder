Ecco il **README.md** completo da copiare **tutto insieme** e incollare nel file `README.md` alla root del tuo progetto (sovrascrivi l’esistente):

````markdown
# Template Builder 🖌️

Toolkit GUI per creare rapidamente template HTML/marketing con  
**preview live**, validazione immediata e gestione undo/redo.

## Feature principali (≥ v0.1.0)

| Funzione                        | Extra req. | Fallback                         |
|---------------------------------|------------|----------------------------------|
| **PreviewEngine** – anteprima HTML in-app   | `tkinterweb`    | scrolled-text readonly          |
| **Undo/Redo UI** (Ctrl/Cmd Z / Y)           | —                | —                                |
| **Drag & Drop immagini** in qualsiasi campo URL | `tkinterdnd2` + `tkdnd` | pulsante “+ Add”       |
| **Validazione live** – bordo rosso/verde    | —                | disattivata se Tk vecchio        |
| **Tooltip contestuali** on-hover             | —                | ignorati in ambiente head-less   |

## Installazione

```bash
# core (Tkinter nativo)
pip install template_builder

# + Drag&Drop e WebPreview
pip install "template_builder[dnd,webpreview]"
````

## Quick start

```python
from template_builder.builder_core import TemplateBuilderApp

app = TemplateBuilderApp()   # si adatta se non c’è display (CI)
if app.root:                 # run solo in modalità GUI
    app.root.mainloop()
```

![screenshot](docs/img/overview.png)

## Contribuire

1. Fork → branch feature → PR
2. `pytest -q` deve restare verde
3. Per funzionalità opzionali, aggiungere i flag `EXTRA_REQ` in `pyproject.toml`

````

1. Salva questo contenuto **in un unico blocco** nel file `README.md` alla root.  
2. Poi esegui:

   ```bash
   git add README.md
   git commit -m "docs: update README with Quick start"
   git push
````
