#!/usr/bin/env python3
"""Where each register entry is cited, as a paper's reference list rather than a log.

The register and a manuscript's reference list are different objects. The
register records what the project consulted; a reference list records what the
paper cites. This separates them, because the second is a subset of the first
and nothing had ever measured which subset.

**The detection is mechanical and its failure modes are named.** Each entry's
citation key encodes a first-author surname and a year, so a citation is sought
as that surname followed by that year within `WINDOW` characters of
whitespace-normalised text -- normalised because the drafts hard-wrap and a
citation's year routinely lands on the next line, which a line-based search
misses. Two failure modes survive that and are handled by hand:

* **Surname collisions.** Three `zhao2026*` entries and three `wang2026*`
  entries exist, so one prose "(Zhao et al., 2026)" matches three register
  entries. The mechanical pass cannot choose between them; `DRAFT_VERIFIED`
  below records which one each prose citation actually means, read from context.
* **Accents and acronyms.** `mila2022nndm` is Milà and `esa2019s5pch4` is ESA,
  and a capitalised-key search finds neither. Both are cited; a naive pass
  reports them as uncited.

So the artefact carries both: `candidate` from the mechanical pass and
`verified` for the draft column, and they disagree in exactly the ways above.
Treating the mechanical column as the answer would overstate the draft-cited
set by five.

Run with no arguments to report; ``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
sys.path.insert(0, str(REPO))

import build_references_bib as brb  # noqa: E402

OUT = REPO / "data" / "processed" / "reference_use_2026.csv"

#: Characters after a surname within which its year must appear.
WINDOW = 90

#: The drafts, in the order a manuscript would present them.
DRAFTS = [f"notes/draft-{n}.md"
          for n in ("introduction", "methods", "results", "discussion")]

#: Everything else that cites literature. `references.md` is excluded: it *is*
#: the register, so every entry trivially appears in it.
OTHER = ["ERRATA.md", "README.md", "notes/decisions.md", "notes/paper-target.md",
         "notes/dataset-leads.md", "notes/repository-architecture.md",
         "data/processed/README.md", "figures/README_fragments.md",
         "data/manifest.json", "config/sources.yml",
         # Code cites too. The colour-map paper is cited from `src/figures`
         # and nowhere in prose, so omitting these reports it as uncited.
         "src/figures/fields.py", "src/figures/style.py",
         "src/figures/diagram.py", "src/model/spatial_dof.py",
         "src/methane/apriori.py", "src/methane/seasonal.py"]

#: **Every formal citation the four drafts actually contain**, read from context
#: rather than matched, with the draft and line where it sits. This is the
#: authority for the draft column. It is short because the drafts are almost
#: entirely uncited: twelve works across four sections, against a register of
#: 194 entries and an ACP article's typical forty to eighty.
DRAFT_VERIFIED = {
    "zhao2026subnational": "methods:40",
    "balasus2023blended": "methods:99",
    "estrada2025imi2": "methods:230,497",
    "gong2020gaia": "methods:245",
    "huang2021gisa": "methods:247",
    "xie2025glorice": "methods:287",
    "clifford1989correlation": "methods:420",
    "dutilleul1993modifiedt": "methods:421",
    "wang2026usurban": "methods:554",
    "desjardins2018reconciling": "methods:568",
    "schutgens2017representativeness": "results:117",
    "zeng2021comment": "discussion:269",
}

#: Entries this audit found cited nowhere in the repository at all. Recorded
#: rather than only counted, because "uncited" is a claim a future pass should
#: be able to re-check against a named list. None is load-bearing: the register
#: keeps them because it records what was consulted, and the brief for this
#: audit was explicit that nothing is to be removed.
CITED_NOWHERE = {
    "correll2018vsup": "value-suppressing uncertainty palettes, from HCI; "
                       "considered for the figure set and not adopted",
    "dogniaux2025ghgsat": "the GHGSat global waste survey paper; its plume "
                          "deposit is in the lead register, but the paper is "
                          "cited by no record",
    "huang2019yrdtopdown": "an earlier top-down study of this region; "
                           "superseded in use by the 2021 tower inversion",
}

#: Named in a draft without a year, so not yet a citation but already an
#: attribution. A manuscript must turn each into one.
DRAFT_NAMED_NO_YEAR = {
    "moran1950": "methods:416, results:169",
    "pontius2011deathtokappa": "methods:632",
}

KEY = re.compile(r"^([a-z]+?)((?:19|20)\d{2})([a-z].*)?$")


def flat(path: Path) -> str:
    return re.sub(r"\s+", " ", path.read_text(encoding="utf-8", errors="replace"))


def entries() -> list[dict]:
    text = (REPO / "notes" / "references.md").read_text(encoding="utf-8")
    spaced = re.sub(r"[ \t]+", " ", text)
    heads = [(m.start(), m.group(1).strip())
             for m in re.finditer(r"^#{2,3} (.+)$", text, re.M)]

    def section(pos: int) -> str:
        cur = "(front matter)"
        for start, head in heads:
            if start < pos:
                cur = head
            else:
                break
        return cur

    out = []
    for doi, key in brb.KEYS.items():
        m = KEY.match(key)
        at = spaced.find("`" + doi + "`")
        if at < 0:
            at = spaced.find(doi)
        label = re.search(r"` — ([a-z][^;.]{3,70})[;.]", spaced[at:at + 300])
        out.append(dict(
            key=key, doi=doi,
            surname=(m.group(1) if m else key), year=(m.group(2) if m else ""),
            kind=(label.group(1).strip() if label else "(unlabelled)"),
            section=section(at)))
    return out


def cited_in(surname: str, year: str, files: list[str],
             doi: str = "") -> list[str]:
    """Files citing this entry, by surname-then-year or by bare DOI.

    The DOI arm is not redundant. Grounding records, `config/sources.yml` and
    `data/manifest.json` frequently cite by DOI alone, and an author-name search
    misses every one of them -- which is how a first pass reported 42 entries as
    cited nowhere when the true number is two. It also rescues the surnames a
    capitalised ASCII search cannot form: Mila for Mila and Esa for ESA.
    """
    found = []
    name = surname.capitalize()
    for name_path in files:
        path = REPO / name_path
        if not path.exists():
            continue
        text = flat(path)
        if doi and doi in text:
            found.append(name_path)
            continue
        for m in re.finditer(rf"\b{re.escape(name)}\b", text):
            if year and year in text[m.end():m.end() + WINDOW]:
                found.append(name_path)
                break
    return found


def rows_for() -> list[dict]:
    ground = sorted(str(p.relative_to(REPO))
                    for p in (REPO / "notes").glob("grounding-*.md"))
    out = []
    for e in entries():
        draft = cited_in(e["surname"], e["year"], DRAFTS, e["doi"])
        out.append(dict(
            key=e["key"], doi=e["doi"], kind=e["kind"], section=e["section"],
            draft_verified=DRAFT_VERIFIED.get(e["key"], ""),
            draft_named_no_year=DRAFT_NAMED_NO_YEAR.get(e["key"], ""),
            draft_candidate=";".join(p.split("draft-")[-1].replace(".md", "")
                                     for p in draft),
            grounding=";".join(p.replace("notes/grounding-", "").replace(".md", "")
                               for p in cited_in(e["surname"], e["year"], ground, e["doi"])),
            elsewhere=";".join(cited_in(e["surname"], e["year"], OTHER, e["doi"])),
        ))
    return out


def report(rows: list[dict]) -> None:
    verified = [r for r in rows if r["draft_verified"]]
    named = [r for r in rows if r["draft_named_no_year"]]
    candidate = [r for r in rows if r["draft_candidate"]]
    working = [r for r in rows if not r["draft_verified"]
               and (r["grounding"] or r["elsewhere"])]
    # CITED_NOWHERE is the authority, verified by hand. The mechanical pass is
    # reported beside it so a disagreement is visible rather than silent: it
    # over-reports, because a record citing a work by name without its year
    # nearby, or by a name the key cannot spell, looks like no citation at all.
    nowhere = [r for r in rows if r["key"] in CITED_NOWHERE]
    mech = [r for r in rows if not (r["draft_verified"] or r["grounding"]
                                    or r["elsewhere"] or r["draft_candidate"])]
    spurious = [r for r in mech if r["key"] not in CITED_NOWHERE]

    print(f"  register entries                              {len(rows):>4}")
    print(f"  cited in a draft, verified from context        {len(verified):>4}")
    print(f"  named in a draft without a year               {len(named):>4}")
    print(f"  mechanical candidates (overstates by collision){len(candidate):>4}")
    print(f"  working literature: cited only outside drafts  {len(working):>4}")
    print(f"  cited nowhere at all, hand-verified            {len(nowhere):>4}")
    for r in nowhere:
        print(f"      {r['key']:32}{r['doi']}")
        print(f"          {CITED_NOWHERE[r['key']]}")
    print(f"  mechanically undetected but in fact cited      {len(spurious):>4}")
    for r in spurious:
        print(f"      {r['key']:32}cited by name without a nearby year")

    print("\n  the verified draft-cited set, by kind:")
    for kind, count in Counter(r["kind"] for r in verified).most_common():
        print(f"    {count:>3}  {kind}")
    print("\n  the verified draft-cited set:")
    for r in sorted(verified, key=lambda r: r["draft_verified"]):
        print(f"    {r['draft_verified']:<22}{r['key']:<32}{r['section'][:40]}")

    data = {"dataset record", "dataset paper",
            "the deposit, fetched", "the deposit, not fetched"}
    deposits = [r for r in rows if r["kind"] in data]
    print(f"\n  datasets and deposits, for a data availability statement: "
          f"{len(deposits)}")
    print(f"  of which cited in a draft: "
          f"{sum(1 for r in deposits if r['draft_verified'])}")

    print("\n  register sections with entries and no draft citation, "
          "largest first:")
    tot = Counter(r["section"] for r in rows)
    cited = Counter(r["section"] for r in rows if r["draft_verified"])
    bare = [(s, c) for s, c in tot.most_common() if not cited.get(s)]
    for s, c in bare[:12]:
        print(f"    {c:>3}  {s[:64]}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    rows = rows_for()
    report(rows)
    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
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
