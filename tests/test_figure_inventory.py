"""The inventory cannot promise a figure that does not exist.

`figures/README.md` is the register of the figure set: what is built, what is
planned, and what in the 2023 thesis each answers to. Nothing checked it.

That gap has a shape. `tests/test_prose_claims.py` verifies every **number**
quoted in prose against the artefact it comes from, which is a strong check and
the wrong one here: a sentence naming a file is not a number, so a stopped task
left four accurate-looking references to `framework_reproduction` in four
committed files while no such figure existed. Nothing failed, because nothing
was looking. What the register needed was a check on **named artefacts against
existence**, in both directions.

The rule the check rests on is structural rather than a matter of phrasing, and
`figures/README.md` states it in its own text:

* a row under *What exists* names a stem in backticks, and both the PNG and the
  PDF must be there;
* a row under *What is planned and does not exist* names a figure in plain
  prose with no backticks, and must not correspond to a file.

A planned figure therefore cannot be written as a stem and a built one cannot be
written as prose, so the guard never has to guess which a row is. The section
headings are matched verbatim: renaming one fails here rather than silently
switching off half the check.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
FIGURES = REPO / "figures"
INVENTORY = FIGURES / "README.md"
CAPTIONS = FIGURES / "README_fragments.md"

BUILT_HEADING = "## What exists"
PLANNED_HEADING = "## What is planned and does not exist"

#: Written-out numbers, because the inventory's counts are prose and a count
#: that is only prose is what let "a planned eleven" sit above a table of
#: twelve.
NUMERALS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20,
}


def section(heading: str) -> str:
    """The text under ``heading``, up to the next heading of the same level."""
    text = INVENTORY.read_text(encoding="utf-8")
    assert heading in text, f"{heading!r} is gone from figures/README.md"
    body = text.split(heading, 1)[1]
    return body.split("\n## ", 1)[0]


def first_cells(body: str) -> list[str]:
    """The first cell of every data row of the one table in ``body``."""
    out = []
    for line in body.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if not cells or cells[0] in ("Figure", "") or set(cells[0]) <= set("- "):
            continue
        out.append(cells[0])
    return out


def built() -> list[str]:
    """Figure stems the inventory says exist."""
    return [cell.strip("`") for cell in first_cells(section(BUILT_HEADING))]


def planned() -> list[str]:
    """Figures the inventory says are planned, as prose."""
    return first_cells(section(PLANNED_HEADING))


def on_disk() -> set[str]:
    return {path.stem for path in FIGURES.glob("*.png")}


# --------------------------------------------------------------------------
# both directions
# --------------------------------------------------------------------------

def test_every_figure_the_inventory_names_exists():
    """The direction that was open. Four committed files named a tenth figure
    for the length of one commit and nothing noticed."""
    missing = [stem for stem in built()
               if not ((FIGURES / f"{stem}.png").exists()
                       and (FIGURES / f"{stem}.pdf").exists())]

    assert missing == [], f"the inventory promises {missing}"


def test_every_figure_that_exists_is_in_the_inventory():
    """The other direction, which is how a figure gets built and forgotten."""
    assert on_disk() - set(built()) == set()


def test_a_planned_figure_is_prose_and_never_a_stem():
    """The marker is structural, so the guard never guesses which a row is."""
    for name in planned():
        assert "`" not in name, name
        assert not (FIGURES / f"{name}.png").exists(), name
        assert name not in built(), name


def test_the_two_sections_are_where_the_guard_expects_them():
    text = INVENTORY.read_text(encoding="utf-8")

    assert text.count(BUILT_HEADING) == 1
    assert text.count(PLANNED_HEADING) == 1
    assert text.index(BUILT_HEADING) < text.index(PLANNED_HEADING)


def test_the_guard_would_catch_a_promised_figure(tmp_path):
    """The positive control. A check that finds nothing must be able to find."""
    stems = built() + ["a_figure_that_was_never_drawn"]
    missing = [stem for stem in stems
               if not (FIGURES / f"{stem}.png").exists()]

    assert missing == ["a_figure_that_was_never_drawn"]


# --------------------------------------------------------------------------
# the inventory, the recipes and the captions are one set
# --------------------------------------------------------------------------

def test_every_built_figure_has_a_recipe_and_every_recipe_a_row():
    entries = yaml.safe_load((REPO / "config" / "recipes.yml").read_text())
    entries = entries["recipes"] if isinstance(entries, dict) else entries
    registered = {Path(entry["artefact"]).stem for entry in entries
                  if entry["artefact"].startswith("figures/")
                  and entry["artefact"].endswith(".png")}

    assert registered == set(built())


def test_every_built_figure_has_a_caption():
    """A figure nobody captioned is as much a gap as one nobody registered."""
    captions = CAPTIONS.read_text(encoding="utf-8")

    for stem in built():
        assert f"]({stem}.png)" in captions, stem


def test_every_built_figure_has_a_module_that_exists():
    """The second column names it, so the second column can be opened."""
    for row in section(BUILT_HEADING).splitlines():
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        if len(cells) < 2 or cells[0] in ("Figure", "") or not cells[0]:
            continue
        if set(cells[0]) <= set("- "):
            continue
        module = cells[1].strip("`")
        assert (REPO / "src" / "figures" / module).exists(), module


# --------------------------------------------------------------------------
# nothing else in the repository may name a figure that is not there
# --------------------------------------------------------------------------

def test_the_verification_script_only_knows_figures_that_exist():
    """`VECTOR_ONLY` named the tenth figure for a commit while it did not exist.

    Subset rather than equality in each case: `coverage_saturation_2018` has no
    builder here because it needs an input that is not committed, which is a
    declared absence and not a gap.
    """
    from scripts.verify_figure import BUILDERS, NATIVE, VECTOR_ONLY

    stems = set(built())
    assert set(BUILDERS) <= stems
    assert set(VECTOR_ONLY) <= stems
    assert set(NATIVE) <= stems


def markdown_files() -> list[Path]:
    import subprocess

    out = subprocess.run(["git", "ls-files", "*.md"], cwd=REPO,
                         capture_output=True, text=True, check=True)
    return [REPO / line for line in out.stdout.split() if line]


def test_every_figures_path_named_in_prose_resolves():
    """`notes/references.md` said "figures/framework_reproduction follows" of a
    file that did not exist. A path in prose is a promise like any other."""
    pattern = re.compile(r"[`(]figures/([A-Za-z0-9_./-]*)")
    unresolved = []
    for path in markdown_files():
        for match in pattern.finditer(path.read_text(encoding="utf-8")):
            token = match.group(1).rstrip("./")
            if not token:
                continue                       # a reference to the directory
            target = FIGURES / token
            if target.exists() or (FIGURES / f"{token}.png").exists():
                continue
            unresolved.append(f"{path.relative_to(REPO)}: figures/{token}")

    assert unresolved == []


def test_every_bare_stem_the_inventory_backticks_is_a_figure():
    """The inventory's Figure 3.1 entry named the tenth figure in prose.

    Scoped to this one file, where a backticked token with no dot and no slash
    is always a figure stem. The same rule over a module docstring would flag
    every backticked word in it -- `decision`, `process`, `observed` -- so the
    guard stops here, and a prose mention inside a docstring is the one member
    of this drift class that is still unguarded.
    """
    text = INVENTORY.read_text(encoding="utf-8")
    known = set(built()) | {name.replace(" ", "_") for name in planned()}
    bare = {token for token in re.findall(r"`([a-z][a-z0-9_]*)`", text)
            if "." not in token and "/" not in token}

    assert bare <= known, f"named but not a figure: {sorted(bare - known)}"


# --------------------------------------------------------------------------
# the counts are counts of the tables
# --------------------------------------------------------------------------

def _numeral(text: str, pattern: str) -> int:
    match = re.search(pattern, text, re.I)
    assert match, f"no match for {pattern!r}"
    word = match.group(1).lower()
    assert word in NUMERALS, word
    return NUMERALS[word]


def test_the_inventorys_own_counts_match_its_tables():
    exists = section(BUILT_HEADING)
    plan = section(PLANNED_HEADING)

    assert _numeral(exists, r"\n(\w+)\.\s") == len(built())
    assert _numeral(plan, r"\n(\w+), so the set is") == len(planned())
    assert _numeral(plan, r"a planned (\w+)") == len(built()) + len(planned())
    assert _numeral(plan, r"and (\w+) of them exist") == len(built())


def test_the_repository_readme_agrees_with_the_inventory():
    """It has not always. "Nine of a planned eleven" sat above twelve."""
    text = (REPO / "README.md").read_text(encoding="utf-8")

    assert _numeral(text, r"(\w+) of a planned \w+\nexist") == len(built())
    assert _numeral(text, r"\w+ of a planned (\w+)\nexist") == (
        len(built()) + len(planned()))


def test_the_numeral_table_covers_what_the_inventory_can_reach():
    assert max(NUMERALS.values()) >= len(built()) + len(planned()) + 4
