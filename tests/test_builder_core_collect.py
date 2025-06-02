from template_builder.builder_core import TemplateBuilderApp

def test_collect_adds_steps_and_alt(monkeypatch):
    app = TemplateBuilderApp(enable_gui=False)
    app._state["STEP1"] = "Mix"
    app._state["IMAGES_STEP"] = ["mix.png"]
    ctx = app._collect()
    assert ctx["STEPS"][0]["IMG_SRC"] == "mix.png"
    assert ctx["STEP1_IMG_ALT"] == "Mix"
