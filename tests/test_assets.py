import re
import pytest

from template_builder.assets import PLACEHOLDER_RGX, DEFAULT_COLS, PALETTE

def test_placeholder_rgx_basic():
    # TAG in maiuscolo e numeri
    html = "<div>{{ TITLE }}</div><p>{{A1_B2}}</p>"
    matches = PLACEHOLDER_RGX.findall(html)
    assert isinstance(matches, list)
    # Ci aspettiamo esattamente le stringhe “TITLE” e “A1_B2”
    assert matches == ["TITLE", "A1_B2"]

def test_placeholder_rgx_ignora_minuscole():
    # TAG tutto minuscolo non deve essere catturato (regex cerca solo [A-Z0-9_]+)
    html = "{{ title }} {{ miSto + spia }}"
    assert PLACEHOLDER_RGX.findall(html) == []

def test_default_cols_positive():
    # DEFAULT_COLS deve essere un intero >= 1 (stub indica 3)
    assert isinstance(DEFAULT_COLS, int)
    assert DEFAULT_COLS >= 1

def test_palette_keys_and_values():
    # PALETTE deve contenere le chiavi obbligatorie con valori stringa
    assert set(PALETTE.keys()) == {"error", "valid", "bg"}
    for k, v in PALETTE.items():
        assert isinstance(v, str)
        # Deve essere un colore esadecimale valido (inizia con “#” e 6 caratteri esadecimali)
        assert re.match(r"^#[0-9A-Fa-f]{6}$", v)
