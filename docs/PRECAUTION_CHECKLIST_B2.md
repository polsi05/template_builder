
---

## 5. `PRECAUTION_CHECKLIST_B2.md`

```markdown
# 🛡️ PRECAUTION CHECKLIST – Batch 2

- [ ] Import loop evitati (`model.py` non importa builder_core).
- [ ] Ogni `render_html()` usa `html.escape`.
- [ ] Nuovi test marcati `@skipif(not HAS_DISPLAY)` se tocchi Tkinter.
- [ ] JSON include `"version": 2` e migrazione da v1 testata.
- [ ] Placeholder Jinja sempre `{{ TAG }}` (spazi regolamentari).
- [ ] `to_dict()` / `from_dict()` simmetrici → test round-trip.
- [ ] CI GitHub Actions (ubuntu-latest, Py 3.12) verde.
- [ ] Nessuna regressione su Batch 1 (test storici verdi).
