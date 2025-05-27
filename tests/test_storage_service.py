import importlib
from pathlib import Path
import pytest

from template_builder.services import storage as st


def test_undo_redo():
    stack = st.UndoRedoStack()
    stack.push({"a": 1})
    stack.push({"a": 2})
    assert stack.undo() == {"a": 1}
    assert stack.redo() == {"a": 2}


def test_quick_save_and_load():
    tmp_state = {"foo": "bar"}
    path = st.quick_save(tmp_state)
    assert path.exists()
    loaded = st.load_recipe(path)
    assert loaded == tmp_state
    path.unlink()


def test_export_html(tmp_path):
    if importlib.util.find_spec("jinja2") is None:
        pytest.skip("jinja2 non installato")
    tpl = tmp_path / "base.html"
    tpl.write_text("<h1>{{ title }}</h1>", encoding="utf-8")
    html = st.export_html({"title": "Hello"}, tpl)
    assert "<h1>Hello</h1>" in html
