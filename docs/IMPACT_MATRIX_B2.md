# 🔄 IMPACT MATRIX – Batch 2

| Entità / Modulo | Importa da | Importato da | Effetti collaterali | Precauzione |
|-----------------|-----------|--------------|---------------------|-------------|
| `model.Hero` | `dataclasses`, `html` | `builder_core`, `storage` | Nuovi campi HERO_* da gestire in `_collect()` | Aggiornare `_collect()` e test |
| `model.StepImage` | `dataclasses`, `html` | `GalleryRow`, `storage`, `step_image` | Ordinamento step, alt obbligatorio | Funzioni helper in step_image.py |
| `model.GalleryRow` | `dataclasses`, `html`, `StepImage` | `builder_core`, `storage` | Variabile `COLS_DESC/REC` nel template | Salvare `COLS_xxx` in stato |
| `step_image.py` | `model.StepImage` | `tests`, futuri servizi | Cambio firma -> test falliti | Versionare funzioni helper |
| `services.storage` (v2) | `json`, `model.*` | `builder_core`, CLI | JSON v2 incompatibile con v1 legacy | Gestire `"version"` e migrazione |

