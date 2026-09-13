"""The palette, checked once over the role set rather than once per figure.

Every figure in this repository draws from :data:`src.figures.style.ROLES`, so
greyscale separation and colour-vision separation are properties of that set
and not of any figure. Checking them per figure measured whatever each figure
happened to use and would have had to be rewritten for each of the nine.

Three things are checked here and a fourth deliberately is not.

* **Greyscale**, over the declared adjacencies. Not over all pairs: sixteen
  roles do not fit into the seven slots a 0.15 convention leaves on a
  zero-to-one scale, and a test that cannot pass is a test that gets deleted.
  The adjacency graph is what makes the check both possible and meaningful, so
  its symmetry is asserted first -- an adjacency one side claims and the other
  does not is a bug in the declaration.
* **Colour vision deficiency**, the same pairs, under simulated protanopia,
  deuteranopia and tritanopia.
* **The relief band**, which is a range rather than a value and so cannot be a
  pairwise check at all. Every overlay must sit clear *below* the darkest tone
  the relief reaches, and the two bands' flat-ground tones must separate, since
  most of the study area is flat.
* **Not** the sequential ramps. A ramp's adjacent samples are arbitrarily close
  by construction, so a minimum pairwise gap says nothing about one. They are
  checked for monotonicity and span in `tests/test_figures_fields.py`, which is
  the test that convention needs and this one cannot provide.

The last test is the one that keeps the whole thing honest: no figure module
may name a colour. Without it the roles are a convention rather than a rule,
and a convention loses to a deadline.
"""

from __future__ import annotations

import numpy as np

import ast
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import pytest

from src.figures import style

FIGURE_MODULES = sorted(
    p for p in (Path(__file__).resolve().parents[1] / "src" / "figures").glob("*.py")
    if p.name not in {"style.py", "__init__.py"})


def test_there_is_at_least_one_figure_module_to_scan():
    """A sweep that searched nothing looks exactly like a sweep that passed."""
    assert len(FIGURE_MODULES) >= 4


def test_every_declared_adjacency_is_declared_by_both_sides():
    assert style.asymmetric_adjacencies() == []


def test_the_adjacency_graph_is_not_empty_and_covers_every_role():
    report = style.greyscale_report()

    assert report["adjacent_pairs"] >= 20
    named = {name for pair in style._pairs() for name in pair}
    assert named == set(style.ROLES)


def test_every_adjacent_pair_separates_in_greyscale():
    report = style.greyscale_report()

    assert report["failures"] == [], report["failures"]
    assert report["min_adjacent_gap"] >= style.MIN_LUMINANCE_GAP


def test_the_all_pairs_gap_is_reported_and_is_not_the_convention():
    """Guards against someone later mistaking one number for the other.

    Two roles do collide in luminance -- absence and the light end of the
    relief are both near-white -- and that is correct, because they are drawn
    in different figures and never meet. The all-pairs minimum is therefore
    near zero by design and is reported, not asserted.
    """
    report = style.greyscale_report()

    assert report["min_any_gap"] < style.MIN_LUMINANCE_GAP
    assert report["min_adjacent_gap"] > report["min_any_gap"]


@pytest.mark.parametrize("kind", style.CVD_KINDS)
def test_every_adjacent_pair_separates_under_colour_vision_deficiency(kind):
    result = style.cvd_report()[kind]

    assert result["failures"] == [], result["failures"]
    assert result["min_distance"] >= style.MIN_CVD_DISTANCE


def test_the_cvd_simulation_actually_changes_colours():
    """A simulation that returned its input would pass every test above."""
    changed = [role.colour for role in style.ROLES.values()
               if style.simulate_cvd(role.colour, "deuteranopia")
               != tuple(matplotlib.colors.to_rgb(role.colour))]

    assert len(changed) >= 6


def test_the_relief_band_leaves_every_overlay_clear_below_it():
    report = style.relief_report()

    assert report["failures"] == [], report["failures"]
    for name, clearance in report["overlay_clearance"].items():
        assert clearance >= style.MIN_LUMINANCE_GAP, (name, clearance)


def test_the_study_region_is_separable_from_its_surroundings_in_greyscale():
    """The region is carried by contrast, not by hue, so a print keeps it."""
    report = style.relief_report()

    assert report["flat_ground_gap"] >= style.MIN_LUMINANCE_GAP
    assert report["sea_clearance"] >= style.MIN_LUMINANCE_GAP


def test_the_relief_ramp_runs_across_the_band_and_nowhere_else():
    low, high = style.relief_band()
    cmap = style.relief_cmap()
    luminance = [style._luminance(cmap(x)[:3]) for x in (0.0, 0.5, 1.0)]

    assert luminance[0] == pytest.approx(low, abs=0.01)
    assert luminance[-1] == pytest.approx(high, abs=0.01)
    assert luminance == sorted(luminance)


def test_role_refuses_a_name_it_does_not_have():
    with pytest.raises(KeyError, match="without adding a role"):
        style.role("chartreuse")


def test_every_role_says_why_it_exists():
    for name, role in style.ROLES.items():
        assert len(role.why) > 40, name
        assert role.kind in {"areal", "tint", "line", "mark", "text"}, name


# A hex triple or a matplotlib grey string, anywhere in a figure module.
_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")
_GREY = re.compile(r"^(?:0(?:\.\d+)?|1(?:\.0+)?)$")
_NAMED = {"white", "black", "red", "green", "blue", "grey", "gray", "cyan",
          "magenta", "yellow", "orange", "navy", "gold", "tan", "teal", "pink"}
#: Strings that are colour-shaped but are not colours a figure chose. "none"
#: is the absence of a colour; the rest are matplotlib enumerations.
_ALLOWED = {"none", "face", "auto"}


def _string_literals(path: Path):
    tree = ast.parse(path.read_text(encoding="utf-8"))
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            yield node.lineno, node.value


@pytest.mark.parametrize("module", FIGURE_MODULES, ids=lambda p: p.name)
def test_no_figure_module_names_a_colour(module):
    """A figure may not introduce a colour without adding a role.

    This is what makes "sea means one colour in every figure that draws sea"
    a fact rather than an intention. The scan is over string literals in the
    module's own syntax tree, so a colour hidden in a keyword argument, a
    default, or a dictionary is caught the same way as one written inline.
    """
    offences = []
    for lineno, value in _string_literals(module):
        if value in _ALLOWED:
            continue
        if _HEX.match(value) or _GREY.match(value) or value.lower() in _NAMED:
            offences.append(f"{module.name}:{lineno} {value!r}")

    assert offences == [], (
        "name a role in src/figures/style.py and use style.role(): "
        + "; ".join(offences))


def test_the_colour_scan_would_catch_a_colour_if_one_were_added(tmp_path):
    """The positive control. A scan that finds nothing must be able to find."""
    planted = tmp_path / "planted.py"
    planted.write_text('x = "#ff00ff"\ny = "white"\nz = "0.88"\n')

    found = [value for _, value in _string_literals(planted)
             if _HEX.match(value) or _GREY.match(value)
             or value.lower() in _NAMED]

    assert found == ["#ff00ff", "white", "0.88"]


def test_the_scientific_colour_maps_are_actually_installed():
    """The palette's luminance guarantees are void without `cmcrameri`.

    `style.sequential` falls back to a matplotlib map when the package is
    absent, and the fallback is silent. Under it `style.series(3)` returns
    three colours separated by 0.004 in luminance where `MIN_LUMINANCE_GAP`
    promises 0.15, so a line figure built in that environment is illegible in
    greyscale and no existing check notices: the greyscale report covers
    `ROLES`, whose values are declared hex, and not `SERIES`, which is derived.

    This was found on 16 September 2026 by running a figure script under the
    wrong interpreter -- `python3` rather than `.venv/bin/python` -- which
    recoloured a committed figure. The recipe check would have caught the
    recoloured bytes; nothing would have explained why.
    """
    from src.figures import style

    assert style._crameri is not None, (
        "cmcrameri is not importable, so every colour map in style.py is a "
        "silent matplotlib substitute and the declared luminance separations "
        "do not hold")


def test_the_categorical_series_separates_by_the_declared_gap():
    """`SERIES` is derived, so unlike `ROLES` nothing had checked it.

    The greyscale report walks the declared role palette. The categorical keys
    a line figure draws from are built at import time from a colour map, and
    the property the docstring claims for them -- that consecutive entries
    separate by at least `MIN_LUMINANCE_GAP` -- was never asserted.
    """
    from src.figures import style

    luminances = [style._luminance(c) for c in style.SERIES]
    gaps = [b - a for a, b in zip(luminances, luminances[1:])]

    assert luminances == sorted(luminances), "series must be ordered by tone"
    assert min(gaps) >= style.MIN_LUMINANCE_GAP, (
        f"consecutive series colours separate by {min(gaps):.3f}, below the "
        f"declared {style.MIN_LUMINANCE_GAP}")


def test_the_categorical_series_survives_colour_vision_deficiency():
    """`cvd_report` walks the role set; the line colours are not in it.

    The greyscale and CVD reports `scripts/verify_figure.py` prints cover
    `ROLES`, whose members are declared hex values with declared adjacencies.
    A line plot's series colours come from `SERIES`, which is derived at import
    time, and nothing simulated them. The two figures added on 16 September
    2026 are both line plots, so the gap became load-bearing.

    The threshold is the one `cvd_report` uses for roles, applied to every pair
    of series colours rather than to declared adjacencies, because every pair
    of lines in a plot is adjacent: a reader compares any curve with any other.
    """
    from src.figures import style

    floor = style.MIN_CVD_DISTANCE
    for kind in ("protanopia", "deuteranopia", "tritanopia"):
        simulated = [style.simulate_cvd(c, kind) for c in style.SERIES]
        for i, a in enumerate(simulated):
            for b in simulated[i + 1:]:
                distance = float(np.linalg.norm(style._lab(a) - style._lab(b)))
                assert distance >= floor, (
                    f"under {kind} two series colours are {distance:.1f} apart, "
                    f"below the {floor} the role set is held to")
