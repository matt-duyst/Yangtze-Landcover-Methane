"""The shape vocabulary, checked once over the set rather than once per figure.

`style.py` holds every colour a figure may draw and a test scans the figure
modules for colour literals. `diagram.py` does the same job for shapes, and
this file is the enforcement: a diagram may not draw an outline of its own.

Four things are checked here.

**The set is declared, and closed.** Every shape names the grammar it belongs
to and what it must not be confused with, and a figure that mixes grammars is
refused. Two visual languages meet in this repository -- ISO 5807's flowchart
symbols and the reproducibility grammar of Patil, Peng and Leek -- and a figure
following both would follow neither.

**Shapes declared against each other are distinguishable by outline.** This is
the shape analogue of the luminance gap the colour roles hold, and it exists
for the same reason: an adjacency nothing checks is a comment. The one pair it
cannot separate is `process` against `predefined process`, which ISO
distinguishes by bars *inside* a shared outline, and the report names that pair
rather than scoring it zero.

**The ISO principles are structural assertions, not intentions.** One entry
point and one exit point per shape, the decision symbol excepted; two labelled
outcomes per decision; a reading order. Each is checked against the declared
edge list, and each check has a positive control, because a rule that cannot
fail is not a rule.

**The Patil grammar is the source's own.** Eleven stage names in the source's
order and four states with the source's spelling, taken from the authors'
reference implementation rather than restated. A fifth state is added here and
is asserted to be *declared* as an addition.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import numpy as np
import pytest

from src.figures import diagram
from src.figures.diagram import Edge, Node


# --------------------------------------------------------------------------
# the set is declared and closed
# --------------------------------------------------------------------------

def test_every_shape_carries_a_grammar_and_a_reason():
    for name, shape in diagram.SHAPES.items():
        assert shape.name == name
        assert shape.grammar in (diagram.ISO, diagram.PATIL), name
        assert len(shape.why) > 40, name


def test_the_adjacency_declaration_is_symmetric():
    """One side claiming an adjacency the other does not is a declaration bug.

    The same assertion `tests/test_figures_palette.py` makes first about the
    colour roles, and for the same reason: the checks below run over declared
    pairs, so a one-sided declaration is silently only half-checked.
    """
    for name, shape in diagram.SHAPES.items():
        for other in shape.against:
            assert other in diagram.SHAPES, f"{name} -> {other}"
            assert name in diagram.SHAPES[other].against, f"{name} vs {other}"


def test_no_shape_is_declared_against_one_from_another_grammar():
    """The two grammars never meet, so an adjacency between them is a mistake."""
    for name, shape in diagram.SHAPES.items():
        for other in shape.against:
            assert diagram.SHAPES[other].grammar == shape.grammar, name


def test_asking_for_an_undeclared_shape_says_what_to_do_instead():
    with pytest.raises(KeyError, match="not a declared shape"):
        diagram.shape("hexagon")


def test_a_figure_may_not_mix_the_two_grammars():
    assert diagram.check_grammar({"process", "decision"}) == diagram.ISO
    assert diagram.check_grammar({"state_observed"}) == diagram.PATIL

    with pytest.raises(ValueError, match="may not mix visual grammars"):
        diagram.check_grammar({"process", "state_observed"})


# --------------------------------------------------------------------------
# shapes declared against each other are distinguishable
# --------------------------------------------------------------------------

def test_every_flowchart_shape_builds_a_closed_outline():
    for name in diagram.PATHS:
        points = diagram.outline(name, 2.0, 1.0)
        assert points.shape[1] == 2
        assert np.allclose(points[0], points[-1]), name


def test_declared_pairs_differ_in_outline():
    report = diagram.outline_report()

    assert report["failures"] == []
    assert report["min_difference"] >= diagram.MIN_OUTLINE_DIFFERENCE
    assert report["pairs"] >= 10


def test_the_one_pair_an_outline_check_cannot_separate_is_named():
    """ISO separates these by bars inside a shared rectangle, not by outline."""
    report = diagram.outline_report()

    assert ("predefined_process", "process") in report["separated_by_decoration"]
    assert diagram.SHAPES["predefined_process"].decoration
    assert not diagram.SHAPES["process"].decoration
    signature = diagram.outline_signature
    assert np.allclose(signature("process"), signature("predefined_process"))


def test_the_outline_check_would_catch_a_near_duplicate():
    """The positive control. A check that finds nothing must be able to find."""
    a = diagram.outline_signature("process")
    b = diagram.outline_signature("data")
    nearly = a + (b - a) * 0.05

    assert float(np.sqrt(np.mean((a - nearly) ** 2))) < (
        diagram.MIN_OUTLINE_DIFFERENCE)


def test_shapes_are_compared_at_the_aspect_they_are_drawn_at():
    """At 1:1 a stadium is a circle, and the terminator would be the connector.

    The comparison has to be of what is drawn, or it declares two shapes
    confusable that on the page are nothing alike -- and, worse, would pass a
    pair that really is.
    """
    square = diagram.outline_signature("terminator", aspect=1.0)
    circle = diagram.outline_signature("connector", aspect=1.0)
    assert np.allclose(square, circle, atol=2e-3)

    drawn = diagram.outline_signature("terminator")
    assert not np.allclose(drawn, diagram.outline_signature("connector"),
                           atol=0.05)


def test_the_signature_measures_form_and_not_size():
    """A connector drawn small is still a different shape from a large one."""
    assert np.allclose(diagram.outline_signature("connector"),
                       diagram.outline_signature("connector"))
    small = diagram._densify(diagram.outline("connector", 0.3, 0.3))
    big = diagram._densify(diagram.outline("connector", 3.0, 3.0))
    for points in (small, big):
        radii = np.hypot(points[:, 0], points[:, 1])
        assert np.allclose(radii / radii.mean(), 1.0, atol=1e-3)


# --------------------------------------------------------------------------
# the ISO principles, each with a control
# --------------------------------------------------------------------------

def _pair(shape_a="process", shape_b="process"):
    return [Node("a", shape_a, "a", 0, 0), Node("b", shape_b, "b", 0, 1)]


def test_a_well_formed_flow_reports_no_violation():
    nodes = _pair()
    assert diagram.iso_violations(nodes, [Edge("a", "b")]) == []


def test_a_second_exit_point_on_a_process_is_caught():
    nodes = _pair() + [Node("c", "process", "c", 1, 1)]
    edges = [Edge("a", "b", exit="bottom"), Edge("a", "c", exit="right")]

    violations = diagram.iso_violations(nodes, edges)
    assert any("more than one exit point" in text for text in violations)


def test_a_branch_may_still_fan_out_from_one_exit_point():
    """One exit *point*, not one line. A branch may split past the box."""
    nodes = _pair() + [Node("c", "process", "c", 1, 1)]
    edges = [Edge("a", "b", exit="bottom"), Edge("a", "c", exit="bottom")]

    assert diagram.iso_violations(nodes, edges) == []


def test_a_second_entry_point_is_caught():
    nodes = _pair() + [Node("c", "process", "c", 1, 0)]
    edges = [Edge("a", "b", entry="top"), Edge("c", "b", entry="left")]

    violations = diagram.iso_violations(nodes, edges)
    assert any("more than one entry point" in text for text in violations)


def test_a_decision_with_one_outcome_is_caught():
    nodes = [Node("d", "decision", "d?", 0, 0), Node("b", "process", "b", 0, 1)]

    violations = diagram.iso_violations(nodes, [Edge("d", "b", "yes")])
    assert any("labelled outcomes" in text for text in violations)


def test_an_unlabelled_decision_branch_is_caught():
    """The violation the standard's principles make easiest to introduce."""
    nodes = [Node("d", "decision", "d?", 0, 0),
             Node("b", "process", "b", 0, 1),
             Node("c", "process", "c", 1, 1)]
    edges = [Edge("d", "b", "yes", exit="bottom"), Edge("d", "c", exit="right")]

    violations = diagram.iso_violations(nodes, edges)
    assert any("unlabelled branch" in text for text in violations)


def test_both_outcomes_leaving_one_side_is_caught():
    nodes = [Node("d", "decision", "d?", 0, 0),
             Node("b", "process", "b", 0, 1),
             Node("c", "process", "c", 1, 1)]
    edges = [Edge("d", "b", "yes", exit="bottom"),
             Edge("d", "c", "no", exit="bottom")]

    violations = diagram.iso_violations(nodes, edges)
    assert any("both outcomes share one side" in text for text in violations)


def test_a_line_running_against_the_reading_order_must_say_so():
    nodes = _pair()
    backwards = [Edge("b", "a")]

    assert any("reading order" in text
               for text in diagram.iso_violations(nodes, backwards))
    assert diagram.iso_violations(nodes, [Edge("b", "a", "retry")]) == []


def test_an_undeclared_shape_in_a_graph_is_caught():
    nodes = [Node("a", "hexagon", "a", 0, 0), Node("b", "process", "b", 0, 1)]

    violations = diagram.iso_violations(nodes, [Edge("a", "b")])
    assert any("not a declared shape" in text for text in violations)


# --------------------------------------------------------------------------
# routing
# --------------------------------------------------------------------------

def test_a_straight_run_stays_straight():
    assert diagram.route((0, 0), (0, -2), "bottom", "top") == [(0, 0), (0, -2)]
    assert diagram.route((0, 0), (3, 0), "right", "left") == [(0, 0), (3, 0)]


def test_a_line_between_rows_turns_in_the_gutter():
    points = diagram.route((0, 0), (3, -2), "bottom", "top")

    assert len(points) == 4
    assert points[1][1] == points[2][1] == -1.0     # halfway, in the gutter


def test_a_shift_moves_the_turn_off_the_halfway_line():
    points = diagram.route((0, 0), (3, -2), "bottom", "top", shift=-0.4)

    assert points[1][1] == pytest.approx(-1.4)


def test_a_label_sits_near_the_source_rather_than_at_the_midpoint():
    """A branch label answers the question in the diamond it leaves."""
    points = diagram.route((0, 0), (6, -4), "bottom", "top")
    near = diagram._label_point(points, 0.3)

    assert near[0] == pytest.approx(0.0)
    assert near[1] == pytest.approx(-0.3)


# --------------------------------------------------------------------------
# the Patil grammar is the source's own
# --------------------------------------------------------------------------

def test_the_stages_are_the_sources_eleven_in_its_own_order():
    """From `scifigure`'s own default, which is the authors' implementation."""
    assert len(diagram.STAGES) == 11
    assert diagram.STAGES[0] == "Population"
    assert diagram.STAGES[-1] == "Claim"
    assert list(diagram.STAGES).index("Code") > list(
        diagram.STAGES).index("Analysis plan")


def test_the_sources_four_states_are_present_under_its_own_names():
    names = {name.removeprefix("state_") for name in diagram.STATE_GLYPH}

    assert {"observed", "different", "unobserved", "incorrect"} <= names


def test_the_fifth_state_is_declared_as_an_addition():
    """Patil has four. This repository needs one more and must say so."""
    extra = diagram.SHAPES["state_unattributable"]

    assert extra.symbol == "not attributable"
    assert "Not one of the source's four states" in extra.why
    assert len(diagram.STATE_GLYPH) == 5


def test_every_state_has_a_glyph_and_a_legend_line():
    assert set(diagram.STATE_GLYPH) == {name for name, _ in diagram.STATES}
    for name in diagram.STATE_GLYPH:
        assert diagram.SHAPES[name].grammar == diagram.PATIL
    assert len({glyph for glyph in diagram.STATE_GLYPH.values()}) == 5


def test_the_state_shapes_carry_no_outline():
    """They are glyphs. Asking for an outline must say so rather than guess."""
    for name in diagram.STATE_GLYPH:
        with pytest.raises(KeyError, match="draws a glyph"):
            diagram.outline(name)
