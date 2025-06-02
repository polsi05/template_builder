# 📄 DECISION RECORD – GalleryRow in model.py

## Decisione
Non creare `gallery.py` in Batch 2.  
La classe `GalleryRow` (e relative funzioni) sarà integrata in `model.py`.

### Contesto
Snippet di template dinamico (cicli Jinja) richiedono dati strutturati:
```jinja
{% for src, alt in IMAGES_DESC %}
  <img src="{{ src }}" alt="{{ alt }}">
{% endfor %}
