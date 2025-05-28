"""UI helper stub – usato solo da widget futuri."""
def show_info(msg: str):  # pragma: no cover
    print(f"[info] {msg}")

def bind_mousewheel(widget):
    """
    Abilita lo scroll fluido con rotellina o gesture su un widget scrollabile.
    Funziona su macOS (MouseWheel), Windows e Linux (Button-4/5).
    """
    target = None
    # Se il widget è scrollabile di per sé
    if hasattr(widget, "yview"):
        target = widget
    else:
        # Cerca un figlio scrollabile
        for child in getattr(widget, "winfo_children", lambda: [])():
            if hasattr(child, "yview"):
                target = child
                break
    if not target:
        return

    def _on_mousewheel(event):
        delta = 0
        if hasattr(event, "delta"):
            # Windows/macOS
            delta = -1 if event.delta > 0 else 1
        else:
            # X11 Linux
            if getattr(event, "num", None) == 4:
                delta = -1
            elif getattr(event, "num", None) == 5:
                delta = 1
        if delta:
            try:
                target.yview_scroll(delta, "units")
            except Exception:
                pass

    target.bind("<MouseWheel>", _on_mousewheel, add="+")
    target.bind("<Button-4>", _on_mousewheel, add="+")
    target.bind("<Button-5>", _on_mousewheel, add="+")
