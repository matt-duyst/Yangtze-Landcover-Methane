"""Anonymous acquisition of Sentinel-5P Level 2 granules from the MEEO mirror.

Copernicus Data Space serves the same products but requires authentication to
download, so it cannot be scripted for anyone who has not registered. The MEEO
mirror at ``meeo-s5p.s3.amazonaws.com`` serves them over plain HTTPS with no
credentials, under the prefixes ``OFFL/``, ``NRTI/``, ``RPRO/`` and ``COGT/``,
which makes it the only route that runs from a fresh clone.

Three properties of the route shape this module.

**There is no usable checksum.** The bucket returns an ``ETag`` for every
object, but every one observed is a multipart tag with a ``-N`` suffix: an MD5
of the concatenated part MD5s, not of the object. Reproducing it requires the
part size the uploader used, which is not published. So the digest verification
the figshare and Science Data Bank routes get is not available here, and
:func:`open_check` substitutes a structural test: the file must open as netCDF4
and contain a ``PRODUCT`` group with the expected variables. That is strictly
weaker. It catches a truncated or HTML body and would not catch a silently
corrupted one.

**Every orbit appears more than once.** A day of ``RPRO/L2__CH4___`` holds 28
keys for 14 orbits, the same orbit at processor versions ``010202`` and
``020400``. Listing naively and downloading everything doubles the volume and
mixes two reconstructions of the same overpass. :func:`latest_per_orbit` keeps
the highest processor version per orbit.

**A filename carries no footprint.** The name encodes an orbit number and a UTC
time window, not a geographic extent, so intersection with a bounding box
cannot be decided from the listing. :func:`candidate_window` predicts the UTC
window during which a sun-synchronous satellite with a 13:30 local equator
crossing is over a given longitude range, and :func:`intersects_box` keeps
granules whose time window overlaps it. **This is a superset, not an exact
test.** It selects roughly one orbit per day out of fourteen; whether the swath
actually reached the box is only knowable after reading the granule's own
latitude and longitude arrays.
"""

from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable, Iterator, Sequence

import requests

from src.fetch.common import (  # noqa: F401  (re-exported for callers)
    DEFAULT_TIMEOUT,
    FetchError,
    FileRecord,
    TruncatedDownload,
    UnexpectedContentType,
    digest_of,
    download_record,
    filter_records,
    is_already_fetched,
    md5_of,
    plan,
)

DEFAULT_BASE_URL = "https://meeo-s5p.s3.amazonaws.com"

#: Sentinel-5P's local solar time at the descending node, in hours. The orbit
#: is sun-synchronous, so this is what makes overpass time predictable from
#: longitude alone.
DESCENDING_NODE_LOCAL_HOURS = 13.5

#: Minutes either side of the predicted overpass to keep. One orbit is about
#: 101 minutes and the swath is 2600 km wide, so a neighbouring orbit can still
#: clip a box the nadir track misses. Widening by roughly half an orbit keeps
#: those; it is why the filter is a superset.
DEFAULT_MARGIN_MINUTES = 55.0

_S3_NS = "{http://s3.amazonaws.com/doc/2006-03-01/}"

#: ``S5P_<stream>_L2__CH4____<start>_<stop>_<orbit>_<collection>_<processor>_<produced>.nc``
_GRANULE_RE = re.compile(
    r"S5P_(?P<stream>[A-Z]+)_(?P<product>L2__[A-Z0-9_]+?)_"
    r"(?P<start>\d{8}T\d{6})_(?P<stop>\d{8}T\d{6})_"
    r"(?P<orbit>\d{5})_(?P<collection>\d{2})_(?P<processor>\d{6})_"
    r"(?P<produced>\d{8}T\d{6})\.nc$"
)


class S5PError(FetchError):
    """Base class for failures specific to this route."""


class NotNetCDF(S5PError):
    """A downloaded file is not a Sentinel-5P netCDF granule."""


@dataclass(frozen=True)
class Granule:
    """One granule on the mirror, described by its key and filename."""

    key: str
    size: int
    stream: str
    product: str
    start: datetime
    stop: datetime
    orbit: int
    collection: int
    processor: int

    @property
    def name(self) -> str:
        return self.key.rsplit("/", 1)[-1]

    def record(self, base_url: str = DEFAULT_BASE_URL) -> FileRecord:
        """As a :class:`~src.fetch.common.FileRecord`, with no digest.

        ``digest`` is None deliberately: the bucket's multipart ETag is not the
        object's MD5 and must not be passed off as one.
        """
        return FileRecord(
            name=self.name,
            content_size=self.size,
            encoding_format="application/x-netcdf",
            digest=None,
            content_url=f"{base_url.rstrip('/')}/{self.key}",
        )


def parse_granule_name(name: str) -> dict | None:
    """Pull the fields out of a granule filename, or None if it is not one."""
    match = _GRANULE_RE.search(name.rsplit("/", 1)[-1])
    if not match:
        return None
    fields = match.groupdict()
    return {
        "stream": fields["stream"],
        "product": fields["product"],
        "start": datetime.strptime(fields["start"], "%Y%m%dT%H%M%S"),
        "stop": datetime.strptime(fields["stop"], "%Y%m%dT%H%M%S"),
        "orbit": int(fields["orbit"]),
        "collection": int(fields["collection"]),
        "processor": int(fields["processor"]),
    }


def list_prefix(
    prefix: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
    max_keys: int = 1000,
) -> list[Granule]:
    """List every granule under one S3 prefix, following continuation tokens."""
    sess = session or requests.Session()
    granules: list[Granule] = []
    token = None
    while True:
        params = {"list-type": "2", "prefix": prefix, "max-keys": str(max_keys)}
        if token:
            params["continuation-token"] = token
        response = sess.get(base_url, params=params, timeout=timeout)
        response.raise_for_status()
        root = ET.fromstring(response.text)
        for contents in root.findall(f"{_S3_NS}Contents"):
            key = contents.findtext(f"{_S3_NS}Key") or ""
            size = int(contents.findtext(f"{_S3_NS}Size") or 0)
            fields = parse_granule_name(key)
            if fields is None:
                continue
            granules.append(Granule(key=key, size=size, **fields))
        truncated = (root.findtext(f"{_S3_NS}IsTruncated") or "false").lower() == "true"
        token = root.findtext(f"{_S3_NS}NextContinuationToken")
        if not truncated or not token:
            break
    return granules


def daily_prefixes(
    start: date, end: date, *, stream: str, product: str
) -> Iterator[str]:
    """One prefix per day in ``[start, end]``, as the mirror lays them out."""
    day = start
    while day <= end:
        yield f"{stream}/{product}/{day:%Y/%m/%d}/"
        day += timedelta(days=1)


def list_range(
    start: date,
    end: date,
    *,
    stream: str,
    product: str,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
) -> list[Granule]:
    """List every granule of one product over a date range."""
    found: list[Granule] = []
    for prefix in daily_prefixes(start, end, stream=stream, product=product):
        found.extend(list_prefix(prefix, base_url=base_url, timeout=timeout,
                                 session=session))
    return found


def latest_per_orbit(granules: Iterable[Granule]) -> list[Granule]:
    """Keep the highest processor version of each orbit.

    The mirror carries every orbit at more than one processor version. Keeping
    all of them doubles the download and mixes two reconstructions of the same
    overpass in one composite.
    """
    best: dict[int, Granule] = {}
    for granule in granules:
        current = best.get(granule.orbit)
        if current is None or (granule.processor, granule.collection) > \
                (current.processor, current.collection):
            best[granule.orbit] = granule
    return sorted(best.values(), key=lambda g: (g.start, g.orbit))


def candidate_window(
    west: float,
    east: float,
    *,
    local_hours: float = DESCENDING_NODE_LOCAL_HOURS,
    margin_minutes: float = DEFAULT_MARGIN_MINUTES,
) -> tuple[float, float]:
    """UTC hours during which the satellite could be over a longitude range.

    Sun-synchronous, so local solar time at the descending node is fixed and
    UTC equals local time minus longitude over fifteen. Returns
    ``(earliest, latest)`` in hours, possibly spanning midnight, widened by
    ``margin_minutes``.
    """
    times = sorted((local_hours - west / 15.0, local_hours - east / 15.0))
    margin = margin_minutes / 60.0
    return (times[0] - margin, times[1] + margin)


def intersects_box(
    granule: Granule,
    west: float,
    east: float,
    *,
    margin_minutes: float = DEFAULT_MARGIN_MINUTES,
) -> bool:
    """Whether a granule could have seen a longitude range.

    A SUPERSET test. The filename carries no footprint, so this compares the
    granule's UTC time window against the window in which a sun-synchronous
    orbit crosses those longitudes. It cannot tell whether the swath actually
    reached the box; only the granule's own latitude and longitude arrays can.
    """
    lo, hi = candidate_window(west, east, margin_minutes=margin_minutes)
    start = granule.start.hour + granule.start.minute / 60.0
    stop = granule.stop.hour + granule.stop.minute / 60.0
    if stop < start:                      # the window crosses midnight
        stop += 24.0
    for shift in (-24.0, 0.0, 24.0):      # so can the candidate window
        if max(start, lo + shift) <= min(stop, hi + shift):
            return True
    return False


def open_check(path: Path, *, required=("methane_mixing_ratio_bias_corrected",
                                        "qa_value", "latitude", "longitude")) -> None:
    """Raise unless ``path`` is a Sentinel-5P netCDF granule.

    This is what stands in for a checksum on this route. It proves the file is
    structurally a granule; it does not prove the bytes are the ones the
    publisher wrote.
    """
    import netCDF4

    try:
        with netCDF4.Dataset(path, "r") as dataset:
            if "PRODUCT" not in dataset.groups:
                raise NotNetCDF(f"{Path(path).name}: no PRODUCT group")
            product = dataset.groups["PRODUCT"]
            missing = [v for v in required if v not in product.variables]
            if missing:
                raise NotNetCDF(
                    f"{Path(path).name}: PRODUCT lacks {missing}")
    except NotNetCDF:
        raise
    except Exception as exc:
        raise NotNetCDF(f"{Path(path).name}: not readable as netCDF4 ({exc})") from exc


def download_granule(
    granule: Granule,
    destination: Path,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
    check: bool = True,
) -> Path:
    """Download one granule, structurally verify it, and put it in place.

    Skips when the destination already holds a file of the expected size. There
    is no digest to check it against, so size is the only test available for an
    existing file, and that is weaker than the other routes' skip check.
    """
    record = granule.record(base_url)
    return download_record(
        record, Path(destination), timeout=timeout, session=session,
        post_check=open_check if check else None,
    )


def volume(granules: Sequence[Granule]) -> int:
    return sum(g.size for g in granules)


def by_year(granules: Iterable[Granule]) -> dict[int, list[Granule]]:
    grouped: dict[int, list[Granule]] = {}
    for granule in granules:
        grouped.setdefault(granule.start.year, []).append(granule)
    return dict(sorted(grouped.items()))
