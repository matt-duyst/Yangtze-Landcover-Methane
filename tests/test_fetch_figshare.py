"""Tests for the figshare fetch module.

Offline throughout: the HTTP layer is a fake defined here, archives are built
with ``zipfile`` inside ``tmp_path``, and no test makes a network call.

The cases that matter are the ones that would let a bad file reach disk: a
digest that does not match, a body shorter than declared, an error page served
with HTTP 200, and an archive member whose name would escape the destination.
"""

from __future__ import annotations

import hashlib
import io
import zipfile
from pathlib import Path

import pytest

from src.fetch import figshare as fs


# --------------------------------------------------------------------------
# fakes
# --------------------------------------------------------------------------

class FakeResponse:
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
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if not self._responses:
            raise AssertionError(f"unexpected extra request to {url}")
        return self._responses.pop(0)


BODY = b"a fake netCDF payload" * 32
BODY_MD5 = hashlib.md5(BODY).hexdigest()
OCTET = {"Content-Type": "application/octet-stream"}


def article(files):
    return {"id": 27965832, "title": "GloRice(I)", "version": 2,
            "license": {"name": "CC BY 4.0"}, "files": list(files)}


def file_entry(name, size, md5, url="https://ndownloader.figshare.invalid/files/1"):
    return {"id": 1, "name": name, "size": size,
            "computed_md5": md5, "supplied_md5": md5,
            "download_url": url, "mimetype": "application/zip"}


def make_zip(path, members):
    with zipfile.ZipFile(path, "w") as bundle:
        for name, payload in members.items():
            bundle.writestr(name, payload)
    return path


# --------------------------------------------------------------------------
# DOI parsing
# --------------------------------------------------------------------------

def test_article_id_and_version_parse_from_the_doi_without_a_request():
    assert fs.article_id_from_doi("10.6084/m9.figshare.27965832.v2") == (27965832, 2)


def test_article_id_parses_without_a_version_suffix():
    assert fs.article_id_from_doi("10.6084/m9.figshare.27965832") == (27965832, None)


def test_a_non_figshare_doi_raises():
    with pytest.raises(fs.FigshareError):
        fs.article_id_from_doi("10.57760/sciencedb.06963")


def test_resolve_doi_reads_the_article_id_from_the_landing_url():
    landing = "https://figshare.com/articles/dataset/GloRice/27965832/2"
    session = FakeSession([FakeResponse(url=landing)])
    assert fs.resolve_doi("10.6084/m9.figshare.27965832.v2", session=session) == 27965832


def test_resolve_doi_raises_when_the_landing_url_carries_no_id():
    session = FakeSession([FakeResponse(url="https://example.invalid/none")])
    with pytest.raises(fs.FigshareError):
        fs.resolve_doi("10.0/none", session=session)


# --------------------------------------------------------------------------
# metadata
# --------------------------------------------------------------------------

def test_fetch_article_requests_the_versioned_endpoint():
    session = FakeSession([FakeResponse(json_body=article([]))])
    fs.fetch_article(27965832, version=2, session=session)
    url, _ = session.calls[0]
    assert url.endswith("/articles/27965832/versions/2")


def test_fetch_article_without_a_version_requests_the_latest():
    session = FakeSession([FakeResponse(json_body=article([]))])
    fs.fetch_article(27965832, session=session)
    url, _ = session.calls[0]
    assert url.endswith("/articles/27965832")


def test_parse_files_reads_name_size_md5_and_url():
    doc = article([file_entry("GloRice-phsc-Ex.zip", 148845107, "ab" * 16)])
    records = fs.parse_files(doc)
    assert len(records) == 1
    record = records[0]
    assert record.name == "GloRice-phsc-Ex.zip"
    assert record.content_size == 148845107
    assert record.digest == "ab" * 16
    assert record.md5 == "ab" * 16
    assert record.digest_algorithm == "md5"


def test_parse_files_prefers_the_computed_digest():
    entry = file_entry("x.zip", 10, "aa" * 16)
    entry["supplied_md5"] = "bb" * 16
    assert fs.parse_files(article([entry]))[0].digest == "aa" * 16


def test_an_article_with_no_files_raises():
    with pytest.raises(fs.NoFilesError):
        fs.parse_files(article([]))


def test_licence_is_read_from_the_record():
    assert fs.licence_of(article([])) == "CC BY 4.0"


# --------------------------------------------------------------------------
# download and verification
# --------------------------------------------------------------------------

def test_download_writes_and_verifies_a_correct_file(tmp_path):
    record = fs.parse_files(article([file_entry("good.zip", len(BODY), BODY_MD5)]))[0]
    session = FakeSession([FakeResponse(content=BODY, headers=OCTET)])
    out = fs.download_record(record, tmp_path / "good.zip", session=session)
    assert out.read_bytes() == BODY


def test_download_raises_on_a_bad_digest_and_writes_nothing(tmp_path):
    record = fs.parse_files(article([file_entry("bad.zip", len(BODY), "00" * 16)]))[0]
    session = FakeSession([FakeResponse(content=BODY, headers=OCTET)])
    with pytest.raises(fs.ChecksumMismatch):
        fs.download_record(record, tmp_path / "bad.zip", session=session)
    assert list(tmp_path.iterdir()) == []


def test_download_raises_on_a_truncated_body_and_writes_nothing(tmp_path):
    record = fs.parse_files(article([file_entry("short.zip", len(BODY) + 99, BODY_MD5)]))[0]
    session = FakeSession([FakeResponse(content=BODY, headers=OCTET)])
    with pytest.raises(fs.TruncatedDownload):
        fs.download_record(record, tmp_path / "short.zip", session=session)
    assert list(tmp_path.iterdir()) == []


def test_download_raises_on_an_html_error_page_served_with_status_200(tmp_path):
    record = fs.parse_files(article([file_entry("page.zip", len(BODY), BODY_MD5)]))[0]
    session = FakeSession([FakeResponse(content=b"<html>no</html>",
                                        headers={"Content-Type": "text/html"})])
    with pytest.raises(fs.UnexpectedContentType):
        fs.download_record(record, tmp_path / "page.zip", session=session)
    assert list(tmp_path.iterdir()) == []


def test_download_skips_when_the_destination_already_matches(tmp_path):
    record = fs.parse_files(article([file_entry("present.zip", len(BODY), BODY_MD5)]))[0]
    target = tmp_path / "present.zip"
    target.write_bytes(BODY)
    session = FakeSession([])              # any request would raise
    assert fs.download_record(record, target, session=session) == target
    assert session.calls == []


# --------------------------------------------------------------------------
# selective extraction
# --------------------------------------------------------------------------

def zip_of_years(path, years):
    return make_zip(path, {
        f"GloRice-phsc-Ex/exten_phsc_{year}.nc": f"payload {year}".encode()
        for year in years
    })


def test_extract_members_takes_only_the_selected_years(tmp_path):
    archive = zip_of_years(tmp_path / "g.zip", range(1961, 1972))
    out = tmp_path / "out"
    taken = fs.extract_members(archive, out, fs.year_selector([1963, 1969]))
    assert sorted(m.member.rsplit("/", 1)[-1] for m in taken) == [
        "exten_phsc_1963.nc", "exten_phsc_1969.nc"]
    assert sorted(p.name for p in out.iterdir()) == [
        "exten_phsc_1963.nc", "exten_phsc_1969.nc"]


def test_extract_members_reports_bytes_and_sha256(tmp_path):
    archive = zip_of_years(tmp_path / "g.zip", [2000])
    taken = fs.extract_members(archive, tmp_path / "out", fs.year_selector([2000]))
    member = taken[0]
    payload = b"payload 2000"
    assert member.bytes == len(payload)
    assert member.sha256 == hashlib.sha256(payload).hexdigest()
    assert member.archive == "g.zip"
    assert "sha256" in member.as_dict()


def test_extract_members_raises_when_nothing_matches(tmp_path):
    archive = zip_of_years(tmp_path / "g.zip", [2000, 2001])
    with pytest.raises(fs.MemberNotFound):
        fs.extract_members(archive, tmp_path / "out", fs.year_selector([1999]))


def test_extract_members_does_not_rewrite_an_existing_member(tmp_path):
    archive = zip_of_years(tmp_path / "g.zip", [2000])
    out = tmp_path / "out"
    fs.extract_members(archive, out, fs.year_selector([2000]))
    target = out / "exten_phsc_2000.nc"
    target.write_bytes(b"already here and different")
    taken = fs.extract_members(archive, out, fs.year_selector([2000]))
    assert target.read_bytes() == b"already here and different"
    assert taken[0].bytes == len(b"already here and different")


def test_extract_members_refuses_a_path_that_escapes_the_destination(tmp_path):
    archive = tmp_path / "evil.zip"
    with zipfile.ZipFile(archive, "w") as bundle:
        bundle.writestr("../escaped_2000.nc", b"x")
    out = tmp_path / "out"
    taken = fs.extract_members(archive, out, fs.year_selector([2000]))
    # Path(name).name strips the traversal, so the file lands inside out/
    assert taken[0].path.parent.resolve() == out.resolve()
    assert not (tmp_path / "escaped_2000.nc").exists()


def test_year_selector_needs_at_least_one_year():
    with pytest.raises(ValueError):
        fs.year_selector([])


# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------

def test_shipped_config_matches_the_published_record():
    import yaml
    path = Path(__file__).resolve().parents[1] / "config" / "sources.yml"
    config = yaml.safe_load(path.read_text(encoding="utf-8"))["glorice"]
    assert fs.article_id_from_doi(config["doi"]) == (config["article_id"],
                                                     config["version"])
    assert config["years"] == [2000, 2010, 2017, 2018, 2019, 2020, 2021]
    assert "Xie" in config["citation"]
