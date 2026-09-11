#!/usr/bin/env python
"""Regenerate notes/references.bib from DOI content negotiation.

    python scripts/build_references_bib.py --write
    python scripts/build_references_bib.py --check   # no network, structural only

`notes/references.md` asserts that the BibTeX beside it is generated and not
typed, so that the two files cannot drift and no transcription step sits between
the registry and the repository. Until now that assertion rested on whoever last
ran the content negotiation by hand. This script is the assertion.

**What is typed here and what is not.** The DOI and the citation key are typed,
in `KEYS` below, because a key is a local naming choice that no registry knows.
Every field of every entry is what `https://doi.org` returned under
`Accept: application/x-bibtex`, reformatted only by having its key replaced and
its whitespace collapsed to one line. Nothing else is edited, including
oddities: Crossref stores the first author of the natural-gas-vehicle paper as
the literal string "Da Pan" with no given name, and returns no author list at
all for the AR6 chapter. Both come through as they are, which is the point.

**Two register entries have no DOI and cannot be here.** ISO 5807:1985 is a
standard and Chaudhuri (2020) is a textbook. They are in the register under the
diagram sources and `EXCLUDED` records why, so the count check below can tell a
deliberate absence from a forgotten one.

`tests/test_references.py` runs `--check`, which needs no network: it asserts
that the DOIs in the register and the DOIs in the BibTeX are the same set, which
is the drift this file exists to prevent.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
REGISTER = REPO / "notes" / "references.md"
BIBTEX = REPO / "notes" / "references.bib"

#: Any DOI in the register in backticks. The register is the source of truth for
#: *which* works belong; this file is the source of truth for what each looks
#: like as BibTeX.
DOI_IN_PROSE = re.compile(r"`(10\.\d{4,9}/[^`\s]+)`")

#: Works in the register that have no DOI, with the reason. A count that does
#: not reconcile is then a real problem rather than one of these two.
EXCLUDED = {
    "ISO 5807:1985": "a standard, not a paper; no DOI exists",
    "Chaudhuri (2020)": "a textbook; no DOI exists",
}

#: doi -> citation key. Keys are lowercase, first author plus year plus a short
#: subject slug, which is the convention the first forty followed.
KEYS = {
    "10.1038/s41597-025-04483-1": "xie2025glorice",
    "10.1016/j.rse.2019.111510": "gong2020gaia",
    "10.1007/s11430-020-9797-9": "huang2021gisa",
    "10.5194/essd-15-3203-2023": "shen2023rice",
    "10.5194/amt-14-665-2021": "lorente2021tropomi",
    "10.5194/amt-19-2407-2026": "schneising2026wfmd",
    "10.1109/CVPR52688.2022.01553": "he2022mae",
    "10.57760/sciencedb.06963": "shen2023ricedata",
    "10.6084/m9.figshare.27965832.v2": "xie2024gloricedata",
    "10.6084/m9.figshare.27245775.v1": "gong2024gaiadata",
    "10.7910/DVN/A50I2T": "ifpri2019spam2000",
    "10.7910/DVN/PRFF8V": "ifpri2019spam2010",
    "10.5270/S5P-3lcdqiv": "esa2021s5pch4",
    "10.5270/S5P-3p6lnwd": "esa2019s5pch4",
    "10.1111/ecog.02881": "roberts2017cv",
    "10.1111/2041-210X.13107": "valavi2019blockcv",
    "10.1038/s41467-020-19160-7": "crameri2020colour",
    "10.1145/3173574.3174216": "correll2018vsup",
    "10.1029/2021GL094151": "liu2021divergence",
    "10.1038/s41562-019-0629-z": "patil2019visual",
    "10.1002/aaai.70004": "desai2025reproducibility",
    "10.1097/SIH.0000000000000622": "lodemann2022process",
    "10.1038/s41467-019-14155-5": "zhang2020fingerprint",
    "10.1038/s41467-021-21434-7": "zeng2021comment",
    "10.1038/s41467-021-21437-4": "zhang2021reply",
    "10.1029/2018JG004850": "hu2019yrd",
    "10.1007/s00376-021-0383-9": "huang2021yrdinversion",
    "10.3390/atmos10040185": "huang2019yrdtopdown",
    "10.1021/acsestair.4c00068": "zhao2024hangzhou",
    "10.1038/s41467-020-18141-0": "dapan2020ngv",
    "10.1017/9781009157896.009": "forster2021ar6ch7",
    "10.1017/CBO9781107415324.018": "myhre2013ar5ch8",
    "10.1016/j.rse.2011.09.027": "veefkind2012tropomi",
    "10.48550/arXiv.1602.07576": "cohen2016equivariant",
    "10.48550/arXiv.1805.12177": "azulay2018invariance",
    "10.1093/biomet/37.1-2.17": "moran1950",
    "10.5194/essd-17-2193-2025": "shen2025ccdrice",
    "10.1016/j.agsy.2022.103437": "han2022apra",
    "10.1029/2024EF005479": "chen2025grpi",
    "10.1021/acs.est.4c09822": "liang2024ricehub",
    # the Yangtze River Delta grounding, 10 September 2026
    "10.1021/acs.est.3c04209": "duan2023agmethane",
    "10.1021/acs.est.5c18654": "zhang2026cityscale",
    "10.5194/essd-16-1689-2024": "li2024ricecalendar",
    "10.7910/DVN/EUP8EY": "liu2023ricecalendardata",
    "10.1038/s41598-017-19110-2": "wu2018watergwp",
    "10.1007/s10333-025-01045-4": "minamikawa2025metasynthesis",
    "10.1016/j.fcr.2019.02.010": "jiang2019watermeta",
    "10.1080/00380768.2017.1413926": "vo2018mekongef",
    "10.1016/j.agwat.2024.109083": "wang2024irrigation",
    "10.1046/j.1365-2486.1998.00129.x": "huang1998ch4mod",
    "10.3390/land12020270": "jiang2023cropping",
    "10.1371/journal.pone.0155926": "yuan2016vegetables",
    "10.3389/fmicb.2026.1750894": "li2026paddyvegetable",
    "10.1016/j.ecss.2021.107258": "yang2021spartina",
    "10.1038/s44284-026-00504-1": "zhao2026gasleakage",
    "10.3390/atmos13081206": "shan2022linan",
    "10.1016/j.apr.2023.101830": "guo2023suzhou",
    "10.1016/j.jes.2025.07.021": "wang2026lulcmeteorology",
    "10.1126/sciadv.aec0536": "sun2026wastewater",
    "10.1007/s13762-024-06050-4": "zhu2024yrdsynthesis",
    # accuracy assessment and the fractional-cover frame
    "10.1016/j.rse.2014.02.015": "olofsson2014goodpractice",
    "10.1016/j.jag.2019.101955": "wickham2020nlcdimpervious",
    "10.1016/j.jag.2022.102787": "huang2022gisa2",
}

HEADER = """% Verified reference register for Yangtze-Landcover-Methane.
% Generated from DOI content negotiation (https://doi.org, Accept:
% application/x-bibtex) by scripts/build_references_bib.py. Every field is what
% doi.org returned; only the citation key is set locally, to match the naming in
% notes/references.md.
% Companion to notes/references.md. Do not edit; regenerate.
%
% {n} entries against {mentions} DOI mentions in the register. The counts differ
% because a DOI may be named more than once there: the two Sentinel-5P
% registrations, the GISA 2021 paper and the city-scale inventory each are, and
% the register explains why in each case.
% TWO REGISTER ENTRIES ARE NOT HERE AND CANNOT BE. ISO 5807:1985 and
% Chaudhuri (2020) have no DOI -- a standard and a textbook -- so no content
% negotiation can produce them, and typing them would break the guarantee this
% header makes. They are in notes/references.md under the diagram sources.
"""


def register_dois() -> list[str]:
    """Every DOI the register names, in the order it names them, deduplicated."""
    text = REGISTER.read_text(encoding="utf-8")
    seen: dict[str, None] = {}
    for match in DOI_IN_PROSE.finditer(text):
        seen.setdefault(match.group(1).rstrip(".,;"), None)
    return list(seen)


def check() -> int:
    """Structural agreement between the two files. No network."""
    register = {d.lower() for d in register_dois()}
    raw = BIBTEX.read_text(encoding="utf-8") if BIBTEX.exists() else ""
    # DataCite's BibTeX writes `doi = {...}` in lower case where Crossref's
    # writes `DOI={...}`, so the field name is matched case-insensitively and
    # the values are compared in lower case throughout.
    inbib = {m.lower()
             for m in re.findall(r"doi\s*=\s*\{([^}]+)\}", raw, re.I)}
    keyed = {d.lower() for d in KEYS}

    problems = []
    for label, missing in (("in the register but not the BibTeX",
                            register - inbib),
                           ("in the BibTeX but not the register",
                            inbib - register),
                           ("in the register but has no citation key",
                            register - keyed),
                           ("has a citation key but is not in the register",
                            keyed - register)):
        for doi in sorted(missing):
            problems.append(f"{doi}: {label}")

    for problem in problems:
        print(problem)
    print(f"{len(register)} DOIs in the register, {len(inbib)} in the BibTeX, "
          f"{len(EXCLUDED)} register entries with no DOI")
    return 1 if problems else 0


def fetch(doi: str, session) -> str:
    response = session.get(f"https://doi.org/{doi}",
                           headers={"Accept": "application/x-bibtex"},
                           timeout=60, allow_redirects=True)
    response.raise_for_status()
    entry = " ".join(response.text.split())
    if not entry.startswith("@"):
        raise RuntimeError(f"{doi}: not BibTeX -- {entry[:80]!r}")
    # Replace whatever key the registry chose with ours, leaving every field.
    return re.sub(r"^@(\w+)\{[^,]*,", rf"@\1{{{KEYS[doi]},", entry, count=1)


def build() -> str:
    import requests

    dois = register_dois()
    unknown = [d for d in dois if d not in KEYS]
    if unknown:
        raise SystemExit("no citation key for: " + ", ".join(unknown))

    session = requests.Session()
    entries = []
    for doi in dois:
        entries.append(fetch(doi, session))
        print(f"  {KEYS[doi]:32s} {doi}", file=sys.stderr)

    mentions = len(DOI_IN_PROSE.findall(REGISTER.read_text(encoding="utf-8")))
    header = HEADER.format(n=len(entries), mentions=mentions)
    return header + "\n" + "\n\n".join(entries) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help="fetch every DOI and rewrite notes/references.bib")
    parser.add_argument("--check", action="store_true",
                        help="structural agreement only; no network")
    args = parser.parse_args()

    if args.check:
        return check()
    if args.write:
        BIBTEX.write_text(build(), encoding="utf-8")
        print(f"wrote {BIBTEX.relative_to(REPO)}")
        return check()
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
