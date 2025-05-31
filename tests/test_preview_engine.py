import pytest
from template_builder.infrastructure.preview_engine import PreviewEngine

def test_preview_engine_defaults_to_empty():
    """
    Se non passiamo argomenti al costruttore, html deve essere stringa vuota.
    render_source() restituisce "".
    """
    engine = PreviewEngine()
    assert engine.html == ""
    assert engine.render_source() == ""

def test_preview_engine_initializes_with_html():
    """
    Se passo una stringa di HTML al costruttore, render_source() deve restituirla
    esattamente senza modifiche.
    """
    sample_html = "<h1>Test</h1>"
    engine = PreviewEngine(html=sample_html)
    assert engine.html == sample_html
    assert engine.render_source() == sample_html

def test_preview_engine_supports_multiple_calls():
    """
    Verifica che render_source() ritorni sempre la stessa stringa, 
    anche se richiamato più volte.
    """
    sample = "<p>Paragrafo</p>"
    engine = PreviewEngine(sample)
    # Chiamo render_source tre volte
    assert engine.render_source() == sample
    assert engine.render_source() == sample
    assert engine.render_source() == sample

@pytest.mark.parametrize("html_input", ["", "<div>1</div>", "<!-- comment -->"])
def test_preview_engine_varie_stringhe(html_input):
    """
    Controlla che preview_engine gestisca qualsiasi stringa di HTML, 
    inclusi commenti o stringa vuota.
    """
    engine = PreviewEngine(html_input)
    assert engine.render_source() == html_input
