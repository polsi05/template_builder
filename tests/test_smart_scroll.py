"""
Test per la feature Smart-Scroll (C2).
Verifica che bind_mousewheel venga applicato correttamente a widget scrollabili.
"""
import importlib

ui_utils = importlib.import_module("template_builder.infrastructure.ui_utils")

class Dummy:
    def __init__(self):
        self.bind_calls = []
        self.scrolled = []

    def bind(self, sequence, func, add=None):
        self.bind_calls.append((sequence, add))
        if sequence in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
            setattr(self, f"_cb_{sequence}", func)

    def yview_scroll(self, n, mode):
        self.scrolled.append((n, mode))

    def yview(self):
        return None

def test_bind_mousewheel_binds_all_events():
    d = Dummy()
    ui_utils.bind_mousewheel(d)
    expected = {"<MouseWheel>", "<Button-4>", "<Button-5>"}
    bound = {seq for seq, add in d.bind_calls}
    assert expected.issubset(bound)
    for _, add in d.bind_calls:
        assert add == "+"

def test_mousewheel_callback_scrolls() -> None:
    """
    Simula gli eventi di scroll per mouse/trackpad e verifica lo scroll sul widget.
    """
    d = Dummy()
    ui_utils.bind_mousewheel(d)

    # Simula rotella su (Windows/macOS)
    event = type("E", (), {"delta": 120})()
    cb_mouse = getattr(d, '_cb_<MouseWheel>', None)
    assert cb_mouse is not None, "Callback MouseWheel non registrato"
    cb_mouse(event)
    assert (-1, "units") in d.scrolled

    # Simula rotella giù
    event.delta = -120
    cb_mouse(event)
    assert (1, "units") in d.scrolled

    # Simula eventi X11 (Button-4 = su, Button-5 = giù)
    event4 = type("E", (), {"num": 4})()
    event5 = type("E", (), {"num": 5})()
    cb4 = getattr(d, '_cb_<Button-4>', None)
    cb5 = getattr(d, '_cb_<Button-5>', None)
    assert cb4 is not None and cb5 is not None, "Callback Button-4/5 non registrati"
    cb4(event4)
    cb5(event5)
    assert (-1, "units") in d.scrolled
    assert (1, "units") in d.scrolled
