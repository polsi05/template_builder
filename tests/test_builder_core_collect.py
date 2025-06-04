from template_builder.builder_core import TemplateBuilderApp
import pytest


def test_collect_skips_steps_without_alt(monkeypatch):
    app = TemplateBuilderApp(enable_gui=False)
    # Imposto STEP1 con testo e caricamento immagine, ma non c'è alt nel widget
    app._state["STEP1"] = "Mix"
    app._state["IMAGES_STEP"] = ["mix.png"]
    ctx = app._collect()
    # Poiché manca l'alt per l'immagine, non viene creato alcuno step
    assert isinstance(ctx.get("STEPS"), list)
    assert len(ctx["STEPS"]) == 0
    # Non deve esistere la chiave STEP1_IMG_ALT nel contesto
    assert "STEP1_IMG_ALT" not in ctx
