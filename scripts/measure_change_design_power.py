#!/usr/bin/env python3
"""Expected effect and statistical power for a change-over-time design.

The design under consideration: per cell, the change in column methane between
two years against the change in impervious and rice fraction over the same
interval, so every static confound -- terrain, coastline, mean albedo, province,
distance to a city -- differences out. This asks whether the expected effect is
detectable before anything is built.

**The answer is no, by a factor of about 17 in effect size**, and the reason is
physical rather than statistical: a realistic urban expansion over a 0.25 degree
cell adds an emission whose column signature is hundredths of a part per
billion, against a field whose per-cell standard error is about two parts per
billion. No arrangement of the available cells recovers that.

**Three structural facts settle it before any power arithmetic.** The methane
record begins 30 April 2018, so there is no 2010 column field to difference
against a 2010 land-cover layer. GISA ends in 2019 and GAIA in 2021, so the only
interval both records cover is one to three years, over which impervious change
is a tenth of the eight-year change. And the two urban products disagree by a
factor of 2.2 about how much changed, while agreeing at r = 0.92 about where.

**The conversion is not a box model.** It is the closed-form averaging-kernel
relation the Integrated Methane Inversion's preview uses, whose constants were
checked line by line against that facility's source: k = alpha * M_air * L * g /
(M_CH4 * U * p), with a column enhancement k * flux. `notes/decisions.md`
records the verification. The wind is this domain's own, from the committed
covariates, which are annual means of the wind *components* -- vector averaging
cancels opposing directions, so the speed used is a lower bound on ventilation
and the enhancement it yields is an upper bound. Every assumption in this script
is chosen to favour the design, so that an underpowered verdict cannot be an
artefact of pessimism.

Run with no arguments to report; ``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import rasterio
from scipy import stats

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "scripts"))

OUT = REPO / "data" / "processed" / "change_design_power_2018.csv"
PROCESSED = REPO / "data" / "processed"

WEST, SOUTH, EAST, NORTH, RES = 114.8, 26.95, 122.55, 35.2, 0.25
N_ROWS, N_COLS = 33, 31

#: IMI preview constants, from `imi_preview.py` at `main`. Quoted, not chosen.
ALPHA, L, G, M_AIR, M_CH4, P_SURF = 0.4, 25_000.0, 9.8, 0.029, 0.01604, 101_325.0
SECONDS_PER_YEAR = 365.25 * 86400.0

#: 80 % power at a 5 % two-sided level.
T_CRIT = float(stats.norm.ppf(0.975) + stats.norm.ppf(0.80))


def cell_area_km2() -> np.ndarray:
    """Each cell's area, by latitude. A degree of longitude shortens northward."""
    lat = np.array([[NORTH - (r + 0.5) * RES] * N_COLS for r in range(N_ROWS)])
    km = RES * 111.32
    return km * km * np.cos(np.deg2rad(lat))


def impervious_bands(product: str) -> dict[int, np.ndarray]:
    """Impervious fraction per lattice cell for each year the raster carries.

    The committed 1/128 degree rasters hold four bands -- 2000, 2010, 2018 and
    2019 -- so a change over any pair of those years needs no raw data. Sub-cells
    are weighted by cos(latitude) rather than counted, because a fraction formed
    from a pixel count is not an area fraction.
    """
    path = PROCESSED / f"urban_extent_{product}.tif"
    with rasterio.open(path) as src:
        years = [int(d.split()[-1]) for d in src.descriptions]
        stack = {y: src.read(i + 1).astype("float64") / 100.0
                 for i, y in enumerate(years)}
        height, width = src.height, src.width

    factor = height // N_ROWS
    lat = NORTH - (np.arange(height) + 0.5) * (RES / factor)
    weight = np.cos(np.deg2rad(lat))[:, None] * np.ones((1, width))
    denominator = weight.reshape(N_ROWS, factor, N_COLS, factor).sum(axis=(1, 3))

    out = {}
    for year, band in stack.items():
        numerator = (band * weight).reshape(
            N_ROWS, factor, N_COLS, factor).sum(axis=(1, 3))
        out[year] = numerator / denominator
    return out


def covered_mask_and_field() -> tuple[np.ndarray, np.ndarray]:
    """The 926 cells carrying a composite value, and the field itself."""
    field = np.full(N_ROWS * N_COLS, np.nan)
    with (PROCESSED / "methane_coverage_2018.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["sounding_count"]) == 0:
                continue
            r = int(round((NORTH - float(row["centre_lat"])) / RES - 0.5))
            c = int(round((float(row["centre_lon"]) - WEST) / RES - 0.5))
            field[r * N_COLS + c] = float(row["ch4_bias_corrected_ppb"])
    return ~np.isnan(field), field


def per_cell_standard_error() -> np.ndarray:
    """Standard error of each cell's annual mean, where it is defined.

    Single-sounding cells have no within-cell standard deviation and are
    excluded rather than imputed: 21 of 926.
    """
    out = []
    with (PROCESSED / "cell_quality_2018.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["sounding_count"]) == 0 or not row["within_cell_sd_ppb"].strip():
                continue
            out.append(float(row["within_cell_sd_ppb"])
                       / np.sqrt(int(row["sounding_count"])))
    return np.asarray(out)


def wind_speed() -> np.ndarray:
    """|mean(u), mean(v)| per covered cell, in m/s.

    This is the magnitude of the mean vector and NOT the mean speed: a year of
    opposing winds cancels. It is therefore a lower bound on ventilation, and
    since the enhancement goes as 1/U it yields an upper bound on the signal.
    """
    out = []
    with (PROCESSED / "methane_covariates_2018.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["sounding_count"]) == 0:
                continue
            out.append(np.hypot(float(row["eastward_wind_mean"]),
                                float(row["northward_wind_mean"])))
    return np.asarray(out)


def sector_grids() -> dict[str, np.ndarray]:
    from measure_sector_composition import lattice_of, SECTORS, ROOT
    grids = {}
    for name, rel in SECTORS.items():
        path = ROOT / rel
        if path.exists():
            grids[name], _ = lattice_of(path)
    return grids


def morans_i(values: np.ndarray, valid: np.ndarray) -> float:
    """Queen-adjacency Moran's I over the valid cells."""
    grid = values.reshape(N_ROWS, N_COLS).astype("float64")
    mask = valid.reshape(N_ROWS, N_COLS)
    z = np.where(mask, grid - grid[mask].mean(), 0.0)
    num, w = 0.0, 0.0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            sl_a = (slice(max(0, dr), N_ROWS + min(0, dr)),
                    slice(max(0, dc), N_COLS + min(0, dc)))
            sl_b = (slice(max(0, -dr), N_ROWS + min(0, -dr)),
                    slice(max(0, -dc), N_COLS + min(0, -dc)))
            both = mask[sl_a] & mask[sl_b]
            num += (z[sl_a][both] * z[sl_b][both]).sum()
            w += both.sum()
    return float((mask.sum() / w) * (num / (z[mask] ** 2).sum()))


def rows_for() -> list[dict]:
    out: list[dict] = []

    def add(quantity, value, unit, basis, note=""):
        out.append(dict(quantity=quantity, value=value, unit=unit,
                        basis=basis, note=note))

    area = cell_area_km2().ravel()
    mask, field = covered_mask_and_field()
    se = per_cell_standard_error()
    speed = wind_speed()
    u_wind = float(np.median(speed))

    add("cell area, mean", f"{area.mean():.0f}", "km2", "lattice", "")
    add("wind speed used", f"{u_wind:.3f}", "m s-1", "covariates",
        "median of |mean(u), mean(v)|; a lower bound on ventilation, so the "
        "enhancement it gives is an upper bound")
    add("per-cell standard error, median", f"{np.median(se):.3f}", "ppb",
        "composite", "within-cell sd over sqrt(count), 905 cells")
    add("per-cell standard error, upper quartile", f"{np.percentile(se, 75):.3f}",
        "ppb", "composite", "")

    # --- Part 1: how much land cover changed
    fracs = {p: impervious_bands(p) for p in ("gaia", "gisa")}
    changes = {}
    for product, bands in fracs.items():
        d = (bands[2018] - bands[2010]).ravel()
        changes[product] = d
        q = np.percentile(d, [25, 50, 75])
        add(f"{product} impervious change 2010-2018, median", f"{q[1]:.4f}",
            "fraction", "urban layer", "")
        add(f"{product} impervious change 2010-2018, upper quartile",
            f"{q[2]:.4f}", "fraction", "urban layer", "")
        add(f"{product} impervious change 2010-2018, maximum", f"{d.max():.4f}",
            "fraction", "urban layer", "")
        add(f"{product} impervious change 2010-2018, sd", f"{d.std(ddof=1):.5f}",
            "fraction", "urban layer", "the regression's treatment spread")
        for t in (0.05, 0.10, 0.20):
            add(f"{product} cells with change above {t:g}", f"{int((d > t).sum())}",
                "cells", "urban layer", f"of {N_ROWS * N_COLS}")
        add(f"{product} impervious change, Moran I", f"{morans_i(d, mask):.4f}",
            "index", "derived", "queen adjacency over the covered cells")
    d1 = (fracs["gaia"][2019] - fracs["gaia"][2018]).ravel()
    changes["gaia_1yr"] = d1
    add("gaia impervious change 2018-2019, median", f"{np.median(d1):.5f}",
        "fraction", "urban layer", "the only interval the methane record shares")
    add("gaia impervious change 2018-2019, sd", f"{d1.std(ddof=1):.5f}",
        "fraction", "urban layer", "")
    add("product agreement on change, correlation",
        f"{np.corrcoef(changes['gaia'], changes['gisa'])[0, 1]:.4f}", "r",
        "derived", "they agree where and disagree how much")
    add("product disagreement on change, ratio of means",
        f"{changes['gaia'].mean() / changes['gisa'].mean():.2f}", "ratio",
        "derived", "against 1.15 for the 2018 extent itself")

    # --- effective sample size
    from src.model.spatial_dof import effective_sample_size
    lat = np.array([NORTH - (r + 0.5) * RES for r in range(N_ROWS)
                    for _ in range(N_COLS)])
    lon = np.array([WEST + (c + 0.5) * RES for _ in range(N_ROWS)
                    for c in range(N_COLS)])
    neff = {}
    for product in ("gaia", "gisa"):
        d = changes[product]
        m = effective_sample_size(d[mask], field[mask], lat[mask], lon[mask])
        neff[product] = m
        add(f"{product} effective sample size, change against methane",
            f"{m:.1f}", "cells", "derived", f"of {int(mask.sum())} nominal")
        for t in (0.05,):
            sub = mask & (d > t)
            if sub.sum() > 30:
                ms = effective_sample_size(d[sub], field[sub], lat[sub], lon[sub])
                add(f"{product} effective sample size, cells changing above {t:g}",
                    f"{ms:.1f}", "cells", "derived", f"of {int(sub.sum())} nominal")

    # --- Part 2: the inventory's rate
    grids = sector_grids()
    if not grids:
        add("inventory available", "0", "flag", "inventory",
            "the CHN-CH4 sector grids are not on disk")
        return out
    urban = (grids["landfills"] + grids["wastewater"] + grids["oil_and_gas"]).ravel()
    imp18 = fracs["gaia"][2018].ravel() * area
    ok = (urban > 0) & (imp18 > 0)
    slope0 = float((urban[ok] * imp18[ok]).sum() / (imp18[ok] ** 2).sum())
    design = np.vstack([imp18[ok], np.ones(int(ok.sum()))]).T
    fit, *_ = np.linalg.lstsq(design, urban[ok], rcond=None)
    ratio = urban[ok] / imp18[ok]
    add("urban-sector emission, domain total", f"{urban.sum() / 1000:.1f}", "Gg yr-1",
        "inventory", "landfill, wastewater, oil and gas")
    add("urban-sector rate, through-origin slope", f"{slope0:.2f}", "Mg km-2 yr-1",
        "inventory", "the rate the calculation uses")
    add("urban-sector rate, ordinary slope", f"{fit[0]:.2f}", "Mg km-2 yr-1",
        "inventory", f"intercept {fit[1]:.0f} Mg yr-1, small and negative")
    add("urban-sector rate, aggregate", f"{urban[ok].sum() / imp18[ok].sum():.2f}",
        "Mg km-2 yr-1", "inventory", "")
    add("urban-sector emission against impervious area, correlation",
        f"{np.corrcoef(urban[ok], imp18[ok])[0, 1]:.4f}", "r", "inventory",
        "proportional in aggregate, loose per cell")
    add("urban-sector rate, 5th to 95th percentile spread",
        f"{np.percentile(ratio, 95) / np.percentile(ratio, 5):.0f}", "ratio",
        "inventory", "per-cell rates span this factor")

    rice = grids["rice"].ravel()
    rice_frac = np.full(N_ROWS * N_COLS, np.nan)
    with (PROCESSED / "analysis_grid_2018.csv").open(newline="") as handle:
        for row in csv.DictReader(handle):
            if not row["rice_fraction_single"]:
                continue
            r = int(round((NORTH - float(row["centre_lat"])) / RES - 0.5))
            c = int(round((float(row["centre_lon"]) - WEST) / RES - 0.5))
            rice_frac[r * N_COLS + c] = float(row["rice_fraction_single"])
    rok = (~np.isnan(rice_frac)) & (rice > 0) & (rice_frac > 0)
    rice_area = rice_frac * area
    add("rice emission against rice area, correlation",
        f"{np.corrcoef(rice[rok], rice_area[rok])[0, 1]:.4f}", "r", "inventory",
        "PROPORTIONALITY FAILS FOR RICE; the inventory cannot supply a rice rate")
    add("rice rate, through-origin slope",
        f"{float((rice[rok] * rice_area[rok]).sum() / (rice_area[rok] ** 2).sum()):.2f}",
        "Mg km-2 yr-1", "inventory", "reported but not relied on, given the above")

    # --- Part 3: emission to column
    k = ALPHA * (M_AIR * L * G) / (M_CH4 * u_wind * P_SURF)
    add("k, emission to column factor", f"{k:.4f}", "kg-1 m2 s", "derived",
        "IMI preview closed form at this domain's wind")

    def enhancement(delta_emission_mg: np.ndarray | float):
        flux = np.asarray(delta_emission_mg) * 1000.0 / SECONDS_PER_YEAR / (L * L)
        return 1e9 * k * flux

    beta = float(enhancement(float(np.median(area)) * slope0))
    add("beta, expected slope", f"{beta:.4f}", "ppb per unit fraction", "derived",
        "the column enhancement a full-cell impervious change would make")
    for product in ("gaia", "gisa"):
        dX = enhancement(changes[product] * area * slope0)
        add(f"{product} implied enhancement, median", f"{np.median(dX):.4f}", "ppb",
            "derived", "")
        add(f"{product} implied enhancement, maximum", f"{dX.max():.4f}", "ppb",
            "derived", "the largest anywhere in the domain")

    # --- Part 4: power
    sigma = float(np.median(se)) * np.sqrt(2.0)
    add("noise on a two-year difference", f"{sigma:.3f}", "ppb", "derived",
        "per-cell standard error times root two, sampling error only")
    for product in ("gaia", "gisa", "gaia_1yr"):
        d = changes[product]
        m = neff.get(product, neff["gaia"])
        sdx = d.std(ddof=1)
        se_beta = sigma / (sdx * np.sqrt(m - 2))
        need = (T_CRIT * sigma / (beta * sdx)) ** 2 + 2
        add(f"{product} t statistic at effective n", f"{beta / se_beta:.4f}", "t",
            "derived", "against 1.96 for significance")
        add(f"{product} effective cells needed for 80 percent power",
            f"{need:.0f}", "cells", "derived", "")
        add(f"{product} shortfall factor", f"{need / m:.0f}", "ratio", "derived",
            f"against {m:.1f} effective cells available")
    se_beta_g = sigma / (changes["gaia"].std(ddof=1) * np.sqrt(neff["gaia"] - 2))
    add("minimum detectable slope", f"{T_CRIT * se_beta_g:.1f}",
        "ppb per unit fraction", "derived", "")
    add("effect-size shortfall", f"{T_CRIT * se_beta_g / beta:.0f}", "ratio",
        "derived", "how many times larger the true effect would have to be")
    add("emission change a detectable cell would need",
        f"{T_CRIT * se_beta_g / beta * float(np.median(area)) * slope0 / 1000:.0f}",
        "Gg yr-1", "derived",
        "in one cell, against a domain urban total of "
        f"{urban.sum() / 1000:.0f} Gg yr-1")

    # --- Part 5c: the same arithmetic on the cross-sectional design
    lo, hi = np.percentile(imp18 / area, [5, 95])
    contrast = float(enhancement((hi - lo) * float(np.median(area)) * slope0))
    add("cross-sectional implied contrast, p5 to p95", f"{contrast:.3f}", "ppb",
        "derived", "the whole impervious range's expected column signature")
    add("cross-sectional contrast as a share of the field sd",
        f"{100 * contrast / 14.86:.1f}", "percent", "derived",
        "against the observed between-cell sd of 14.86 ppb")
    add("cross-sectional implied R squared", f"{(contrast / 3.29 / 14.86) ** 2:.6f}",
        "fraction", "derived",
        "treating the p5-p95 contrast as 3.29 sd of a normal; the observed "
        "held-out R squared for impervious fraction is 0.085, three orders of "
        "magnitude larger, so the observed association is not this signal")
    return out


def report(rows: list[dict]) -> None:
    if not rows:
        print("  nothing measured")
        return
    width = max(len(r["quantity"]) for r in rows)
    for r in rows:
        print(f"  {r['quantity']:<{width}}  {r['value']:>12}  {r['unit']}")


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
            writer = csv.DictWriter(
                handle, fieldnames=["quantity", "value", "unit", "basis", "note"])
            writer.writeheader()
            writer.writerows(rows)
        try:
            shown = Path(args.out).resolve().relative_to(REPO)
        except ValueError:
            # The recipe verifier redirects --out to a temporary directory
            # outside the repository, and relative_to raises there. The other
            # measurement scripts already guard this; this one did not, and the
            # slow tier caught it because the default tier never re-runs a
            # local-input recipe.
            shown = Path(args.out)
        print(f"\n  wrote {shown}")
    else:
        print("\n  re-run with --write to write the artefact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
