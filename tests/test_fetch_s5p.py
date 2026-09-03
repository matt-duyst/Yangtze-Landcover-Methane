"""Tests for the Sentinel-5P mirror fetch module.

Offline throughout. S3 listings are synthetic XML, HTTP is a fake, and the
netCDF granules are built in ``tmp_path`` with the real group structure:
a PRODUCT group holding the methane variables with their own ``_FillValue``,
``qa_value`` as uint8 with ``scale_factor``, and latitude and longitude.

The case worth naming is the one this route cannot do properly. There is no
usable checksum, so a corrupted body would pass every check the other two
fetch routes would catch. What is tested here is the weaker thing that is
available: a body that is not a netCDF granule is rejected and not written.
"""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path

import numpy as np
import pytest

from src.fetch import s5p

FILL = 9.969209968386869e+36

NAME = ("S5P_RPRO_L2__CH4____20180514T042147_20180514T060317"
        "_03019_03_020400_20221109T092730.nc")
OLDER = ("S5P_RPRO_L2__CH4____20180514T042048_20180514T060416"
         "_03019_01_010202_20181215T075435.nc")
NIGHT = ("S5P_RPRO_L2__CH4____20180514T175200_20180514T193600"
         "_03027_03_020400_20221109T092730.nc")


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------

def listing_xml(entries, *, truncated=False, token=None):
    """An S3 ListObjectsV2 response. ETags are multipart, as the real ones are."""
    body = "".join(
        f"<Contents><Key>{key}</Key><Size>{size}</Size>"
        f"<ETag>&quot;{'ab' * 16}-7&quot;</ETag></Contents>"
        for key, size in entries
    )
    more = f"<NextContinuationToken>{token}</NextContinuationToken>" if token else ""
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<ListBucketResult xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
        f"<Name>meeo-s5p</Name><KeyCount>{len(entries)}</KeyCount>"
        f"<IsTruncated>{'true' if truncated else 'false'}</IsTruncated>"
        f"{more}{body}</ListBucketResult>"
    )


class FakeResponse:
    def __init__(self, *, text="", content=b"", headers=None, status=200):
        self.text, self.content = text, content
        self.headers, self.status_code = headers or {}, status

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def iter_content(self, chunk_size=1):
        for i in range(0, len(self.content), chunk_size):
            yield self.content[i:i + chunk_size]


class FakeSession:
    def __init__(self, responses):
        self._responses, self.calls = list(responses), []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if not self._responses:
            raise AssertionError(f"unexpected extra request to {url}")
        return self._responses.pop(0)


def write_granule(path, *, n=6, with_product=True, missing=()):
    """A minimal but structurally real S5P granule."""
    import netCDF4

    with netCDF4.Dataset(path, "w", format="NETCDF4") as ds:
        group = ds.createGroup("PRODUCT") if with_product else ds
        group.createDimension("time", 1)
        group.createDimension("scanline", n)
        group.createDimension("ground_pixel", n)
        dims = ("time", "scanline", "ground_pixel")
        for name in ("methane_mixing_ratio_bias_corrected", "methane_mixing_ratio"):
            if name in missing:
                continue
            var = group.createVariable(name, "f4", dims, fill_value=FILL)
            var[:] = np.full((1, n, n), 1900.0, dtype="f4")
        if "qa_value" not in missing:
            qa = group.createVariable("qa_value", "u1", dims, fill_value=255)
            qa.scale_factor = 0.01
            qa[:] = np.full((1, n, n), 100, dtype="u1")
        for name, base in (("latitude", 31.0), ("longitude", 118.0)):
            if name in missing:
                continue
            var = group.createVariable(name, "f4", dims)
            var[:] = np.full((1, n, n), base, dtype="f4")
    return path


# --------------------------------------------------------------------------
# filename parsing
# --------------------------------------------------------------------------

def test_granule_name_parses_into_its_fields():
    fields = s5p.parse_granule_name(NAME)
    assert fields["stream"] == "RPRO"
    assert fields["product"] == "L2__CH4___"
    assert fields["orbit"] == 3019
    assert fields["collection"] == 3
    assert fields["processor"] == 20400
    assert fields["start"] == datetime(2018, 5, 14, 4, 21, 47)
    assert fields["stop"] == datetime(2018, 5, 14, 6, 3, 17)


def test_a_name_that_is_not_a_granule_returns_none():
    assert s5p.parse_granule_name("index.html") is None
    assert s5p.parse_granule_name("RPRO/L2__CH4___/2018/05/14/") is None


# --------------------------------------------------------------------------
# listing
# --------------------------------------------------------------------------

def test_list_prefix_parses_keys_and_sizes():
    session = FakeSession([FakeResponse(text=listing_xml(
        [(f"RPRO/L2__CH4___/2018/05/14/{NAME}", 58511239)]))])
    got = s5p.list_prefix("RPRO/L2__CH4___/2018/05/14/", session=session)
    assert len(got) == 1
    assert got[0].size == 58511239
    assert got[0].orbit == 3019
    assert got[0].name == NAME


def test_list_prefix_follows_continuation_tokens():
    session = FakeSession([
        FakeResponse(text=listing_xml([(f"p/{NAME}", 1)], truncated=True, token="T1")),
        FakeResponse(text=listing_xml([(f"p/{OLDER}", 2)])),
    ])
    got = s5p.list_prefix("p/", session=session)
    assert len(got) == 2
    assert len(session.calls) == 2
    assert session.calls[1][1]["params"]["continuation-token"] == "T1"


def test_list_prefix_ignores_entries_that_are_not_granules():
    session = FakeSession([FakeResponse(text=listing_xml(
        [("RPRO/L2__CH4___/2018/05/14/", 0), (f"p/{NAME}", 1)]))])
    assert len(s5p.list_prefix("p/", session=session)) == 1


def test_daily_prefixes_covers_the_range_inclusively():
    prefixes = list(s5p.daily_prefixes(date(2018, 5, 14), date(2018, 5, 16),
                                       stream="RPRO", product="L2__CH4___"))
    assert prefixes == ["RPRO/L2__CH4___/2018/05/14/",
                        "RPRO/L2__CH4___/2018/05/15/",
                        "RPRO/L2__CH4___/2018/05/16/"]


def test_list_range_requests_one_prefix_per_day():
    session = FakeSession([FakeResponse(text=listing_xml([])) for _ in range(3)])
    s5p.list_range(date(2018, 5, 14), date(2018, 5, 16), stream="RPRO",
                   product="L2__CH4___", session=session)
    assert len(session.calls) == 3


# --------------------------------------------------------------------------
# duplicate orbits
# --------------------------------------------------------------------------

def test_latest_per_orbit_keeps_the_highest_processor_version():
    """A day of L2__CH4___ holds every orbit twice; keeping both doubles the fetch."""
    granules = [
        s5p.Granule(key=f"p/{OLDER}", size=1, **s5p.parse_granule_name(OLDER)),
        s5p.Granule(key=f"p/{NAME}", size=2, **s5p.parse_granule_name(NAME)),
    ]
    kept = s5p.latest_per_orbit(granules)
    assert len(kept) == 1
    assert kept[0].processor == 20400
    assert kept[0].collection == 3


def test_latest_per_orbit_keeps_distinct_orbits():
    granules = [
        s5p.Granule(key=f"p/{NAME}", size=1, **s5p.parse_granule_name(NAME)),
        s5p.Granule(key=f"p/{NIGHT}", size=1, **s5p.parse_granule_name(NIGHT)),
    ]
    assert len(s5p.latest_per_orbit(granules)) == 2


# --------------------------------------------------------------------------
# the candidacy superset
# --------------------------------------------------------------------------

def test_candidate_window_matches_sun_synchronous_timing():
    """13:30 local at 114.8-122.6 east is about 05:19 to 05:50 UTC."""
    lo, hi = s5p.candidate_window(114.8, 122.6, margin_minutes=0.0)
    assert hi == pytest.approx(13.5 - 114.8 / 15.0, abs=1e-6)
    assert lo == pytest.approx(13.5 - 122.6 / 15.0, abs=1e-6)
    assert 5.3 < lo < 5.4 and 5.8 < hi < 5.9


def test_the_daylight_orbit_over_the_box_is_a_candidate():
    granule = s5p.Granule(key=f"p/{NAME}", size=1, **s5p.parse_granule_name(NAME))
    assert s5p.intersects_box(granule, 114.8, 122.6) is True


def test_an_orbit_on_the_far_side_of_the_earth_is_not():
    granule = s5p.Granule(key=f"p/{NIGHT}", size=1, **s5p.parse_granule_name(NIGHT))
    assert s5p.intersects_box(granule, 114.8, 122.6) is False


def test_the_filter_keeps_a_small_fraction_of_a_day():
    """Fourteen orbits a day; the box is over one of them."""
    made = []
    for i, hour in enumerate(range(0, 24, 2)):
        name = (f"S5P_RPRO_L2__CH4____201805 14T{hour:02d}0000_"
                f"20180514T{(hour + 1) % 24:02d}4000_0{3000 + i}_03_020400_"
                f"20221109T092730.nc").replace(" ", "")
        fields = s5p.parse_granule_name(name)
        made.append(s5p.Granule(key=f"p/{name}", size=1, **fields))
    kept = [g for g in made if s5p.intersects_box(g, 114.8, 122.6)]
    assert 0 < len(kept) < len(made) / 3


def test_a_wider_margin_keeps_more(monkeypatch):
    granule = s5p.Granule(key=f"p/{NIGHT}", size=1, **s5p.parse_granule_name(NIGHT))
    assert s5p.intersects_box(granule, 114.8, 122.6, margin_minutes=0.0) is False
    assert s5p.intersects_box(granule, 114.8, 122.6, margin_minutes=12 * 60) is True


# --------------------------------------------------------------------------
# structural verification, standing in for a checksum
# --------------------------------------------------------------------------

def test_open_check_accepts_a_real_granule(tmp_path):
    path = write_granule(tmp_path / "ok.nc")
    s5p.open_check(path)


def test_open_check_rejects_a_file_without_a_product_group(tmp_path):
    path = write_granule(tmp_path / "flat.nc", with_product=False)
    with pytest.raises(s5p.NotNetCDF, match="PRODUCT"):
        s5p.open_check(path)


def test_open_check_rejects_a_granule_missing_a_required_variable(tmp_path):
    path = write_granule(tmp_path / "thin.nc", missing=("qa_value",))
    with pytest.raises(s5p.NotNetCDF, match="qa_value"):
        s5p.open_check(path)


def test_open_check_rejects_something_that_is_not_netcdf_at_all(tmp_path):
    path = tmp_path / "page.nc"
    path.write_bytes(b"<html>not a granule</html>")
    with pytest.raises(s5p.NotNetCDF):
        s5p.open_check(path)


def test_a_record_carries_no_digest_because_the_etag_is_multipart():
    granule = s5p.Granule(key=f"p/{NAME}", size=10, **s5p.parse_granule_name(NAME))
    record = granule.record()
    assert record.digest is None
    assert record.md5 is None
    assert record.content_size == 10
    assert record.content_url.endswith(NAME)


# --------------------------------------------------------------------------
# download
# --------------------------------------------------------------------------

def test_download_writes_a_granule_that_passes_the_structural_check(tmp_path):
    source = write_granule(tmp_path / "src.nc")
    body = source.read_bytes()
    granule = s5p.Granule(key=f"p/{NAME}", size=len(body),
                          **s5p.parse_granule_name(NAME))
    session = FakeSession([FakeResponse(
        content=body, headers={"Content-Type": "application/x-netcdf"})])
    out = s5p.download_granule(granule, tmp_path / "out.nc", session=session)
    assert out.exists()
    s5p.open_check(out)


def test_download_rejects_a_body_that_is_not_netcdf_and_writes_nothing(tmp_path):
    body = b"<html>error</html>" * 4
    granule = s5p.Granule(key=f"p/{NAME}", size=len(body),
                          **s5p.parse_granule_name(NAME))
    session = FakeSession([FakeResponse(
        content=body, headers={"Content-Type": "application/x-netcdf"})])
    target = tmp_path / "out.nc"
    with pytest.raises(s5p.NotNetCDF):
        s5p.download_granule(granule, target, session=session)
    assert not target.exists()
    assert not (tmp_path / "out.nc.part").exists()


def test_download_rejects_a_truncated_body(tmp_path):
    source = write_granule(tmp_path / "src.nc")
    body = source.read_bytes()
    granule = s5p.Granule(key=f"p/{NAME}", size=len(body) + 500,
                          **s5p.parse_granule_name(NAME))
    session = FakeSession([FakeResponse(
        content=body, headers={"Content-Type": "application/x-netcdf"})])
    with pytest.raises(s5p.TruncatedDownload):
        s5p.download_granule(granule, tmp_path / "out.nc", session=session)
    assert not (tmp_path / "out.nc").exists()


def test_download_skips_when_a_file_of_the_expected_size_is_present(tmp_path):
    source = write_granule(tmp_path / "src.nc")
    body = source.read_bytes()
    target = tmp_path / "out.nc"
    target.write_bytes(body)
    granule = s5p.Granule(key=f"p/{NAME}", size=len(body),
                          **s5p.parse_granule_name(NAME))
    session = FakeSession([])          # any request would raise
    assert s5p.download_granule(granule, target, session=session) == target
    assert session.calls == []


# --------------------------------------------------------------------------
# summarising
# --------------------------------------------------------------------------

def test_by_year_and_volume():
    granules = [
        s5p.Granule(key=f"p/{NAME}", size=100, **s5p.parse_granule_name(NAME)),
        s5p.Granule(key=f"p/{NIGHT}", size=50, **s5p.parse_granule_name(NIGHT)),
    ]
    assert s5p.volume(granules) == 150
    assert list(s5p.by_year(granules)) == [2018]
    assert len(s5p.by_year(granules)[2018]) == 2


def test_shipped_config_declares_the_box_grid_and_threshold():
    import yaml
    config = yaml.safe_load(
        (Path(__file__).resolve().parents[1] / "config" / "sources.yml")
        .read_text(encoding="utf-8"))["s5p"]
    box = config["bounding_box"]
    assert (box["west"], box["south"], box["east"], box["north"]) == \
        (114.8, 27.0, 122.6, 35.2)
    assert config["grid_resolution_deg"] == 0.25
    assert config["qa_threshold"] == 0.75
    assert config["base_url"].endswith("meeo-s5p.s3.amazonaws.com")
