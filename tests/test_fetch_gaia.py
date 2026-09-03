"""Tests for the GAIA fetch entry point and the manifest helper.

A separate file from tests/test_fetch_figshare.py because what is under test is
different: figshare's tests cover the reusable module, these cover the GAIA
entry point's wiring and the manifest update rules. The figshare module itself
is not re-tested here.

Offline throughout. The archive is a synthetic zip built in ``tmp_path``, HTTP
is a fake, and no test touches the real manifest or the real data directory.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import zipfile
from pathlib import Path

import pytest

from src.fetch import manifest as mf

REPO = Path(__file__).resolve().parents[1]


def load_script(name):
    path = REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_script_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gaia = load_script("fetch_gaia")

TILES = [
    "GAIA_1985_2022_110_30.tif", "GAIA_1985_2022_110_35.tif",
    "GAIA_1985_2022_110_40.tif", "GAIA_1985_2022_115_30.tif",
    "GAIA_1985_2022_115_35.tif", "GAIA_1985_2022_115_40.tif",
    "GAIA_1985_2022_120_30.tif", "GAIA_1985_2022_120_35.tif",
    "GAIA_1985_2022_120_40.tif",
]

#: Tiles the real archive holds that this study does not want.
DECOYS = ["GAIA_1985_2022_95_80.tif", "GAIA_1985_2022_-100_20.tif",
          "GAIA_1985_2022_125_35.tif", "GAIA_1985_2022_110_45.tif"]


class FakeResponse:
    def __init__(self, *, json_body=None, content=b"", headers=None, status=200):
        self._json, self.content = json_body, content
        self.headers, self.status_code = headers or {}, status

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
        self._responses, self.calls = list(responses), []

    def get(self, url, **kwargs):
        self.calls.append((url, kwargs))
        if not self._responses:
            raise AssertionError(f"unexpected extra request to {url}")
        return self._responses.pop(0)


def build_archive(path):
    """A zip shaped like the real one: the nine wanted tiles plus decoys."""
    with zipfile.ZipFile(path, "w") as bundle:
        for name in TILES + DECOYS:
            bundle.writestr(name, f"pixels for {name}".encode())
    return path.read_bytes()


def payload_sha(name):
    return hashlib.sha256(f"pixels for {name}".encode()).hexdigest()


def write_config(path, dest):
    path.write_text(
        "gaia:\n"
        "  product: GAIA test\n"
        "  doi: 10.6084/m9.figshare.27245775.v1\n"
        "  article_id: 27245775\n"
        "  version: 1\n"
        "  licence: CC BY 4.0\n"
        "  api_base: https://api.figshare.invalid/v2\n"
        f"  destination: {dest}\n"
        "  archive: GAIA_1985_2022.zip\n"
        "  tiles:\n" + "".join(f"    - {t}\n" for t in TILES)
    )
    return path


def write_manifest(path, files):
    path.write_text(json.dumps({
        "gaia_1985_2022": {
            "product": "GAIA", "version": "1", "citation": "Gong et al. (2020)",
            "archive": {"name": "GAIA_1985_2022.zip", "bytes": 10, "sha256": None},
            "files": files,
        }
    }, indent=2))
    return path


def article_for(archive_bytes):
    return {"id": 27245775, "license": {"name": "CC BY 4.0"}, "files": [
        {"id": 1, "name": "GAIA_1985_2022.zip", "size": len(archive_bytes),
         "computed_md5": hashlib.md5(archive_bytes).hexdigest(),
         "download_url": "https://ndownloader.figshare.invalid/files/1",
         "mimetype": "application/zip"},
        {"id": 2, "name": "ReadMe-GAIA.txt", "size": 5, "computed_md5": "aa" * 16,
         "download_url": "https://ndownloader.figshare.invalid/files/2",
         "mimetype": "text/plain"},
    ]}


def run(tmp_path, *, manifest_files, extra_args=(), monkeypatch=None):
    dest = tmp_path / "gaia"
    archive_bytes = build_archive(tmp_path / "src.zip")
    config = write_config(tmp_path / "sources.yml", dest)
    manifest = write_manifest(tmp_path / "manifest.json", manifest_files)
    session = FakeSession([
        FakeResponse(json_body=article_for(archive_bytes)),
        FakeResponse(content=archive_bytes,
                     headers={"Content-Type": "application/zip"}),
    ])
    monkeypatch.setattr(gaia.fs.requests, "Session", lambda: session)
    code = gaia.main(["--config", str(config), "--manifest", str(manifest),
                      *extra_args])
    return code, dest, manifest, session


# --------------------------------------------------------------------------
# dry run
# --------------------------------------------------------------------------

def test_dry_run_writes_nothing(tmp_path, monkeypatch, capsys):
    code, dest, manifest, _ = run(
        tmp_path, manifest_files=[], monkeypatch=monkeypatch)
    assert code == 0
    assert not dest.exists()
    before = json.loads(Path(manifest).read_text())
    assert before["gaia_1985_2022"]["archive"]["sha256"] is None
    out = capsys.readouterr().out
    assert "dry run: nothing was downloaded" in out
    assert "NOT internally addressable" in out
    assert "9 members would be extracted" in out


# --------------------------------------------------------------------------
# selection
# --------------------------------------------------------------------------

def test_only_the_nine_configured_tiles_are_extracted(tmp_path, monkeypatch):
    code, dest, _, _ = run(tmp_path, manifest_files=[],
                           extra_args=["--download"], monkeypatch=monkeypatch)
    assert code == 0
    got = sorted(p.name for p in dest.iterdir())
    assert got == sorted(TILES)
    for decoy in DECOYS:
        assert not (dest / decoy).exists()


def test_the_archive_is_deleted_after_extraction(tmp_path, monkeypatch):
    code, dest, _, _ = run(tmp_path, manifest_files=[],
                           extra_args=["--download"], monkeypatch=monkeypatch)
    assert code == 0
    assert not (dest / "GAIA_1985_2022.zip").exists()
    assert not (dest / "_staging").exists()


# --------------------------------------------------------------------------
# manifest
# --------------------------------------------------------------------------

def test_a_null_archive_sha256_is_filled_in(tmp_path, monkeypatch):
    code, _, manifest, _ = run(tmp_path, manifest_files=[],
                               extra_args=["--download"], monkeypatch=monkeypatch)
    assert code == 0
    entry = json.loads(Path(manifest).read_text())["gaia_1985_2022"]
    assert entry["archive"]["sha256"] is not None
    assert len(entry["archive"]["sha256"]) == 64
    assert len(entry["files"]) == 9


def test_matching_tile_digests_are_left_unchanged(tmp_path, monkeypatch, capsys):
    files = [{"path": f"gaia/{t}", "bytes": len(f"pixels for {t}"),
              "sha256": payload_sha(t)} for t in TILES]
    code, _, manifest, _ = run(tmp_path, manifest_files=files,
                               extra_args=["--download"], monkeypatch=monkeypatch)
    assert code == 0
    entry = json.loads(Path(manifest).read_text())["gaia_1985_2022"]
    for record in entry["files"]:
        assert record["sha256"] == payload_sha(record["path"].rsplit("/", 1)[-1])
    assert "9 unchanged" in capsys.readouterr().out


def test_a_disagreeing_tile_digest_stops_the_run_and_writes_nothing(
        tmp_path, monkeypatch, capsys):
    """A changed distribution is a finding, not a routine manifest update."""
    files = [{"path": f"gaia/{t}", "bytes": 99, "sha256": "de" * 32} for t in TILES]
    code, dest, manifest, _ = run(tmp_path, manifest_files=files,
                                  extra_args=["--download"], monkeypatch=monkeypatch)
    assert code == 1
    entry = json.loads(Path(manifest).read_text())["gaia_1985_2022"]
    assert entry["archive"]["sha256"] is None          # not written
    assert all(f["sha256"] == "de" * 32 for f in entry["files"])
    printed = capsys.readouterr().out
    assert "DIFFER from the recorded digests" in printed
    assert "distributed archive has changed" in printed
    # the fetched tiles stay in staging rather than replacing the verified ones
    assert not sorted(p.name for p in dest.iterdir()) == sorted(TILES)


# --------------------------------------------------------------------------
# the manifest helper on its own
# --------------------------------------------------------------------------

def test_check_files_classifies_match_mismatch_new_and_absent():
    entry = {"files": [{"path": "a", "sha256": "aa", "bytes": 1},
                       {"path": "b", "sha256": "bb", "bytes": 1},
                       {"path": "c", "sha256": "cc", "bytes": 1}]}
    comparisons = {c.path: c for c in mf.check_files(
        entry, {"a": (1, "aa"), "b": (1, "ZZ"), "d": (1, "dd")})}
    assert comparisons["a"].status == "match"
    assert comparisons["b"].status == "MISMATCH"
    assert comparisons["c"].status == "absent"
    assert comparisons["d"].status == "new"
    assert [c.path for c in mf.mismatches(comparisons.values())] == ["b"]


def test_fill_archive_digest_never_overwrites_a_populated_field():
    entry = {"archive": {"sha256": None}}
    assert mf.fill_archive_digest(entry, sha256="abc") == "filled"
    assert entry["archive"]["sha256"] == "abc"
    assert mf.fill_archive_digest(entry, sha256="abc") == "unchanged"
    assert mf.fill_archive_digest(entry, sha256="different") == "MISMATCH"
    assert entry["archive"]["sha256"] == "abc"


def test_update_files_fills_nulls_and_leaves_disagreements_alone():
    entry = {"files": [{"path": "a", "sha256": None, "bytes": None},
                       {"path": "b", "sha256": "bb", "bytes": 2}]}
    summary = mf.update_files(entry, {"a": (1, "aa"), "b": (2, "ZZ"), "c": (3, "cc")})
    by_path = {f["path"]: f for f in entry["files"]}
    assert by_path["a"]["sha256"] == "aa"
    assert by_path["b"]["sha256"] == "bb"          # untouched
    assert by_path["c"]["sha256"] == "cc"
    assert summary == {"filled": ["a"], "unchanged": [], "mismatched": ["b"],
                       "added": ["c"]}


def test_shipped_config_lists_the_nine_tiles():
    import yaml
    config = yaml.safe_load(
        (REPO / "config" / "sources.yml").read_text(encoding="utf-8"))["gaia"]
    assert sorted(config["tiles"]) == sorted(TILES)
    assert config["archive"] == "GAIA_1985_2022.zip"
    from src.fetch import figshare as figs
    assert figs.article_id_from_doi(config["doi"]) == (config["article_id"],
                                                       config["version"])
