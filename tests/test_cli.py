# tests/test_cli.py

import json
import os
import sys
import tempfile
import subprocess
from pathlib import Path
import pytest

# Percorso al pacchetto (ci mettiamo nella cartella project-root affinché funzioni il "python -m template_builder")
PACKAGE_ROOT = Path(__file__).parent.parent.resolve()
PYTHON = sys.executable  # path all’interprete corrente

def write_tmp_file(content: str, suffix: str) -> Path:
    """
    Crea un file temporaneo con contenuto `content` e suffisso `.suffix`.
    Ritorna il Path.
    """
    fd, path_str = tempfile.mkstemp(suffix=suffix)
    os.close(fd)
    path = Path(path_str)
    path.write_text(content, encoding="utf-8")
    return path

def run_cli(args: list, cwd: Path = PACKAGE_ROOT) -> subprocess.CompletedProcess:
    """
    Esegue `python -m template_builder <args>` nella cartella cwd.
    Ritorna il CompletedProcess.
    """
    cmd = [PYTHON, "-m", "template_builder"] + args
    return subprocess.run(
        cmd, cwd=str(cwd),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8"
    )

def test_missing_template_file(tmp_path):
    data = write_tmp_file("{}", suffix=".json")
    # Chiedo un template che non esiste
    result = run_cli(["--template", "non_esiste.html", "--data", str(data)])
    assert result.returncode == 1
    assert "Template non trovato" in result.stderr

def test_missing_data_file(tmp_path):
    tpl = write_tmp_file("<h1>{{ title }}</h1>", suffix=".html")
    # Data inesistente
    result = run_cli(["-t", str(tpl), "-d", "non_esiste.json"])
    assert result.returncode == 1
    assert "File JSON non trovato" in result.stderr

def test_invalid_json_in_data(tmp_path):
    tpl = write_tmp_file("<h1>{{ title }}</h1>", suffix=".html")
    bad_json = write_tmp_file("{ not a valid json }", suffix=".json")
    result = run_cli(["-t", str(tpl), "-d", str(bad_json)])
    assert result.returncode == 1
    assert "Errore di parsing JSON" in result.stderr

def test_render_to_stdout(tmp_path):
    tpl = write_tmp_file("<p>{{ greeting }}</p>", suffix=".html")
    data = write_tmp_file(json.dumps({"greeting": "Ciao"}), suffix=".json")
    result = run_cli(["-t", str(tpl), "-d", str(data)])
    assert result.returncode == 0
    # stdout deve contenere <p>Ciao</p>
    assert "<p>Ciao</p>" in result.stdout
    assert result.stderr == ""

def test_render_to_file(tmp_path):
    tpl = write_tmp_file("<div>{{ name }}</div>", suffix=".html")
    data = write_tmp_file(json.dumps({"name": "Alice"}), suffix=".json")
    out_file = tmp_path / "output.html"
    result = run_cli(["-t", str(tpl), "-d", str(data), "-o", str(out_file)])
    assert result.returncode == 0
    # stdout deve essere vuoto
    assert result.stdout == ""
    assert result.stderr == ""
    # Controllo contenuto su disco
    content = out_file.read_text(encoding="utf-8")
    assert "<div>Alice</div>" in content

def test_jinja2_not_installed(monkeypatch, tmp_path):
    """
    Ora che export_html utilizza il fallback _simple_render senza Jinja2,
    ci aspettiamo che il comando termini con successo (returncode 0) e
    che lo stdout contenga il rendering di {{ k }} → "X".
    """
    tpl = write_tmp_file("<p>{{ k }}</p>", suffix=".html")
    data = write_tmp_file(json.dumps({"k": "X"}), suffix=".json")
    # Simulo l’assenza di jinja2 rimuovendo sys.modules["jinja2"]
    monkeypatch.setitem(sys.modules, "jinja2", None)
    result = run_cli(["-t", str(tpl), "-d", str(data)])
    # Prima aspettavamo errore, ora ci aspettiamo successo con fallback
    assert result.returncode == 0
    # stdout deve contenere il fallback <p>X</p>
    assert "<p>X</p>" in result.stdout
    assert result.stderr == ""
