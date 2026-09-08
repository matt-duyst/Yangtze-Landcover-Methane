"""Geospatial conventions shared by every map in this repository.

Seven more figures need coastlines, province boundaries, a graticule and a
projection, and they should inherit those from here rather than each restating
them. Nothing in this module knows about any particular figure.

**The projection is equirectangular with its standard parallel at the centre of
the study area.** Coordinates stay in degrees and the aspect ratio of the axes
is set to cos(31.075 deg) = 0.8565, so a degree of longitude is drawn 0.8565
times as long as a degree of latitude, which is what it is on the ground at
that latitude.

The reasoning, and what it costs:

* The analysis lattice is defined in geographic coordinates, so in this
  projection its cells stay axis-aligned rectangles and a reader can count
  them. In a conic projection the same lattice fans out and curves, which is
  honest about the geometry and much harder to read against.
* The projection carries **no analytical weight**. Areas in this project are
  computed analytically on the authalic sphere, not by projecting, and were
  validated that way to within 0.13 percent. Nothing is measured off the map,
  so an equal-area projection buys nothing here.
* Plate carree without the aspect correction, which is the easy default, draws
  the study area **16.8 percent too wide** east to west at this latitude. That
  is the specific error this constant exists to prevent.

What it distorts: scale is exact only at the standard parallel. East-west scale
runs 3.9 percent small at the southern edge and 4.8 percent large at the
northern edge. Area is not preserved, and since the drawn cells are all the
same size while a southern cell covers 9.1 percent more ground than a northern
one, the map slightly overstates the north. None of that reaches a number,
because no number is taken from the map.

This is emphatically **not** the projection the 2023 figures used. `ERRATA.md`
2.4 records those as ESRI:102029, Asia South Equidistant Conic, whose standard
parallels are 7 N and 32 S while the study area is at 31 N, in which a one
degree box here measures 26.89 percent larger than the geodesic truth.

The locator inset uses :data:`CHINA_ALBERS` instead, the equal-area conic this
project already uses for area measurement, because an inset spans most of
China and an equirectangular map of that extent is badly distorted at its
northern edge.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

#: Equal-area conic used for area measurement throughout this project, and for
#: the locator inset. Defined here so the seven remaining figures share it.
CHINA_ALBERS = ("+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 "
                "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")

#: Geographic CRS everything is stored in.
GEOGRAPHIC = "EPSG:4326"

#: Where the committed boundary layers live. Never the cartopy cache.
REFERENCE_DIR = Path(__file__).resolve().parents[2] / "data" / "reference"

PROVINCES = REFERENCE_DIR / "yrd_provinces.geojson"
LAND = REFERENCE_DIR / "yrd_land.geojson"
CHINA = REFERENCE_DIR / "china_admin1_dissolved.geojson"

#: Terrain and place layers, built by `scripts/build_map_reference.py`.
HILLSHADE = REFERENCE_DIR / "yrd_hillshade.tif"
INSET_RELIEF = REFERENCE_DIR / "china_hypsometric.tif"
PLACES = REFERENCE_DIR / "yrd_places.geojson"
NEIGHBOURS = REFERENCE_DIR / "yrd_neighbours.geojson"
INSET_BOUNDARIES = REFERENCE_DIR / "inset_boundaries.geojson"


@dataclass(frozen=True)
class Extent:
    """A lon/lat box, in the order matplotlib wants for ``set_extent``."""

    west: float
    east: float
    south: float
    north: float

    def as_tuple(self) -> tuple[float, float, float, float]:
        return (self.west, self.east, self.south, self.north)

    @property
    def centre_latitude(self) -> float:
        return 0.5 * (self.south + self.north)

    def padded(self, degrees: float) -> "Extent":
        return Extent(self.west - degrees, self.east + degrees,
                      self.south - degrees, self.north + degrees)


CONFIG = Path(__file__).resolve().parents[2] / "config" / "sources.yml"


def study_spec():
    """The analysis grid, read from the configuration.

    One definition for every figure. A figure that writes its own literals can
    drift from the grid the data was built on, which is the failure this whole
    module exists because of.
    """
    import yaml

    from src.methane.grid import GridSpec

    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["s5p"]
    box = config["bounding_box"]
    return GridSpec(box["west"], box["south"], box["east"], box["north"],
                    config["grid_resolution_deg"])


def lattice_extent(spec) -> Extent:
    """The extent the analysis lattice **actually** occupies.

    Derived from the cell count, never from the declared bounds, because a
    lattice built by rounding a declared extent to a cell size does not in
    general occupy it.

    The study grid used to be exactly such a case, and it rounded in **opposite
    directions on the two axes**: 7.8 degrees of longitude was 31.2 cells,
    rounded down to 31, so the lattice stopped short of the declared east edge
    at 122.55 rather than 122.6; 8.2 degrees of latitude was 32.8 cells,
    rounded up to 33, so it ran past the declared south edge to 26.95 rather
    than 27.0. The configuration now declares 122.55 and 26.95, so the two
    coincide and this function returns the declared bounds unchanged. It is
    kept, and still used everywhere, because nothing enforces that a future box
    or cell size divides evenly.
    """
    return Extent(west=spec.west,
                  east=spec.west + spec.n_cols * spec.resolution,
                  south=spec.north - spec.n_rows * spec.resolution,
                  north=spec.north)


def geographic_aspect(latitude: float) -> float:
    """Axes aspect that makes a degree of longitude its true length.

    A degree of longitude is cos(latitude) as long as a degree of latitude, so
    an axes drawn in degrees needs this as its aspect ratio. Without it the map
    is stretched east-west by 1/cos(latitude), which is 16.8 percent here.
    """
    return float(np.cos(np.radians(latitude)))


def display_ratio(extent: Extent) -> float:
    """Drawn height divided by drawn width for ``extent`` in this projection.

    A degree of longitude is shorter than a degree of latitude, so a box that
    is wider than it is tall in degrees can still be taller than it is wide on
    the page. The study box is: 7.75 degrees of longitude by 8.25 of latitude
    draws 1.24 times taller than wide.
    """
    width = (extent.east - extent.west) * geographic_aspect(extent.centre_latitude)
    return (extent.north - extent.south) / width


def figure_height_cm(extent: Extent, width_cm: float,
                     margins_cm: tuple[float, float] = (1.55, 1.30)) -> float:
    """Figure height that lets a map of ``extent`` fill its width.

    Sizing the figure to the map, rather than fitting the map into a figure
    chosen first, is what keeps a projected map from sitting in a band of
    white space. ``margins_cm`` is the horizontal and vertical furniture:
    axis labels, ticks and the outer padding.
    """
    horizontal, vertical = margins_cm
    return (width_cm - horizontal) * display_ratio(extent) + vertical


def apply_projection(ax, extent: Extent) -> None:
    """Set an axes to the project map projection over ``extent``."""
    ax.set_xlim(extent.west, extent.east)
    ax.set_ylim(extent.south, extent.north)
    ax.set_aspect(1.0 / geographic_aspect(extent.centre_latitude))


def to_albers(lon, lat):
    """Project lon/lat to :data:`CHINA_ALBERS`, for the inset."""
    from pyproj import Transformer
    transformer = Transformer.from_crs(GEOGRAPHIC, CHINA_ALBERS, always_xy=True)
    return transformer.transform(np.asarray(lon), np.asarray(lat))


def degree_formatter(axis: str):
    """Tick labels as degrees with a hemisphere letter, never a bare number.

    An unlabelled 120 on an axis could be anything. The venue standard asks for
    units on every axis label, and for a map the unit belongs on the tick.
    """
    suffix = {"x": ("E", "W"), "y": ("N", "S")}[axis]

    def format_tick(value, _position=None) -> str:
        letter = suffix[0] if value >= 0 else suffix[1]
        return f"{abs(value):g}°{letter}"

    return format_tick


def graticule(extent: Extent, step: float = 2.0) -> tuple[np.ndarray, np.ndarray]:
    """Tick positions at a whole-degree step covering ``extent``."""
    return (np.arange(np.ceil(extent.west / step) * step, extent.east + 1e-9, step),
            np.arange(np.ceil(extent.south / step) * step, extent.north + 1e-9, step))


def cell_edges(spec) -> tuple[np.ndarray, np.ndarray]:
    """Longitudes and latitudes of every analysis cell edge.

    Derived from the grid specification rather than written down, so the drawn
    lattice cannot disagree with the lattice the data was gridded onto.
    """
    extent = lattice_extent(spec)
    return (np.linspace(extent.west, extent.east, spec.n_cols + 1),
            np.linspace(extent.south, extent.north, spec.n_rows + 1))


def read_layer(path: Path):
    """Read a committed reference layer, in geographic coordinates."""
    import geopandas as gpd
    frame = gpd.read_file(path)
    if frame.crs is not None and frame.crs.to_epsg() != 4326:
        frame = frame.to_crs(GEOGRAPHIC)
    return frame


def read_raster(path: Path):
    """A committed reference raster and the extent matplotlib wants for it.

    Returns ``(array, (west, east, south, north))``. Bands come back as a
    (rows, cols) array for a single band and (rows, cols, bands) otherwise, so
    the caller can hand either straight to ``imshow``.
    """
    import rasterio

    with rasterio.open(path) as src:
        data = src.read()
        bounds = src.bounds
    array = data[0] if data.shape[0] == 1 else np.moveaxis(data, 0, -1)
    return array, (bounds.left, bounds.right, bounds.bottom, bounds.top)


def polygon_path(geometries):
    """One matplotlib Path covering every polygon in ``geometries``.

    Used as a clip path, which is how the relief is drawn twice -- once veiled
    for land outside the study region and once tinted inside it -- from a
    single raster and with no second copy of the array. Interiors are included
    as reversed rings so a hole in a polygon stays a hole.
    """
    from matplotlib.path import Path as MplPath

    vertices, codes = [], []

    def add(ring, reverse=False):
        points = list(ring.coords)
        if reverse:
            points = points[::-1]
        vertices.extend(points)
        codes.extend([MplPath.MOVETO] + [MplPath.LINETO] * (len(points) - 2)
                     + [MplPath.CLOSEPOLY])

    for geometry in geometries:
        if geometry is None or geometry.is_empty:
            continue
        parts = (geometry.geoms if geometry.geom_type.startswith("Multi")
                 else [geometry])
        for part in parts:
            if part.geom_type != "Polygon":
                continue
            add(part.exterior)
            for interior in part.interiors:
                add(interior, reverse=True)
    if not vertices:
        raise ValueError("no polygon geometry to build a clip path from")
    return MplPath(np.asarray(vertices), np.asarray(codes))
