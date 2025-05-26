import re
import pytest

from template_builder.services import text as tx

# ---------------------------------------------------------------------------
# smart_paste
# ---------------------------------------------------------------------------

class TestSmartPaste:
    """Unit tests for :pyfunc:`template_builder.services.text.smart_paste`."""

    def test_semicolon_and_newlines_are_normalised(self):
        raw = " uno ;due;\ntre  \n\n quattro ; "
        expected = ["uno", "due", "tre", "quattro"]
        assert tx.smart_paste(raw) == expected

    def test_iterable_input_is_flattened_and_trimmed(self):
        data = ["alpha", " beta ;gamma", "delta\n epsilon "]
        expected = ["alpha", "beta", "gamma", "delta", "epsilon"]
        assert tx.smart_paste(data) == expected


# ---------------------------------------------------------------------------
# auto_format
# ---------------------------------------------------------------------------

class TestAutoFormat:
    """Unit tests for :pyfunc:`template_builder.services.text.auto_format`."""

    def test_ul_conversion_and_html_escaping(self):
        plain = "uno\ndue\n& speciale"
        out = tx.auto_format(plain)
        assert out == "<ul><li>uno</li><li>due</li><li>&amp; speciale</li></ul>"

    def test_p_conversion(self):
        plain = "one\ntwo"
        out = tx.auto_format(plain, mode="p")
        assert out == "<p>one</p><p>two</p>"

    def test_existing_markup_is_left_unmodified(self):
        html_snippet = "<ul><li>Already</li></ul>"
        assert tx.auto_format(html_snippet) == html_snippet


# ---------------------------------------------------------------------------
# extract_placeholders
# ---------------------------------------------------------------------------

class TestExtractPlaceholders:
    """Unit tests for :pyfunc:`template_builder.services.text.extract_placeholders`."""

    def test_unique_placeholder_names_are_collected(self):
        src = "<p>{{ FOO }}</p><div>{{BAR}}</div><span>{{ FOO }}</span>"
        assert tx.extract_placeholders(src) == {"FOO", "BAR"}


# ---------------------------------------------------------------------------
# images_to_html
# ---------------------------------------------------------------------------

class TestImagesToHtml:
    """Unit tests for :pyfunc:`template_builder.services.text.images_to_html`."""

    def test_grid_dimensions_and_sequential_placeholders(self):
        rows, cols = 2, 3
        html_grid = tx.images_to_html(rows, cols)
        # Correct number of rows and images
        assert html_grid.count("<tr>") == rows
        assert html_grid.count("<img") == rows * cols
        # Placeholders should be sequential from 1 to rows*cols (row‑major)
        numbers = list(map(int, re.findall(r"IMG(\d+)", html_grid)))
        assert numbers == list(range(1, rows * cols + 1))

    def test_zero_or_negative_values_fall_back_to_one_by_one(self):
        html_grid = tx.images_to_html(0, -5)
        assert html_grid.count("<img") == 1
