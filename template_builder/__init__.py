"""
Template Builder – package initializer.
Espone la classe `TemplateBuilderApp` (import lazy) e la funzione `main()`.
"""
from importlib import import_module

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
