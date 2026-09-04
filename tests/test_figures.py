"""Tests for the shared figure conventions and the export path.

Offline, into `tmp_path`, reading nothing from `data/raw/` and drawing nothing
that depends on the composite. The figures under test are blank or trivially
constructed, because what is being tested is the machinery rather than any
particular figure.

The tests that carry the weight are the refusals. An export path that quietly
writes a 100 dpi figure is worse than one that has no checks at all, because
the check gives false confidence, so each limit is tested by the failure it is
supposed to cause and by the absence of any file afterwards. A half-written
figure left behind by a failed export is the specific bad outcome: on a rerun
it looks like a current figure and it is not.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402  no display in the test environment

import matplotlib.pyplot as plt
import pytest

import src.figures.output as output_module
from src.figures import style
from src.figures.output import MAX_BYTES, Export, export, figures_root


@pytest.fixture
def blank():
    """A conforming figure, closed afterwards whatever the test does."""
    fig = style.figure(width_cm=style.DOUBLE_COLUMN_CM, height_cm=6.0)
    fig.add_subplot(111)
    yield fig
    plt.close(fig)


def test_export_writes_both_a_vector_and_a_raster_from_one_call(blank, tmp_path):
    result = export(blank, "both", directory=tmp_path)

    assert result.vector == tmp_path / "both.pdf"
    assert result.raster == tmp_path / "both.png"
    assert result.vector.exists() and result.raster.exists()
    assert result.vector.read_bytes()[:5] == b"%PDF-"
    assert result.raster.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_export_reports_what_it_measured_not_what_it_was_asked_for(blank, tmp_path):
    result = export(blank, "measured", directory=tmp_path)

    assert isinstance(result, Export)
    # Width in cm recovered from the figure, and pixels recovered from the
    # PNG header, must agree with the dpi the export claims.
    assert result.width_cm == pytest.approx(style.DOUBLE_COLUMN_CM, abs=1e-6)
    assert result.raster_pixels[0] == pytest.approx(
        result.width_cm * style.CM * result.dpi, abs=2)
    assert result.raster_bytes == result.raster.stat().st_size
    assert result.vector_bytes == result.vector.stat().st_size


def test_export_refuses_a_dpi_below_the_minimum_and_writes_nothing(blank, tmp_path):
    with pytest.raises(ValueError, match="below the 300 dpi minimum"):
        export(blank, "coarse", directory=tmp_path, dpi=150)

    assert list(tmp_path.iterdir()) == []


def test_export_refuses_a_figure_narrower_than_the_minimum(tmp_path):
    # Built through pyplot rather than style.figure, which refuses first.
    fig = plt.figure(figsize=(6.0 * style.CM, 5.0 * style.CM))
    try:
        with pytest.raises(ValueError, match="below the 8.0 cm minimum"):
            export(fig, "narrow", directory=tmp_path)
    finally:
        plt.close(fig)

    assert list(tmp_path.iterdir()) == []


def test_style_figure_refuses_an_undersized_width_before_anything_is_drawn():
    with pytest.raises(ValueError, match="below the 8.0 cm minimum"):
        style.figure(width_cm=7.9)


def test_export_refuses_a_file_over_the_size_limit_and_leaves_nothing(monkeypatch,
                                                                     blank,
                                                                     tmp_path):
    monkeypatch.setattr(output_module, "MAX_BYTES", 10)

    with pytest.raises(ValueError, match="above the 10 B limit"):
        export(blank, "heavy", directory=tmp_path)

    assert list(tmp_path.iterdir()) == []


def test_a_failed_export_does_not_replace_a_figure_already_written(blank, tmp_path):
    good = export(blank, "stable", directory=tmp_path)
    before = good.raster.read_bytes()

    with pytest.raises(ValueError):
        export(blank, "stable", directory=tmp_path, dpi=72)

    assert good.raster.read_bytes() == before
    assert sorted(p.name for p in tmp_path.iterdir()) == ["stable.pdf", "stable.png"]


def test_the_size_limit_is_the_venue_limit():
    assert MAX_BYTES == 5 * 1024 * 1024


def test_palette_resolves_to_a_usable_colour_map():
    cmap = style.sequential()

    assert cmap is not None
    rgba = cmap(0.5)
    assert len(rgba) == 4
    assert all(0.0 <= channel <= 1.0 for channel in rgba)


def test_palette_records_which_source_it_came_from():
    assert style.PALETTE_SOURCE in {"cmcrameri", "matplotlib-fallback"}


def test_categorical_colours_are_distinct_and_ordered_in_lightness():
    colours = style.categories(4)

    assert len(colours) == 4
    assert len(set(colours)) == 4
    # Sampling along a sequential map must give a monotone greyscale order, so
    # the keys stay distinguishable in a black and white print.
    grey = [0.299 * r + 0.587 * g + 0.114 * b for r, g, b, _ in colours]
    assert grey == sorted(grey)


def test_conventions_forbid_gridlines_and_embed_fonts():
    style.apply()

    assert matplotlib.rcParams["axes.grid"] is False
    # Type 42 keeps the glyphs as a real font; type 3 would draw them as paths.
    assert matplotlib.rcParams["pdf.fonttype"] == 42
    assert matplotlib.rcParams["font.family"] == ["sans-serif"]


def test_figures_root_is_overridable_so_tests_never_touch_the_working_tree(monkeypatch,
                                                                          tmp_path):
    monkeypatch.setenv("FIGURES_DIR", str(tmp_path / "elsewhere"))

    assert figures_root() == tmp_path / "elsewhere"


def test_figures_root_defaults_to_the_repository_figures_directory(monkeypatch):
    monkeypatch.delenv("FIGURES_DIR", raising=False)

    root = figures_root()
    assert root.name == "figures"
    assert (root.parent / "src" / "figures").is_dir()
