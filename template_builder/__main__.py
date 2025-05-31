# template_builder/__main__.py

"""
Entry‐point a linea di comando per Template Builder.

Permette di:
  1. Caricare un template Jinja2 (HTML) da disco.
  2. Caricare un file JSON di contesto da disco.
  3. Renderizzare il template con il contesto.
  4. Stampare l’HTML risultante su stdout o salvarlo su file (--output).

Esempi d’uso (dalla shell):
  $ python -m template_builder --template tpl.html --data data.json
  $ python -m template_builder -t tpl.html -d data.json -o risultato.html
"""

import argparse
import json
import sys
import os
from pathlib import Path

from template_builder.services.storage import export_html

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="template_builder",
        description=(
            "Template Builder CLI: "
            "Renderizza un template Jinja2 con un file JSON di contesto."
        ),
    )

    parser.add_argument(
        "-t", "--template",
        type=str,
        required=True,
        help="Percorso al file template (HTML/Jinja2)."
    )
    parser.add_argument(
        "-d", "--data",
        type=str,
        required=True,
        help="Percorso al file JSON contenente il contesto (dizionario)."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help=(
            "Se specificato, salva l’HTML generato in questo percorso; "
            "altrimenti lo stampa su stdout."
        )
    )

    return parser.parse_args()

def load_json(path: str) -> dict:
    """
    Carica un file JSON da disco e restituisce il dizionario.
    In caso di errore (file non trovato o JSON invalido), esce con codice 1.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            print(f"[ERROR] Il file dati '{path}' non contiene un oggetto JSON (dict).",
                  file=sys.stderr)
            sys.exit(1)
        return data
    except FileNotFoundError:
        print(f"[ERROR] File JSON non trovato: '{path}'.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[ERROR] Errore di parsing JSON in '{path}': {e}", file=sys.stderr)
        sys.exit(1)

def main() -> None:
    args = parse_args()

    tpl_path = args.template
    data_path = args.data
    out_path = args.output

    # Controllo esistenza template
    if not os.path.isfile(tpl_path):
        print(f"[ERROR] Template non trovato: '{tpl_path}'", file=sys.stderr)
        sys.exit(1)

    # Caricamento JSON di contesto
    ctx = load_json(data_path)

    # Render HTML tramite export_html
    try:
        html_str = export_html(ctx, tpl_path)
    except Exception as e:
        print(f"[ERROR] Impossibile renderizzare il template: {e}", file=sys.stderr)
        sys.exit(1)

    # Se è specificato --output, scrivo su file; altrimenti stampo su stdout
    if out_path:
        try:
            out_file = Path(out_path)
            out_file.write_text(html_str, encoding="utf-8")
        except Exception as e:
            print(f"[ERROR] Errore scrittura su file '{out_path}': {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Stampiamo su stdout (senza newline aggiuntivo)
        sys.stdout.write(html_str)

if __name__ == "__main__":
    main()
