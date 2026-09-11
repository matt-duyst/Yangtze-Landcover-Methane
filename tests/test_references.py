"""The register and the BibTeX beside it cannot drift apart.

`notes/references.md` claims that `notes/references.bib` is generated from DOI
content negotiation and not typed. That claim was unenforced until 10 September
2026: the file was in fact produced that way, but nothing said so afterwards,
and a work added to the register without a regeneration would have left the two
disagreeing silently. This repository has already found two assertions of that
shape to be false -- a regeneration command that could not produce its artefact,
and a README table maintained beside the registry it described -- so an
unenforced claim about a generated file is a known failure mode here rather than
a hypothetical one.

These tests need no network. They check the structure the generator guarantees,
which is that the set of DOIs is the same on both sides and that every DOI has a
citation key. Whether each entry's *fields* match what doi.org returns cannot be
checked offline and is guaranteed by construction instead: the generator writes
the response body unaltered except for the key.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.build_references_bib import (  # noqa: E402
    BIBTEX,
    EXCLUDED,
    KEYS,
    REGISTER,
    register_dois,
)

BIB = BIBTEX.read_text(encoding="utf-8")

#: DataCite writes `doi = {...}`, Crossref writes `DOI={...}`.
BIB_DOIS = {m.lower() for m in re.findall(r"doi\s*=\s*\{([^}]+)\}", BIB, re.I)}
REGISTER_DOIS = {d.lower() for d in register_dois()}


def test_every_register_doi_is_in_the_bibtex():
    """A work added to the register without regenerating fails here."""
    assert REGISTER_DOIS - BIB_DOIS == set()


def test_every_bibtex_entry_is_in_the_register():
    """And the reverse: the BibTeX may not carry a work the register dropped."""
    assert BIB_DOIS - REGISTER_DOIS == set()


def test_every_register_doi_has_a_citation_key():
    assert REGISTER_DOIS - {d.lower() for d in KEYS} == set()


def test_no_citation_key_is_orphaned():
    assert {d.lower() for d in KEYS} - REGISTER_DOIS == set()


def test_citation_keys_are_unique():
    """Two works sharing a key would silently overwrite one another."""
    assert len(set(KEYS.values())) == len(KEYS)


def test_the_bibtex_entry_count_matches_its_own_header():
    """The header states a count; a stale count is the drift in miniature."""
    stated = re.search(r"^% (\d+) entries against (\d+) DOI mentions", BIB,
                       re.M)
    assert stated, "the header no longer states a count"
    assert int(stated.group(1)) == BIB.count("\n@")
    mentions = len(re.findall(r"`(10\.\d{4,9}/[^`\s]+)`",
                              REGISTER.read_text(encoding="utf-8")))
    assert int(stated.group(2)) == mentions


def test_the_register_states_the_number_of_entries_it_holds():
    """The preamble's word-number is checked, because it was wrong once.

    It said "forty" after the register had grown past forty. Spelled numbers in
    prose are exactly the claims this repository's drift mechanisms exist for,
    and this one is cheap to assert.
    """
    words = {40: "forty", 63: "sixty-three", 64: "sixty-four",
             65: "sixty-five", 66: "sixty-six"}
    count = len(REGISTER_DOIS)
    assert count in words, (
        f"{count} DOIs in the register; add the word to this test and update "
        f"the register's preamble")
    text = REGISTER.read_text(encoding="utf-8")
    assert f"carries {words[count]} entries as BibTeX" in text
    assert f"All {words[count]} DOIs\nresolved" in text or \
        f"All {words[count]} DOIs resolved" in text


@pytest.mark.parametrize("name,reason", sorted(EXCLUDED.items()))
def test_the_dois_less_entries_are_named_in_the_register(name, reason):
    """A deliberate absence must look different from a forgotten one."""
    text = REGISTER.read_text(encoding="utf-8")
    stem = name.split()[0].rstrip(":,")

    assert stem in text, f"{name} is excluded from the BibTeX but not named"
    assert reason


def test_the_generator_reports_agreement():
    from scripts.build_references_bib import check

    assert check() == 0
