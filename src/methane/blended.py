"""Reading the blended TROPOMI+GOSAT product, which is not shaped like the
operational one.

The blended product of Balasus et al. (2023, doi:10.5194/amt-16-3787-2023)
applies a machine-learned correction for SWIR surface albedo, aerosol and
cirrus scattering, and across-track striping to the operational TROPOMI
methane retrieval, referenced to GOSAT. It adds one variable,
`methane_mixing_ratio_blended`, to a subset of the operational file.

Why this is a separate reader and not a flag on the other one
-------------------------------------------------------------

`src.methane.grid.read_soundings` reads the operational layout, and three
committed composites rest on it. It does seven things that are *about* that
layout: it walks into the `PRODUCT` group; it takes fill values and scale
factors from each variable's own attributes inside that group; it filters on
`qa_value` in stored units; it finds covariates in **three different**
subgroups of `PRODUCT/SUPPORT_DATA` through `CovariateSpec.group`; it derives
the a priori column from profiles in one of them; and it recovers the
acquisition time from attributes or the filename.

Two of those are structurally absent here. The blended files are **flat
rooted** -- "they no longer reside in netCDF groups", says the product user
manual -- so there is no group path to walk, and three of the seven covariates
this project grids are simply not in the file. Making the group path optional
would leave `CovariateSpec.group` meaningless on one branch and would turn the
operational reader's assumption about where albedo lives from a declared fact
into an implicit one. That assumption is load-bearing for the committed
composites, so it should stay declared.

So this module reads what the blended files actually contain and says so, and
`read_soundings` is untouched. The cost is that the two share no reading code;
what they do share is `GridSpec`, `GranuleContribution` and `Composite`, which
is where the like-for-like guarantee lives.

qa is asserted rather than relied on
------------------------------------

The manual states the files hold only soundings with `qa_value == 1.0`. A
census of all 578 candidate granules of 2018 and 399,630,175 soundings found
`qa_value` takes only the raw bytes {0, 16, 40, 100}, so `>= 0.75` and
`== 1.0` select the identical set and the blended product loses nothing the
operational composite kept. The threshold is applied here anyway, in stored
units exactly as `grid.py` does it, and the number of soundings it drops is
recorded per granule. It is zero, and a future file where it is not would show
up as a number rather than as a silent change of sample.

Reading one variable out of a remote file
-----------------------------------------

The AWS bucket answers `Accept-Ranges: bytes`, so :class:`RangeFile` lets HDF5
fetch only the chunks holding the variables asked for. A blended granule is 8
to 46 MB and the four variables needed come to about 2 MB in 8 range requests.
Validated before use: on two granules, one the largest in-box contributor and
one the smallest, a range read and a whole-file read returned bit-identical
arrays for every variable.
"""

from __future__ import annotations

import io
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Sequence

import numpy as np

from .grid import Composite, GranuleContribution, GridSpec, MethaneError

#: The variable the correction adds. Everything else in the file is the
#: operational value, unaltered.
BLENDED = "methane_mixing_ratio_blended"

#: The AWS Registry of Open Data bucket. Anonymous, us-west-2, partitioned by
#: orbit inside monthly folders. See `data/manifest.json` for the terms.
BUCKET = "blended-tropomi-gosat-methane"
BASE_URL = f"https://{BUCKET}.s3.us-west-2.amazonaws.com"

#: Block size for a remote read. Measured rather than chosen: at 128 kB one
#: granule costs 1.4 MB in 11 requests, at 256 kB 2.1 MB in 8, at 512 kB 2.6 MB
#: in 5. The middle one is the compromise between bytes and round trips.
BLOCK_BYTES = 1 << 18

_ORBIT = re.compile(r"_(\d{5})_\d{2}_\d{6}_")
_TIMES = re.compile(r"_(\d{8}T\d{6})_(\d{8}T\d{6})_")


class BlendedError(MethaneError):
    """The file is not shaped the way the product manual describes."""


class RangeFile(io.RawIOBase):
    """A read-only file over HTTP range requests, for h5py.

    Blocks are cached, so HDF5's many small reads collapse into a few
    requests. Nothing is written to disk: the point is to read one variable out
    of a file without fetching the rest of it.
    """

    def __init__(self, url: str, size: int, block: int = BLOCK_BYTES,
                 session=None):
        import requests

        self.url, self.size, self.block = url, int(size), int(block)
        self.pos = 0
        self._blocks: dict[int, bytes] = {}
        self.requests = 0
        self.bytes = 0
        self.session = session or requests.Session()

    @classmethod
    def open(cls, url: str, block: int = BLOCK_BYTES, session=None):
        """Open ``url``, taking the size from a HEAD request."""
        import requests

        session = session or requests.Session()
        head = session.head(url, timeout=90)
        head.raise_for_status()
        if head.headers.get("Accept-Ranges") != "bytes":
            raise BlendedError(
                f"{url} does not answer Accept-Ranges: bytes, so one variable "
                f"cannot be read without the whole file")
        return cls(url, int(head.headers["Content-Length"]), block, session)

    def _fetch(self, index: int) -> bytes:
        if index in self._blocks:
            return self._blocks[index]
        start = index * self.block
        stop = min(start + self.block, self.size) - 1
        response = self.session.get(
            self.url, headers={"Range": f"bytes={start}-{stop}"}, timeout=90)
        response.raise_for_status()
        self.requests += 1
        self.bytes += len(response.content)
        self._blocks[index] = response.content
        return response.content

    def readable(self) -> bool:
        return True

    def seekable(self) -> bool:
        return True

    def seek(self, offset: int, whence: int = 0) -> int:
        self.pos = (offset if whence == 0
                    else self.pos + offset if whence == 1
                    else self.size + offset)
        return self.pos

    def tell(self) -> int:
        return self.pos

    def read(self, n: int = -1) -> bytes:
        if n is None or n < 0:
            n = self.size - self.pos
        n = min(n, self.size - self.pos)
        out = bytearray()
        while n > 0:
            index, inside = divmod(self.pos, self.block)
            chunk = self._fetch(index)[inside:inside + n]
            if not chunk:
                break
            out += chunk
            self.pos += len(chunk)
            n -= len(chunk)
        return bytes(out)

    def readinto(self, b) -> int:
        data = self.read(len(b))
        b[:len(data)] = data
        return len(data)


@dataclass(frozen=True)
class BlendedSoundings:
    """One granule's in-box soundings, after fill and qa filtering."""

    row: np.ndarray
    col: np.ndarray
    value: np.ndarray
    contribution: GranuleContribution
    #: How many soundings the qa threshold dropped. Zero for every 2018
    #: granule; recorded so that stops being an assumption.
    dropped_by_qa: int = 0


def parse_blended_name(name: str) -> dict:
    """Orbit and acquisition time from a blended filename.

    The manual states the only differences from the operational name are the
    processing type, which becomes BLND, and the generation time. So the orbit
    and the start time are in the same fields and the acquisition time needs
    no attribute.
    """
    orbit = _ORBIT.search(name)
    times = _TIMES.search(name)
    if not (orbit and times):
        raise BlendedError(f"{name} is not a blended granule name")
    return {
        "orbit": int(orbit.group(1)),
        "start": datetime.strptime(times.group(1), "%Y%m%dT%H%M%S"),
        "stop": datetime.strptime(times.group(2), "%Y%m%dT%H%M%S"),
    }


def _masked(dataset) -> tuple[np.ndarray, np.ndarray]:
    """A flat array and its validity, from the variable's own attributes.

    The fill value is read from `_FillValue` and never assumed, which is the
    same rule `grid.py` follows and for the same reason: it is a property of
    the file rather than of the product.
    """
    values = np.asarray(dataset[:]).ravel()
    fill = dataset.attrs.get("_FillValue")
    valid = np.ones(values.shape, dtype=bool)
    if fill is not None:
        valid &= values != np.asarray(fill).ravel()[0]
    if np.issubdtype(values.dtype, np.floating):
        valid &= np.isfinite(values)
    return values, valid


def read_blended(source, spec: GridSpec, *, name: str | None = None,
                 qa_threshold: float = 0.75,
                 variable: str = BLENDED) -> BlendedSoundings:
    """Read one blended granule and return its in-box soundings.

    ``source`` is a path or any file-like object h5py can open, so the same
    code reads a local file and a :class:`RangeFile`. ``name`` supplies the
    granule name when ``source`` is not a path.
    """
    import h5py

    granule = name or Path(str(getattr(source, "url", source))).name
    with h5py.File(source, "r") as handle:
        if handle.attrs.get("Title", b"") not in (
                "Blended TROPOMI+GOSAT Methane Product",
                b"Blended TROPOMI+GOSAT Methane Product"):
            raise BlendedError(
                f"{granule}: Title is not the blended product's; this reader "
                f"is for the blended layout only")
        for wanted in (variable, "latitude", "longitude", "qa_value"):
            if wanted not in handle:
                raise BlendedError(
                    f"{granule}: no {wanted!r} at the file root. The blended "
                    f"files are flat; an operational file needs "
                    f"src.methane.grid.read_soundings instead.")
        value, value_ok = _masked(handle[variable])
        lat, lat_ok = _masked(handle["latitude"])
        lon, lon_ok = _masked(handle["longitude"])
        qa = handle["qa_value"]
        qa_raw = np.asarray(qa[:]).ravel()
        qa_scale = qa.attrs.get("scale_factor")
        qa_offset = qa.attrs.get("add_offset")
        qa_fill = qa.attrs.get("_FillValue")

    from .grid import stored_threshold

    cutoff = stored_threshold(
        qa_threshold,
        None if qa_scale is None else float(np.asarray(qa_scale).ravel()[0]),
        None if qa_offset is None else float(np.asarray(qa_offset).ravel()[0]))
    good = value_ok & lat_ok & lon_ok
    if qa_fill is not None:
        good &= qa_raw != np.asarray(qa_fill).ravel()[0]
    passes = qa_raw >= cutoff
    dropped = int((good & ~passes).sum())
    good &= passes

    row, col, inside = spec.cell_of(lat, lon)
    keep = good & inside
    contribution = GranuleContribution(
        granule=granule,
        acquired=parse_blended_name(granule)["start"],
        soundings_read=int(lat.size),
        soundings_valid=int(good.sum()),
        soundings_in_box=int(keep.sum()),
    )
    return BlendedSoundings(row=row[keep], col=col[keep], value=value[keep],
                            contribution=contribution, dropped_by_qa=dropped)


def grid_blended(sources: Sequence, spec: GridSpec, *,
                 names: Sequence[str] | None = None,
                 qa_threshold: float = 0.75, variable: str = BLENDED,
                 on_granule=None) -> Composite:
    """Accumulate blended granules onto ``spec``, one at a time.

    Built as a :class:`~src.methane.grid.Composite` with the blended variable
    in ``sums``, so everything downstream -- ``mean_of``, ``coverage_of``, the
    export path -- works on it unchanged and the comparison with the
    operational composite is made on the same object.
    """
    counts = np.zeros(spec.shape, dtype="int64")
    total = np.zeros(spec.shape, dtype="float64")
    contributions, dropped = [], 0
    for index, source in enumerate(sources):
        name = names[index] if names else None
        soundings = read_blended(source, spec, name=name,
                                 qa_threshold=qa_threshold, variable=variable)
        np.add.at(counts, (soundings.row, soundings.col), 1)
        np.add.at(total, (soundings.row, soundings.col), soundings.value)
        contributions.append(soundings.contribution)
        dropped += soundings.dropped_by_qa
        if on_granule is not None:
            on_granule(index, soundings)
    if dropped:
        raise BlendedError(
            f"{dropped} soundings failed the qa threshold in a product "
            f"documented to hold only qa_value == 1.0; the sample is not what "
            f"the operational composite used and the comparison would not be "
            f"like for like")
    return Composite(spec=spec, qa_threshold=qa_threshold, counts=counts,
                     sums={variable: total}, contributions=tuple(contributions))
