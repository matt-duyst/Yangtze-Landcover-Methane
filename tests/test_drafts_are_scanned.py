"""Every draft section must be in the claim checker's scanned set.

**Why this is a test rather than a check.** `scripts/verify_claims.py` verifies
each marked number in the prose against the artefact it names, and it only looks
at the files listed in its `SCANNED` tuple. A draft that is not in that tuple
carries markers that are never evaluated: **the checker passes, reporting a
count that excludes the file entirely, and every number in it is unverified
while looking verified.**

That happened. `notes/draft-discussion.md` was written on 13 September 2026 with
24 marked claims and was not added to `SCANNED`; the omission was caught by
reading the tuple rather than by any failure. A fourth draft was written the
next day and the same omission was available to make again.

So the rule is asserted here: any file matching the draft naming convention is
scanned. The convention is the filename — `notes/draft-*.md` — which is what
makes the rule checkable without a manifest to maintain.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))

import verify_claims as vc  # noqa: E402

#: The naming convention that defines a draft section.
PATTERN = "draft-*.md"


def drafts() -> list[Path]:
    return sorted((REPO / "notes").glob(PATTERN))


def test_there_are_drafts_to_check():
    """If the convention changes this guard must fail rather than pass empty."""
    assert len(drafts()) >= 4, (
        f"expected at least four notes/{PATTERN} sections; the naming "
        f"convention has probably changed and this guard is now blind")


def test_every_draft_is_scanned_by_the_claim_checker():
    """The claim this guard exists for."""
    scanned = {Path(name).as_posix() for name in vc.SCANNED}
    missing = [d.relative_to(REPO).as_posix() for d in drafts()
               if d.relative_to(REPO).as_posix() not in scanned]
    assert not missing, (
        "drafts absent from verify_claims.SCANNED, so their markers are never "
        "evaluated and the checker passes while verifying nothing in them: "
        + ", ".join(missing))


def test_every_draft_actually_carries_marked_claims():
    """A scanned draft with no markers is a draft whose numbers went unresolved.

    Weaker than the check above and worth having separately: being in the tuple
    is necessary and not sufficient. A draft quoting artefact numbers with no
    markers at all would pass the previous test and verify nothing.
    """
    bare = []
    for draft in drafts():
        text = draft.read_text(encoding="utf-8")
        if not vc.CLAIM.search(text):
            bare.append(draft.relative_to(REPO).as_posix())
    assert not bare, (
        "scanned drafts carrying no marked claims at all, which means any "
        "artefact number in them is unverified: " + ", ".join(bare))
