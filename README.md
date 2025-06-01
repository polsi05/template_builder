# Template Builder

Template Builder è un tool modulare per generare documenti HTML a partire da template Jinja2 e da un contesto JSON.  
Il progetto è stato completamente rifattorizzato in moduli indipendenti (core, widget, servizi testo, servizi immagini, infrastruttura, CLI) e coperto da una suite completa di test.

## Struttura del progetto

- **template_builder/**  
  - `__main__.py` : entrypoint CLI (`python -m template_builder`)  
  - `assets.py`    : costanti (regex placeholder, colori, colonne di default)  
  - `builder_core.py`: controller principale (stato, undo/redo, audit placeholder)  
  - `filters.py`   : filtri Jinja2 stub  
  - `model.py`     : dataclass di dominio (Hero, StepImage, GalleryRow)  
  - **infrastructure/**  
    - `ui_utils.py`        : helper per dialog/info sullo stdout  
    - `preview_engine.py`  : stub per motore di anteprima HTML  
  - **services/**  
    - `text.py`    : estrazione e formattazione testo (smart_paste, auto_format, images_to_html…)  
    - `images.py`  : gestione placeholder, griglie HTML, data URI, validazione URL, metadata immagine  
    - `storage.py` : persistenza (undo/redo), `export_html` (fallback _simple_render o Jinja2)  
  - **widgets.py** : widget Tkinter (PlaceholderEntry, Spinbox, TextField, SortableImageRepeater)  

- **tests/**  
  Contiene tutti i test unitari e di integrazione: service text, service images, service storage, test widget, test core, test CLI, test infrastruttura, test assets, test filters, test model.

## Come installare

1. Clona il repository:
   ```bash
   git clone git@github.com:polsi05/template_builder.git
   cd template_builder
