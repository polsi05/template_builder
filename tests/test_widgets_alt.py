# tests/test_widgets_alt.py

import unittest
import tkinter as tk

from template_builder.widgets import SortableImageRepeaterField


class TestSortableImageRepeaterFieldAlt(unittest.TestCase):
    def setUp(self) -> None:
        # Creiamo una root Tkinter; se non c'è DISPLAY, usiamo tk.Tcl() come fallback
        try:
            self.root = tk.Tk()
            self.root.withdraw()  # non mostriamo la finestra
        except tk.TclError:
            self.skipTest("Tkinter/Display non disponibile")
        self.field = SortableImageRepeaterField(self.root)

    def tearDown(self) -> None:
        # Se abbiamo effettivamente una finestra Tk, la distruggiamo
        if isinstance(self.root, tk.Tk):
            self.root.destroy()

    def test_get_alts_returns_correct_list(self):
        # Aggiungiamo due righe con URL e ALT
        self.field._add_row("http://example.com/img1.png", "alt1")
        self.field._add_row("http://example.com/img2.png", "alt2")
        expected_alts = ["alt1", "alt2"]
        self.assertEqual(self.field.get_alts(), expected_alts)

    def test_get_alts_empty_strings_when_no_alt(self):
        # Aggiungiamo due righe con URL ma ALT vuoti
        self.field._add_row("http://example.com/img1.png", "")
        self.field._add_row("http://example.com/img2.png", "")
        # Poiché get_alts() restituisce get_value(), otteniamo liste di stringhe vuote
        self.assertEqual(self.field.get_alts(), ["", ""])

    def test_validation_sets_border_red_when_alt_missing(self):
        # Aggiungiamo una riga con URL valido ma ALT vuoto
        self.field._add_row("http://example.com/img1.png", "")
        # Preleviamo i widget interni (frame, entry_src, entry_alt)
        row_frame, entry_src, entry_alt = self.field._rows[0]
        # Simuliamo uscita dal focus per innescare _validate
        self.field._validate(entry_src, entry_alt)
        # Dopo validazione, entry_alt dovrebbe avere highlightbackground rosso
        self.assertEqual(entry_alt.cget("highlightbackground"), "#f44336")
        # Anche entry_src dovrebbe essere evidenziato in rosso (ALT mancante)
        self.assertEqual(entry_src.cget("highlightbackground"), "#f44336")

    def test_validation_keeps_border_green_when_alt_and_url_valid(self):
        # Aggiungiamo una riga con URL valido e ALT valido
        self.field._add_row("http://example.com/img1.png", "descrizione")
        row_frame, entry_src, entry_alt = self.field._rows[0]
        # Simuliamo uscita dal focus per innescare _validate
        self.field._validate(entry_src, entry_alt)
        # Ora entrambi i campi dovrebbero avere highlightbackground verde
        self.assertEqual(entry_alt.cget("highlightbackground"), "#4caf50")
        self.assertEqual(entry_src.cget("highlightbackground"), "#4caf50")

    def test_move_and_delete_rows_preserve_alts_order(self):
        # Aggiungiamo tre righe con URL e ALT diversi
        self.field._add_row("url1", "alt1")
        self.field._add_row("url2", "alt2")
        self.field._add_row("url3", "alt3")
        # L'ordine iniziale degli ALT è ["alt1", "alt2", "alt3"]
        self.assertEqual(self.field.get_alts(), ["alt1", "alt2", "alt3"])
        # Spostiamo la seconda riga in cima
        second_row = self.field._rows[1][0]
        self.field._move_row(second_row, -1)  # ora l'ordine righe è: url2, url1, url3
        self.assertEqual(self.field.get_alts(), ["alt2", "alt1", "alt3"])
        # Cancelliamo la riga iniziale (ora "url2"/"alt2")
        first_row = self.field._rows[0][0]
        self.field._del_row(first_row)
        # L'ordine diventa: ["alt1", "alt3"]
        self.assertEqual(self.field.get_alts(), ["alt1", "alt3"])
