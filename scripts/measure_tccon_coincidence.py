#!/usr/bin/env python3
"""The Hefei TCCON record for 2018, and its coincidence with this project's granules.

Three numbers reached four documents with no artefact behind them: the 2018
retrieval count, the number of days those retrievals fall on, and the number of
days carrying both a TCCON retrieval and a TROPOMI overpass of the station's
cell. They were computed once, recorded in prose, and the data was deleted. This
makes them reproducible.

**Why the data is fetched and not committed.** The TCCON Data License is not an
open licence. Clause 4 reads "All other rights, including redistribution,
display, and publishing adaptations are reserved", so committing the station
file to a public repository is not permitted whatever its size. The licence is
quoted in `data/manifest.json` and the deposit is registered there like any
other fetched source. What is committed is this script's output: counts derived
from the record, which are facts about the dataset rather than the dataset.

**Clause 5 is an obligation this script cannot discharge.** At a minimum of four
to six weeks before a manuscript is submitted, the individuals listed on the DOI
landing page must be contacted with a description of the intended publication.
That applies to any work including TCCON data; only the co-authorship
expectation is conditioned on the data being essential. See notes/decisions.md.

**Why no granules are downloaded.** The coincident-day count needs the days a
TROPOMI granule covered the station's cell, and the committed checkpoint already
holds that: one packed cell bitmap per granule in `granule_cells`, index-aligned
with a `contributions` array carrying each granule's filename and acquisition
time. An earlier record priced this recovery at roughly 480 MB of granules and
that figure was 2.47 times too low: the 21 granules on the nine coincident days
total 1,185,376,777 B, a mean of 56.4 MB each, measured from the mirror's own
bucket listings on 17 September 2026 rather than estimated. The checkpoint makes
all of it unnecessary and the only transfer is the station file.

**What this is not.** It is not the prior-profile alignment a TCCON-satellite
comparison needs, and it does not make the comparison valid. It makes the
feasibility numbers checkable. The drafts describe the comparison as unaligned
and that description is unchanged.

Run with no arguments to report; ``--download`` to fetch the deposit if absent;
``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import json
import urllib.request
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "processed" / "tccon_hefei_2018.csv"
RAW = REPO / "data" / "raw" / "tccon_hefei"
CHECKPOINT = REPO / "data" / "interim" / "extent_2018_extended.npz"

#: The deposit. CaltechDATA record `etz11-jpg19`, whose files are served from
#: the Open Storage Network bucket below rather than from data.caltech.edu.
DOI = "10.14291/tccon.ggg2020.hefei01.R1"
BASE = f"https://sdsc.osn.xsede.org/ini210004tommorrell/{DOI}"
STATION_FILE = "hf20151102_20251230.public.qc.nc"
FILES = (STATION_FILE, "README.txt", "LICENSE.txt")

YEAR = 2018


def fetch() -> None:
    """The deposit, if it is not already on disk.

    A plain urllib request with no signature games. Recorded because three
    other routes in this project answer differently to different user agents:
    this one does not, as of 14 September 2026, and a failure here is a route
    change rather than a broken pipeline.
    """
    RAW.mkdir(parents=True, exist_ok=True)
    for name in FILES:
        target = RAW / name
        if target.exists():
            print(f"  have {name}")
            continue
        print(f"  fetching {name}")
        with urllib.request.urlopen(f"{BASE}/{name}", timeout=300) as response:
            target.write_bytes(response.read())


def tccon_days() -> tuple[int, set[str], float, float]:
    """The 2018 retrievals, the days they fall on, and the station position.

    The position is the median of the per-retrieval `lat`/`long` rather than a
    hard-coded pair, so the cell the station falls in is derived from the file
    and a re-release that moved the reported position would move the cell.
    """
    import netCDF4

    with netCDF4.Dataset(RAW / STATION_FILE) as data:
        seconds = np.asarray(data.variables["time"][:], dtype="float64")
        xch4 = np.ma.filled(data.variables["xch4"][:], np.nan)
        lat = float(np.median(np.asarray(data.variables["lat"][:])))
        lon = float(np.median(np.asarray(data.variables["long"][:])))

    stamps = seconds.astype("datetime64[s]")
    years = stamps.astype("datetime64[Y]").astype(int) + 1970
    keep = (years == YEAR) & np.isfinite(xch4)
    days = {str(d) for d in stamps[keep].astype("datetime64[D]")}
    return int(keep.sum()), days, lat, lon


def granule_days(lat: float, lon: float) -> tuple[int, int, set[str], int, int, int]:
    """The days a granule covered the station's cell, from the checkpoint.

    `granule_cells` is one `np.packbits` bitmap per granule over the flat grid,
    so the station's cell is bit `row * n_cols + col`. Row 0 is the north edge,
    which is the exporter's own convention and the one mistake this lookup can
    make silently, the lattice being nearly square.
    """
    checkpoint = np.load(CHECKPOINT, allow_pickle=True)
    west, _south, _east, north, res = (float(v) for v in checkpoint["spec"])
    n_rows, n_cols = checkpoint["counts"].shape

    row = int(np.floor((north - lat) / res))
    col = int(np.floor((lon - west) / res))
    flat = row * n_cols + col

    bits = np.unpackbits(checkpoint["granule_cells"], axis=1)[:, :n_rows * n_cols]
    touched = bits[:, flat].astype(bool)
    contributions = json.loads(str(checkpoint["contributions"]))
    days = {contributions[i]["acquired"][:10] for i in np.nonzero(touched)[0]}
    soundings = int(checkpoint["counts"][row, col])
    return int(touched.sum()), len(days), days, soundings, row, col


def rows_for() -> list[dict]:
    if not (RAW / STATION_FILE).exists():
        return []
    retrievals, days, lat, lon = tccon_days()
    granules, granule_day_count, gdays, soundings, row, col = granule_days(lat, lon)
    coincident = sorted(days & gdays)

    out: list[dict] = []

    def add(quantity, value, unit, basis, note=""):
        out.append(dict(quantity=quantity, value=value, unit=unit,
                        basis=basis, note=note))

    add("station latitude", f"{lat:.4f}", "degrees north", "tccon",
        "median of the per-retrieval reported position")
    add("station longitude", f"{lon:.4f}", "degrees east", "tccon", "")
    add("station cell row", f"{row}", "index", "derived",
        "row 0 is the north edge")
    add("station cell column", f"{col}", "index", "derived", "")
    add(f"retrievals in {YEAR}", f"{retrievals}", "retrievals", "tccon",
        "rows with a finite xch4")
    add(f"days with a retrieval in {YEAR}", f"{len(days)}", "days", "tccon", "")
    add("granules covering the station cell", f"{granules}", "granules",
        "checkpoint", "from the packed per-granule cell sets")
    add("days a granule covered the station cell", f"{granule_day_count}",
        "days", "checkpoint", "")
    add("soundings in the station cell", f"{soundings}", "soundings",
        "checkpoint", "qa-passing, over the eight-month record")
    add("coincident days", f"{len(coincident)}", "days", "derived",
        "a TCCON retrieval and a granule covering the cell on the same day")
    add("coincident days, listed", " ".join(coincident), "dates", "derived",
        "UTC calendar days")
    return out


def report(rows: list[dict]) -> None:
    if not rows:
        print("  the Hefei deposit is not on disk; re-run with --download")
        return
    table = {r["quantity"]: r["value"] for r in rows}
    print(f"  Hefei TCCON, {table['station latitude']} N "
          f"{table['station longitude']} E, cell "
          f"({table['station cell row']}, {table['station cell column']})\n")
    for key in (f"retrievals in {YEAR}", f"days with a retrieval in {YEAR}",
                "granules covering the station cell",
                "days a granule covered the station cell",
                "soundings in the station cell", "coincident days"):
        print(f"    {key:<44}{table[key]:>8}")
    print(f"\n    {table['coincident days, listed']}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--download", action="store_true",
                        help="fetch the deposit if it is not on disk")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    if args.download:
        fetch()

    rows = rows_for()
    report(rows)
    if not rows:
        return 1
    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["quantity", "value", "unit", "basis", "note"])
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
