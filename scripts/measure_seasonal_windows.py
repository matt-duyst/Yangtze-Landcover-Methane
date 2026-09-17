#!/usr/bin/env python3
"""The land-cover association measured on seasonal composites, not on the year.

The annual composite averages every sounding a cell received into one number.
That was the right object for a cross-sectional question and it destroys the
seasonal dimension, and paddy methane is seasonal: a flooded paddy emits and a
drained one does not. So an annual null is consistent with two seasonal signals
of opposite sign cancelling, and nothing in the annual field can tell the two
apart.

**This costs nothing to test, which is why it is here.** The checkpoint
``data/interim/extent_2018_extended.npz`` carries ``msum::`` -- monthly partial
sums for both methane fields at (12, 33, 31) -- beside the ``month_counts`` an
earlier pass used for the sounding distribution. Any composite over any set of
whole months is therefore a division, and the growing-season composite that
`notes/paper-target.md` priced as needing a 28.9 GB re-grid needs no granules at
all.

**What the sums do not carry is precision.** There is no ``msumsq::``: the sums
of squares exist annually and not monthly. So a seasonal composite has a mean
and **no per-cell standard error**, no within-cell variance and no per-cell
significance. Every correlation below is therefore a correlation whose target
carries no error bar, and that is a property of the checkpoint rather than a
choice made here. It is the reason this script reports correlations with
spatial-dependence corrections rather than held-out R squared against the
baseline suite: the suite's weighting needs per-cell precision.

**The comparison is made on a common cell set, because otherwise it is not a
comparison.** A cell observed in October and not in June contributes to one
window and not another, so a difference between windows computed on all
available cells is partly a difference between samples. The strict set requires
soundings in every window; the paired sets require them only in the two windows
a contrast actually uses, which is a weaker and larger definition, and both are
reported so that the result's dependence on the choice is visible.

**Significance is corrected throughout.** Nominal degrees of freedom treat
spatially dependent cells as independent and this project has already measured
what that costs -- a median effective sample size of 53.4 cells of 926. The
Dutilleul correction in ``src/model/spatial_dof.py`` is applied to every
correlation here, and the nominal value is reported beside it rather than
instead of it.

Run with no arguments to report; ``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model.spatial_dof import modified_t_test  # noqa: E402

OUT = REPO / "data" / "processed" / "seasonal_windows_2018.csv"
CHECKPOINT = REPO / "data" / "interim" / "extent_2018_extended.npz"
GRID = REPO / "data" / "processed" / "analysis_grid_2018.csv"

WEST, SOUTH, EAST, NORTH, RES = 114.8, 26.95, 122.55, 35.2, 0.25
N_ROWS, N_COLS = 33, 31

#: Whole-month windows. The sums are monthly, so nothing finer is available and
#: the rice calendar's day-resolved transplanting dates cannot be matched.
#: "flooded" is transplanting through mid-season, "growing" the fuller season,
#: "off" the two months after harvest, and October is singled out because it
#: alone holds 30.75 percent of the year's soundings.
WINDOWS = {"annual": tuple(range(1, 13)),
           "flooded": (5, 6, 7, 8),
           "growing": (6, 7, 8, 9),
           "october": (10,),
           "off": (11, 12)}

#: The two contrasts. Each is a within-cell difference, so every time-invariant
#: cell property -- position, elevation, mean albedo, province, and the
#: sampling composition insofar as it is fixed -- differences out.
CONTRASTS = {"flooded_minus_off": ("flooded", "off"),
             "growing_minus_off": ("growing", "off")}

FIELDS = {"bias_corrected": "methane_mixing_ratio_bias_corrected",
          "raw": "methane_mixing_ratio"}

#: Both rice definitions, because the committed correlation-DOF artefact reports
#: `rice_fraction_single` and an earlier measurement of this contrast used
#: `rice_fraction_combined`. Whether the seasonal result depends on the choice
#: is a question the artefact should answer rather than leave open.
PREDICTORS = ("impervious_fraction", "rice_fraction_single",
              "rice_fraction_combined")

#: Minimum soundings a cell needs in a window to enter a set.
STRICT_MIN = 15


def checkpoint():
    if not CHECKPOINT.exists():
        raise SystemExit(
            f"{CHECKPOINT.relative_to(REPO)} is not present. It is local data, "
            "gitignored, and this recipe is registered as local-input for that "
            "reason.")
    return np.load(CHECKPOINT, allow_pickle=True)


def grid_rows() -> list[dict]:
    with GRID.open(newline="") as handle:
        return list(csv.DictReader(handle))


def indices(rows: list[dict]) -> tuple[np.ndarray, np.ndarray]:
    """Lattice row and column for each analysis-grid row, from its centre."""
    lat = np.array([float(r["centre_lat"]) for r in rows])
    lon = np.array([float(r["centre_lon"]) for r in rows])
    return (np.round((NORTH - lat) / RES - 0.5).astype(int),
            np.round((lon - WEST) / RES - 0.5).astype(int))


def counts_and_fields(z, row, col) -> tuple[dict, dict]:
    """Per-window sounding counts, and per-window means for each field."""
    month_counts = z["month_counts"]
    counts, fields = {}, {}
    for name, months in WINDOWS.items():
        idx = [m - 1 for m in months]
        k = month_counts[idx].sum(axis=0)[row, col].astype("float64")
        counts[name] = k
        for short, variable in FIELDS.items():
            total = z[f"msum::{variable}"][idx].sum(axis=0)[row, col]
            value = np.full(len(k), np.nan)
            present = k > 0
            value[present] = total[present] / k[present]
            fields[(short, name)] = value
    return counts, fields


def cell_sets(counts: dict) -> dict[str, np.ndarray]:
    """The strict set and the weaker paired sets, as boolean masks."""
    sets = {}
    strict = np.ones(len(counts["annual"]), bool)
    for k in counts.values():
        strict &= k >= STRICT_MIN
    sets[f"every window >= {STRICT_MIN}"] = strict
    for contrast, (a, b) in CONTRASTS.items():
        for minimum in (STRICT_MIN, 10, 5, 1):
            mask = (counts[a] >= minimum) & (counts[b] >= minimum)
            sets[f"{contrast} pair >= {minimum}"] = mask
    return sets


def measure(x: np.ndarray, y: np.ndarray, lat: np.ndarray,
            lon: np.ndarray) -> dict:
    """One correlation, with the Dutilleul correction beside the nominal test."""
    test = modified_t_test(x, y, lat, lon)
    order = np.argsort(np.argsort(x)).astype("float64")
    order_y = np.argsort(np.argsort(y)).astype("float64")
    spearman = float(np.corrcoef(order, order_y)[0, 1])
    slope = float(np.polyfit(x, y, 1)[0])
    return dict(n_cells=int(len(x)), pearson=float(test.r), spearman=spearman,
                slope_ppb_per_unit=slope, effective_n=float(test.effective_n),
                p_nominal=float(test.p_nominal),
                p_corrected=float(test.p_corrected))


def rows_for() -> list[dict]:
    z = checkpoint()
    grid = grid_rows()
    row, col = indices(grid)
    counts, fields = counts_and_fields(z, row, col)
    sets = cell_sets(counts)
    lat = np.array([float(r["centre_lat"]) for r in grid])
    lon = np.array([float(r["centre_lon"]) for r in grid])
    predictors = {}
    for name in PREDICTORS:
        predictors[name] = np.array(
            [float(r[name]) if r[name].strip() else np.nan for r in grid])

    out: list[dict] = []

    def add(**kwargs):
        out.append(kwargs)

    # The composites themselves, so a reader can see the sample each rests on.
    strict_key = f"every window >= {STRICT_MIN}"
    for name in WINDOWS:
        present = np.isfinite(fields[("bias_corrected", name)])
        value = fields[("bias_corrected", name)][present]
        add(quantity=f"{name} composite cells", field="bias_corrected",
            window=name, predictor="", cell_set="any coverage",
            value=f"{int(present.sum())}", n_cells=int(present.sum()),
            pearson="", spearman="", slope_ppb_per_unit="", effective_n="",
            p_nominal="", p_corrected="",
            note="cells with at least one sounding in the window")
        add(quantity=f"{name} composite soundings", field="bias_corrected",
            window=name, predictor="", cell_set="any coverage",
            value=f"{int(counts[name].sum())}", n_cells=int(present.sum()),
            pearson="", spearman="", slope_ppb_per_unit="", effective_n="",
            p_nominal="", p_corrected="", note="soundings in the window")
        add(quantity=f"{name} composite between-cell sd", field="bias_corrected",
            window=name, predictor="", cell_set="any coverage",
            value=f"{value.std(ddof=1):.4f}", n_cells=int(present.sum()),
            pearson="", spearman="", slope_ppb_per_unit="", effective_n="",
            p_nominal="", p_corrected="", note="ppb, between covered cells")

    # Levels: each window against each predictor, on the strict set.
    for short in FIELDS:
        for name in WINDOWS:
            for pred in PREDICTORS:
                mask = sets[strict_key] & np.isfinite(predictors[pred]) \
                    & np.isfinite(fields[(short, name)])
                if mask.sum() < 30:
                    continue
                stats = measure(predictors[pred][mask],
                                fields[(short, name)][mask],
                                lat[mask], lon[mask])
                add(quantity=f"{short} {name} level vs {pred}", field=short,
                    window=name, predictor=pred, cell_set=strict_key,
                    value=f"{stats['pearson']:+.4f}",
                    note="Pearson on the strict common set", **stats)

    # Contrasts: the within-cell difference, on the strict set and on each
    # weaker paired set, which is what shows whether the result needs the
    # strict definition.
    for short in FIELDS:
        for contrast, (a, b) in CONTRASTS.items():
            keys = [strict_key] + [f"{contrast} pair >= {m}"
                                   for m in (STRICT_MIN, 10, 5, 1)]
            for key in keys:
                difference = fields[(short, a)] - fields[(short, b)]
                for pred in PREDICTORS:
                    mask = sets[key] & np.isfinite(predictors[pred]) \
                        & np.isfinite(difference)
                    if mask.sum() < 30:
                        continue
                    stats = measure(predictors[pred][mask], difference[mask],
                                    lat[mask], lon[mask])
                    add(quantity=f"{short} {contrast} vs {pred}", field=short,
                        window=contrast, predictor=pred, cell_set=key,
                        value=f"{stats['pearson']:+.4f}",
                        note="Pearson of the within-cell difference", **stats)
    return out


FIELDNAMES = ["quantity", "field", "window", "predictor", "cell_set", "value",
              "n_cells", "pearson", "spearman", "slope_ppb_per_unit",
              "effective_n", "p_nominal", "p_corrected", "note"]


def report(rows: list[dict]) -> None:
    if not rows:
        print("  nothing measured")
        return
    strict = f"every window >= {STRICT_MIN}"
    print(f"\n  the composites, from monthly partial sums and no re-grid\n")
    print(f"    {'window':10s} {'cells':>6s} {'soundings':>10s} {'sd ppb':>8s}")
    for name in WINDOWS:
        pick = {r["quantity"]: r for r in rows if r["window"] == name}
        print(f"    {name:10s} "
              f"{pick[f'{name} composite cells']['value']:>6s} "
              f"{pick[f'{name} composite soundings']['value']:>10s} "
              f"{float(pick[f'{name} composite between-cell sd']['value']):>8.2f}")
    for pred in PREDICTORS:
        shown = [r for r in rows if r["predictor"] == pred
                 and r["cell_set"] == strict and r["field"] == "bias_corrected"]
        if not shown:
            continue
        print(f"\n  {pred}, bias-corrected field, {strict}")
        print(f"    {'quantity':22s} {'n':>4s} {'r':>8s} {'eff n':>7s} "
              f"{'p nom':>9s} {'p corr':>8s}")
        for r in shown:
            label = r["window"]
            print(f"    {label:22s} {r['n_cells']:>4d} {r['pearson']:+8.4f} "
                  f"{r['effective_n']:7.1f} {r['p_nominal']:9.3g} "
                  f"{r['p_corrected']:8.3g}")
    print(f"\n  the contrast on weaker window definitions, bias-corrected")
    print(f"    {'cell set':34s} {'predictor':24s} {'n':>4s} {'r':>8s} "
          f"{'p corr':>8s}")
    for r in rows:
        if (r["window"] == "flooded_minus_off" and r["field"] == "bias_corrected"
                and r["predictor"] in ("impervious_fraction",
                                       "rice_fraction_combined")):
            print(f"    {r['cell_set']:34s} {r['predictor']:24s} "
                  f"{r['n_cells']:>4d} {r['pearson']:+8.4f} "
                  f"{r['p_corrected']:8.3g}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)
    rows = rows_for()
    report(rows)
    if not rows:
        return 1
    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
            writer.writeheader()
            for r in rows:
                writer.writerow({k: r.get(k, "") for k in FIELDNAMES})
        try:
            shown = Path(args.out).resolve().relative_to(REPO)
        except ValueError:
            # The recipe verifier redirects --out outside the repository.
            shown = Path(args.out)
        print(f"\n  wrote {shown}")
    else:
        print("\n  re-run with --write to write the artefact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
