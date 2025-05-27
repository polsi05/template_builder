# tests/test_builder_import.py
"""
Head-less smoke-test for template_builder.builder_core.
It must run on CI servers without a GUI/display.
"""

import os
import importlib

# simulate head-less
os.environ.pop("DISPLAY", None)

core = importlib.import_module("template_builder.builder_core")
TemplateBuilderApp = core.TemplateBuilderApp


def test_import_and_shortcuts() -> None:
    """Import module, construct app, call a few methods – expect no crash."""
    app = TemplateBuilderApp(enable_gui=False)
    app._bind_global_shortcuts()      # should be a NOP in head-less
    app.quick_save()                  # relies on services.storage.quick_save stub
    app.load_recipe("/tmp/does_not_exist.json")  # stub returns {}
    app.update_preview()              # safe NOP without PreviewEngine
