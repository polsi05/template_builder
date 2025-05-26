# Architecture – Phase A Skeleton

```mermaid
graph TD
  subgraph template_builder
    builder_core --> widgets
    builder_core --> services
    builder_core --> filters
    widgets --> services
    services -->|pure| text
    services --> images
    services --> storage
    builder_core --> infrastructure
  end
  subgraph legacy
    monolithic((template_builder.py))
  end
  infrastructure -->|wrap| legacy

builder_core.py – avvierà la GUI (stub oggi).

widgets.py – conterrà PlaceholderEntry, ImageRepeater, …

services/ – funzioni pure, testabili.

infrastructure/ – copia (o stub) dei vecchi moduli di supporto.

Gli stub odierni espongono soltanto nomi; il refactor vero avverrà in branch feat/*.

---

## 5. scripts/legacy_coverage_check.py   (stub che passa)

```python
"""Coverage stub – sempre verde finché non si decide di attivare il diff reale."""
if __name__ == "__main__":
    print("legacy coverage skipped (phase A)")
