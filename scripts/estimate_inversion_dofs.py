#!/usr/bin/env python3
"""Evaluate the IMI preview's own DOFS formula over this study area.

    python scripts/estimate_inversion_dofs.py
    python scripts/estimate_inversion_dofs.py --write

**This is not an IMI preview run and must not be reported as one.** The
Integrated Methane Inversion runs on AWS or on a local cluster holding
GEOS-Chem input data, and neither route is available from this session: the
free AWS Marketplace product needs an AWS account, the source route needs the
input archive, and the Integral Earth interface needs a registration. What is
available is the preview's *formula*, which is published in the IMI source and
closed-form in quantities this repository already has.

So this script answers the question the preview would answer, by the preview's
own arithmetic, using this composite's observation counts. It is labelled a
reimplementation everywhere it is reported.

**The formula.** From `src/inversion_scripts/imi_preview.py` in
`geoschem/integrated_methane_inversion` at `main`, with the observational error
from Chen et al. (2023) as that file cites it:

    k        = alpha * (M_air * L * g) / (M_CH4 * U * p)
    P        = num_obs / m_super              observations per superobservation
    s_superO = sqrt(sO^2 * ((1 - r) / P + r) + s_transport^2) / 1e9
    sA       = PriorError * E_cell / L^2      kg m-2 s-1
    a        = sA^2 / (sA^2 + (s_superO / k)^2 / m_super)
    DOFS     = sum(a)

with the IMI defaults `PriorError = 0.5`, `ObsError = 15` ppb,
`Res = "0.25x0.3125"` giving `L = 25 km`, `alpha = 0.4`, `U = 5 km/h`,
`r_retrieval = 0.55` and `s_transport = 4.5` ppb. `m_super` is the number of
days on which a cell carried at least one successful retrieval, and that is the
one input this repository has to derive rather than read: it comes from the
per-granule cell bitmaps in the composite checkpoint, which record which cells
each granule touched.

**What is exact here and what is assumed.** The observational side is exact for
this composite: sounding counts and observation days are measured, not modelled.
The prior side is not available — no gridded prior emission inventory is held
here — so the script does two things instead of one. It reports the **emission
rate a cell would need for `a = 0.5`**, which follows from the observations
alone and needs no prior at all, and it sweeps the domain prior total across a
range wide enough to bracket every value the literature supports, reporting
DOFS against it. The first is the prior-free result and is the one to quote.

**Reading the answer.** IMI's own documentation calls DOFS above 1 the minimum
for viability and below 2 marginal for most applications. The Permian weekly
work adopted DOFS above 0.5 per inversion as a practical minimum for a basin
total with 2-sigma error under 30 percent. A global TROPOMI inversion of all of
China constrained 113 independent pieces of information. A domain-total DOFS
for four provinces should be read against all three.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

CHECKPOINT = REPO / "data" / "interim" / "extent_2018.npz"
OUT = REPO / "data" / "processed" / "inversion_dofs_2018.csv"

#: IMI defaults, from `config.yml` at `main`. Quoted rather than chosen.
PRIOR_ERROR = 0.5          # relative fraction
OBS_ERROR = 15.0           # ppb
L = 25_000.0               # m, for Res "0.25x0.3125"
ALPHA = 0.4                # turbulence parameterisation
U = 5 * (1000 / 3600)      # 5 km/h in m/s
P_SURF = 101_325.0         # Pa
G = 9.8                    # m/s2
M_AIR = 0.029              # kg/mol
M_CH4 = 0.01604            # kg/mol
R_RETRIEVAL = 0.55         # Chen et al. (2023)
S_TRANSPORT = 4.5          # ppb, Chen et al. (2023)
CONV = 1e9                 # ppb per mole fraction

#: Domain prior totals to sweep, Tg/y over the four-province lattice. The range
#: is deliberately wide: 0.1 Tg is implausibly low and 30 Tg is about half
#: China's entire anthropogenic total, so the answer is bracketed rather than
#: assumed. Values near 1 to 3 Tg are where a regional share of China's 65.0
#: Tg a-1 would fall for four provinces.
SWEEP = (0.1, 0.3, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 12.0, 20.0, 30.0)

#: Where the literature already in `notes/references.md` puts this domain's
#: total, so the sweep can be read against something. Huang et al. (2021)
#: inverted the Yangtze River Delta for 2018 and put agricultural soils at 4.58
#: Tg a-1, which they report as 39 percent of the regional total, implying
#: about 11.7 Tg a-1 for their domain. Duan et al. (2023) put the seven-province
#: middle and lower Yangtze at 38.4 percent of national agricultural methane,
#: which against China's agricultural total of roughly 23 to 30 Tg a-1 is 9 to
#: 11 Tg for seven provinces and so less for these four. The two bracket 5 to 12
#: Tg a-1 and neither domain is exactly this lattice, which is why the sweep is
#: reported rather than a single number.
ANCHOR = (5.0, 12.0)

#: **The sweep spreads each total uniformly and that makes it a lower bound.**
#: At small sensitivity `a` is approximately proportional to the square of a
#: cell's emission, so concentrating the same domain total into fewer cells
#: raises the sum. Real emissions are concentrated. A uniform prior is therefore
#: the least favourable arrangement of any given total, and the DOFS reported
#: against it is the floor rather than the estimate.

#: Thresholds this is read against, with their sources.
THRESHOLDS = {
    "IMI minimum viability (DOFS > 1)": 1.0,
    "IMI marginal ceiling (DOFS < 2)": 2.0,
    "Permian per-inversion practical minimum (DOFS > 0.5)": 0.5,
}


def k_factor() -> float:
    """The IMI preview's concentration-to-flux scale factor, kg-1 m2 s."""
    return ALPHA * (M_AIR * L * G) / (M_CH4 * U * P_SURF)


def superobservation_error(p: np.ndarray) -> np.ndarray:
    """Observational error for a superobservation of `p` retrievals, in ppb.

    Equation 5 of Chen et al. (2023) as the IMI source cites it. The retrieval
    error correlation of 0.55 is the part that does not average away, which is
    the same correlated-error structure `notes/grounding-methods.md` records for
    superobservations generally.
    """
    p = np.where(p >= 1.0, p, 1.0)
    return np.sqrt(OBS_ERROR ** 2 * ((1 - R_RETRIEVAL) / p + R_RETRIEVAL)
                   + S_TRANSPORT ** 2)


def observation_days(path: Path = CHECKPOINT) -> tuple[np.ndarray, np.ndarray]:
    """Sounding counts and distinct observation days per cell.

    The checkpoint stores, per granule, a packed bitmap over the flat grid of
    which cells that granule touched, and the granule's acquisition time. The
    number of distinct dates on which a cell was touched is IMI's `m_super`:
    the count of superobservations, one per cell per day with any successful
    retrieval.
    """
    data = np.load(path, allow_pickle=True)
    counts = data["counts"]
    n_cells = counts.size
    member = np.unpackbits(data["granule_cells"], axis=1)[:, :n_cells].astype(bool)
    dates = np.array([dt.datetime.fromisoformat(c["acquired"]).date().toordinal()
                      for c in json.loads(str(data["contributions"]))])

    days = np.zeros(n_cells, dtype="int64")
    for cell in range(n_cells):
        touched = member[:, cell]
        if touched.any():
            days[cell] = np.unique(dates[touched]).size
    return counts.ravel(), days


def sensitivity(emission_per_cell_kgs: np.ndarray, num_obs: np.ndarray,
                m_super: np.ndarray) -> np.ndarray:
    """Estimated averaging kernel sensitivity per cell, IMI's equation."""
    k = k_factor()
    with np.errstate(divide="ignore", invalid="ignore"):
        p = np.where(m_super > 0, num_obs / np.maximum(m_super, 1), 0.0)
        s_super = superobservation_error(p) / CONV
        sa = PRIOR_ERROR * emission_per_cell_kgs / L ** 2
        denom = sa ** 2 + (s_super / k) ** 2 / np.maximum(m_super, 1)
        a = np.where(denom > 0, sa ** 2 / denom, 0.0)
    return np.where(m_super > 0, a, 0.0)


def emission_for_half_sensitivity(num_obs: np.ndarray,
                                  m_super: np.ndarray) -> np.ndarray:
    """Per-cell emission giving a = 0.5, in Tg/y. Needs no prior.

    Setting `a = 0.5` in IMI's equation gives `sA = (s_superO / k) / sqrt(m)`,
    so the emission a cell would need for the inversion to constrain it half
    independently of the prior follows from the observation counts alone. This
    is the prior-free result, and the one worth quoting: it says what size of
    source this observing system could see over this domain.
    """
    k = k_factor()
    p = np.where(m_super > 0, num_obs / np.maximum(m_super, 1), 0.0)
    s_super = superobservation_error(p) / CONV
    sa_needed = (s_super / k) / np.sqrt(np.maximum(m_super, 1))
    kgs = sa_needed * L ** 2 / PRIOR_ERROR
    tgy = kgs * (3600 * 24 * 365) / 1e9
    return np.where(m_super > 0, tgy, np.nan)


def rows() -> list[dict]:
    num_obs, m_super = observation_days()
    covered = m_super > 0
    half = emission_for_half_sensitivity(num_obs, m_super)

    out: list[dict] = []
    out.append({"quantity": "cells with at least one observation day",
                "value": f"{int(covered.sum())}", "unit": "cells",
                "note": "the maximum DOFS attainable, since a tends to 1"})
    out.append({"quantity": "observation days per covered cell, median",
                "value": f"{np.median(m_super[covered]):.1f}", "unit": "days",
                "note": "IMI m_super: days with at least one retrieval"})
    out.append({"quantity": "observation days per covered cell, mean",
                "value": f"{m_super[covered].mean():.2f}", "unit": "days",
                "note": ""})
    out.append({"quantity": "observation days per covered cell, max",
                "value": f"{int(m_super[covered].max())}", "unit": "days",
                "note": ""})
    out.append({"quantity": "retrievals per superobservation, median",
                "value": f"{np.median(num_obs[covered] / m_super[covered]):.2f}",
                "unit": "retrievals", "note": "IMI P"})
    out.append({"quantity": "k", "value": f"{k_factor():.5f}",
                "unit": "kg-1 m2 s", "note": "IMI preview scale factor"})
    out.append({
        "quantity": "emission for a = 0.5, median cell",
        "value": f"{np.nanmedian(half):.4f}", "unit": "Tg/y per cell",
        "note": "prior-free: the source size this observing system could see"})
    out.append({
        "quantity": "emission for a = 0.5, best-observed cell",
        "value": f"{np.nanmin(half):.4f}", "unit": "Tg/y per cell",
        "note": f"the cell with {int(m_super[covered].max())} observation days"})
    out.append({
        "quantity": "emission for a = 0.5, summed over covered cells",
        "value": f"{np.nansum(half):.2f}", "unit": "Tg/y",
        "note": "domain total at which a typical cell reaches a = 0.5"})

    for total in SWEEP:
        per_cell_kgs = (total * 1e9 / (3600 * 24 * 365)) / max(int(covered.sum()), 1)
        a = sensitivity(np.where(covered, per_cell_kgs, 0.0), num_obs, m_super)
        out.append({
            "quantity": f"expected DOFS at {total:g} Tg/y domain prior",
            "value": f"{a.sum():.3f}", "unit": "DOFS",
            "note": f"mean a = {a[covered].mean():.5f}; "
                    f"cells with a > 0.5: {int((a > 0.5).sum())}"})
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true",
                        help=f"write {OUT.relative_to(REPO)}")
    parser.add_argument("--out", default=str(OUT),
                        help="where to write; the recipe runner redirects it")
    args = parser.parse_args()

    if not CHECKPOINT.exists():
        print(f"missing {CHECKPOINT.relative_to(REPO)}; this needs the "
              f"composite checkpoint, which is gitignored", file=sys.stderr)
        return 1

    table = rows()
    width = max(len(r["quantity"]) for r in table)
    for r in table:
        print(f"  {r['quantity']:<{width}}  {r['value']:>10}  "
              f"{r['unit']:<16} {r['note']}")

    print()
    swept = [(float(r["quantity"].split()[3]), float(r["value"])) for r in table
             if r["quantity"].startswith("expected DOFS")]
    for label, threshold in THRESHOLDS.items():
        above = [tg for tg, dofs in swept if dofs >= threshold]
        if above:
            print(f"  {label}: crossed at or below {min(above):g} Tg/y")
        else:
            print(f"  {label}: NOT reached in the swept range")
    lo, hi = ANCHOR
    band = [dofs for tg, dofs in swept if lo <= tg <= hi]
    print(f"\n  Over the literature-anchored band {lo:g} to {hi:g} Tg/y, "
          f"expected DOFS runs {min(band):.2f} to {max(band):.2f},")
    print("  and that is a lower bound because the sweep spreads emissions "
          "uniformly.")

    if args.write:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["quantity", "value", "unit", "note"])
            writer.writeheader()
            writer.writerows(table)
        print(f"\nwrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
