import pytest
from template_builder.services import text as txt

def test_smart_paste_string():
    raw = "one; two\nthree\nfour;"
    result = txt.smart_paste(raw)
    assert result == ["one", "two", "three", "four"]

def test_smart_paste_list():
    raw_list = ["a", "b;c", "d\ne"]
    result = txt.smart_paste(raw_list)
    # Verifica che tutti gli elementi appaiano senza spazi bianchi
    assert all(x in result for x in ["a", "b", "c", "d", "e"])

@pytest.mark.parametrize("mode,text,expected", [
    ("ul", "apple", "<ul><li>apple</li></ul>"),
    ("p", "apple", "<p>apple</p>"),
    ("ul", "line1\nline2", "<ul><li>line1</li><li>line2</li></ul>"),
    ("p", "one; two", "<p>one</p><p>two</p>"),
    ("p", "a<b>c", "<p>a&lt;b&gt;c</p>"),
    ("ul", "<tag>", "<tag>"),
])
def test_auto_format(mode, text, expected):
    result = txt.auto_format(text, mode=mode)
    assert result == expected

def test_extract_placeholders():
    html_src = "<div>{{ NAME }} and {{ AGE }} {{NOTAPH}}</div>"
    placeholders = txt.extract_placeholders(html_src)
    assert placeholders == {"NAME", "AGE", "NOTAPH"}

def test_images_to_html():
    html = txt.images_to_html(2, 3)
    # Controlla che la tabella abbia 2 righe e 3 colonne con i segnaposto numerati
    assert html.startswith("<table>")
    assert "{{ IMG1 }}" in html and "{{ IMG6 }}" in html
    assert html.count("<tr>") == 2 and html.count("<td>") == 6

def test_get_field_help():
    assert txt.get_field_help("title").startswith("Titolo")
    assert txt.get_field_help("Description").startswith("Descrizione")
    assert txt.get_field_help("unknown") == ""
