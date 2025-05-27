"""
Smoke-test head-less per i Tooltip (Issue #6).

Verifica:
* import dei moduli senza display;
* flag booleano HAS_TOOLTIP presente;
* text.get_field_help restituisce stringa.
"""

import os
import importlib

os.environ.pop("DISPLAY", None)  # forza ambiente head-less

widgets = importlib.import_module("template_builder.widgets")
text    = importlib.import_module("template_builder.services.text")


def test_has_tooltip_flag() -> None:
    assert hasattr(widgets, "HAS_TOOLTIP")
    assert isinstance(widgets.HAS_TOOLTIP, bool)


def test_get_field_help() -> None:
    assert hasattr(text, "get_field_help")
    msg = text.get_field_help("title")
    assert isinstance(msg, str)
