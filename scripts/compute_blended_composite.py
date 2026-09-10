#!/usr/bin/env python3
"""Grid the blended TROPOMI+GOSAT methane field onto the analysis lattice.

    python scripts/compute_blended_composite.py                 # report only
    python scripts/compute_blended_composite.py --write

Reads `methane_mixing_ratio_blended` for the orbits that carry an in-box
sounding and accumulates it onto the same 0.25 degree lattice the operational
composite uses. Two things make this cheap enough to run from a laptop.

**Only the productive orbits are read.** Which orbits those are is not a guess:
the committed composite's checkpoint records `soundings_in_box` for every one
of the 578 candidate granules, and 223 of them are non-zero. The other 355
contributed nothing to the operational composite and cannot contribute here
either, because the blended files hold a subset of the same soundings.

**Only the variables needed are read.** The AWS bucket answers range requests,
so `src.methane.blended.RangeFile` lets HDF5 fetch the chunks holding the
blended methane, latitude, longitude and qa_value and nothing else: about 2 MB
of a file that runs from 8 to 46 MB.

The result is written as its own file rather than as extra bands on
`methane_composite_2018.tif`. The blended field is a **third** field beside the
raw and bias-corrected ones, not a replacement for either, so the effect of the
correction stays visible instead of being chosen silently; and a reader who
found four bands in the methane file would reasonably divide any of them by the
count band, which is right here but is the mistake `export_covariates` exists
to prevent.

The product's terms, from the AWS Registry of Open Data entry: "There are no
restrictions on the use of this data, but please contact
nicholasbalasus@g.harvard.edu before its use in a publication." The product
user manual asks more broadly to be contacted before use in research. **The
author has not been contacted.** Cite Balasus et al. (2023),
doi:10.5194/amt-16-3787-2023.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.methane import blended as bl  # noqa: E402
from src.methane.grid import GridSpec, coverage_of  # noqa: E402

CHECKPOINT = REPO / "data" / "interim" / "extent_2018.npz"
PROCESSED = REPO / "data" / "processed"
OPERATIONAL = PROCESSED / "methane_composite_2018.tif"
STEM = PROCESSED / "methane_blended_2018"
COLUMN = "ch4_blended_ppb"
_ORBIT = re.compile(r"_(\d{5})_\d{2}_\d{6}_")


def study_spec() -> GridSpec:
    """The lattice, from the committed composite rather than from a constant."""
    import rasterio

    with rasterio.open(OPERATIONAL) as src:
        b = src.bounds
        return GridSpec(b.left, b.bottom, b.right, b.top, src.res[0])


def productive_orbits() -> dict:
    """Orbit to the operational contribution, for the orbits that carried one.

    From the checkpoint the committed composite was exported from, so the two
    composites are built over the same orbits by construction rather than by
    a filter applied twice.
    """
    contributions = json.loads(
        str(np.load(CHECKPOINT, allow_pickle=True)["contributions"]))
    return {int(_ORBIT.search(c["granule"]).group(1)): c
            for c in contributions if c["soundings_in_box"] > 0}


def blended_keys(months=range(4, 13)) -> dict:
    """Every 2018 blended key, by orbit, from the bucket listing."""
    out: dict[int, str] = {}
    for month in months:
        token = None
        while True:
            query = {"list-type": "2", "prefix": f"data/2018-{month:02d}/",
                     "max-keys": "1000"}
            if token:
                query["continuation-token"] = token
            url = f"{bl.BASE_URL}/?{urllib.parse.urlencode(query)}"
            with urllib.request.urlopen(url, timeout=90) as response:
                body = response.read().decode()
            for key in re.findall(r"<Key>([^<]+\.nc)</Key>", body):
                out[int(_ORBIT.search(key).group(1))] = key
            token = None
            match = re.search(r"<NextContinuationToken>([^<]+)<", body)
            if re.search(r"<IsTruncated>true", body) and match:
                token = match.group(1)
            else:
                break
    return out


def export(composite, stem: Path) -> tuple[Path, Path]:
    """Two bands, mean then its own count, and a complete per-cell CSV."""
    import rasterio
    from rasterio.transform import from_origin

    spec = composite.spec
    mean = composite.mean_of(bl.BLENDED)
    counts = composite.counts
    tif = stem.with_suffix(".tif")
    stem.parent.mkdir(parents=True, exist_ok=True)
    transform = from_origin(spec.west, spec.north, spec.resolution,
                            spec.resolution)
    with rasterio.open(
        tif, "w", driver="GTiff", height=spec.shape[0], width=spec.shape[1],
        count=2, dtype="float32", crs="EPSG:4326", transform=transform,
        nodata=float("nan"), compress="deflate",
    ) as dst:
        dst.write(mean.astype("float32"), 1)
        dst.write(counts.astype("float32"), 2)
        dst.set_band_description(1, "methane_mixing_ratio_blended mean, ppb")
        dst.set_band_description(2, "soundings in cell, count")
        dst.update_tags(
            qa_threshold=str(composite.qa_threshold),
            granules_gridded=str(len(composite.contributions)),
            granules_with_data=str(sum(
                1 for c in composite.contributions if c.soundings_in_box)),
            soundings=str(int(counts.sum())),
            product="Blended TROPOMI+GOSAT, Balasus et al. 2023, "
                    "doi:10.5194/amt-16-3787-2023",
            terms="No restrictions on use; the product user manual asks to be "
                  "contacted before research use. Author NOT yet contacted.",
            note="Band 1 is NaN and band 2 is 0 where nothing was observed.",
        )

    csv_path = stem.with_suffix(".csv")
    with open(csv_path, "w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["centre_lat", "centre_lon", "sounding_count", COLUMN])
        for row in range(spec.shape[0]):
            lat = spec.north - (row + 0.5) * spec.resolution
            for col in range(spec.shape[1]):
                lon = spec.west + (col + 0.5) * spec.resolution
                n = int(counts[row, col])
                writer.writerow([f"{lat:.4f}", f"{lon:.4f}", n,
                                 "" if n == 0 else f"{mean[row, col]:.2f}"])
    return tif, csv_path


def compare(composite) -> dict:
    """Assert the like-for-like property rather than assume it."""
    import rasterio

    with rasterio.open(OPERATIONAL) as src:
        op_counts = src.read(3)
        op_mean = src.read(1)
    counts = composite.counts.astype("float32")
    mean = composite.mean_of(bl.BLENDED)
    same = np.array_equal(counts, op_counts)
    covered = op_counts > 0
    difference = mean[covered] - op_mean[covered]
    return {
        "cells": int(counts.size),
        "covered": int((counts > 0).sum()),
        "operational_covered": int(covered.sum()),
        "soundings": int(counts.sum()),
        "operational_soundings": int(op_counts.sum()),
        "per_cell_counts_identical": bool(same),
        "cells_differing": int((counts != op_counts).sum()),
        "difference": difference,
        "operational_mean": op_mean[covered],
        "blended_mean": mean[covered],
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--limit", type=int, default=None,
                        help="read only the first N orbits, for a smoke test")
    args = parser.parse_args(argv)

    spec = study_spec()
    print(f"lattice {spec.west} to {spec.east} E, {spec.south} to "
          f"{spec.north} N at {spec.resolution} deg, {spec.shape} cells")
    wanted = productive_orbits()
    keys = blended_keys()
    print(f"{len(wanted)} productive orbits; {len(keys)} blended keys for 2018")
    missing = sorted(set(wanted) - set(keys))
    print(f"productive orbits with no blended counterpart: {len(missing)} "
          f"{missing}")
    if missing:
        raise SystemExit("the two composites would not be comparable")

    orbits = sorted(wanted)[:args.limit] if args.limit else sorted(wanted)
    import requests
    session = requests.Session()
    sources, names, read_bytes, read_requests = [], [], 0, 0
    start = time.time()

    counts = np.zeros(spec.shape, dtype="int64")
    total = np.zeros(spec.shape, dtype="float64")
    contributions, dropped = [], 0
    for index, orbit in enumerate(orbits, 1):
        url = f"{bl.BASE_URL}/{keys[orbit]}"
        handle = bl.RangeFile.open(url, session=session)
        soundings = bl.read_blended(handle, spec,
                                    name=keys[orbit].split("/")[-1])
        np.add.at(counts, (soundings.row, soundings.col), 1)
        np.add.at(total, (soundings.row, soundings.col), soundings.value)
        contributions.append(soundings.contribution)
        dropped += soundings.dropped_by_qa
        read_bytes += handle.bytes
        read_requests += handle.requests
        expected = wanted[orbit]["soundings_in_box"]
        got = soundings.contribution.soundings_in_box
        flag = "" if got == expected else f"   <-- operational had {expected}"
        if index % 40 == 0 or index == len(orbits) or flag:
            print(f"  {index:3d}/{len(orbits)}  orbit {orbit}  in box {got:5d}"
                  f"  {read_bytes/1e6:7.1f} MB  {read_requests:5d} req"
                  f"  {time.time()-start:6.0f}s{flag}")

    print(f"\nread {read_bytes/1e6:.1f} MB in {read_requests} range requests, "
          f"{time.time()-start:.0f}s; {read_bytes/1e6/len(orbits):.2f} MB and "
          f"{read_requests/len(orbits):.1f} requests per granule")
    print(f"soundings dropped by the qa threshold: {dropped}")
    if dropped:
        raise SystemExit("the blended sample is not the operational sample")

    from src.methane.grid import Composite
    composite = Composite(spec=spec, qa_threshold=0.75, counts=counts,
                          sums={bl.BLENDED: total},
                          contributions=tuple(contributions))
    coverage = coverage_of(composite)
    print(f"\ncoverage: {coverage.covered_cells} of {coverage.n_cells} cells "
          f"({coverage.fraction:.2%}), {composite.total_soundings:,} soundings")

    if not args.limit:
        result = compare(composite)
        print(f"\nlike-for-like against methane_composite_2018.tif")
        print(f"  covered cells   {result['covered']} against "
              f"{result['operational_covered']}")
        print(f"  soundings       {result['soundings']:,} against "
              f"{result['operational_soundings']:,}")
        print(f"  per-cell counts identical: "
              f"{result['per_cell_counts_identical']} "
              f"({result['cells_differing']} cells differ)")
        d = result["difference"]
        print(f"\nblended minus operational bias corrected, per cell "
              f"({d.size} cells)")
        print(f"  mean {d.mean():+.3f} ppb, sd {d.std(ddof=1):.3f}, "
              f"min {d.min():+.2f}, max {d.max():+.2f}")
        for q in (1, 5, 25, 50, 75, 95, 99):
            print(f"    p{q:<3d} {np.percentile(d, q):+8.3f}")
        for name, values in (("operational", result["operational_mean"]),
                             ("blended", result["blended_mean"])):
            print(f"  {name:12s} mean {values.mean():8.2f} ppb, sd "
                  f"{values.std(ddof=1):6.2f}, range "
                  f"{values.min():8.2f} to {values.max():8.2f} "
                  f"({values.max()-values.min():.2f} wide)")

    if args.write:
        tif, csv_path = export(composite, STEM)
        for path in (tif, csv_path):
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            print(f"\nwrote {path.relative_to(REPO)}  "
                  f"{path.stat().st_size:,} B\n  sha256 {digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
