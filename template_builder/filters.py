# template_builder/filters.py

"""Registro filtri Jinja2 – STUB."""

try:
    from jinja2 import pass_context
except ImportError:
    # Se Jinja2 non è installato, definiamo pass_context come no‐op
    def pass_context(func):
        return func  # restituisce la funzione senza decorarla

@pass_context
def steps_bind(ctx, raw):  # pylint: disable=unused-argument
    """Stub legacy filter – restituisce l'input invariato."""
    return raw
