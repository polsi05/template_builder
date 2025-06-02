# ✅ ROADMAP – Batch 2 – Rifattorizzazione template_builder

> **Goal generale**  
> Portare nello stato “definitivo” i modelli dati (Hero, StepImage, GalleryRow) e
> l’infrastruttura di persistenza, garantendo compatibilità con template sia
> statici sia dinamici (cicli Jinja2, filtri, set, if).

---

## 🔑 Principi di progettazione aggiunti

| Cod. | Principio | Implicazioni |
|------|-----------|-------------|
| **P1** | I modelli serializzano **solo dati**, non HTML. | `to_dict()` restituisce dict/liste utilizzabili da Jinja. |
| **P2** | Il render finale è delegato a Jinja2 se presente. | Se Jinja manca, modelli forniscono `fallback_html()`. |
| **P3** | Placeholders sempre `{{ TAG }}` (doppie graffe). | Compatibilità totale con estrazione segnaposti/legacy. |
| **P4** | Il filtro `steps_bind` rimane plug-in. | `RECIPE_STEPS_TEXT` passa come stringa multilinea. |
| **P5** | Modelli progettati per iterazione Jinja. | Es. `GalleryRow` -> `{"IMAGES_DESC": [[src,alt]…]}`. |

---

## 📌 Milestone Batch 2

| Cod. | Task | Modulo | Tipo |
|------|------|--------|------|
| **F1** | `Hero` dataclass (title, img, intro) + `to_dict()` + `fallback_html()` | `model.py` | nuovo |
| **F2** | `StepImage` dataclass (img, alt, text, order) + validazioni | `model.py` | nuovo |
| **F3** | `GalleryRow` dataclass (lista `StepImage`, max 3) + `to_jinja_ctx()` | `model.py` | nuovo |
| **F4** | Rifattorizzare funzioni helper step (sort, swap, renumber) | `step_image.py` | rifatt. |
| **F5** | Patch `services/storage.py` (version 2, round-trip JSON) | `services/storage.py` | patch |
| **F6** | Patch `builder_core.py` (`load_recipe`, `_collect`) per nuovi modelli | `builder_core.py` | patch |
| **F7** | **Nuovi test**: `test_model.py`, `test_step_image.py`, `test_jinja_integration.py` | `tests/` | test |
| **F8** | Aggiornare docs: DEV_PLAN, IMPACT_MATRIX, INTEGRATION_GUIDE, CHECKLIST | docs | doc |
| **F9** | CI verde GitHub Actions (head-less) | repo | CI |

---

## 🧪 Struttura nuovi test

- **tests/test_model.py**  
  - `test_hero_roundtrip()`  
  - `test_step_image_validation()`  
  - `test_gallery_row_to_jinja_ctx()`

- **tests/test_step_image.py**  
  - `test_step_sort_swap()`  
  - `test_step_renumber()`  

- **tests/test_jinja_integration.py**  
  - `test_jinja_loop_gallery()`  
  - `test_steps_bind_filter()`  
  - `test_fallback_preview_no_jinja()`

---

## 📅 Sequenza consigliata

1. Implementare F1–F3 ➜ `pytest -q tests/test_model.py`
2. F4 ➜ `pytest -q tests/test_step_image.py`
3. F5–F6 ➜ `pytest -q` (suite completa)
4. F7 ➜ CI
5. Completare F8–F9 (docs + verde finale)
