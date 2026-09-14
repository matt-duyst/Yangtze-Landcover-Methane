#!/usr/bin/env python3
"""Every claim in the drafts and captions, with the evidence behind it or none.

**Why an artefact rather than prose.** Three later passes need this — the
apparatus audit, the errata audit, and the write-up — and each would otherwise
walk the drafts again and reach a slightly different count. A table they read
cannot drift from a table they re-derive, and the recipe's byte comparison means
a draft gaining a marker fails the suite until this is regenerated.

**Granularity, stated because it bounds what the artefact can be used for.** One
row per *numeric* claim, which is the unit a marker attaches to and the unit a
resolver can verify. Prose claims — mechanisms, attributions, comparisons
carrying no number — are inventoried separately and by class rather than by
instance, in `notes/claim-audit.md`, because classifying "the sources are
interspersed" needs a reading and not a rule. **So this file is exhaustive for
numbers and deliberately not exhaustive for prose.**

## The five categories, and the fifth is the useful one

``measured``
    The number carries an inline resolver, so the claim checker verifies it
    against a committed artefact on every run. Mechanical, exact, no judgement:
    the marker names the artefact.

``cited``
    A literature figure the drafts' own exemption notes enumerate. Those notes
    are the authority here rather than this script's guess, because the drafts
    maintain them and a paper's author is the right person to say which of their
    numbers came from reading. **Note what this category does and does not
    assert**: that the number came from the literature, not that a citation
    appears beside it. The reference audit established that the drafts carry
    twelve citations in total, so almost every number in this category is
    attributed in a drafting note and *not* in the prose a reader sees.

``self_evident``
    Needs no support: a section reference, a panel letter, a year used as a
    date, the grid resolution, a count of the paper's own sections.

``unresolved``
    In a committed artefact and carrying no resolver, so it is supported but not
    verified. **The brief for this audit specified four categories and this is a
    fifth**, found by sampling the classifications: the drafts' own notes say
    several numbers are "read from the artefact", which is neither verified nor
    unsupported. It is the cheapest state to leave — adding a resolver is one
    line — and the easiest to mistake for either neighbour.

``neither``
    Asserted with neither a resolver nor a place in an exemption list. The point
    of the exercise, and split on write-up into claims needing a citation and
    claims needing a measurement.

## What the rules are, so a classification can be argued with

Each row carries the ``rule`` that classified it. A reader who disagrees with a
category can see which rule fired and change the rule rather than the number.
Rules are applied in the order below and the first match wins.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "processed" / "claim_inventory_2026.csv"

SOURCES = [f"notes/draft-{n}.md"
           for n in ("introduction", "methods", "results", "discussion")]
SOURCES.append("figures/README_fragments.md")

#: Where a draft's own commentary starts. Everything after it is drafting notes
#: rather than the section, and its numbers are about the draft rather than
#: claims in it.
TAIL = "## Drafting notes, not part of the section"

MARK = re.compile(r"(-?\d[\d,]*(?:\.\d+)?)\s*<!--#([a-zA-Z0-9_.]+)-->")
#: Scientific notation is matched whole. Without the exponent branch a p-value
#: of 1.3e-04 becomes two claims, "1.3" and "04", and both look unsupported.
NUM = re.compile(r"(?<![\w.#-])(-?\d[\d,]*?(?:\.\d+)?(?:[eE][-+]?\d+)?)(?![\w,]\d)(?![\w])")

#: Literature figures, taken from the drafts' own "Numbers not marked" and
#: "Numbers without a resolver" notes. The value is the note that names it, so
#: the authority for every entry is checkable.
LITERATURE = {
    # draft-introduction's list
    "30": "introduction: inventory spread, at least 30 percent",
    "15": "introduction: fifteen Tg, the inventory gap",
    "60": "introduction: 60 percent of emissions in three regions",
    "21.0": "introduction: national prior, coal",
    "13.7": "introduction/discussion: rice prior Tg, and the water-regime ratio",
    "9.5": "introduction: national prior, wastewater",
    "8.2": "introduction: national prior, livestock",
    "5.2": "introduction: national prior, landfills",
    "2.0": "introduction: national prior, wetlands",
    "1.3": "introduction: national prior, lakes and aquaculture",
    "64": "introduction: anthropogenic total Tg",
    "26": "introduction/discussion: 26 percent aquaculture share",
    "53": "introduction: posterior uncertainty, lower bound",
    "69": "introduction: posterior uncertainty, upper bound",
    "0.98": "introduction: downscaling R squared for CO2",
    "0.63": "introduction/discussion: downscaling R squared for CH4",
    "13.26": "introduction/discussion: downscaling RMSE ppb",
    "0.5": "introduction/discussion: averaging-kernel sensitivity threshold",
    # draft-discussion's list
    "197": "discussion: within-class aquaculture ratio",
    "38": "discussion: collection efficiency",
    "70": "discussion: collection efficiency",
    "85": "discussion: collection efficiency",
    "0.35": "discussion: posterior error correlation, distinct sector",
    "0.45": "discussion: posterior error correlation, shared surface, lower",
    "0.87": "discussion: posterior error correlation, shared surface, upper",
    "12": "discussion: transport error standard deviation ppb",
    "61": "discussion: rice isotopic signature",
    "56.1": "discussion: waste isotopic signature",
    "53.8": "discussion: South Asian campaign isotopic signature",
    "311": "discussion: South Asian campaign deuterium signature",
    "40": "discussion: bias reduction percent",
    "0.43": "discussion: Heilongjiang Tg pair, lower",
    "0.85": "discussion: Heilongjiang Tg pair, upper",
    "73.61": "discussion: SinoLC-1 overall accuracy",
    "0.954": "discussion: accuracy figure in section 8",
    # draft-results' list
    "11.9": "results: blended single-retrieval precision ppb",
    "14.5": "results: operational single-retrieval precision ppb",
    "0.475": "results: albedo-impervious zero-order correlation",
    "0.746": "results: albedo-NIR zero-order correlation",
    "0.695": "results: solar-zenith correlation",
    # methods' preprocessing chain
    "0.02": "methods: published SWIR albedo floor",
    "0.05": "methods: published albedo floor",
    "0.75": "methods: blended-albedo ceiling",
    "10": "methods: published precision filter, under 10 ppb",
}

#: Numbers that are structure rather than evidence. Matched on the surrounding
#: text rather than the value, because "8" is a section number in one place and
#: a measurement in another.
STRUCTURAL_CONTEXT = (
    re.compile(r"§\s*$"),                      # a section reference
    re.compile(r"(?:section|§)s?\s*\d*\s*(?:to|and|-|–)?\s*$", re.I),
    re.compile(r"panel\s*\(?$", re.I),
    re.compile(r"\bFigure\s*$", re.I),
    re.compile(r"\bTable\s*$", re.I),
)

#: Values that are always structure in this corpus.
STRUCTURAL_VALUES = {"0.25", "0.3125"}

#: A year used as a date rather than as a measurement.
YEAR = re.compile(r"^(19[5-9]\d|20[0-2]\d)$")

#: The study box and the lattice, which are configuration rather than findings.
#: They appear constantly in the captions and would otherwise dominate the
#: unsupported count with the same six numbers.
CONFIG_VALUES = {"114.8", "122.55", "122.6", "26.95", "27.0", "35.2",
                 "33", "31", "1023", "926", "97",
                 # the analysis-cell detail box the study-area figure draws
                 "31.3248", "31.3582", "121.0", "121.25",
                 # the 1/64 degree inking cell, in degrees and in km
                 "64", "1.4"}

#: Buffer radii swept by the decay curve. They are the figure's x-axis and a
#: parameter this work chose, not a finding about the domain.
SWEPT_VALUES = {"0", "25", "50", "75", "100", "150", "200", "300", "400", "500"}

#: Lines describing how a figure is drawn rather than what it shows. A caption
#: explaining a luminance choice or a dots-per-inch floor is documentation, and
#: its numbers are not claims about the domain.
DRAWING_LINE = re.compile(
    r"luminance|tone|palette|colour|color|dpi|\bcm\b|greyscale|grayscale|marker|hue|ISO 5807|arrow cap", re.I)

#: A pointer into another document, so the number is an address.
CROSSREF_CONTEXT = re.compile(
    r"(?:ERRATA\.md|README\.md|decisions\.md|ISO)`?\s*$", re.I)

#: Typography and code. A point size or a selector expression is neither a
#: finding nor a citation.
TYPOGRAPHY = re.compile(r"\b(?:pt|point size|font|axis label)\b", re.I)
CODE_SPAN = re.compile(r"`[^`]*$")

#: Lines that are structure by their shape rather than by their content.
STRUCTURAL_LINE = (
    re.compile(r"^#{1,6}\s"),                   # a heading, so "4.3" is a number
    re.compile(r"^\s*\d+\.\s+\*\*"),          # an enumerated list item
    re.compile(r"^\s*\|\s*-+"),                # a table rule
)

#: Patterns where the number is part of a token rather than a quantity.
TOKEN_CONTEXT = (
    re.compile(r"\d[:.]$"),                     # inside a time or a version
    re.compile(r"version\s*$", re.I),
    re.compile(r"processor\s*$", re.I),
    re.compile(r"[Ss]entinel-$"),
    re.compile(r"[A-Za-z]$"),                   # glued to a word, e.g. v2
)

#: A number that follows a marked number on the same line is usually the
#: marked one's label or its companion in a stated pair, not an independent
#: claim. Recorded as its own rule rather than folded into another, so the
#: count can be inspected.
ADJACENT_WINDOW = 60

#: Numbers the drafts' own notes say are in a committed artefact and carry no
#: resolver. This is a fifth state the brief's four categories do not cover:
#: not verified, but supported, and the cheapest of all to fix. The value names
#: the artefact the note points at.
UNRESOLVED = {
    "0.475": "albedo_confounder_2018.csv, zero-order correlation",
    "0.746": "albedo_confounder_2018.csv, zero-order correlation",
    "0.695": "albedo_confounder_2018.csv, solar-zenith correlation",
    "0.129": "baseline_results_2018.csv, a table cell left unmarked by design",
    "0.078": "baseline_results_2018.csv, a table cell left unmarked by design",
    "0.118": "albedo_confounder_2018.csv, partial correlation",
    "33.3462": "the Anhui raster bound, exempted in the methods note",
    "2,767": "the Hefei TCCON retrieval count",
    "44": "the Hefei TCCON day count",
}


#: Every resolver's current value, keyed by the string it would be written as
#: at each plausible precision. Built once.
#:
#: **This is what turns the audit's largest class into a fix list.** A number
#: that equals a committed resolver's value but carries no marker is not an
#: unsupported claim -- it is a verified quantity written without its marker,
#: and the remedy is one comment rather than a measurement or a citation. The
#: captions do this repeatedly, because they were written before the claim
#: checker covered them.
_RESOLVED: dict[str, str] | None = None


def resolver_values() -> dict[str, str]:
    global _RESOLVED
    if _RESOLVED is not None:
        return _RESOLVED
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "_vc", REPO / "scripts" / "verify_claims.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    table: dict[str, str] = {}
    for name, fn in module.QUANTITIES.items():
        # The `claims.*` resolvers read this artefact, so letting them into the
        # matching table would make the artefact depend on its own contents. It
        # converges today because no draft quotes a claim count, and that is
        # luck rather than design.
        if name.startswith("claims."):
            continue
        try:
            v = fn()
        except Exception:
            continue
        if not isinstance(v, (int, float)) or v != v:
            continue
        for places in range(0, 5):
            key = f"{v:.{places}f}"
            table.setdefault(key, name)
            table.setdefault(key.lstrip("+"), name)
            if abs(v) >= 1000:
                table.setdefault(f"{v:,.{places}f}", name)
    _RESOLVED = table
    return table


#: A value must be distinctive before a resolver match means anything. With
#: several hundred resolvers evaluated at five precisions, "2" and "0.5" match
#: something by coincidence; "14.86" does not. Three significant digits, or two
#: decimal places, is the bar.
DISTINCTIVE = re.compile(r"\.\d{2}|\d{3}")


def resolver_for(value: str) -> str:
    """The resolver whose value this number equals, if any.

    Returns "" for values too common to be evidence of anything.
    """
    if not DISTINCTIVE.search(value.replace(",", "")):
        return ""
    table = resolver_values()
    for candidate in (value, value.lstrip("-"), value.replace(",", "")):
        if candidate in table:
            return table[candidate]
    return ""


def body_of(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    cut = text.find(TAIL)
    return text[:cut] if cut > 0 else text


def classify(value: str, before: str, after: str,
             line: str, marked_at: list[int], pos: int) -> tuple[str, str, str]:
    """(category, rule, evidence) for one unmarked number. First match wins."""
    if value in STRUCTURAL_VALUES:
        return "self_evident", "grid resolution", ""
    bare = value.replace(",", "")
    if value in CONFIG_VALUES or bare in CONFIG_VALUES:
        return "self_evident", "study box or lattice shape", ""
    if CROSSREF_CONTEXT.search(before):
        return "self_evident", "cross-reference address", ""
    if CODE_SPAN.search(before):
        return "self_evident", "inside a code span", ""
    if TYPOGRAPHY.search(line):
        return "self_evident", "typography", ""
    if DRAWING_LINE.search(line) and (value in SWEPT_VALUES or "." in value
                                      or bare.isdigit()):
        return "self_evident", "describes the drawing", ""
    if value in SWEPT_VALUES and re.search(r"\bkm\b|radius|radii|buffer",
                                           line, re.I):
        return "self_evident", "swept buffer radius", ""
    for pattern in STRUCTURAL_LINE:
        if pattern.match(line):
            return "self_evident", "structural line", ""
    for pattern in STRUCTURAL_CONTEXT:
        if pattern.search(before):
            return "self_evident", "structural context", ""
    for pattern in TOKEN_CONTEXT:
        if pattern.search(before):
            return "self_evident", "part of a token", ""
    if YEAR.match(value.replace(",", "")):
        return "self_evident", "year as a date", ""
    if value in UNRESOLVED:
        return "unresolved", "in an artefact, no resolver", UNRESOLVED[value]
    # The drafts' own exemption lists outrank a coincidental resolver match. A
    # literature figure that happens to equal some artefact value is still a
    # literature figure, and checking the resolver table first stole 94 rows
    # from `cited` on the run that found this.
    if value in LITERATURE:
        return "cited", "in a draft's own exemption list", LITERATURE[value]
    hit = resolver_for(value)
    if hit:
        return "unresolved", "equals a resolver's value, written unmarked", hit
    if any(abs(pos - m) <= ADJACENT_WINDOW for m in marked_at):
        return "self_evident", "label or pair beside a marked number", ""
    return "neither", "no resolver and no exemption", ""


def rows_for() -> list[dict]:
    out: list[dict] = []
    for name in SOURCES:
        path = REPO / name
        body = body_of(path)
        section = "(none)"
        for lineno, line in enumerate(body.split("\n"), start=1):
            head = re.match(r"^#{2,4}\s+(.+)$", line)
            if head:
                section = head.group(1).strip()[:60]
            for m in MARK.finditer(line):
                out.append(dict(
                    source=name, line=lineno, section=section,
                    value=m.group(1), category="measured",
                    rule="inline resolver", evidence=m.group(2),
                    context=re.sub(r"\s+", " ", line)[:150]))
            stripped = MARK.sub(lambda mm: " " * len(mm.group(0)), line)
            marked_at = [mm.start() for mm in MARK.finditer(line)]
            for m in NUM.finditer(stripped):
                cat, rule, ev = classify(
                    m.group(1), stripped[:m.start()], stripped[m.end():],
                    line, marked_at, m.start())
                out.append(dict(
                    source=name, line=lineno, section=section,
                    value=m.group(1), category=cat, rule=rule, evidence=ev,
                    context=re.sub(r"\s+", " ", line)[:150]))
    return out


def report(rows: list[dict]) -> None:
    print(f"  {len(rows)} numeric claims across {len(SOURCES)} files\n")
    counts = Counter(r["category"] for r in rows)
    for cat in ("measured", "cited", "unresolved", "self_evident", "neither"):
        print(f"    {cat:<14}{counts[cat]:>6}  {100 * counts[cat] / len(rows):>5.1f} %")

    print("\n  by source, with the uncited share:")
    print(f"    {'source':<36}{'total':>7}{'meas':>6}{'cited':>7}{'unres':>7}"
          f"{'self-ev':>9}{'neither':>9}{'neither %':>11}")
    for name in SOURCES:
        sub = [r for r in rows if r["source"] == name]
        c = Counter(r["category"] for r in sub)
        share = 100 * c["neither"] / len(sub) if sub else 0
        print(f"    {name.split('/')[-1][:34]:<36}{len(sub):>7}{c['measured']:>6}"
              f"{c['cited']:>7}{c['unresolved']:>7}{c['self_evident']:>9}"
              f"{c['neither']:>9}{share:>10.1f} %")

    print("\n  the sections with the most unsupported numbers:")
    bare = Counter((r["source"].split("/")[-1], r["section"])
                   for r in rows if r["category"] == "neither")
    for (src, sec), n in bare.most_common(12):
        print(f"    {n:>4}  {src[:26]:<28}{sec[:46]}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    rows = rows_for()
    report(rows)
    if args.write:
        fields = ["source", "line", "section", "value", "category", "rule",
                  "evidence", "context"]
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(rows)
        try:
            shown = Path(args.out).resolve().relative_to(REPO)
        except ValueError:
            shown = Path(args.out)
        print(f"\n  wrote {shown}")
    else:
        print("\n  re-run with --write to write the artefact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
