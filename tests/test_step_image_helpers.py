import pytest
from template_builder.step_image import sort_steps, swap_steps, renumber_steps, bind_steps
from template_builder.model import StepImage

def test_bind_steps_alt_and_trim():
    texts  = ["Uno", "", "  "]
    images = ["a.png", "b.png"]
    steps  = bind_steps(texts, images)
    # due step (terzo vuoto ignorato)
    assert len(steps) == 2
    assert steps[0].alt == "Uno"
    # secondo non ha testo -> alt default
    assert steps[1].alt == "Step 2"

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
