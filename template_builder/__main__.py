# template_builder/__main__.py

from .builder_core import TemplateBuilderApp
import argparse


def main() -> None:
    parser = argparse.ArgumentParser(prog="template_builder")
    # NOTA: non servono manualmente --help/-h, Argparse li genera di default
    # Aggiungi qui altre opzioni se necessario:
    # parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.parse_args()

    app = TemplateBuilderApp()
    if app.root:
        app.root.mainloop()


if __name__ == "__main__":
    main()
