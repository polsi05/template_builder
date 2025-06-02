import json, tempfile
from template_builder.services.storage import quick_save, load_recipe, SCHEMA_VERSION

def test_quick_save_schema_v2(tmp_path):
    p = tmp_path / "x.json"
    ctx = {"TITLE": "Hi"}
    saved = quick_save(ctx)
    data = json.loads(saved.read_text("utf-8"))
    assert data["schema"] == SCHEMA_VERSION
    assert data["data"]["TITLE"] == "Hi"

def test_migrate_v1(tmp_path):
    # crea artificiosamente un file v1
    f = tmp_path / "old.json"
    old = {"created": "t", "data": {"STEP1": "X", "IMAGES_STEP": ["x.png"]}}
    f.write_text(json.dumps(old), "utf-8")
    new_ctx = load_recipe(f)
    assert "STEPS" in new_ctx
    assert new_ctx["STEP1_IMG_ALT"] == "X"
