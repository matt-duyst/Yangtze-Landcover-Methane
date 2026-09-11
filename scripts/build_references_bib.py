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

#: DOIs the register **names in order to warn against them**. They resolve, or
#: fail to resolve, and in either case they are not citations: the register
#: records them so that a future reader who meets one in a search snippet knows
#: it was tested. They must not receive a citation key or a BibTeX entry, and
#: the check below excludes them rather than reporting them as gaps.
#:
#: This distinction was forced by the methods grounding, which met three of them
#: at once. A resolving DOI that points at the wrong paper is the failure mode
#: this register is least protected against, because resolution looks like
#: verification.
NOT_CITATIONS = {
    "10.1016/j.rse.2025.114953":
        "resolves to a paper on apple-tree disease spectral indices; the "
        "prediction-powered inference paper is 10.1016/j.rse.2025.114949",
    "10.1016/j.spasta.2025.100893":
        "resolves to 'A spatial autoregressive graphical model'; the "
        "spatially-lagged errors-in-variables paper is "
        "10.1016/j.spasta.2025.100909",
    "10.1016/j.rse.2019.111199":
        "does not resolve; 111199 is Stehman and Foody's article number and "
        "their DOI is 10.1016/j.rse.2019.05.018",
    "10.1016/j.jclepro.2023.137100":
        "resolves to 'Accuracy design optimization of a CNC grinding machine "
        "towards low-carbon manufacturing'; the rice emission-factor paper is "
        "10.1016/j.jclepro.2023.137245, same journal and year, 145 apart",
    "10.1038/s41599-026-07688-w":
        "does not resolve at all: the article number is right and the prefix is "
        "wrong, since Humanities and Social Sciences Communications registers "
        "under 10.1057. The correct DOI is 10.1057/s41599-026-07688-w. This is "
        "the register's first prefix error rather than a wrong-paper error",
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
    # the methods grounding, 11 September 2026
    "10.1016/j.rse.2010.05.010": "riemann2010continuous",
    "10.1080/15481603.2023.2181143": "wickham2023nlcd2019",
    "10.1126/science.adi6000": "angelopoulos2023ppi",
    "10.1016/j.rse.2025.114949": "lu2025ppiremote",
    "10.48550/arXiv.2501.18577": "kluger2025nonuniform",
    "10.48550/arXiv.2608.10356": "shirota2026designppi",
    "10.48550/arXiv.2106.04285": "nab2021sensitivity",
    "10.1080/20964471.2026.2660552": "xu2026simexwls",
    "10.1016/j.spasta.2025.100909": "masjkur2025laggedeiv",
    "10.1080/01431161.2011.552923": "pontius2011deathtokappa",
    "10.1016/j.rse.2019.05.018": "stehman2019keyissues",
    "10.1016/j.ecolmodel.2021.109692": "wadoux2021spatialcv",
    "10.1111/2041-210X.13851": "mila2022nndm",
    "10.5194/gmd-17-5897-2024": "linnenbrink2024knndm",
    "10.1038/s41467-020-18321-y": "ploton2020spatialvalidation",
    "10.3389/fpls.2022.858711": "hawinkel2022fieldtrials",
    "10.2307/2532039": "clifford1989correlation",
    "10.2307/2532625": "dutilleul1993modifiedt",
    "10.1016/j.neuroimage.2019.05.011": "afyouni2019edf",
    "10.5194/amt-16-3787-2023": "balasus2023blended",
    "10.5194/acp-17-9761-2017": "schutgens2017representativeness",
    "10.5194/gmd-18-483-2025": "rijsdijk2025superobservations",
    "10.5194/essd-17-4627-2025": "glissenaar2025no2l3",
    "10.5194/acp-23-9071-2023": "schuit2023superemitters",
    "10.5194/acp-24-5069-2024": "nesser2024usinversion",
    "10.5194/acp-26-10423-2026": "sicsikpare2026european",
    "10.1093/braincomms/fcae007": "bourached2023scaling",
    "10.1016/j.jocm.2018.07.002": "alwosheel2018samplesize",
    "10.1186/s12864-020-07181-x": "passafaro2020broilers",
    "10.48550/arXiv.2505.14312": "multitab2025",
    "10.5194/amt-11-6379-2018": "sheng2018osse",
    "10.5194/acp-21-14159-2021": "qu2021comparative",
    "10.1098/rsbl.2025.0506": "halsey2025sayingno",
    "10.5194/essd-18-4279-2026": "xco2transformerbilstm2026",
    "10.1016/j.atmosres.2024.107542": "xco2deepfusion2024",
    "10.1016/j.apr.2026.102918": "xch4gapfill2026",
    "10.1038/s41598-024-84593-9": "arabianpeninsula2025",
    # the inversion frame and the urban layer, 11 September 2026
    "10.5194/acp-22-10809-2022": "chen2022chinainversion",
    "10.5194/acp-25-15121-2025": "feng2025reggcas",
    "10.1016/j.jclepro.2026.148229": "xia2026chengdu",
    "10.5194/gmd-18-3311-2025": "estrada2025imi2",
    "10.1126/sciadv.adz9007": "he2026attribution",
    "10.1038/s41467-023-40671-6": "shen2023fuelexploitation",
    "10.5194/amt-19-4759-2026": "zhong2026groundvalue",
    "10.5194/acp-23-7503-2023": "varon2023permian",
    "10.1016/j.jclepro.2023.137245": "nikolaisen2023riceef",
    "10.1093/biostatistics/kxae038": "lee2024twostagebayes",
    "10.1093/aje/kwz133": "vanderweele2019differential",
    "10.1111/rssb.12348": "cinelli2020sensitivity",
    "10.1038/s41562-020-0912-z": "simonsohn2020speccurve",
    "10.1126/sciadv.adz9308": "wang2026usurban",
    "10.1038/s41893-024-01307-9": "wang2024landfills",
    "10.1038/s41467-025-58237-z": "luo2025oilgas",
    "10.1038/s41597-026-07320-1": "chen2026seasia",
    "10.1016/j.jenvman.2025.128450": "gao2026mswmitigation",
    "10.1021/acs.est.4c00408": "ma2024mswdecrease",
    "10.1016/j.jenvman.2026.128672": "zhang2026landfillsites",
    "10.1038/s41586-025-09683-8": "dogniaux2025ghgsat",
    "10.1038/s41598-022-19462-4": "wang2022nechina",
    "10.1038/s44284-024-00183-w": "lu2025canine",
    "10.1038/s41597-024-03815-x": "zhou2024wwtp",
    # the thesis's own rice method, added 12 September 2026
    "10.1080/15481603.2021.1943214": "zhu2021pppm",
    # coal, building form and the proxy comparison, 13 September 2026
    "10.1021/acs.estlett.9b00294": "sheng2019coalgrid",
    "10.1016/j.coal.2009.05.001": "liu2009huainancbm",
    "10.1038/s41598-024-79922-x": "wei2024qinan",
    "10.3390/ijerph19127408": "zhu2022coalch4",
    "10.1057/s41599-026-07688-w": "li2026popchange",
    "10.1038/s41467-025-56906-7": "langritter2025rural",
    "10.1080/01431161.2020.1841322": "wei2020imperviouspop",
    "10.5194/essd-18-5329-2026": "zhang2026buildingheight",
    "10.5194/essd-16-5357-2024": "che2024globfp",
    "10.1016/j.rse.2023.113578": "wu2023cnbh10m",
    "10.1038/s41597-025-04730-5": "zhang2025cmab",
    "10.1126/sciadv.abn9683": "maasakkers2022landfills",
    "10.1016/j.jes.2024.03.045": "pang2025shaoxing",
    "10.5194/acp-26-5477-2026": "fu2026shanghaicanopy",
    "10.5194/essd-13-5969-2021": "han2021nesearice10",
    "10.5281/zenodo.5555721": "han2021apra500data",
    "10.3390/rs14030759": "wei2022efsp",
    "10.1016/j.srs.2024.100172": "fang2024ricereview",
    "10.6084/m9.figshare.28407710": "hou2025nericedata",
    "10.5194/essd-18-5583-2026": "zhao2026searice30m",
    "10.1021/acs.est.8b05535": "runkle2019awd",
    "10.1038/srep28255": "sun2016warmdry",
    "10.1021/acs.est.2c00738": "qian2022parabolic",
    "10.1371/journal.pone.0191352": "wassmann2018nighttime",
    "10.1016/j.agrformet.2024.110238": "li2024nocturnal",
    "10.3390/rs11010035": "jiang2018cropintensity",
    "10.1021/acsestair.5c00446": "he2026gba",
    "10.1038/s43247-026-03902-4": "mehla2026ricereview",
    "10.1038/s43017-023-00482-1": "qian2023ricereview",
    "10.3390/rs17183152": "li2025cityreview",
    "10.1073/pnas.2504211123": "whiting2026urbantrend",
    "10.5194/egusphere-2026-2570": "long2026urbanpreprint",
    "10.17226/24987": "nasem2018methane",
    "10.1016/j.scib.2026.06.019": "zhao2026subnational",
    "10.1038/s41467-024-54038-y": "khanna2024mitigation",
    "10.1038/s41597-022-01522-z": "zhang2022irrigated",
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
% Five further DOIs appear in the register and are deliberately absent here:
% the register names them to warn against them, not to cite them. See
% NOT_CITATIONS in scripts/build_references_bib.py for each and why.
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
        doi = match.group(1).rstrip(".,;")
        if doi in NOT_CITATIONS or doi.lower() in {d.lower()
                                                   for d in NOT_CITATIONS}:
            continue
        seen.setdefault(doi, None)
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
