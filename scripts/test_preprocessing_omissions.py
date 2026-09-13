#!/usr/bin/env python3
"""Test the preprocessing steps this project does not apply.

`notes/draft-methods.md` §2.5 states four omissions: no destriping, no
retrieval-precision filter, no albedo floor, and no representativeness
weighting. **All four became testable** when the Tier 3 retention pass
retained the quantities they need.

Destriping was the one this repository had called unrecoverable, and the reason
was true as stated -- nothing retained the across-track detector column -- but
it was a statement about what had been kept, not about what could be. The
column is the flat index modulo the ground-pixel count, so retaining it cost no
extra variable read, and the per-cell per-column counts are enough to apply an
additive correction afterwards. It is tested here at first order only, and
`column_offsets` states that limit precisely.

**These are sensitivities, not replacements.** The committed composite stays
the primary field. Each variant here answers one question: if the omitted step
had been applied, would a reported conclusion move? A variant that changes a
number without changing a conclusion is the expected outcome and is reported as
such.

**Why a filter can be tested at all without another granule read.** A gridded
covariate cannot do it -- a cell's *mean* precision says nothing about what its
methane mean would become if the imprecise soundings were dropped. The pass
therefore accumulated methane **binned by** precision and by SWIR albedo, with
the published thresholds falling on bin edges, so the surviving subset's sum and
count are read straight off the histogram. The joint slot does the same for
both filters applied together, which the two marginal histograms cannot give.

**What is held fixed.** The covariates are the committed, unfiltered ones. A
filter would also shift each cell's mean albedo and wind, and letting both move
at once would confound the target's change with the predictors'. Holding the
predictors fixed isolates the question asked, which is what the filter does to
the association.

**The two weightings are nearly orthogonal, which is the point.** Sounding count
is the inverse-variance weight when the only error is uncorrelated and shrinks
as 1/n. The representativeness weight adds the spatial term the Level 3
literature specifies, which does not shrink with n at all; over this domain that
term dominates, so the second weighting is close to weighting by within-cell
homogeneity and is almost independent of the first.

Run with no arguments to report; ``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

CHECKPOINT = REPO / "data" / "interim" / "extent_2018_extended.npz"
GRID = REPO / "data" / "processed" / "analysis_grid_2018.csv"
COVARIATES = REPO / "data" / "processed" / "methane_covariates_2018.csv"
OUT = REPO / "data" / "processed" / "preprocessing_sensitivity_2018.csv"

PRIMARY = "methane_mixing_ratio_bias_corrected"
TARGET = "ch4_bias_corrected_ppb"
PER_SOUNDING_PPB = 29.0

#: The models whose movement carries the argument: the two land-cover
#: predictors and their combination, against the references the drafts report
#: them alongside. The full suite is 22 models; naming a subset keeps the
#: artefact readable and every model named here is quoted in a draft.
MODELS = (
    "OLS impervious_fraction",
    "OLS rice_fraction_single",
    "OLS impervious_fraction + rice_fraction_single",
    "constant (global mean)",
    "spatial null (queen neighbour mean)",
    "OLS wind (u, v, speed)",
    "OLS trend surface (lat, lon)",
)


def bin_subset(data, prefix: str, counts_key: str, keep) -> tuple:
    """Summed methane and count over a set of histogram slots."""
    sums = data[f"{prefix}::{PRIMARY}"]
    counts = data[counts_key].astype("int64")
    return sums[keep].sum(axis=0), counts[keep].sum(axis=0)


def variants(data) -> dict:
    """Each variant's per-cell (sum, count) for the primary field."""
    counts = data["counts"].astype("int64")
    total = data[f"sum::{PRIMARY}"]

    precision_edges = [float(x) for x in data["precision_edges"]]
    albedo_edges = [float(x) for x in data["albedo_edges"]]
    n_precision = len(precision_edges) + 2
    n_albedo = len(albedo_edges) + 2

    # Precision under 10 ppb: every slot at or below the 10.0 edge. The
    # trailing missing slot is excluded, so a sounding whose precision the
    # granule did not carry is treated as not passing a precision filter
    # rather than as passing one.
    p_keep = np.arange(n_precision) <= precision_edges.index(10.0)
    # SWIR albedo at least 0.05: every slot above the 0.05 edge, missing
    # slot excluded on the same grounds.
    a_keep = (np.arange(n_albedo) > albedo_edges.index(0.05)) & \
        (np.arange(n_albedo) < n_albedo - 1)

    out = {"committed (no filter)": (total, counts)}
    out["precision under 10 ppb"] = bin_subset(
        data, "psum", "precision_counts", p_keep)
    out["SWIR albedo at least 0.05"] = bin_subset(
        data, "asum", "albedo_counts", a_keep)
    joint = data[f"jsum::{PRIMARY}"]
    joint_counts = data["joint_counts"].astype("int64")
    out["both filters"] = (joint[3], joint_counts[3])
    if "across_track_counts" in data.files:
        out["first-order destriping"] = (destriped(data), counts)
    return out


def column_offsets(data):
    """Per-across-track-column offset from the domain mean, in ppb.

    **This is a first-order stripe estimate and the caveat is not incidental.**
    A published destriping estimates the stripe from the across-track structure
    of a field with its spatial signal already removed, per orbit. All this
    accumulator retains is each column's sum over the whole domain and year, so
    the offset here is measured against the domain mean and therefore absorbs
    any systematic relationship between detector column and geography -- the
    column is a viewing-geometry axis and a swath crosses the domain at an
    angle, so the two are not independent. The estimate is an upper bound on
    what destriping would remove, and a variant built on it says whether the
    omission could matter, not what the correction would be.
    """
    sums = data[f"atsum::{PRIMARY}"]
    counts = data["across_track_counts"].astype("int64")
    with np.errstate(invalid="ignore", divide="ignore"):
        means = np.where(counts > 0, sums / np.maximum(counts, 1), np.nan)
    overall = float(sums.sum() / counts.sum())
    return np.where(np.isfinite(means), means - overall, 0.0), overall


def destriped(data):
    """Cell sums with the per-column offset removed from each sounding.

    Exact for an additive per-column stripe, and needs only the per-cell
    per-column *counts*: subtracting a constant from every sounding in column
    j reduces a cell's sum by that constant times how many soundings the cell
    drew from j.
    """
    offsets, _ = column_offsets(data)
    cell_counts = data["across_track_cell_counts"].astype("float64")
    correction = np.tensordot(offsets, cell_counts, axes=(0, 0))
    return data[f"sum::{PRIMARY}"] - correction


def centres(data):
    west, _, _, north, res = [float(x) for x in data["spec"]]
    rows, cols = data["counts"].shape
    # Row 0 is the NORTH edge; see summarise_composite_quality for how a
    # mirrored latitude passes every join and fails silently.
    lat = north - (np.arange(rows) + 0.5) * res
    lon = west + (np.arange(cols) + 0.5) * res
    return lat, lon, rows, cols


def write_target(data, sums, counts, path: Path) -> None:
    lat, lon, rows, cols = centres(data)
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["centre_lat", "centre_lon", TARGET])
        for r in range(rows):
            for c in range(cols):
                n = int(counts[r, c])
                writer.writerow([f"{lat[r]:.4f}", f"{lon[c]:.4f}",
                                 "" if n == 0 else f"{sums[r, c] / n:.2f}"])


def write_grid_with_weight(data, weight, path: Path) -> None:
    """The committed grid with `sounding_count` replaced by another weight.

    `src.model.baselines` reads its weight from that column, so substituting it
    tests a different weighting through the same tested code path rather than
    through a second implementation of the metrics.
    """
    lat, lon, _, _ = centres(data)
    lookup = {}
    rows, cols = data["counts"].shape
    for r in range(rows):
        for c in range(cols):
            lookup[(f"{lat[r]:.4f}", f"{lon[c]:.4f}")] = weight[r, c]
    records = list(csv.DictReader(GRID.open(newline="")))
    fields = list(records[0])
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for record in records:
            # Re-format through float on both sides. The grid stores "35.075"
            # and the lattice key is "35.0750"; comparing the raw strings
            # silently matches nothing, leaves every weight at its committed
            # value, and reports a weighting variant that is really the
            # committed run under another name.
            key = (f"{float(record['centre_lat']):.4f}",
                   f"{float(record['centre_lon']):.4f}")
            value = lookup.get(key)
            if value is not None and np.isfinite(value) and value > 0:
                record["sounding_count"] = f"{value:.10f}"
            writer.writerow(record)


def write_grid_subset(data, counts, path: Path) -> int:
    """The committed grid, restricted to cells the variant still observes.

    Necessary because `Table.complete` checks the *predictor* columns only: a
    cell whose target became NaN is not dropped, it propagates NaN into every
    metric and the whole run reports `nan`. Restricting the grid removes the
    cell properly, so `n` reflects the surviving sample.
    """
    lat, lon, rows, cols = centres(data)
    alive = {(f"{lat[r]:.4f}", f"{lon[c]:.4f}")
             for r in range(rows) for c in range(cols) if counts[r, c] > 0}
    records = list(csv.DictReader(GRID.open(newline="")))
    kept = [r for r in records
            if (f"{float(r['centre_lat']):.4f}",
                f"{float(r['centre_lon']):.4f}") in alive]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(kept)
    return len(kept)


def run_baselines(grid: Path, target_from: Path | None, out: Path) -> list[dict]:
    command = [sys.executable, str(REPO / "scripts" / "run_baselines.py"),
               "--grid", str(grid), "--covariates", str(COVARIATES),
               "--out", str(out), "--write"]
    if target_from is not None:
        command += ["--target-from", str(target_from)]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        raise SystemExit(f"run_baselines failed for {out.name}:\n"
                         f"{result.stdout[-2000:]}\n{result.stderr[-2000:]}")
    return list(csv.DictReader(out.open(newline="")))


def representativeness_weight(data):
    counts = data["counts"].astype("int64")
    total = data[f"sum::{PRIMARY}"]
    total_sq = data[f"sumsq::{PRIMARY}"]
    with np.errstate(invalid="ignore", divide="ignore"):
        variance = np.where(
            counts > 1,
            (total_sq - total ** 2 / np.maximum(counts, 1))
            / np.maximum(counts - 1, 1), np.nan)
    spread = np.sqrt(np.maximum(variance, 0.0))
    with np.errstate(invalid="ignore", divide="ignore"):
        weight = 1.0 / (PER_SOUNDING_PPB ** 2 / np.maximum(counts, 1)
                        + spread ** 2)
    return np.where((counts > 1) & np.isfinite(spread), weight, np.nan), spread


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--checkpoint", default=str(CHECKPOINT))
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    path = Path(args.checkpoint)
    if not path.exists():
        print(f"  missing {path}; this needs the extended granule checkpoint")
        return 1
    data = np.load(path, allow_pickle=False)
    if "precision_counts" not in data.files:
        print(f"  {path.name} predates the binned accumulators")
        return 1

    table = variants(data)
    base_sums, base_counts = table["committed (no filter)"]
    base_total = int(base_counts.sum())
    weight, spread = representativeness_weight(data)

    print("  what each filter removes, before any model is fitted\n")
    header = (f"  {'variant':<28}{'soundings':>12}{'kept %':>9}"
              f"{'cells':>7}{'lost':>6}{'mean ppb':>10}{'shift':>8}")
    print(header)
    base_mean = float(base_sums.sum() / base_total)
    composite = {}
    for name, (sums, counts) in table.items():
        n = int(counts.sum())
        cells = int((counts > 0).sum())
        mean = float(sums.sum() / n) if n else float("nan")
        composite[name] = dict(soundings=n, cells=cells, mean=mean)
        print(f"  {name:<28}{n:>12,}{n / base_total * 100:>8.2f}%"
              f"{cells:>7}{int((base_counts > 0).sum()) - cells:>6}"
              f"{mean:>10.2f}{mean - base_mean:>+8.2f}")

    rows: list[dict] = []
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        reference = None
        for name, (sums, counts) in table.items():
            target = tmp / "target.csv"
            write_target(data, sums, counts, target)
            same_cells = np.array_equal(counts > 0, base_counts > 0)
            grid = GRID
            if not same_cells:
                grid = tmp / "grid_subset.csv"
                write_grid_subset(data, counts, grid)
            results = run_baselines(grid, target, tmp / "out.csv")
            if reference is None:
                reference = {(r["model"], r["scheme"], r["weighting"]):
                             float(r["held_out_r2"]) for r in results}

            # A filter that empties cells changes the sample as well as the
            # values, and an R squared on 752 cells is not comparable with one
            # on 926. Where the surviving set differs, the committed target is
            # re-run **restricted to exactly the same cells**, and the delta is
            # taken against that matched reference rather than against the
            # published one. Without this the albedo row compares two different
            # samples and reports the difference as an effect of the filter.
            matched, matched_note = reference, "same cells as committed"
            if not same_cells:
                matched_target = tmp / "matched.csv"
                write_target(data, np.where(counts > 0, base_sums, 0.0),
                             np.where(counts > 0, base_counts, 0), matched_target)
                matched = {(r["model"], r["scheme"], r["weighting"]):
                           float(r["held_out_r2"])
                           for r in run_baselines(grid, matched_target,
                                                  tmp / "out_m.csv")}
                matched_note = (f"matched reference on the "
                                f"{int((counts > 0).sum())} surviving cells")

            for r in results:
                if r["model"] not in MODELS:
                    continue
                key = (r["model"], r["scheme"], r["weighting"])
                value = float(r["held_out_r2"])
                rows.append(dict(
                    variant=name, model=r["model"], scheme=r["scheme"],
                    weighting=r["weighting"], n=r["n"],
                    held_out_r2=f"{value:.4f}",
                    delta_vs_committed=f"{value - reference[key]:+.4f}",
                    delta_vs_matched=f"{value - matched[key]:+.4f}",
                    comparison=matched_note,
                    soundings=composite[name]["soundings"],
                    basis="filter"))

        # The weighting variant: same target, a different weight column.
        grid = tmp / "grid.csv"
        write_grid_with_weight(data, weight, grid)
        results = run_baselines(grid, None, tmp / "out_w.csv")
        for r in results:
            if r["model"] not in MODELS:
                continue
            key = (r["model"], r["scheme"], r["weighting"])
            value = float(r["held_out_r2"])
            rows.append(dict(
                variant="representativeness weighting", model=r["model"],
                scheme=r["scheme"], weighting=r["weighting"], n=r["n"],
                held_out_r2=f"{value:.4f}",
                delta_vs_committed=f"{value - reference[key]:+.4f}",
                delta_vs_matched=f"{value - reference[key]:+.4f}",
                comparison="same cells as committed",
                soundings=base_total, basis="weighting"))

    print(f"\n  held-out R squared, {len(MODELS)} models x 4 scheme-weighting "
          f"combinations x {len(set(r['variant'] for r in rows))} variants")
    moved = [r for r in rows if abs(float(r["delta_vs_committed"])) >= 0.01]
    print(f"  rows moving by at least 0.01: {len(moved)} of {len(rows)}")
    for r in sorted(moved, key=lambda r: -abs(float(r["delta_vs_committed"])))[:12]:
        print(f"    {r['variant']:<30}{r['model']:<46}"
              f"{r['scheme'][:14]:<15}{r['weighting'][:11]:<12}"
              f"{r['held_out_r2']:>9}  {r['delta_vs_committed']:>8}")

    corr = np.corrcoef(
        base_counts[np.isfinite(weight) & (base_counts > 1)].astype(float),
        weight[np.isfinite(weight) & (base_counts > 1)])[0, 1]
    print(f"\n  correlation between the two weightings: {corr:+.4f}")
    finite = np.isfinite(spread) & (base_counts > 1)
    share = (spread[finite] ** 2
             / (PER_SOUNDING_PPB ** 2 / base_counts[finite] + spread[finite] ** 2))
    print(f"  share of the representativeness variance that is spatial: "
          f"median {np.median(share) * 100:.1f} %")

    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        try:
            shown = Path(args.out).resolve().relative_to(REPO)
        except ValueError:
            shown = Path(args.out)
        print(f"  wrote {shown}")
    else:
        print("\n  re-run with --write to write the artefact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
