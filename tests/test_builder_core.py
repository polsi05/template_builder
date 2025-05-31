import pytest
import os
import json
from template_builder.builder_core import TemplateBuilderApp

def test_repr_and_display_available():
    app = TemplateBuilderApp(enable_gui=False)
    r = repr(app)
    assert "TemplateBuilderApp" in r
    # Simula assenza di DISPLAY su Linux
    orig_display = os.environ.get("DISPLAY")
    os.environ["DISPLAY"] = ""
    assert TemplateBuilderApp._display_available() == False
    os.environ["DISPLAY"] = ":0"
    assert TemplateBuilderApp._display_available() == True
    # Ripristina DISPLAY
    if orig_display is None:
        del os.environ["DISPLAY"]
    else:
        os.environ["DISPLAY"] = orig_display

def test_undo_redo_and_state():
    app = TemplateBuilderApp(enable_gui=False)
    # Stato iniziale vuoto
    assert app._state == {}
    # Push di due stati differenti
    app._state = {"A": 1}
    app._undo.push(app._state)
    app._state = {"A": 2}
    app._undo.push(app._state)
    # Undo torna al primo stato
    app.undo()
    assert app._state == {"A": 1}
    # Redo torna al secondo stato
    app.redo()
    assert app._state == {"A": 2}

def test_load_recipe(tmp_path):
    app = TemplateBuilderApp(enable_gui=False)
    data = {"X": 10}
    file = tmp_path / "recipe.json"
    file.write_text(json.dumps(data))
    app.load_recipe(str(file))
    assert app._state == data
    # File non JSON -> stato diventa vuoto
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not json")
    app.load_recipe(str(bad_file))
    assert app._state == {}

def test_audit_placeholders():
    app = TemplateBuilderApp(enable_gui=False)
    app.template_src = "Hello {{FOO}} and {{BAR}}"
    app._state = {"FOO": "value"}
    result = app.audit_placeholders()
    # FOO gestito (✅), BAR non gestito (❌)
    assert any("✅ FOO" in line for line in result)
    assert any("❌ BAR" in line for line in result)
