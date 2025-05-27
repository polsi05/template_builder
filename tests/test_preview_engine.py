# tests/test_preview_engine_import.py
"""
Import-only smoke test for the refactored PreviewEngine.

The goal is to confirm that:
* the module imports with **no display** available;
* the class can be instantiated without a parent widget;
* calling its public methods is a safe no-op.
"""

import os
import importlib

# Simulate head-less CI environment.
os.environ.pop("DISPLAY", None)

preview_mod = importlib.import_module("template_builder.infrastructure.preview_engine")
PreviewEngine = preview_mod.PreviewEngine


def test_preview_engine_import_only() -> None:
    """Import and basic API calls should never raise."""
    prev = PreviewEngine(enable_gui=False)   # head-less
    prev.render("<h1>Hello</h1>")            # no effect, but must not crash
    ctx = prev.collect_context()
    assert isinstance(ctx, dict)
