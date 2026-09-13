#!/usr/bin/env python3
"""Count the CCD-Rice validation polygons that fall in this study area.

**Why this table exists.** The CCD-Rice validation polygons are the best
reference-data lead in this work: independent, published, CC-BY, in-domain, and
interpreted from imagery more accurate than any map here. What a Tier 2
accuracy assessment needs before it can be designed is not the polygons
themselves but their *shape* -- how many fall in each province, in which years,
under which class, and how many analysis cells they reach. That is a few
hundred bytes, and computing it costs a 1.9 MB download and a parquet read.

So the counts are committed and the polygons are not. A Tier 2 task reads this
file to decide whether the assessment is worth designing, and only then fetches
the deposit.

**What the counts establish, and it is not all encouraging.** All 777
four-province polygons fall inside the analysis lattice's bounding box, which
is the good news. They reach only 62 distinct cells of its 926, because visual
interpretation was done in clusters rather than spread over the domain, and 50
of the Jiangsu polygons sit north of 33.3462 N, where the committed NESDC rice
raster stops. So the usable count against the committed rice layer is 727
polygons in at most 62 cells, and any per-cell comparison rests on those.

The per-province ``cells_reached`` rows sum to 63 rather than 62, because one
cell is reached from two provinces. The distinct count is the one to quote and
the row-wise sum is not it.

**Two things a fetcher has to handle**, both found by reading the file rather
than its description. Every ``region`` value carries a trailing space, so a
match on ``"Anhui"`` silently returns nothing. And 296 of the 777 geometries
are MultiPolygon where the deposit's own description says the geometries are
polygons; 281 of those hold a single part and 15 hold up to 24.

Run with ``--download`` to fetch the deposit; the default reports what it would
do. The parquet is deleted after the counts are written unless ``--keep``.

    python scripts/summarise_ccdrice_polygons.py --download
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.fetch import figshare as fs  # noqa: E402

#: The deposit. Article 25515019 at version 3, a single GeoParquet file whose
#: MD5 the figshare record publishes and which this script checks.
ARTICLE_DOI = "10.6084/m9.figshare.25515019.v3"
EXPECTED_MD5 = "927e517583c1999650b90a087db19ffb"

OUT = REPO / "data" / "processed" / "ccdrice_polygons_yrd_2026.csv"

#: The four provinces, as this repository names them. The deposit's own
#: ``region`` field pads every value with a trailing space.
FOUR = ("Anhui", "Jiangsu", "Shanghai", "Zhejiang")

#: The deposit's class codes, from its description.
CLASSES = {
    0: "non-cropland",
    1: "single-season rice, certain",
    2: "double-season rice, certain",
    3: "rice, season uncertain",
    4: "other crops",
    5: "non-rice",
}

#: The analysis lattice, from data/processed/analysis_grid_2018.csv: 926 cells
#: of 0.25 degrees, centres on a quarter-degree grid offset by 0.075/0.025.
LAT_RANGE = (26.95, 35.20)
LON_RANGE = (114.80, 122.55)
CELL = 0.25
LAT0, LON0 = 27.075, 114.925

#: Where the committed NESDC rice raster stops, from data/processed/README.md.
#: Polygons north of this cannot validate the rice layer the grid carries.
NESDC_NORTH_LIMIT = 33.3462


def read_polygons(path: Path):
    """Yield ``(province, year, covertype, centroid_lat, centroid_lon)``.

    Geometry is read through shapely so that MultiPolygon records resolve to a
    single centroid rather than raising on ``.exterior``.
    """
    import pyarrow.parquet as pq
    import shapely.wkb as swkb

    table = pq.read_table(path).to_pydict()
    for region, year, covertype, blob in zip(
        table["region"], table["year"], table["covertype"], table["geometry"]
    ):
        centre = swkb.loads(blob).centroid
        yield str(region).strip(), int(year), int(covertype), centre.y, centre.x


def rows(path: Path) -> list[dict]:
    """The committed table: one row per province, year and class present."""
    counts: Counter = Counter()
    cells: dict[str, set] = {}
    every_cell: set = set()
    north: Counter = Counter()
    outside = 0

    for province, year, covertype, lat, lon in read_polygons(path):
        if province not in FOUR:
            continue
        counts[(province, year, covertype)] += 1
        if not (LAT_RANGE[0] <= lat <= LAT_RANGE[1]
                and LON_RANGE[0] <= lon <= LON_RANGE[1]):
            outside += 1
            continue
        cell = (round((lat - LAT0) / CELL), round((lon - LON0) / CELL))
        cells.setdefault(province, set()).add(cell)
        every_cell.add(cell)
        if lat > NESDC_NORTH_LIMIT:
            north[province] += 1

    if outside:
        raise SystemExit(f"{outside} polygons fell outside the lattice box; "
                         "the bounds in this script no longer match the grid")

    out = []
    for (province, year, covertype), n in sorted(counts.items()):
        out.append({
            "province": province,
            "year": year,
            "covertype": covertype,
            "covertype_label": CLASSES[covertype],
            "polygons": n,
        })
    # One summary row per province, so a reader does not have to add up.
    for province in FOUR:
        total = sum(n for (p, _, _), n in counts.items() if p == province)
        out.append({
            "province": province,
            "year": "all",
            "covertype": "all",
            "covertype_label": "all classes",
            "polygons": total,
        })
        out.append({
            "province": province,
            "year": "all",
            "covertype": "cells_reached",
            "covertype_label": "distinct 0.25-degree analysis cells reached",
            "polygons": len(cells.get(province, ())),
        })
        out.append({
            "province": province,
            "year": "all",
            "covertype": "north_of_nesdc_limit",
            "covertype_label":
                f"north of {NESDC_NORTH_LIMIT} N, unusable for the NESDC layer",
            "polygons": north.get(province, 0),
        })
    # The distinct cell count, which is not the sum of the per-province rows:
    # one cell is reached from two provinces.
    out.append({
        "province": "four provinces",
        "year": "all",
        "covertype": "cells_reached_distinct",
        "covertype_label":
            "distinct 0.25-degree analysis cells reached, counted once",
        "polygons": len(every_cell),
    })
    return out


def write(table: list[dict], path: Path) -> None:
    fields = ["province", "year", "covertype", "covertype_label", "polygons"]
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(table)


def shown(path: Path) -> str:
    """A path to print. Repo-relative where it can be, absolute otherwise.

    ``verify_recipes.py`` redirects output to a temp directory outside the
    repository, so ``relative_to(REPO)`` raises there and a recipe that prints
    its own output path would fail verification rather than the artefact.
    """
    try:
        return str(path.resolve().relative_to(REPO))
    except ValueError:
        return str(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--download", action="store_true",
                        help="fetch the deposit; otherwise report only")
    parser.add_argument("--keep", action="store_true",
                        help="keep the parquet instead of deleting it")
    parser.add_argument("--parquet", default=None,
                        help="use an already-downloaded parquet")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    if args.parquet:
        path = Path(args.parquet)
    elif args.download:
        article, version = fs.article_id_from_doi(ARTICLE_DOI)
        records = fs.parse_files(fs.fetch_article(article, version=version))
        if len(records) != 1:
            raise SystemExit(f"expected one file in {ARTICLE_DOI}, "
                             f"found {len(records)}")
        record = records[0]
        if record.digest and record.digest != EXPECTED_MD5:
            raise SystemExit(f"MD5 changed: {record.digest} is not "
                             f"{EXPECTED_MD5}; the deposit was revised")
        staging = REPO / "data" / "interim" / "ccdrice_polygons"
        staging.mkdir(parents=True, exist_ok=True)
        path = staging / record.name
        fs.download_record(record, path)
        print(f"  fetched {record.name}, {record.content_size:,} B, MD5 verified")
    else:
        print(f"  would fetch {ARTICLE_DOI} (one file, about 1.9 MB, "
              f"MD5 {EXPECTED_MD5})")
        print(f"  and write {shown(Path(args.out))}")
        print("  re-run with --download")
        return 0

    table = rows(path)
    write(table, Path(args.out))

    total = next(r["polygons"] for r in table
                 if r["province"] == "Shanghai" and r["covertype"] == "all")
    grand = sum(r["polygons"] for r in table if r["covertype"] == "all")
    cells = next(r["polygons"] for r in table
                 if r["covertype"] == "cells_reached_distinct")
    north = sum(r["polygons"] for r in table
                if r["covertype"] == "north_of_nesdc_limit")
    print(f"  {grand} polygons in the four provinces "
          f"({total} of them in Shanghai)")
    print(f"  reaching {cells} of the 926 analysis cells")
    print(f"  {north} north of {NESDC_NORTH_LIMIT} N, so {grand - north} "
          f"are usable against the committed NESDC layer")
    print(f"  wrote {shown(Path(args.out))}")

    if not args.keep and not args.parquet:
        path.unlink()
        print(f"  deleted {path.name}; the counts are the artefact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
