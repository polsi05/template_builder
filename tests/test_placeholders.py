from template_builder.services.text import extract_placeholders

def test_extract_basic():
    html = "<h1>{{ TITLE }}</h1>"
    assert extract_placeholders(html) == {"TITLE"}
