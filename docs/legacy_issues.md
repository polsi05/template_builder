
---

## Patch ― **docs/legacy_issues.md**

```markdown
# Legacy issues – tracking

## Risolti (Phase B, v0.1.0)

- [x] **Preview non carica HTML complesso** → nuova `PreviewEngine` con fallback.
- [x] **Undo/Redo perde stato dei widget** → `UndoRedoStack` collegata a UI.
- [x] **Impossibile trascinare immagini** → integrazione `tkinterdnd2`.
- [x] **Placeholder resta in input su focus** → `PlaceholderEntry`/`MultiTextField` fix.
- [x] **Nessun feedback sui campi vuoti** → validazione live bordo rosso/verde.
- [x] **Utente non sa cosa inserire** → tooltip contestuali da `text.get_field_help`.

## Rimasti / da valutare

| ID | Descrizione | Note |
|----|-------------|------|
| L-07 | Gestione temi scuri/chiari | Post-1.0 |
| L-11 | Supporto i18n (gettext)   | — |
