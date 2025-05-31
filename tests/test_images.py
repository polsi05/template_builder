import pytest
from template_builder.services import images as img
from pathlib import Path
from PIL import Image

def test_guess_grid_default():
    assert img.guess_grid(5, cols=3) == (2, 3)
    assert img.guess_grid(2, cols=5) == (1, 2)
    assert img.guess_grid(0, cols=0) == (1, 1)

def test_generate_placeholders():
    placeholders = img.generate_placeholders(3)
    assert placeholders == ["{{ IMG1 }}", "{{ IMG2 }}", "{{ IMG3 }}"]
    # anche 0 immagini produce almeno IMG1
    assert img.generate_placeholders(0) == ["{{ IMG1 }}"]

def test_encode_file_to_data_uri(tmp_path):
    file = tmp_path / "test.txt"
    file.write_text("hello")
    uri = img.encode_file_to_data_uri(str(file))
    # Controlla prefisso e base64 di "hello"
    assert uri.startswith("data:text/plain;base64,") or uri.startswith("data:application/")
    assert "aGVsbG8=" in uri

def test_paths_to_html_grid_and_images_to_html(tmp_path):
    # Caso paths=None (placeholder)
    html = img.paths_to_html_grid(None)
    assert "<table>" in html and "{{ IMG1 }}" in html
    # Caso paths veri senza inline
    paths = ["foo.png", "bar.jpg"]
    html = img.paths_to_html_grid(paths, cols=2, inline=False, alt_texts=["A", "B"])
    assert "foo.png" in html and "bar.jpg" in html and "<tr>" in html
    # Caso inline True: crea Data URI da immagine
    file = tmp_path / "test.png"
    im = Image.new("RGB", (2,2), color=(73,109,137))
    im.save(file, format="PNG")
    html_inline = img.paths_to_html_grid([file], cols=1, inline=True)
    assert "data:image/png;base64," in html_inline

def test_smart_paste_images():
    raw = "a.png; b.jpg\nc.gif"
    result = img.smart_paste_images(raw)
    assert result == ["a.png", "b.jpg", "c.gif"]
    lst = ["one", "two;three"]
    result2 = img.smart_paste_images(lst)
    assert "one" in result2 and "three" in result2

def test_validate_url(monkeypatch):
    from template_builder.services import images as img_module
    # Simula validazione corretta
    monkeypatch.setattr(img_module, "_legacy_validate", lambda url: None)
    img_module.validate_url("http://example.com/image.jpg")
    # Simula fallimento di validazione
    monkeypatch.setattr(img_module, "_legacy_validate", lambda url: (_ for _ in ()).throw(ValueError("bad")))
    with pytest.raises(ValueError):
        img_module.validate_url("bad_url")

def test_fetch_metadata(tmp_path):
    file = tmp_path / "test.jpg"
    im = Image.new("RGB", (10, 20))
    im.save(file, "JPEG")
    metadata = img.fetch_metadata(str(file))
    assert metadata["width"] == 10 and metadata["height"] == 20
    assert metadata["format"] == "JPEG"
