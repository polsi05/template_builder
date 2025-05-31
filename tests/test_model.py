import pytest
from template_builder.model import Hero, StepImage, GalleryRow

def test_hero_defaults_and_assignment():
    # Senza parametri, i campi devono essere stringhe vuote
    h = Hero()
    assert isinstance(h.url, str) and h.url == ""
    assert isinstance(h.alt, str) and h.alt == ""

    # Possiamo passare parametri esplicitamente
    h2 = Hero(url="https://example.com/hero.png", alt="Hero Image")
    assert h2.url == "https://example.com/hero.png"
    assert h2.alt == "Hero Image"

def test_stepimage_defaults_and_assignment():
    # Senza parametri, url="" alt="" order=0
    s = StepImage()
    assert isinstance(s.url, str) and s.url == ""
    assert isinstance(s.alt, str) and s.alt == ""
    assert isinstance(s.order, int) and s.order == 0

    # Possiamo passare valori custom
    s2 = StepImage(url="img.jpg", alt="Step", order=5)
    assert s2.url == "img.jpg"
    assert s2.alt == "Step"
    assert s2.order == 5

def test_galleryrow_defaults_and_assignment():
    # Senza parametri, urls=None
    g = GalleryRow()
    assert g.urls is None

    # Possiamo passare lista di URL
    urls = ["a.png", "b.jpg", "c.gif"]
    g2 = GalleryRow(urls=urls)
    assert isinstance(g2.urls, list)
    assert g2.urls == urls

def test_model_equality_and_repr():
    # I dataclass implementano __eq__ e __repr__
    a = Hero(url="u", alt="a")
    b = Hero(url="u", alt="a")
    c = Hero(url="x", alt="y")
    assert a == b
    assert a != c
    # __repr__ contiene il nome della classe
    assert "Hero" in repr(a)
    # Stessa cosa per StepImage e GalleryRow
    s1 = StepImage(url="i", alt="j", order=1)
    s2 = StepImage(url="i", alt="j", order=1)
    assert s1 == s2
    assert "StepImage" in repr(s1)

    g1 = GalleryRow(urls=["x"])
    g2 = GalleryRow(urls=["x"])
    assert g1 == g2
    assert "GalleryRow" in repr(g1)
