# ✅ CHECKLIST – Interventi su `fix-verde-clean`

## FASE 1: Test stringenti (analisi e baseline)
- [ ] F1. Validare ambiente test (Pillow, tkinter)
- [ ] F1. Annotare test falliti (`pytest -q`)

## FASE 2: Refactoring moduli

### builder_core.py
- [ ] F2. Fix `audit_placeholders()` (logica gruppi _SRC/_ALT)
- [ ] F7. Fix `_display_available()` su DISPLAY=""
  
### text.py
- [ ] F3. Fix `auto_format()` (escape `<`, `>`, `&` se non HTML)
- [ ] F4. Fix `images_to_html()` (uso corretto di `{{ IMGn }}`)

### images.py
- [ ] F5. Fix `validate_url()` con validazione base HTTP/HTTPS
- [ ] F8. Gestione `fetch_metadata()` senza Pillow

### widgets.py
- [ ] F6. Definizione fallback `HAS_TOOLTIP = False` in caso di ImportError

## FASE 3: Allineamento e rifinitura
- [ ] F9. Sincronizzare nomi tra moduli (get_urls, render_html, segnaposti)
- [ ] F10. Verificare CI GitHub (`CI #91+`) post patch

---

## ✅ Output attesi
- Tutti i test verdi in `tests/test_*.py`
- CI GitHub verde
- Nessuna funzione placeholder nei moduli
- Coerenza semantica tra moduli, test, template
