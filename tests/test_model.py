# tests/test_model.py
import pytest
from template_builder.model import Hero, StepImage, GalleryRow


def test_hero_roundtrip():
    hero = Hero(title="T", img="img.jpg", intro="intro", alt="alt")
    assert hero.to_dict() == {
        "TITLE": "T",
        "HERO_IMAGE_SRC": "img.jpg",
        "HERO_IMAGE_ALT": "alt",
        "INTRO": "intro",
    }
    html = hero.fallback_html()
    assert "<h1>T</h1>" in html and "img.jpg" in html
    # placeholders se vuoto
    empty = Hero()
    ph = empty.fallback_html()
    assert "{{ TITLE }}" in ph and "{{ HERO_IMAGE_SRC }}" in ph


def test_step_image_validation():
    with pytest.raises(ValueError):
        StepImage(img="any.png", alt="", text="t", order=1)
    ok = StepImage(img="ok.png", alt="descr", text="t", order=2)
    assert ok.alt == "descr"
    StepImage(img="", alt="", text="no img", order=3)  # valido


def test_gallery_row_to_jinja_ctx():
    s1 = StepImage(img="1.png", alt="a1", order=1)
    s2 = StepImage(img="2.png", alt="a2", order=2)
    row = GalleryRow([s2, s1])   # fuori ordine
    assert row.to_jinja_ctx() == {"IMAGES_DESC": [["1.png", "a1"], ["2.png", "a2"]]}
    with pytest.raises(ValueError):
        GalleryRow([s1, s2, StepImage(img="3.png", alt="a3", order=2)])  # dup order
    with pytest.raises(ValueError):
        GalleryRow([s1, s2, StepImage(img="3.png", alt="a3", order=3),
                    StepImage(img="4.png", alt="a4", order=4)])  # >3 imgs
