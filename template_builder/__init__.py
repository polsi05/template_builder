"""
Template Builder – package initializer.
Espone la classe `TemplateBuilderApp` (import lazy) e la funzione `main()`.
"""
from importlib import import_module
#   in __init__.py
from .step_image import sort_steps, swap_steps, renumber_steps  # noqa: F401
from template_builder.services.storage import *  # noqa

def _lazy():
    core = import_module(".builder_core", __package__)
    return core.TemplateBuilderApp

TemplateBuilderApp = _lazy()  # type: ignore[attr-defined]

def main() -> None:  # pragma: no cover
    """Entry-point CLI: `python -m template_builder`."""
    app_cls = _lazy()
    app = app_cls()
    app.mainloop()

if __name__ == "__main__":  # pragma: no cover
    main()
