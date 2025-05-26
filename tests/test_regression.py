from template_builder.services.text import smart_paste

def test_smart_paste_basic():
    assert smart_paste("a\nb") == ["a", "b"]
