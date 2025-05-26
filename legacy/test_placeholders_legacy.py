# tests/test_placeholders.py
import unittest
import tkinter as tk
from ui_utils import PlaceholderEntry, PlaceholderSpinbox

class TestPlaceholders(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()

    def tearDown(self):
        self.root.destroy()

    def test_entry_placeholder_initial(self):
        ph = "Inserisci nome"
        e = PlaceholderEntry(self.root, placeholder=ph)
        e.pack()
        self.root.update_idletasks()
        self.assertEqual(e.get(), ph)
        self.assertEqual(e.cget('foreground'), 'grey')

    def test_entry_focus_in_out(self):
        ph = "Username"
        e = PlaceholderEntry(self.root, placeholder=ph)
        e.pack()
        self.root.update_idletasks()
        e.event_generate('<FocusIn>')
        self.root.update_idletasks()
        self.assertEqual(e.get(), '')
        self.assertEqual(e.cget('foreground'), e.default_fg)
        e.event_generate('<FocusOut>')
        self.root.update_idletasks()
        self.assertEqual(e.get(), ph)
        self.assertEqual(e.cget('foreground'), 'grey')

    def test_spinbox_placeholder_initial(self):
        ph = "Seleziona"
        sb = PlaceholderSpinbox(self.root, placeholder=ph, from_=0, to=0)
        sb.pack()
        self.root.update_idletasks()
        self.assertEqual(sb.get(), ph)
        self.assertEqual(sb.cget('foreground'), 'grey')

    def test_spinbox_focus_in_out(self):
        ph = "0"
        sb = PlaceholderSpinbox(self.root, placeholder=ph, from_=0, to=0)
        sb.pack()
        self.root.update_idletasks()
        sb.event_generate('<FocusIn>')
        self.root.update_idletasks()
        self.assertEqual(sb.get(), '')
        self.assertEqual(sb.cget('foreground'), sb.default_fg)
        sb.event_generate('<FocusOut>')
        self.root.update_idletasks()
        self.assertEqual(sb.get(), ph)
        self.assertEqual(sb.cget('foreground'), 'grey')

if __name__ == '__main__':
    unittest.main()
