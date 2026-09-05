"""Every regeneration recipe is checked against the artefact it claims to make.

A recipe is a claim about the repository: run this and you get that file. Two
such claims had drifted, and nothing noticed, because they were written as
prose in a README that a human maintained beside the code. One command could
not produce the committed file at all; another produced a different file and
said nothing. Both were found by accident, months later.

`config/recipes.yml` holds every recipe as data. These tests execute it.

Three tiers, and the repository is honest about which is which:

* **continuously** -- every input is committed, so the recipe runs on a fresh
  clone in about a second. Run on every suite invocation.
* **on_local** -- needs `data/raw/` or `data/interim/`, both gitignored. Run
  where those exist and skipped with a reason where they do not. Marked `slow`
  because the analysis grid takes about three minutes.
* **on_demand** -- the composite, which needs 28.9 GB of transfer. Never run
  here. Its checksum is recorded and asserted, which catches a stale artefact
  but not a drifted recipe, and the registry says when it was last verified by
  actually running it.

The slow tier is excluded from a default run and invoked with

    python -m pytest -m slow

which is documented in README.md, because a test nobody runs is not a test.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.verify_recipes import (  # noqa: E402
    BEGIN,
    END,
    readme_table,
    recipes,
    run_one,
)

RECIPES = recipes()
CONTINUOUS = [r for r in RECIPES if r["verified"] == "continuously"]
ON_LOCAL = [r for r in RECIPES if r["verified"] == "on_local"]
ON_DEMAND = [r for r in RECIPES if r["verified"] == "on_demand"]

DOCS = {"data/processed/README.md", "figures/README_fragments.md"}


def committed_artefacts() -> set[str]:
    out = subprocess.run(["git", "ls-files", "data/processed", "figures"],
                         cwd=REPO, capture_output=True, text=True, check=True)
    return {line for line in out.stdout.split() if line} - DOCS


# --------------------------------------------------------------------------
# the registry and the documentation cannot drift apart
# --------------------------------------------------------------------------

def test_every_committed_artefact_has_a_recipe():
    """Adding an artefact without a recipe fails here.

    An artefact nothing produces is the strongest form of drift and this
    repository had one, committed with no code that makes it. It is now
    registered as `unregenerable`, which is a deliberate declaration rather
    than an omission, so the honest case and the forgotten case look different.
    """
    registered = {r["artefact"] for r in RECIPES}

    assert committed_artefacts() - registered == set()


def test_every_recipe_names_an_artefact_that_exists():
    for entry in RECIPES:
        assert (REPO / entry["artefact"]).exists(), entry["artefact"]


def test_the_readme_table_is_the_generated_one():
    """The documentation is generated from the registry, not kept beside it.

    Prose maintained alongside code is what produced the original problem, so
    the README's regeneration table is written by
    `scripts/verify_recipes.py --update-readme` and this asserts the committed
    README still matches. Edit the registry, not the table.
    """
    text = (REPO / "README.md").read_text(encoding="utf-8")

    assert BEGIN in text and END in text, "the generated block markers are gone"
    block = text.split(BEGIN, 1)[1].split(END, 1)[0].strip()
    assert block == readme_table().strip(), \
        "README table is stale; run python scripts/verify_recipes.py --update-readme"


def test_every_recipe_declares_a_tier_and_a_comparison():
    for entry in RECIPES:
        assert entry["inputs"] in ("committed", "local", "network", "none")
        assert entry["compare"] in ("bytes", "subset", "none")
        assert entry["verified"] in ("continuously", "on_local", "on_demand",
                                     "unregenerable")
        if entry["verified"] == "unregenerable":
            assert entry["command"] is None
            assert entry["note"], "an unregenerable artefact must record provenance"
        else:
            assert entry["command"], entry["artefact"]


# --------------------------------------------------------------------------
# the cheap recipes are run
# --------------------------------------------------------------------------

@pytest.mark.parametrize("entry", CONTINUOUS, ids=lambda e: e["artefact"])
def test_a_fresh_clone_recipe_reproduces_its_artefact(entry, tmp_path):
    status, detail = run_one(entry, tmp_path)

    assert status == "identical", f"{entry['artefact']}: {status} {detail}"


@pytest.mark.slow
@pytest.mark.parametrize("entry", ON_LOCAL, ids=lambda e: e["artefact"])
def test_a_local_input_recipe_reproduces_its_artefact(entry, tmp_path):
    status, detail = run_one(entry, tmp_path)
    if status == "skipped":
        pytest.skip(detail)

    assert status == "identical", f"{entry['artefact']}: {status} {detail}"


# --------------------------------------------------------------------------
# the expensive ones are pinned rather than run
# --------------------------------------------------------------------------

@pytest.mark.parametrize("entry", ON_DEMAND, ids=lambda e: e["artefact"])
def test_an_on_demand_artefact_matches_its_recorded_checksum(entry):
    """Catches a stale or hand-edited artefact. It cannot catch a drifted recipe.

    That limitation is the reason the registry also records when each was last
    verified by running the command, and the reason this tier is named
    on_demand rather than verified.
    """
    digest = hashlib.sha256((REPO / entry["artefact"]).read_bytes()).hexdigest()

    assert digest == entry["sha256"], (
        f"{entry['artefact']} no longer matches config/recipes.yml; if it was "
        f"regenerated, update sha256 and last_verified there")


def test_every_on_demand_recipe_records_when_it_was_last_verified():
    import datetime as dt

    for entry in ON_DEMAND:
        assert entry.get("sha256"), entry["artefact"]
        assert entry.get("last_verified_by"), entry["artefact"]
        stamp = dt.date.fromisoformat(str(entry["last_verified"]))
        assert stamp <= dt.date.today()


def test_the_tiers_partition_the_registry():
    """No artefact may be silently in no tier."""
    counted = len(CONTINUOUS) + len(ON_LOCAL) + len(ON_DEMAND) + \
        len([r for r in RECIPES if r["verified"] == "unregenerable"])

    assert counted == len(RECIPES)
