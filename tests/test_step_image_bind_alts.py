import unittest

from template_builder.step_image import bind_steps, steps_to_html
from template_builder.model import StepImage


class TestBindStepsWithAlts(unittest.TestCase):
    def test_bind_steps_uses_provided_alts(self):
        texts = ["First step text", "Second step text"]
        images = ["http://img1.png", "http://img2.png"]
        alts = ["Alt text 1", "Alt text 2"]
        steps = bind_steps(texts, images, alts)
        # Verifichiamo che siano creati due StepImage con alt corrispondenti
        self.assertEqual(len(steps), 2)
        self.assertIsInstance(steps[0], StepImage)
        self.assertEqual(steps[0].alt, "Alt text 1")
        self.assertEqual(steps[1].alt, "Alt text 2")

        # Controlliamo anche steps_to_html
        html_output = steps_to_html(steps)
        self.assertIn("<ol>", html_output)
        self.assertIn("<li>", html_output)
        self.assertIn('src="http://img1.png"', html_output)
        self.assertIn("First step text", html_output)

    def test_bind_steps_missing_alt_raises(self):
        texts = ["Some text", "Other text"]
        images = ["http://img1.png", "http://img2.png"]
        alts = ["", "NoAlt2"]
        # Il primo alt è vuoto: deve sollevare ValueError
        with self.assertRaises(ValueError) as cm:
            bind_steps(texts, images, alts)
        self.assertIn(
            "Errore: l'immagine in posizione 1 non ha l'attributo ALT", str(cm.exception)
        )        

    def test_bind_steps_all_missing_alts_raises(self):
        texts = ["", "Text2"]
        images = ["http://img1.png", "http://img2.png"]
        alts = ["", ""]
        # Tutti e due gli alt sono vuoti: deve sollevare per la prima immagine mancante
        with self.assertRaises(ValueError) as cm:
            bind_steps(texts, images, alts)
        self.assertIn(
            "Errore: l'immagine in posizione 2 non ha l'attributo ALT", str(cm.exception)
        )