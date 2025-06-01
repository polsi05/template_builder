import pytest
import builtins
from template_builder.infrastructure.ui_utils import show_info

def test_show_info_prints_correct_prefix(capsys):
    """
    show_info(msg) deve stampare su stdout una riga iniziando con "[info] ":
      - ad esempio, show_info("Ciao") → "[info] Ciao\n"
    """
    # Chiamiamo show_info con un messaggio di prova
    show_info("Messaggio di prova")
    # Catturiamo stdout / stderr
    captured = capsys.readouterr()
    assert captured.out == "[info] Messaggio di prova\n"
    assert captured.err == ""

@pytest.mark.parametrize("msg", ["", "A solo testo", "123", "Test con\nandata"])
def test_show_info_varie_stringhe(capsys, msg):
    """
    Verifica che show_info stampi esattamente "[info] <msg>\n" anche se msg è vuoto
    o contiene caratteri speciali (es. newline).
    """
    show_info(msg)
    captured = capsys.readouterr()
    # Se msg contiene newline, show_info lo stampa comunque intero:
    # ad esempio msg="Line1\nLine2" → "[info] Line1\nLine2\n"
    expected = "[info] " + msg + "\n"
    assert captured.out == expected
    assert captured.err == ""
