import pytest
from template_builder.model import StepImage
from template_builder.step_image import (
    sort_steps,
    swap_steps,
    renumber_steps,
)

# ────────────────── helpers ──────────────────
def _make_steps():
    return [
        StepImage(img="3.png", alt="a3", text="C", order=3),
        StepImage(img="1.png", alt="a1", text="A", order=1),
        StepImage(img="2.png", alt="a2", text="B", order=2),
    ]

# ────────────────── sort_steps ───────────────
def test_sort_steps():
    steps = _make_steps()
    sort_steps(steps)
    assert [s.order for s in steps] == [1, 2, 3]
    assert [s.text for s in steps]  == ["A", "B", "C"]

# ────────────────── swap_steps ───────────────
def test_swap_steps_ok():
    steps = _make_steps()
    sort_steps(steps)  # 1,2,3
    swap_steps(steps, 0, 2)        # scambia primo-ultimo
    assert [s.text for s in steps] == ["C", "B", "A"]

def test_swap_steps_errors():
    steps = _make_steps()
    with pytest.raises(ValueError):
        swap_steps(steps, 0, 99)
    with pytest.raises(ValueError):
        swap_steps(steps, -1, 0)

# ────────────────── renumber_steps ───────────
def test_renumber_steps_basic():
    steps = _make_steps()
    # dopo sort ordine corretto ma numeri 1-2-3 già ok → idempotente
    sort_steps(steps)
    renumber_steps(steps)
    assert [s.order for s in steps] == [1, 2, 3]

def test_renumber_steps_gap_duplicates():
    steps = [
        StepImage(img="x.png", alt="x", text="X", order=10),
        StepImage(img="y.png", alt="y", text="Y", order=5),
        StepImage(img="y2.png", alt="y2", text="Y2", order=5),
    ]
    renumber_steps(steps)
    assert [s.order for s in steps] == [1, 2, 3]

def test_renumber_steps_empty():
    assert renumber_steps([]) == []

def test_renumber_steps_single():
    s = StepImage(img="one.png", alt="o", text="One", order=7)
    renumber_steps([s])
    assert s.order == 1
