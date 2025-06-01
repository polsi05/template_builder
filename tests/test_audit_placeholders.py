import pytest
from template_builder.builder_core import TemplateBuilderApp

def test_audit_placeholders_logic(monkeypatch, tmp_path):
    # Setup applicazione in modalità head-less (no GUI)
    app = TemplateBuilderApp(enable_gui=False)
    # Simula un template HTML con due segnaposto attesi
    html = "<p>{{ ONE }}</p>{{ TWO_SRC }}{{ TWO_ALT }}"
    app.template_src = html
    # Stato attuale: manca ONE e TWO_ALT, presente un extra THREE, e TWO_SRC fornito
    app._state = {"THREE": "x", "TWO_SRC": "url"}
    lines = app.audit_placeholders()
    # Verifica risultati: ONE e TWO_ALT segnalati mancanti, TWO_SRC presente, THREE ignorato
    assert "❌ ONE" in lines
    assert "✅ TWO_SRC" in lines
    assert "✅ TWO_ALT" in lines
    assert "❌ THREE" not in lines  # "THREE" non fa parte dei segnaposto definiti nel template
