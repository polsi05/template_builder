from template_builder.services import images as imgs

def test_guess_grid_basic():
    assert imgs.guess_grid(5, cols=4) == (2, 4)

def test_generate_placeholders():
    assert imgs.generate_placeholders(3) == ["{{ IMG1 }}", "{{ IMG2 }}", "{{ IMG3 }}"]
