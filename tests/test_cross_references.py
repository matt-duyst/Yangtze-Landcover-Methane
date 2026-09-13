"""A quoted cross-reference must still be present in the file it names.

**The drift class this guards.** This repository has three drift guards already:
recipes against artefacts, prose numbers against artefacts, and the figure
inventory against the files it names. A fourth class had no mechanism — one
record characterising another record's content, which goes stale when the cited
record is corrected and the citing one is not. It happened once, in
`notes/paper-target.md`, which cited `notes/grounding-methods.md` as holding two
claims that had been superseded three passes earlier.

**Why only quoted claims are guarded.** A survey on 14 September 2026 found 133
places where one record characterises another's content. **127 of them
paraphrase**, and a paraphrase cannot be checked mechanically: prose about prose
has no artefact to compare against, and asserting that a paraphrase is faithful
is the thing a reader does. **Six quote their target**, and a quotation is
checkable by substring — which makes the convention the guard: *where a
cross-file claim can quote, it should, because a quotation is the only form of
this claim a test can verify.*

That is the cheaper of the two designs considered. The alternative was a marker
naming the target section with a content hash, and it was rejected on the rule
`notes/grounding-methods.md` records about checks: a hash over prose fires on
every edit to the target file, including edits nowhere near the claim, and a
check that fires on things that are fine gets suppressed and then catches
nothing. A quotation check fires only when the quoted words are gone.

**What it does not do**, stated so nobody reads more into it: it says nothing
about the 127 paraphrases, it does not check that a quotation is used in the
sense the source intended, and it binds new claims only when they quote.

### Three false-positive classes, each found by building this

The first three versions of this check reported 6 of 6, then 2 of 6, then 1 of 6
failures, and every one of those was the check's fault rather than the prose's.
They are handled here and named because the next person to extend this will hit
them again.

* **Hard-wrapped prose.** Both records wrap at about 80 columns, so a quoted
  phrase spans a line break at a different position in the quote than in the
  source. Whitespace is normalised on both sides before comparing.
* **Sentence case.** A quotation dropped into the middle of a sentence is
  lower-cased where the source capitalises it — "one figure exists so far"
  against "One figure exists so far". The comparison is case-folded.
* **Deliberate historical quotation.** This repository's correction convention
  is to quote the superseded text beside the correction, so a corrected passage
  *contains* a quotation that is legitimately absent from the target. Those are
  exempt, recognised by a superseded marker near the claim.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

#: Where a cross-file claim may live. References.md is excluded: it is a
#: register of external sources whose "Cited in" lines are pointers rather than
#: characterisations, and it names files several hundred times.
SEARCHED = tuple(sorted(p for p in (REPO / "notes").glob("*.md")
                        if p.name != "references.md")) + (
    REPO / "ERRATA.md", REPO / "README.md",
    REPO / "data" / "processed" / "README.md",
)

#: A backticked or linked markdown filename, a characterising verb, then a
#: quotation. The verb list is the one the survey found in use.
CLAIM = re.compile(
    r"(?:`(?:notes/)?(?P<bare>[A-Za-z_.\-]+\.md)`"
    r"|\[`(?:notes/)?(?P<linked>[A-Za-z_.\-]+\.md)`\]\([^)]*\))"
    r"[^\n]{0,120}?"
    r"(?:records|states|establishes|holds|says|notes|documents|reports)\s+"
    r"(?:that\s+)?[^\n\"]{0,80}"
    r"\"(?P<quote>[^\"]{12,200})\"",
    re.IGNORECASE,
)

#: A superseded quotation is a record of what a passage used to say, so the
#: quoted words are meant to be absent from the target.
HISTORICAL = ("previously said", "previously read", "previously listed",
              "until this date", "used to say", "this entry said",
              "this passage said", "this passage previously")


def normalise(text: str) -> str:
    """Collapse whitespace and fold case, so wrapping and sentence case do not
    decide whether a quotation is present."""
    return re.sub(r"\s+", " ", text).strip().casefold()


def resolve(target: str, citing: Path) -> Path | None:
    """The file a claim names, looked for where this repository puts things."""
    for candidate in (REPO / target, REPO / "notes" / target,
                      citing.parent / target):
        if candidate.is_file():
            return candidate
    return None


def claims() -> list[tuple[Path, int, str, str, bool]]:
    """Every quoted cross-file claim: citing file, line, target, quote, historical."""
    found = []
    for path in SEARCHED:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        for match in CLAIM.finditer(text):
            target = match.group("bare") or match.group("linked")
            line = text[:match.start()].count("\n") + 1
            window = " ".join(lines[max(0, line - 4):line + 2]).lower()
            historical = any(marker in window for marker in HISTORICAL)
            found.append((path, line, target, match.group("quote"), historical))
    return found


def test_the_survey_still_finds_quoted_cross_references():
    """If this reaches zero the guard has stopped guarding anything.

    The regex depends on a phrasing convention rather than on a marker, so a
    change of house style would silently empty it. Six were found on
    14 September 2026.
    """
    assert len(claims()) >= 4, (
        "no quoted cross-file claims found; the CLAIM pattern has probably "
        "stopped matching this repository's phrasing")


def test_every_quoted_cross_reference_is_still_in_the_file_it_names():
    """The claim this guard exists for."""
    stale = []
    for path, line, target, quote, historical in claims():
        if historical:
            continue
        resolved = resolve(target, path)
        if resolved is None:
            stale.append(f"{path.name}:{line} names {target}, which does not exist")
            continue
        if normalise(quote) not in normalise(resolved.read_text(encoding="utf-8")):
            stale.append(
                f"{path.name}:{line} quotes {target} as saying "
                f"{normalise(quote)[:70]!r}, which is no longer there. Either the "
                f"quotation is stale, or it records what the target used to say "
                f"and should be marked with a superseded phrase such as "
                f"'previously said'.")
    assert not stale, "stale quoted cross-references:\n  " + "\n  ".join(stale)


def test_historical_quotations_are_exempt_and_at_least_one_exists():
    """The exemption has to be exercised or it is untested machinery.

    `notes/paper-target.md` carries one: the Olofsson recommendation claim,
    corrected on 13 September 2026 with the superseded text quoted beside the
    correction. If that stops being true the exemption is dead code.
    """
    historical = [c for c in claims() if c[4]]
    assert historical, (
        "no historical quotations found, so the exemption in this guard is "
        "untested; check whether the correction convention has changed")
