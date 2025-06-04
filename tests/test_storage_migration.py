import json, tempfile
from template_builder.services.storage import quick_save, load_recipe, SCHEMA_VERSION
import pytest

def test_quick_save_schema_v2(tmp_path):
    p = tmp_path / "x.json"
    ctx = {"TITLE": "Hi"}
    saved = quick_save(ctx)
    data = json.loads(saved.read_text("utf-8"))
    assert data["schema"] == SCHEMA_VERSION
    assert data["data"]["TITLE"] == "Hi"

def test_migrate_v1_raises_on_missing_alt(tmp_path):
    # crea artificialmente un file v1 senza alt
    f = tmp_path / "old.json"
    old = {"created": "t", "data": {"STEP1": "X", "IMAGES_STEP": ["x.png"]}}
    f.write_text(json.dumps(old), "utf-8")
    with pytest.raises(ValueError) as exc_info:
        load_recipe(f)
    # Controlla la presenza del messaggio relativo alla posizione 1
    assert "Errore: l'immagine in posizione 1 non ha l'attributo ALT" in str(exc_info.value)

