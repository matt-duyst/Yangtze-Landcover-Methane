"""Tests for the Science Data Bank fetch module.

Every test runs offline. The HTTP layer is a fake built in this file, and every
file these tests touch lives under ``tmp_path``, so the suite runs on a clone
with no data fetched and no network reachable.

The cases that matter most are the two silent failures the live route can
produce: a version string without its ``V`` prefix, which returns HTTP 200 and
an empty record rather than an error, and a download that answers HTTP 200 with
an error page or a truncated body.
"""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from src.fetch import scidb


# --------------------------------------------------------------------------
# fakes
# --------------------------------------------------------------------------

class FakeResponse:
    """Minimal stand-in for ``requests.Response``."""

    def __init__(self, *, json_body=None, content=b"", headers=None, status=200, url=""):
        self._json = json_body
        self.content = content
        self.headers = headers or {}
        self.status_code = status
        self.url = url

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self):
        return self._json

    def iter_content(self, chunk_size=1):
        for i in range(0, len(self.content), chunk_size):
            yield self.content[i:i + chunk_size]


class FakeSession:
    """Records calls and returns queued responses."""

    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if not self._responses:
            raise AssertionError(f"unexpected extra request to {url}")
        return self._responses.pop(0)


def croissant(entries):
    return {"@type": "sc:Dataset", "name": "test record", "distribution": list(entries)}


def entry(name, size, md5, url="https://example.invalid/download?fileId=abc"):
    return {
        "name": name,
        "contentSize": f"{size} B",
        "encodingFormat": "image/tiff",
        "md5": md5,
        "contentUrl": url,
        "sha256": None,
    }


BODY = b"a fake GeoTIFF payload" * 16
BODY_MD5 = hashlib.md5(BODY).hexdigest()

OCTET = {"Content-Type": "application/octet-stream"}


# --------------------------------------------------------------------------
# parsing
# --------------------------------------------------------------------------

def test_parse_distribution_reads_well_formed_records():
    doc = croissant([
        entry("classified-Anhui-2018-middle_rice-WGS84-v1.1.tif", 86324306, "aa" * 16),
        entry("classified-Ningxia-2025-middle_rice-WGS84-v1.tif", 1025415, "bb" * 16),
    ])
    records = scidb.parse_distribution(doc, version="V8")
    assert len(records) == 2
    first = records[0]
    assert first.name == "classified-Anhui-2018-middle_rice-WGS84-v1.1.tif"
    assert first.content_size == 86324306
    assert first.encoding_format == "image/tiff"
    assert first.md5 == "aa" * 16
    assert first.content_url.startswith("https://")
    assert first.stem == first.name


def test_parse_distribution_handles_nested_names():
    doc = croissant([entry("2021/classified-Anhui-2021-rice-WGS84-v1.tif", 10, "cc" * 16)])
    assert scidb.parse_distribution(doc)[0].stem == "classified-Anhui-2021-rice-WGS84-v1.tif"


def test_content_size_accepts_plain_integers():
    doc = {"distribution": [{"name": "x.tif", "contentSize": 4096,
                             "contentUrl": "https://example.invalid/x"}]}
    assert scidb.parse_distribution(doc)[0].content_size == 4096


# --------------------------------------------------------------------------
# the V-prefix trap
# --------------------------------------------------------------------------

def test_empty_distribution_raises_and_names_the_version():
    """version=8 returns HTTP 200 and this skeleton rather than an error."""
    skeleton = {"@type": "sc:Dataset", "name": "", "version": ".0.0", "distribution": []}
    with pytest.raises(scidb.EmptyDistributionError) as excinfo:
        scidb.parse_distribution(skeleton, version="8")
    message = str(excinfo.value)
    assert "'8'" in message
    assert "V" in message


def test_require_versioned_rejects_a_bare_number():
    with pytest.raises(ValueError, match="V"):
        scidb.require_versioned("8")


def test_require_versioned_accepts_a_prefixed_version():
    assert scidb.require_versioned("V8") == "V8"


def test_fetch_croissant_refuses_an_unprefixed_version_before_any_request():
    session = FakeSession([])          # any request at all would raise
    with pytest.raises(ValueError):
        scidb.fetch_croissant("deadbeef", "8", session=session)
    assert session.calls == []


def test_fetch_croissant_sends_both_parameters():
    doc = croissant([entry("a.tif", 10, "dd" * 16)])
    session = FakeSession([FakeResponse(json_body=doc)])
    got = scidb.fetch_croissant("abc123", "V8", session=session)
    assert got == doc
    _, kwargs = session.calls[0]
    assert kwargs["params"] == {"datasetId": "abc123", "version": "V8"}


# --------------------------------------------------------------------------
# filtering
# --------------------------------------------------------------------------

def test_province_filter_selects_the_expected_subset():
    names = [
        "classified-Anhui-2018-middle_rice-WGS84-v1.1.tif",
        "classified-Zhejiang-2018-middle_rice-WGS84-v1.1.tif",
        "classified-Jiangsu-2018-middle_rice-WGS84-v1.tif",
        "classified-Shanghai-2018-middle_rice-WGS84-v1.tif",
        "classified-Hunan-2018-middle_rice-WGS84-v1.1.tif",
        "classified-Ningxia-2018-middle_rice-WGS84-v1.tif",
    ]
    records = scidb.parse_distribution(croissant(
        [entry(n, 10, "ee" * 16) for n in names]))
    selected = scidb.filter_records(
        records, scidb.name_contains_any(["Anhui", "Zhejiang", "Jiangsu", "Shanghai"]))
    assert [r.stem for r in selected] == names[:4]


def test_province_filter_is_case_insensitive():
    records = scidb.parse_distribution(croissant(
        [entry("classified-ANHUI-2018-x.tif", 10, "ff" * 16)]))
    assert scidb.filter_records(records, scidb.name_contains_any(["anhui"]))


def test_province_filter_matches_on_the_stem_not_the_directory():
    """A directory named for a province must not drag in every file under it."""
    records = scidb.parse_distribution(croissant(
        [entry("Anhui/classified-Hunan-2021-x.tif", 10, "ab" * 16)]))
    assert scidb.filter_records(records, scidb.name_contains_any(["Anhui"])) == []


# --------------------------------------------------------------------------
# download and verification
# --------------------------------------------------------------------------

def test_download_writes_and_verifies_a_correct_file(tmp_path):
    record = scidb.parse_distribution(croissant(
        [entry("good.tif", len(BODY), BODY_MD5)]))[0]
    session = FakeSession([FakeResponse(content=BODY, headers=OCTET)])
    out = scidb.download_record(record, tmp_path / "good.tif", session=session)
    assert out.read_bytes() == BODY
    assert scidb.md5_of(out) == BODY_MD5


def test_download_raises_on_a_corrupted_body_and_writes_nothing(tmp_path):
    record = scidb.parse_distribution(croissant(
        [entry("bad.tif", len(BODY), "00" * 16)]))[0]     # published md5 will not match
    session = FakeSession([FakeResponse(content=BODY, headers=OCTET)])
    target = tmp_path / "bad.tif"
    with pytest.raises(scidb.ChecksumMismatch):
        scidb.download_record(record, target, session=session)
    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


def test_download_raises_on_a_truncated_body_and_writes_nothing(tmp_path):
    record = scidb.parse_distribution(croissant(
        [entry("short.tif", len(BODY) + 500, BODY_MD5)]))[0]
    session = FakeSession([FakeResponse(content=BODY, headers=OCTET)])
    target = tmp_path / "short.tif"
    with pytest.raises(scidb.TruncatedDownload) as excinfo:
        scidb.download_record(record, target, session=session)
    assert "partial" in str(excinfo.value).lower()
    assert not target.exists()
    assert list(tmp_path.iterdir()) == []


def test_download_raises_on_an_html_error_page_served_with_status_200(tmp_path):
    record = scidb.parse_distribution(croissant(
        [entry("page.tif", len(BODY), BODY_MD5)]))[0]
    session = FakeSession([FakeResponse(
        content=b"<html><body>error</body></html>",
        headers={"Content-Type": "text/html; charset=utf-8"})])
    target = tmp_path / "page.tif"
    with pytest.raises(scidb.UnexpectedContentType):
        scidb.download_record(record, target, session=session)
    assert not target.exists()


def test_download_skips_when_the_destination_already_matches(tmp_path):
    record = scidb.parse_distribution(croissant(
        [entry("present.tif", len(BODY), BODY_MD5)]))[0]
    target = tmp_path / "present.tif"
    target.write_bytes(BODY)
    session = FakeSession([])                     # any request would raise
    out = scidb.download_record(record, target, session=session)
    assert out == target
    assert session.calls == []


def test_download_refetches_when_the_existing_file_does_not_match(tmp_path):
    record = scidb.parse_distribution(croissant(
        [entry("stale.tif", len(BODY), BODY_MD5)]))[0]
    target = tmp_path / "stale.tif"
    target.write_bytes(b"stale contents")
    session = FakeSession([FakeResponse(content=BODY, headers=OCTET)])
    scidb.download_record(record, target, session=session)
    assert target.read_bytes() == BODY
    assert len(session.calls) == 1


def test_is_already_fetched_is_false_without_a_checksum_or_size(tmp_path):
    """An unverifiable file is not a fetched file."""
    record = scidb.FileRecord("x.tif", None, None, None, "https://example.invalid/x")
    target = tmp_path / "x.tif"
    target.write_bytes(b"anything")
    assert scidb.is_already_fetched(record, target) is False


# --------------------------------------------------------------------------
# planning
# --------------------------------------------------------------------------

def test_plan_splits_present_from_missing(tmp_path):
    records = scidb.parse_distribution(croissant([
        entry("here.tif", len(BODY), BODY_MD5),
        entry("absent.tif", 4096, "cd" * 16),
    ]))
    (tmp_path / "here.tif").write_bytes(BODY)
    report = scidb.plan(records, tmp_path)
    assert [r.stem for r in report["present"]] == ["here.tif"]
    assert [r.stem for r in report["missing"]] == ["absent.tif"]
    assert report["total_bytes"] == len(BODY) + 4096
    assert report["missing_bytes"] == 4096


# --------------------------------------------------------------------------
# DOI resolution
# --------------------------------------------------------------------------

def test_resolve_doi_extracts_the_dataset_id():
    landing = "https://www.scidb.cn/detail?dataSetId=b07f90ea5f0c4e359fa4119a0030f9da"
    session = FakeSession([FakeResponse(url=landing)])
    assert scidb.resolve_doi("10.57760/sciencedb.06963", session=session) == \
        "b07f90ea5f0c4e359fa4119a0030f9da"


def test_resolve_doi_raises_when_the_landing_url_carries_no_id():
    session = FakeSession([FakeResponse(url="https://example.invalid/nope")])
    with pytest.raises(scidb.ScidbError):
        scidb.resolve_doi("10.0/none", session=session)


# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------

def test_shipped_config_declares_a_prefixed_version_and_the_study_provinces():
    """The config is data the fetch layer trusts, so its shape is tested."""
    import yaml
    config_path = Path(__file__).resolve().parents[1] / "config" / "sources.yml"
    config = yaml.safe_load(config_path.read_text(encoding="utf-8"))["scidb_rice"]
    assert scidb.require_versioned(config["version"]) == "V8"
    assert set(config["provinces"]) == {"Anhui", "Zhejiang", "Jiangsu", "Shanghai"}
    assert config["dataset_id"] == "b07f90ea5f0c4e359fa4119a0030f9da"
