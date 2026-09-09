"""Tests for the pipeline framework figure.

Offline, reading only committed artefacts. The figure is built and asserted on
in memory; nothing is written.

A diagram fails differently from a map, and these tests are shaped by that.

**A diagram can be wrong about the repository and look perfect.** A box naming
a module that was renamed, or a step the code stopped performing, is the
diagram equivalent of a stale prose figure, and no other test in this suite
would catch one. Every node declares the paths it stands for and this file
opens them. It goes further where it can and asserts the *content*: that the
manifest really does refuse a disagreeing digest, that the area scripts really
do compare at a tenth of a percent, that the exporter really does refuse below
300 dpi. A path that exists is weaker evidence than a threshold that matches.

**ISO's principles are structural and are asserted as such.** One entry point
and one exit point per shape, the decision excepted; two labelled outcomes per
decision; a reading order. `tests/test_figures_diagram.py` proves those checks
can fail; this file applies them to the figure.

**The two things a naive pipeline diagram omits are asserted to be present.**
Which inputs are obtained and which are committed, carried by shape; and the
four refusals, without which the diagram describes a system that warns and
carries on.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

from src.figures import diagram, style
from src.figures import framework_pipeline as fp
from src.figures.framework_pipeline import framework_pipeline_figure


@pytest.fixture(scope="module")
def figure():
    fig = framework_pipeline_figure()
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = framework_pipeline_figure()
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# every box corresponds to something that exists
# --------------------------------------------------------------------------

def test_every_box_names_paths_that_are_in_the_repository():
    """The check a diagram needs and nothing else in this suite provides."""
    assert fp.missing_paths() == []


def test_every_box_that_stands_for_code_names_it():
    """A terminator and a connector stand for nothing; everything else does."""
    for node in fp.nodes():
        if node.shape in ("terminator", "connector"):
            assert node.exists == (), node.key
        else:
            assert node.exists, node.key


def test_the_manifest_gate_is_a_refusal_and_not_a_warning():
    """A path existing is weak evidence. This asserts the behaviour."""
    from src.fetch import manifest

    entry = {"archive": {"sha256": "a" * 64}}
    assert manifest.fill_archive_digest(entry, sha256="b" * 64) == "MISMATCH"
    assert entry["archive"]["sha256"] == "a" * 64      # left where it is
    assert manifest.fill_archive_digest(entry, sha256="a" * 64) == "unchanged"

    empty: dict = {}
    assert manifest.fill_archive_digest(empty, sha256="c" * 64) == "filled"


def test_the_area_gate_really_compares_at_a_tenth_of_a_percent():
    """The number written in the diamond, read off the scripts it names."""
    import ast

    for path in ("scripts/compute_urban_areas.py",
                 "scripts/compute_rice_areas.py"):
        source = (fp.REPO / path).read_text()
        tree = ast.parse(source)
        defaults = [node for node in ast.walk(tree)
                    if isinstance(node, ast.Constant) and node.value == 0.001]
        assert defaults, path
        assert "--tolerance" in source, path


def test_the_coverage_gate_really_refuses_above_one_point_zero_two():
    from importlib import import_module

    module = import_module("scripts.compute_rice_extent")
    assert module.COVERAGE_CEILING == 1.02
    assert module.COVERAGE_FLOOR == 0.80


def test_the_export_gate_really_refuses_below_the_venue_floors():
    from src.figures import output

    fig = style.figure(width_cm=style.MIN_WIDTH_CM, height_cm=4.0)
    try:
        with pytest.raises(ValueError, match="dpi minimum"):
            output.export(fig, "unused", dpi=150)
    finally:
        plt.close(fig)

    narrow = style.figure(width_cm=style.MIN_WIDTH_CM, height_cm=4.0)
    narrow.set_figwidth(4.0 * style.CM)
    try:
        with pytest.raises(ValueError, match="cm minimum"):
            output.export(narrow, "unused")
    finally:
        plt.close(narrow)


def test_the_recipe_counts_on_the_figure_come_from_the_register(figure):
    tiers = fp.recipe_tiers()
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert tiers["total"] == sum(
        tiers[key] for key in tiers if key != "total")
    assert f"Of {tiers['total']} registered recipes" in flat
    assert f"{tiers['continuously']} rebuild" in flat
    assert f"{tiers['on_local']} need a fetched input" in flat
    assert f"{tiers['on_demand']} need a network run" in flat


def test_the_figure_count_is_read_from_the_register_and_not_typed():
    """A figure on disk that nobody registered is not part of the set."""
    import yaml

    entries = yaml.safe_load((fp.REPO / "config" / "recipes.yml").read_text())
    entries = entries["recipes"] if isinstance(entries, dict) else entries
    registered = [e["artefact"] for e in entries
                  if e["artefact"].startswith("figures/")
                  and e["artefact"].endswith(".png")]

    assert fp.figure_pairs() == len(registered)
    published = next(n for n in fp.nodes() if n.key == "published")
    assert f"{len(registered)} PDF and PNG" in published.label


# --------------------------------------------------------------------------
# ISO conformance
# --------------------------------------------------------------------------

def test_the_flowchart_holds_the_structural_principles():
    assert diagram.iso_violations(fp.nodes(), fp.edges()) == []


def test_every_shape_drawn_is_from_the_declared_set_and_one_grammar():
    used = {node.shape for node in fp.nodes()}

    assert used <= set(diagram.SHAPES)
    assert diagram.check_grammar(used) == diagram.ISO


def test_no_shape_from_the_other_grammar_appears_here():
    """The two grammars are not fused, and this is where that is enforced."""
    used = {node.shape for node in fp.nodes()}

    assert not used & set(diagram.STATE_GLYPH)


def test_the_flow_reads_top_down_in_a_and_left_right_in_b():
    by_key = {node.key: node for node in fp.nodes()}

    for edge in fp.edges():
        source, target = by_key[edge.source], by_key[edge.target]
        if source.panel != target.panel:
            continue
        if source.panel == fp.PANEL_A and edge.label != "no":
            assert target.row >= source.row, f"{edge.source}->{edge.target}"
        if source.panel == fp.PANEL_B and edge.label != "no":
            assert target.column >= source.column, \
                f"{edge.source}->{edge.target}"


def test_every_decision_has_two_labelled_outcomes():
    """The violation the principles make easiest to introduce."""
    labels: dict = {}
    for edge in fp.edges():
        labels.setdefault(edge.source, set()).add(edge.label)

    for node in fp.nodes():
        if node.shape != "decision":
            continue
        assert labels[node.key] == {"yes", "no"}, node.key


def test_no_step_runs_on_nothing():
    """ISO's principle that an event needing information must show it."""
    for key, incoming in fp.inputs_shown().items():
        assert incoming >= 1, key


def test_the_two_panels_are_joined_by_the_connector_symbol():
    """ISO's own answer to a chart too long for its frame."""
    connectors = [n for n in fp.nodes() if n.shape == "connector"]

    assert len(connectors) == 2
    assert {n.panel for n in connectors} == {fp.PANEL_A, fp.PANEL_B}
    assert len({n.label for n in connectors}) == 1


# --------------------------------------------------------------------------
# the two things a naive pipeline diagram would omit
# --------------------------------------------------------------------------

def test_obtained_and_committed_inputs_are_told_apart_by_shape():
    """Carried by shape, so it costs no colour and survives a greyscale print."""
    obtained = [n for n in fp.nodes() if n.shape == "data"]
    committed = [n for n in fp.nodes() if n.shape == "stored_data"]

    assert len(obtained) == 5
    assert {n.key for n in obtained} == {"gaia", "glorice", "nesdc", "s5p",
                                         "gisa"}
    assert "reference" in {n.key for n in committed}


def test_the_five_fetch_routes_are_the_ones_the_repository_has():
    """Four platforms across five sources, checked against src/fetch/."""
    routes = {node.key: node.exists for node in fp.nodes()
              if node.shape == "data"}

    assert "src/fetch/figshare.py" in routes["gaia"]
    assert "src/fetch/figshare.py" in routes["glorice"]
    assert "src/fetch/scidb.py" in routes["nesdc"]
    assert "src/fetch/s5p.py" in routes["s5p"]
    assert routes["gisa"] == ("scripts/fetch_gisa.py",)   # no module: a bundle


def test_the_figure_says_why_the_obtained_boxes_are_a_different_shape(figure):
    """The set's functional-label convention, not a caption inside the frame."""
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)
    labels = [" ".join(t.get_text().split()) for ax in figure.axes
              for t in ax.texts if t.get_style() == "italic"]

    assert "data/raw/ is gitignored" in flat            # in the note
    assert labels == ["obtained: data/raw/ is gitignored",
                      "committed: arrives with the clone"]


def test_all_four_refusals_are_drawn(figure):
    """A diagram without them describes a system that warns and carries on."""
    gates = [node for node in fp.nodes() if node.shape == "decision"]

    assert len(gates) == 4
    assert {g.key for g in gates} == {"manifest", "area", "coverage", "export"}
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)
    assert "the failing branch stops" in flat


def test_every_refusal_ends_in_a_stop_rather_than_rejoining_the_flow():
    by_key = {node.key: node for node in fp.nodes()}
    outgoing = {node.key: 0 for node in fp.nodes()}
    for edge in fp.edges():
        outgoing[edge.source] += 1

    for edge in fp.edges():
        if edge.label != "no":
            continue
        target = by_key[edge.target]
        assert target.shape == "terminator", edge.target
        assert outgoing[target.key] == 0, edge.target


# --------------------------------------------------------------------------
# layout and what the figure says
# --------------------------------------------------------------------------

def test_the_figure_carries_no_title_of_its_own(figure):
    """The set's convention: the caption carries the title, the image does not."""
    assert figure._suptitle is None
    for ax in figure.axes:
        assert ax.get_title() == ""
    bold = [t.get_text() for t in figure.texts if t.get_fontweight() == "bold"]
    assert bold == ["(a) from source to lattice", "(b) from lattice to result"]


def test_the_layout_is_two_panels_and_says_why(figure):
    assert len(figure.axes) == 2
    assert figure.get_figwidth() / style.CM == pytest.approx(fp.FIG_WIDTH_CM)
    # One top-down frame would be eleven rows and over a page tall.
    rows = max(node.row for node in fp.nodes()) + 1
    one_panel = fp.BOTTOM_CM + (rows + 5) * fp.ROW_CM
    assert one_panel > figure.get_figheight() / style.CM


def test_every_axes_sits_inside_the_figure(figure):
    for index, ax in enumerate(figure.axes):
        box = ax.get_position()
        assert 0.0 <= box.x0 and box.x1 <= 1.0, index
        assert 0.0 <= box.y0 and box.y1 <= 1.0, index


def test_no_two_boxes_on_a_row_overlap():
    """The failure a declared grid makes possible to check and easy to make."""
    from collections import defaultdict

    rows = defaultdict(list)
    for node in fp.nodes():
        half = fp.BOX_W_CM * node.span / 2
        centre = node.column * fp.COL_CM
        rows[(node.panel, node.row)].append((centre - half, centre + half,
                                             node.key))
    for key, spans in rows.items():
        spans.sort()
        for (_, right, a), (left, _, b) in zip(spans, spans[1:]):
            assert left > right, f"{key}: {a} overlaps {b}"


def test_the_figure_says_it_is_not_the_thesis_architecture_diagram(figure):
    """ERRATA 4.1 and 3.3: that architecture was neither described accurately
    nor implemented as described, so it must not be redrawn."""
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "not a redrawing of the 2023 thesis's Figure 3.1" in flat
    assert "ERRATA.md 4.1 and 3.3" in flat
    assert "notes/repository-architecture.md" in flat


def test_no_box_mentions_a_network_or_an_architecture():
    """The reproduction built no network. The diagram must not imply one."""
    words = " ".join(node.label.lower() for node in fp.nodes())

    for banned in ("deeplab", "resnet", "encoder", "decoder", "epoch",
                   "training", "neural"):
        assert banned not in words, banned
