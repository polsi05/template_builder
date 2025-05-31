import pytest
from template_builder.filters import steps_bind

class DummyContext:
    """Un semplice oggetto qualunque da passare come contesto Jinja2."""
    def __init__(self, val):
        self.val = val

@pytest.mark.parametrize("raw_input", [
    "", "Hello", "123", "line1\nline2", ["uno", "due", "tre"], 12345
])
def test_steps_bind_returns_raw(raw_input):
    """
    steps_bind deve restituire esattamente `raw_input`, indipendentemente
    dal valore di `ctx`. Provato con:
      - stringhe (vuote e non)
      - multilinea
      - sequenze di stringhe (anche se la funzione ignora `raw` come lista)
      - tipo non-string, es. numero (passato così com’è)
    """
    dummy = DummyContext("qualcosa")
    result = steps_bind(dummy, raw_input)
    # Poiché il decorator @pass_context colloca `ctx` come primo argomento,
    # il secondo parametro – `raw_input` – deve essere restituito invariato.
    assert result == raw_input

def test_steps_bind_works_without_ctx():
    """
    Se chiamato senza passare un contesto (dovrebbe funzionare comunque),
    forziamo la chiamata con None: dovrebbe restituire lo stesso raw.
    """
    result = steps_bind(None, "abc")
    assert result == "abc"
