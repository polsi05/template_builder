import pytest
import tkinter
from template_builder.builder_core import TemplateBuilderApp

def test_audit_placeholders_logic(monkeypatch, tmp_path):
    # Setup app headless
    app = TemplateBuilderApp(enable_gui=False)
    # Simula template_src con due segnaposto
    html = "<p>{{ ONE }}</p>{{ TWO_SRC }}{{ TWO_ALT }}"
    app.template_src = html
    # Stato mancante ONE e TWO_ALT, extra THREE
    app._state = {"THREE": "x", "TWO_SRC": "url"}
    lines = app.audit_placeholders()
    assert "❌ ONE" in lines
    assert "✅ TWO_SRC" in lines
    assert "✅ TWO_ALT" in lines
    assert "❌ THREE" not in lines  # non fa parte di placeholders estratti
