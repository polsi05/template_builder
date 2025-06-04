import pytest
from template_builder.step_image import sort_steps, swap_steps, renumber_steps, bind_steps
from template_builder.model import StepImage

def test_bind_steps_alt_and_trim_raise_on_missing_alt():
    texts  = ["Uno", "", "  "]
    images = ["a.png", "b.png"]
    # Il primo step (indice 0) ha testo "Uno" e immagine "a.png", ma alt mancanti
    # Deve quindi sollevare ValueError subito alla posizione 1 (i+1)
    with pytest.raises(ValueError) as exc_info:
        bind_steps(texts, images)
    # Controlla che il messaggio di errore indichi la posizione 1
    assert "Errore: l'immagine in posizione 1 non ha l'attributo ALT" in str(exc_info.value)

def test_helpers_ok():
    steps = [
        StepImage(img="", alt="", text="B", order=2),
        StepImage(img="", alt="", text="A", order=1),
    ]
    sort_steps(steps)
    assert [s.text for s in steps] == ["A", "B"]
    swap_steps(steps, 0, 1)
    assert [s.text for s in steps] == ["B", "A"]
    renumber_steps(steps)
    assert [s.order for s in steps] == [1, 2]
