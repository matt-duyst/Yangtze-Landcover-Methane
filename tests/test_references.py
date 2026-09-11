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


ONES = ("zero", "one", "two", "three", "four", "five", "six", "seven",
        "eight", "nine", "ten", "eleven", "twelve", "thirteen", "fourteen",
        "fifteen", "sixteen", "seventeen", "eighteen", "nineteen")
TENS = ("", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy",
        "eighty", "ninety")


def spell(n: int) -> str:
    """English for 0-999, hyphenated, as this register's prose writes numbers.

    Written out rather than tabulated because the previous version of this test
    held a hand-maintained lookup of five numbers and failed the moment the
    register grew past them -- which is the same brittleness the mechanism
    exists to catch, reproduced inside the check.
    """
    if n < 20:
        return ONES[n]
    if n < 100:
        return TENS[n // 10] + ("" if n % 10 == 0 else f"-{ONES[n % 10]}")
    rest = n % 100
    return f"{ONES[n // 100]} hundred" + ("" if rest == 0 else f" {spell(rest)}")


def test_the_register_states_the_number_of_entries_it_holds():
    """The preamble's word-number is checked, because it was wrong twice.

    It said "forty" after the register had grown past forty, and "sixty-three"
    after it passed a hundred. Spelled numbers in prose are exactly the claims
    this repository's drift mechanisms exist for, and this one is cheap.
    """
    word = spell(len(REGISTER_DOIS))
    # Whitespace is collapsed before matching. An earlier version enumerated
    # the places a line break might fall, and then failed when the register
    # grew past a hundred and the break landed inside the spelled number
    # itself -- a check that depended on line wrapping rather than on the
    # claim, which is the brittleness this file exists to remove.
    text = " ".join(REGISTER.read_text(encoding="utf-8").split())

    assert f"carries {word} entries as BibTeX" in text, \
        f"the register should say it carries {word} entries"
    assert f"All {word} cited DOIs resolved" in text or \
        f"All {word} DOIs resolved" in text, \
        f"the register should say all {word} resolved"


def test_the_warned_against_dois_are_in_the_register_and_not_the_bibtex():
    """A DOI named as a warning must not become a citation by accident.

    Three of these arrived at once in the methods pass: two resolve to the
    wrong paper and one does not resolve. The register names them so a future
    reader knows they were tested, which means they appear in the prose and
    must be kept out of the BibTeX.
    """
    from scripts.build_references_bib import NOT_CITATIONS

    register_text = REGISTER.read_text(encoding="utf-8")
    for doi, reason in NOT_CITATIONS.items():
        assert doi in register_text, f"{doi} is warned against but not named"
        assert reason, f"{doi} has no reason recorded"
        assert doi.lower() not in BIB_DOIS, \
            f"{doi} is a warning, not a citation, and must not be in the BibTeX"
        assert doi not in KEYS, f"{doi} must not have a citation key"


def test_no_duplicate_section_headings():
    """Two groups carried the heading "Findings relied on" until 11 September.

    A duplicate heading is not navigable and a cross-reference to it is
    ambiguous, which is the same class of defect as an unchecked count.
    """
    import collections

    headings = re.findall(r"^(#{2,3} .+)$",
                          REGISTER.read_text(encoding="utf-8"), re.M)
    repeated = [h for h, n in collections.Counter(headings).items() if n > 1]

    assert repeated == [], f"duplicated headings: {repeated}"


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
