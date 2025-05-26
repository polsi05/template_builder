"""Registro filtri Jinja2 – STUB."""
try:
    from jinja2 import pass_context
except ImportError:  # pragma: no cover
    from jinja2 import contextfilter as pass_context  # type: ignore

@pass_context
def steps_bind(ctx, raw):  # pylint: disable=unused-argument
    """Stub legacy filter – restituisce l'input invariato."""
    return raw
