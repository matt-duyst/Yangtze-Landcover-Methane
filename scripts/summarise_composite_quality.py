#!/usr/bin/env python3
"""Expose the quantities the extended granule pass retained.

Queue items 0g, 12, 13, 14 and 15 all needed a granule read, and the Tier 3
retention pass collected them together because that pass is transfer-bound:
120 of its 122.7 minutes are download, so a quantity computed during it costs
accumulator arithmetic and a quantity deferred costs another 28.9 GB.

Two artefacts, one command, because they are two views of one accumulator and a
reader who has one without the other can misread both.

**`granule_quality_2018.csv`**, one row per granule: what was read, what the
quality threshold removed, and the footprint the file declares.

**`cell_quality_2018.csv`**, one row per cell: the same accounting per cell,
the within-cell spread, and the two candidate weightings side by side.

**Why the rejection rate is two numbers and not one.** The obvious reading of
"what did the filter remove" is a single rate, and it would be wrong here. Most
in-box soundings carry **no retrieval at all** -- cloud, geometry -- so the
threshold does not reject them; there is nothing to reject. Of those that do
carry a retrieval, the threshold removes a further share. Collapsing the two
into one rate attributes cloud cover to the quality filter. Both are reported.

**The threshold removes whole bins rather than a tail.** The year's `qa_value`
takes four distinct values -- 0, 0.16, 0.4 and 1.0 -- so a cut at 0.75 keeps
exactly the 1.0 bin and discards the 0.4 bin entire. It is a bin selection
written as an inequality, which matters because moving the threshold anywhere
between 0.4 and 1.0 changes nothing at all.

Run with no arguments to report; ``--write`` to write both artefacts.
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

CHECKPOINT = REPO / "data" / "interim" / "extent_2018_extended.npz"
OUT_GRANULE = REPO / "data" / "processed" / "granule_quality_2018.csv"
OUT_CELL = REPO / "data" / "processed" / "cell_quality_2018.csv"

#: Effective per-sounding uncertainty: the TCCON single-retrieval precision for
#: the operational product times the mission's recommended error
#: multiplication factor of 2. Both from `notes/grounding-methods.md`.
PER_SOUNDING_PPB = 29.0

PRIMARY = "methane_mixing_ratio_bias_corrected"


def load(path: Path):
    data = np.load(path, allow_pickle=False)
    return data, json.loads(str(data["contributions"]))


def granule_rows(records) -> list[dict]:
    out = []
    for r in records:
        total = r.get("soundings_in_box_total", 0)
        retrieved = r.get("soundings_in_box_retrieved", 0)
        passed = r["soundings_in_box"]
        out.append(dict(
            granule=r["granule"],
            acquired=r["acquired"] or "",
            pixel_size=r.get("pixel_size") or "",
            soundings_read=r["soundings_read"],
            soundings_valid_global=r["soundings_valid"],
            in_box_total=total,
            in_box_retrieved=retrieved,
            in_box_passed=passed,
            no_retrieval_share=("" if not total
                                else f"{(total - retrieved) / total:.6f}"),
            threshold_rejected_share=("" if not retrieved
                                      else f"{(retrieved - passed) / retrieved:.6f}"),
        ))
    return out


def cell_rows(data) -> list[dict]:
    spec = [float(x) for x in data["spec"]]
    west, _, _, north, res = spec
    counts = data["counts"].astype("int64")
    pre = data["prefilter_counts"].astype("int64")
    ret = data["retrieved_counts"].astype("int64")
    total = data[f"sum::{PRIMARY}"]
    total_sq = data[f"sumsq::{PRIMARY}"]

    with np.errstate(invalid="ignore", divide="ignore"):
        mean = np.where(counts > 0, total / np.maximum(counts, 1), np.nan)
        variance = np.where(
            counts > 1,
            (total_sq - total ** 2 / np.maximum(counts, 1))
            / np.maximum(counts - 1, 1), np.nan)
    # Clamp at zero: a cell whose soundings are identical can give a tiny
    # negative variance from cancellation, and a negative variance must not
    # propagate into a square root.
    spread = np.sqrt(np.maximum(variance, 0.0))

    months = data["month_counts"].astype("int64")
    out = []
    rows, cols = counts.shape
    for row in range(rows):
        for col in range(cols):
            n = int(counts[row, col])
            sd = float(spread[row, col]) if n > 1 else float("nan")
            # The two weightings, side by side rather than one replacing the
            # other. Sounding count is the inverse-variance weight when the
            # only error is uncorrelated and shrinks as 1/n. The
            # representativeness weight adds the spatial term the Level 3
            # literature specifies, which does not shrink with n, and is taken
            # at its low-coverage limit -- equal to the within-cell standard
            # deviation -- because that is the value the source states for a
            # cell of which only a small fraction is observed, and no
            # within-cell spatial coverage is recoverable from this
            # accumulator.
            if n > 1 and np.isfinite(sd):
                variance_total = PER_SOUNDING_PPB ** 2 / n + sd ** 2
                w_rep = 1.0 / variance_total if variance_total > 0 else 0.0
            else:
                w_rep = float("nan")
            out.append(dict(
                # Row 0 is the NORTH edge, as `from_origin(west, north, ...)`
                # in the exporter fixes it. Getting this backwards mirrors the
                # grid in latitude and still joins, because the lattice is
                # symmetric in shape -- it was caught only by reproducing the
                # committed baseline results.
                centre_lat=f"{north - (row + 0.5) * res:.4f}",
                centre_lon=f"{west + (col + 0.5) * res:.4f}",
                sounding_count=n,
                in_box_prefilter=int(pre[row, col]),
                in_box_retrieved=int(ret[row, col]),
                months_observed=int((months[:, row, col] > 0).sum()),
                ch4_bias_corrected_ppb=("" if n == 0
                                        else f"{float(mean[row, col]):.2f}"),
                within_cell_sd_ppb=("" if not np.isfinite(sd) else f"{sd:.3f}"),
                weight_by_count=n,
                weight_representativeness=("" if not np.isfinite(w_rep)
                                           else f"{w_rep:.8f}"),
            ))
    return out


def report(data, records) -> None:
    gr = granule_rows(records)
    read = sum(r["soundings_read"] for r in gr)
    total = sum(r["in_box_total"] for r in gr)
    retrieved = sum(r["in_box_retrieved"] for r in gr)
    passed = sum(r["in_box_passed"] for r in gr)
    sizes = sorted({r["pixel_size"] for r in gr if r["pixel_size"]})

    print(f"  granules                        {len(gr):>12,}")
    print(f"  soundings read (whole granules) {read:>12,}")
    print(f"  in box, before any filtering    {total:>12,}")
    print(f"  in box, carrying a retrieval    {retrieved:>12,}"
          f"   ({(total - retrieved) / total * 100:.2f} % of in-box lost to "
          f"no retrieval)")
    print(f"  in box, passing qa              {passed:>12,}"
          f"   ({(retrieved - passed) / retrieved * 100:.2f} % of retrieved "
          f"removed by the threshold)")
    print(f"  declared ground pixel size(s)   {', '.join(sizes) or 'none'}")

    cells = cell_rows(data)
    sd = np.array([float(r["within_cell_sd_ppb"]) for r in cells
                   if r["within_cell_sd_ppb"]])
    q = np.percentile(sd, [0, 25, 50, 75, 100])
    print(f"\n  within-cell sd, ppb, over {sd.size} cells with n>1:")
    print(f"    min {q[0]:.2f}  q1 {q[1]:.2f}  median {q[2]:.2f}  "
          f"q3 {q[3]:.2f}  max {q[4]:.2f}")
    months = np.array([r["months_observed"] for r in cells
                       if r["sounding_count"]])
    print(f"  months observed per covered cell: median {np.median(months):.0f}, "
          f"min {months.min()}, max {months.max()}")


def write(rows: list[dict], path: Path) -> None:
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    try:
        shown = path.resolve().relative_to(REPO)
    except ValueError:
        shown = path
    print(f"  wrote {shown}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--checkpoint", default=str(CHECKPOINT))
    # Defaulting to None rather than to the committed path matters: the recipe
    # runner redirects one artefact at a time via `out_flag`, and a script that
    # wrote its *other* artefact to the default would write into the working
    # tree during a verification run, which the runner forbids. So naming
    # either output restricts the write to the outputs named.
    parser.add_argument("--out-granule", default=None)
    parser.add_argument("--out-cell", default=None)
    args = parser.parse_args(argv)

    path = Path(args.checkpoint)
    if not path.exists():
        print(f"  missing {path}; this needs the extended granule checkpoint, "
              f"which is gitignored. Build it with "
              f"compute_methane_composite.py --run")
        return 1
    data, records = load(path)
    if "prefilter_counts" not in data.files:
        print(f"  {path.name} predates the extended accumulator; it holds no "
              f"pre-filter counts and they cannot be reconstructed from it")
        return 1

    report(data, records)
    if args.write:
        named = args.out_granule is not None or args.out_cell is not None
        if args.out_granule is not None or not named:
            write(granule_rows(records),
                  Path(args.out_granule or OUT_GRANULE))
        if args.out_cell is not None or not named:
            write(cell_rows(data), Path(args.out_cell or OUT_CELL))
    else:
        print("\n  re-run with --write to write the artefacts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
