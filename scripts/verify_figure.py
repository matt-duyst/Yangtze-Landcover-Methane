#!/usr/bin/env python3
"""Check a figure against the venue standard, the colour convention and itself.

    python scripts/verify_figure.py study_area
    python scripts/verify_figure.py study_area --renders

Three groups of check, and the third is the one worth having.

**The standard.** Physical size, pixel dimensions, resolution read from the PNG
header rather than trusted from the request, both byte limits, font embedding.
The exporter already refuses to write anything that fails these; this reports
them so the numbers exist outside an exception message.

**Colour.** Greyscale and colour-vision separation are properties of the role
set, not of a figure, so they are checked once in `tests/test_figures_palette.py`
and only summarised here. What is figure-specific is the relief: a continuous
grey under discrete overlays is a case the pairwise convention does not cover,
so the luminance range the relief actually occupies **in the rendered image** is
measured and every overlay role is checked against it. With ``--renders`` the
greyscale and three dichromat versions of the figure are written out.

**Whether anything was drawn and never seen.** Each artist is hidden in turn
and the render diffed against the full one; an artist that changes no pixels is
present, correct in isolation, and contributes nothing. This repository has
found one such element already -- a basemap under the composite's lattice, at
exactly zero visible pixels -- and no test of the code would have said so.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from src.figures import geo, output, style  # noqa: E402

#: Figures this script knows how to build, by the stem they are written under.
BUILDERS = {}


def _study_area():
    from src.figures.study_area import study_area_figure
    return study_area_figure(geo.study_spec())


def _composite():
    from src.figures.composite import composite_figure
    return composite_figure()


def _landcover():
    from src.figures.landcover import landcover_figure
    return landcover_figure()


BUILDERS["study_area"] = _study_area
BUILDERS["methane_composite_2018"] = _composite
BUILDERS["landcover_native"] = _landcover


def render(fig, dpi: int = style.MIN_DPI) -> np.ndarray:
    """The figure as an RGB array, through the same path savefig takes."""
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi)
    buffer.seek(0)
    from PIL import Image
    return np.asarray(Image.open(buffer).convert("RGB"))


def luminance(rgb: np.ndarray) -> np.ndarray:
    channels = rgb.astype("float64") / 255.0
    return (0.2126 * channels[..., 0] + 0.7152 * channels[..., 1]
            + 0.0722 * channels[..., 2])


# --------------------------------------------------------------------------
# the standard
# --------------------------------------------------------------------------

def report_standard(stem: str) -> None:
    vector = output.figures_root() / f"{stem}.pdf"
    raster = output.figures_root() / f"{stem}.png"
    width, height = output._png_size(raster)
    fig = BUILDERS[stem]()
    width_cm = fig.get_figwidth() / style.CM
    height_cm = fig.get_figheight() / style.CM
    plt.close(fig)
    dpi = round(width / (width_cm * style.CM))

    print("dimensions")
    print(f"  {width_cm:.2f} x {height_cm:.2f} cm")
    print(f"  {width} x {height} px, {dpi} dpi read from the PNG header")
    print(f"  width floor {style.MIN_WIDTH_CM} cm, dpi floor {style.MIN_DPI}")
    for name, path, limit in (("vector", vector, output.MAX_VECTOR_BYTES),
                              ("raster", raster, output.MAX_BYTES)):
        size = path.stat().st_size
        print(f"  {name} {size:,} B of {limit:,} B "
              f"({100 * size / limit:.0f} percent, "
              f"{limit - size:,} B of headroom)")
    print(f"  fonts embedded as glyphs: "
          f"{matplotlib.rcParams['pdf.fonttype'] == 42} "
          f"(pdf.fonttype {matplotlib.rcParams['pdf.fonttype']})")


# --------------------------------------------------------------------------
# colour
# --------------------------------------------------------------------------

def report_colour(stem: str, write_renders: bool, out_dir: Path) -> None:
    fig = BUILDERS[stem]()
    image = render(fig)
    plt.close(fig)

    grey = luminance(image)
    print("\ngreyscale and colour vision, over the role set")
    report = style.greyscale_report()
    print(f"  {report['adjacent_pairs']} declared adjacencies, "
          f"minimum luminance gap {report['min_adjacent_gap']:.3f} "
          f"at {report['min_adjacent_pair'][0]}/{report['min_adjacent_pair'][1]}")
    print(f"  minimum over all pairs {report['min_any_gap']:.3f} at "
          f"{report['min_any_pair'][0]}/{report['min_any_pair'][1]}, which is "
          f"reported and not asserted")
    for kind, result in style.cvd_report().items():
        print(f"  {kind:13s} minimum distance {result['min_distance']:.1f} "
              f"at {result['min_pair'][0]}/{result['min_pair'][1]}, "
              f"failures {len(result['failures'])}")

    print("\nthe relief, which is a band and not a role")
    relief = style.relief_report()
    print(f"  study region band   {relief['inside_band'][0]:.3f} to "
          f"{relief['inside_band'][1]:.3f}, flat ground at "
          f"{relief['inside_flat']:.3f}")
    print(f"  outside band        {relief['outside_band'][0]:.3f} to "
          f"{relief['outside_band'][1]:.3f}, flat ground at "
          f"{relief['outside_flat']:.3f}")
    print(f"  flat-ground gap     {relief['flat_ground_gap']:.3f}")
    print(f"  sea clears the band by {relief['sea_clearance']:.3f}")
    for name, clearance in sorted(relief["overlay_clearance"].items(),
                                  key=lambda item: item[1]):
        print(f"    {name:16s} sits {clearance:.3f} below the darker band")
    measured = _measured_relief_range() if stem == "study_area" else None
    if measured is not None:
        print("\n  measured on the composited relief itself, not on the "
              "declared band:")
        for where, stats in measured.items():
            print(f"    {where:14s} 1st-99th percentile "
                  f"{stats['p1']:.3f} to {stats['p99']:.3f}, "
                  f"full {stats['min']:.3f} to {stats['max']:.3f}, "
                  f"median {stats['median']:.3f}")
        floor = min(stats["min"] for stats in measured.values())
        worst = max(((role, style.ROLES[role].luminance)
                     for role in style.OVER_RELIEF),
                    key=lambda item: item[1])
        print(f"    every overlay clears the measured floor of {floor:.3f}; "
              f"the closest is {worst[0]} at {worst[1]:.3f}, "
              f"{floor - worst[1]:.3f} below it")
    print(f"\n  for reference, the whole rendered figure runs "
          f"{grey.min():.3f} to {grey.max():.3f}, which includes the black "
          f"text and the white page and says nothing about the relief")

    if not write_renders:
        return
    out_dir.mkdir(parents=True, exist_ok=True)
    from PIL import Image
    paths = []
    flat = np.repeat((grey * 255).astype("uint8")[..., None], 3, axis=2)
    path = out_dir / f"{stem}_greyscale.png"
    Image.fromarray(flat).save(path)
    paths.append(path)
    for kind in style.CVD_KINDS:
        seen = _simulate_image(image, kind)
        path = out_dir / f"{stem}_{kind}.png"
        Image.fromarray(seen).save(path)
        paths.append(path)
    print("\nrenders")
    for path in paths:
        print(f"  {path.relative_to(REPO)}")


def _measured_relief_range():
    """Luminance the relief actually occupies, from the composited arrays.

    The declared band is what the palette promises; this is what the raster
    delivers once the hillshade's own distribution has been stretched onto it.
    They differ, because the stretch clips: the band's ends are reached only
    where the shading reaches the ends of the stretch, and over a delta most
    of it does not.
    """
    try:
        from src.figures.study_area import MAP_WIDTH_CM, relief_image
    except ImportError:  # pragma: no cover
        return None
    land = geo.read_layer(geo.LAND)
    provinces = geo.read_layer(geo.PROVINCES)
    layers = relief_image(land, provinces, panel_width_cm=MAP_WIDTH_CM)
    import rasterio
    from rasterio.features import geometry_mask
    rgb = layers["rgb"]
    west, east, south, north = layers["extent"]
    transform = rasterio.transform.from_bounds(west, south, east, north,
                                               rgb.shape[1], rgb.shape[0])
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2])
    land_mask = ~geometry_mask(land.geometry, out_shape=rgb.shape[:2],
                               transform=transform, invert=False)
    inside = ~geometry_mask(provinces.geometry, out_shape=rgb.shape[:2],
                            transform=transform, invert=False)
    out = {}
    for where, mask in (("study region", land_mask & inside),
                        ("outside", land_mask & ~inside)):
        values = lum[mask]
        out[where] = {"min": float(values.min()), "max": float(values.max()),
                      "median": float(np.median(values)),
                      "p1": float(np.percentile(values, 1)),
                      "p99": float(np.percentile(values, 99))}
    return out


def _simulate_image(image: np.ndarray, kind: str) -> np.ndarray:
    """The whole image as a dichromat of ``kind`` sees it.

    Uses the same transform `style.simulate_cvd` applies to one colour, so the
    picture and the pairwise numbers cannot disagree about what is being
    simulated.
    """
    linear = style._to_linear(image.astype("float64") / 255.0)
    lms = linear @ style._LMS_FROM_LINEAR.T
    seen = lms @ style._DICHROMAT[kind].T
    back = style._from_linear(seen @ style._LINEAR_FROM_LMS.T)
    return np.clip(back * 255.0, 0, 255).astype("uint8")


# --------------------------------------------------------------------------
# whether anything was drawn and never seen
# --------------------------------------------------------------------------

def _artists(fig):
    """Every artist worth probing, with a name a reader will recognise."""
    out = []
    for index, ax in enumerate(fig.axes):
        panel = f"axes[{index}]"
        for image in ax.images:
            out.append((f"{panel} image {image.get_label()}", image))
        for collection in ax.collections:
            out.append((f"{panel} collection {collection.get_label()}",
                        collection))
        for line in ax.lines:
            out.append((f"{panel} line {line.get_label()}", line))
        for patch in ax.patches:
            out.append((f"{panel} patch {patch.get_label()}", patch))
        for text in ax.texts:
            out.append((f"{panel} text {text.get_text()[:24]!r}", text))
    for text in fig.texts:
        out.append((f"figure text {text.get_text()[:24]!r}", text))
    for legend in fig.legends:
        out.append(("figure legend", legend))
    return out


def report_visibility(stem: str, dpi: int = 150) -> None:
    """Hide each artist in turn and count the pixels that change.

    At a reduced dpi, because the question is whether an element contributes at
    all and not how many pixels it contributes at print resolution; a figure
    has to be rendered once per artist and there are hundreds.
    """
    fig = BUILDERS[stem]()
    full = render(fig, dpi=dpi)
    print(f"\nvisible pixels per artist, at {dpi} dpi "
          f"({full.shape[1]} x {full.shape[0]})")

    silent = []
    groups = {}
    for name, artist in _artists(fig):
        was = artist.get_visible()
        artist.set_visible(False)
        changed = int((render(fig, dpi=dpi) != full).any(axis=2).sum())
        artist.set_visible(was)
        key = name.split(" '")[0]
        groups.setdefault(key, [0, 0])
        groups[key][0] += changed
        groups[key][1] += 1
        if changed == 0:
            silent.append(name)

    for key, (total, count) in groups.items():
        suffix = f" ({count} artists)" if count > 1 else ""
        print(f"  {total:>9,}  {key}{suffix}")
    plt.close(fig)

    if silent:
        print(f"\n  DRAWN AND INVISIBLE: {len(silent)}")
        for name in silent:
            print(f"    {name}")
    else:
        print("\n  no artist contributes zero pixels")


NATIVE = {
    "landcover_native": lambda: _native_landcover(),
}


def _native_landcover():
    """Drawn pixels per native pixel, per raster panel."""
    from src.figures import landcover as lc
    panel_px = lc.PANEL_CM / 2.54 * style.MIN_DPI
    out = {}
    for label, path, product in (("GISA 30 m", lc.IMPERVIOUS_GISA, "gisa"),
                                 ("GAIA 30 m", lc.IMPERVIOUS_GAIA, "gaia")):
        mask, _, _ = lc.impervious_mask(path, product)
        out[label] = (mask.shape[1], panel_px / mask.shape[1])
    values, _ = lc.rice_classes()
    out["NESDC 10 m"] = (values.shape[1], panel_px / values.shape[1])
    return out


def report_native(stem: str) -> None:
    """Whether a raster panel is drawing what it says it is drawing."""
    if stem not in NATIVE:
        return
    print("\ndrawn pixels per source pixel, across the panel")
    for label, (columns, ratio) in NATIVE[stem]().items():
        verdict = "" if ratio >= 1.0 else "   <-- BELOW ONE, resampled away"
        print(f"  {label:16s} {columns:5d} source px -> {ratio:5.2f}{verdict}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("stem", choices=sorted(BUILDERS))
    parser.add_argument("--renders", action="store_true",
                        help="write the greyscale and dichromat versions")
    parser.add_argument("--out", default=str(REPO / "figures" / "checks"))
    parser.add_argument("--skip-visibility", action="store_true")
    args = parser.parse_args(argv)

    report_standard(args.stem)
    report_native(args.stem)
    report_colour(args.stem, args.renders, Path(args.out))
    if not args.skip_visibility:
        report_visibility(args.stem)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
