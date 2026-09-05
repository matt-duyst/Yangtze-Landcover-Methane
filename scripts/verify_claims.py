#!/usr/bin/env python
"""Check numeric claims in the prose against the artefacts they came from.

    python scripts/verify_claims.py            # report every marked claim
    python scripts/verify_claims.py --stale    # only the ones that disagree
    python scripts/verify_claims.py --coverage # how much prose is marked

A third drift class, after recipes drifting from artefacts and artefacts
drifting from each other. Every figure quoted in the prose was correct when it
was written. Regenerating a table moves the values, and the sentences quoting
them go stale silently, because nothing connects a sentence to the table it
came from.

**How a claim is marked.** The number stays where it is, in the sentence, and
carries an HTML comment naming the quantity:

    There are 926<!--#grid.rows--> of them and fifteen columns.

The marker is invisible in rendered markdown and travels with the sentence it
belongs to, so it cannot drift from its claim the way a parallel table of
claims maintained beside the prose would. That parallel table is exactly the
failure this repository already had once, in the README regeneration table.

**Three classes of number, and only one is checked.** A claim derived from a
committed artefact is marked and checked. A property of external data -- a
DOI, a granule's byte count, an accuracy figure from a cited paper -- is stable
and needs no watching. A historical record of what was measured at some past
time must **not** be updated even when the current value differs, because
rewriting it destroys the record; `notes/decisions.md` is full of these by
design and is excluded from this mechanism entirely.

Marking is therefore a deliberate act at writing time, not something inferred.
An unmarked number is not checked, and `--coverage` reports how many there are
so the gap is visible rather than assumed away.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
PROCESSED = REPO / "data" / "processed"

#: Files scanned for markers. `notes/decisions.md` is deliberately absent: it
#: is a decision log, its figures are as-measured-at-the-time, and a mechanism
#: that corrected them would destroy what it records.
SCANNED = ("README.md", "ERRATA.md", "data/processed/README.md",
           "data/reference/README.md", "figures/README_fragments.md",
           "notes/repository-architecture.md")

#: number, then optional space, then the marker naming what it is
CLAIM = re.compile(r"(-?[\d][\d,]*(?:\.\d+)?)\s*<!--#([a-zA-Z0-9_.]+)-->")

#: Every marker in the prose must name one of these.
_cache: dict = {}


def _grid() -> list[dict]:
    if "grid" not in _cache:
        with (PROCESSED / "analysis_grid_2018.csv").open(newline="") as h:
            _cache["grid"] = list(csv.DictReader(h))
    return _cache["grid"]


def _covariates() -> list[dict]:
    if "cov" not in _cache:
        with (PROCESSED / "methane_covariates_2018.csv").open(newline="") as h:
            rows = list(csv.DictReader(h))
        _cache["cov"] = [r for r in rows
                         if r.get("sounding_count") not in ("", "0", None)]
    return _cache["cov"]


def _composite():
    if "comp" not in _cache:
        import rasterio
        with rasterio.open(PROCESSED / "methane_composite_2018.tif") as src:
            _cache["comp"] = (src.read(1), src.read(2), src.read(3), src.tags())
    return _cache["comp"]


def _column(name: str) -> np.ndarray:
    return np.array([float(r[name]) if r[name] not in ("", None) else np.nan
                     for r in _grid()])


def _cov_column(name: str) -> np.ndarray:
    return np.array([float(r[name]) for r in _covariates()
                     if r.get(name) not in ("", None)])


def _shares() -> np.ndarray:
    keys = [k for k in _grid()[0] if k.startswith("share_")]
    return np.array([[float(r[k]) if r[k] else 0.0 for k in keys]
                     for r in _grid()])


#: name -> a callable returning the current value. Adding a quantity here and a
#: marker in the prose is what brings a claim under the check.
QUANTITIES = {
    "composite.covered_cells": lambda: int((_composite()[2] > 0).sum()),
    "composite.uncovered_cells": lambda: int((_composite()[2] == 0).sum()),
    "composite.total_cells": lambda: int(_composite()[2].size),
    "composite.soundings": lambda: int(_composite()[2].sum()),
    "composite.coverage_percent":
        lambda: 100.0 * (_composite()[2] > 0).sum() / _composite()[2].size,
    "composite.median_soundings":
        lambda: float(np.median(_composite()[2][_composite()[2] > 0])),
    "composite.max_soundings": lambda: int(_composite()[2].max()),
    "composite.granules_gridded": lambda: int(_composite()[3]["granules_gridded"]),
    "composite.granules_with_data":
        lambda: int(_composite()[3]["granules_with_data"]),
    "composite.bias_mean": lambda: float(
        (_composite()[0] - _composite()[1])[_composite()[2] > 0].mean()),

    "grid.rows": lambda: len(_grid()),
    "grid.rice_rows": lambda: int(np.isfinite(_column("rice_fraction_single")).sum()),
    "grid.rows_without_rice":
        lambda: len(_grid()) - int(np.isfinite(_column("rice_fraction_single")).sum()),
    "grid.impervious_median": lambda: float(np.nanmedian(_column("impervious_fraction"))),
    "grid.impervious_zeros": lambda: int((_column("impervious_fraction") == 0).sum()),
    "grid.rice_single_median": lambda: float(np.nanmedian(_column("rice_fraction_single"))),
    "grid.rice_combined_median":
        lambda: float(np.nanmedian(_column("rice_fraction_combined"))),
    "grid.rice_coverage_median": lambda: float(np.nanmedian(_column("rice_coverage"))),
    "grid.rice_coverage_below_99":
        lambda: int((_column("rice_coverage") < 0.99).sum()),
    "grid.straddling_cells":
        lambda: int(((_shares() > 1e-9).sum(axis=1) > 1).sum()),
    "grid.cells_outside_in_file":
        lambda: int((_shares().sum(axis=1) <= 1e-9).sum()),

    "cov.rows": lambda: len(_covariates()),
    "cov.albedo_negative":
        lambda: int((_cov_column("surface_albedo_SWIR_mean") < 0).sum()),
    "cov.eastward_wind_median": lambda: float(np.median(_cov_column("eastward_wind_mean"))),
    "cov.northward_wind_median": lambda: float(np.median(_cov_column("northward_wind_mean"))),
    "cov.northward_wind_max": lambda: float(_cov_column("northward_wind_mean").max()),
    "cov.albedo_swir_median": lambda: float(np.median(_cov_column("surface_albedo_SWIR_mean"))),
    "cov.albedo_nir_median": lambda: float(np.median(_cov_column("surface_albedo_NIR_mean"))),
    "cov.solar_zenith_median": lambda: float(np.median(_cov_column("solar_zenith_angle_mean"))),
    "cov.altitude_median": lambda: float(np.median(_cov_column("surface_altitude_mean"))),
    "cov.pressure_median": lambda: float(np.median(_cov_column("surface_pressure_mean"))),
}


def find_claims(text: str) -> list[tuple[str, str, int]]:
    """Every (quantity, literal, line number) marked in ``text``."""
    found = []
    for match in CLAIM.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        found.append((match.group(2), match.group(1), line))
    return found


def agrees(literal: str, value: float) -> bool:
    """Whether the written number matches the computed one at its own precision.

    The prose decides the precision. "90.52" is checked to two decimals and
    "926" to none, so rounding in the sentence is not treated as drift while a
    real change in the underlying value is.
    """
    plain = literal.replace(",", "")
    places = len(plain.split(".")[1]) if "." in plain else 0
    return round(float(plain), places) == round(float(value), places)


def check(paths=SCANNED) -> list[dict]:
    """Every marked claim, with what the prose says and what the data says."""
    results = []
    for name in paths:
        path = REPO / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for quantity, literal, line in find_claims(text):
            if quantity not in QUANTITIES:
                results.append(dict(file=name, line=line, quantity=quantity,
                                    written=literal, actual=None, ok=False,
                                    reason="unknown quantity"))
                continue
            value = QUANTITIES[quantity]()
            results.append(dict(file=name, line=line, quantity=quantity,
                                written=literal, actual=value,
                                ok=agrees(literal, value), reason=""))
    return results


def unmarked(paths=SCANNED) -> dict[str, int]:
    """Numbers with no marker, per file. The unchecked surface."""
    out = {}
    for name in paths:
        path = REPO / name
        if not path.exists():
            continue
        text = CLAIM.sub("", path.read_text(encoding="utf-8"))
        out[name] = len(re.findall(r"\d[\d,]*(?:\.\d+)?", text))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stale", action="store_true")
    parser.add_argument("--coverage", action="store_true")
    args = parser.parse_args(argv)

    results = check()
    if args.coverage:
        marked = len(results)
        print(f"  {marked} marked claims across {len(SCANNED)} files")
        print(f"  {'file':<40}{'marked':>8}{'unmarked numbers':>18}")
        counts = unmarked()
        for name in SCANNED:
            n = sum(1 for r in results if r["file"] == name)
            print(f"  {name:<40}{n:>8}{counts.get(name, 0):>18}")
        return 0

    shown = [r for r in results if not r["ok"]] if args.stale else results
    for r in shown:
        mark = "ok " if r["ok"] else "STALE"
        actual = "?" if r["actual"] is None else f"{r['actual']:g}"
        print(f"  {mark} {r['file']}:{r['line']:<5} {r['quantity']:<30} "
              f"prose {r['written']:>12}   data {actual:>12} {r['reason']}")
    bad = sum(1 for r in results if not r["ok"])
    print(f"\n  {len(results)} claims checked, {bad} stale")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
