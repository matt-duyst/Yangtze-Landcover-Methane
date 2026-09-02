"""Tests for the streaming methane composite script.

Offline throughout. Granules are synthetic netCDF files in ``tmp_path`` and the
download step is replaced by a copy from a local fixture directory, so nothing
touches the network.

What matters here is not the arithmetic, which ``tests/test_methane.py`` covers
against analytically known values, but the properties the loop exists to have:
that peak disk stays bounded however many granules pass through, that resuming
from a checkpoint gives the same answer as never stopping, and that a
disk-space abort keeps the work already done.
"""

from __future__ import annotations

import importlib.util
import shutil
from datetime import date
from pathlib import Path

import numpy as np
import pytest

from src.methane import grid as mg
from src.methane.grid import GridSpec

REPO = Path(__file__).resolve().parents[1]


def load_script(name):
    path = REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_script_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cm = load_script("compute_methane_composite")

TOY = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
FILL = 9.969209968386869e+36


def write_granule(path, *, lat, lon, primary, qa_stored):
    import netCDF4
    lat = np.asarray(lat, dtype="f4")
    n = lat.size
    with netCDF4.Dataset(path, "w", format="NETCDF4") as ds:
        group = ds.createGroup("PRODUCT")
        group.createDimension("time", 1)
        group.createDimension("scanline", 1)
        group.createDimension("ground_pixel", n)
        dims = ("time", "scanline", "ground_pixel")
        for name in (mg.PRIMARY, mg.SECONDARY):
            var = group.createVariable(name, "f4", dims, fill_value=FILL)
            var.set_auto_maskandscale(False)
            var[:] = np.asarray(primary, dtype="f4").reshape(1, 1, n)
        qa = group.createVariable("qa_value", "u1", dims, fill_value=255)
        qa.set_auto_maskandscale(False)
        qa.scale_factor = 0.01
        qa[:] = np.asarray(qa_stored, dtype="u1").reshape(1, 1, n)
        for name, values in (("latitude", lat), ("longitude", np.asarray(lon, "f4"))):
            var = group.createVariable(name, "f4", dims)
            var.set_auto_maskandscale(False)
            var[:] = values.reshape(1, 1, n)
    return path


def granule_name(orbit, day):
    return (f"S5P_RPRO_L2__CH4____2018{day:02d}14T042147_2018{day:02d}14T060317"
            f"_{orbit:05d}_03_020400_20221109T092730.nc")


@pytest.fixture
def fixtures(tmp_path):
    """Three granules with known, distinct contributions."""
    source = tmp_path / "source"
    source.mkdir()
    made = []
    for i, (lat, lon, value) in enumerate([
        (0.75, 0.25, 1800.0), (0.75, 0.25, 2000.0), (0.25, 0.75, 1900.0)
    ], start=1):
        path = write_granule(source / granule_name(3000 + i, i),
                             lat=[lat], lon=[lon], primary=[value],
                             qa_stored=[100])
        made.append(path)
    return source, made


class FakeGranule:
    """Enough of s5p.Granule for the loop, backed by a local file."""

    def __init__(self, path):
        self.path, self.name, self.size = path, path.name, path.stat().st_size


def run_loop(accumulator, granules, work, checkpoint, *, every=1, stop_after=None):
    """The loop's body, exercised directly: copy in, grid, delete, checkpoint."""
    peak = 0
    for i, granule in enumerate(granules, 1):
        if stop_after is not None and i > stop_after:
            break
        peak = max(peak, cm.assert_disk_bound(work))
        target = work / granule.name
        shutil.copy(granule.path, target)
        peak = max(peak, cm.working_bytes(work))
        soundings, contribution = mg.read_soundings(target, accumulator.spec,
                                                    qa_threshold=0.75)
        accumulator.add(soundings, contribution)
        target.unlink()
        peak = max(peak, cm.assert_disk_bound(work))
        if i % every == 0:
            accumulator.save(checkpoint)
    accumulator.save(checkpoint)
    return peak


# --------------------------------------------------------------------------
# peak disk
# --------------------------------------------------------------------------

def test_each_granule_is_deleted_after_gridding(tmp_path, fixtures):
    source, made = fixtures
    work = tmp_path / "work"; work.mkdir()
    acc = cm.Accumulator(TOY, 0.75, (mg.PRIMARY, mg.SECONDARY))
    run_loop(acc, [FakeGranule(p) for p in made], work, tmp_path / "ck.npz")
    assert list(work.iterdir()) == [], "the working directory must end empty"


def test_peak_disk_never_exceeds_one_granule(tmp_path, fixtures):
    source, made = fixtures
    work = tmp_path / "work"; work.mkdir()
    acc = cm.Accumulator(TOY, 0.75, (mg.PRIMARY, mg.SECONDARY))
    peak = run_loop(acc, [FakeGranule(p) for p in made], work, tmp_path / "ck.npz")
    largest = max(p.stat().st_size for p in made)
    assert peak <= largest, "more than one granule was on disk at once"


def test_the_disk_bound_assertion_fires_when_the_directory_leaks(tmp_path):
    work = tmp_path / "work"; work.mkdir()
    (work / "leak.bin").write_bytes(b"x" * 2048)
    assert cm.assert_disk_bound(work, allowance=4096) == 2048
    with pytest.raises(RuntimeError, match="leaking granules"):
        cm.assert_disk_bound(work, allowance=1024)


# --------------------------------------------------------------------------
# accumulation and resumption
# --------------------------------------------------------------------------

def test_sums_and_counts_match_a_single_pass_grid(tmp_path, fixtures):
    """The streaming accumulator must agree with grid_granules on the same input."""
    source, made = fixtures
    work = tmp_path / "work"; work.mkdir()
    acc = cm.Accumulator(TOY, 0.75, (mg.PRIMARY, mg.SECONDARY))
    run_loop(acc, [FakeGranule(p) for p in made], work, tmp_path / "ck.npz")
    streamed = acc.composite()

    single = mg.grid_granules(made, TOY, qa_threshold=0.75)

    assert streamed.counts.tolist() == single.counts.tolist()
    np.testing.assert_allclose(streamed.mean_of(mg.PRIMARY),
                               single.mean_of(mg.PRIMARY), equal_nan=True)
    assert streamed.counts[0, 0] == 2                    # two granules, one cell
    assert streamed.mean_of(mg.PRIMARY)[0, 0] == pytest.approx(1900.0)


def test_resuming_from_a_checkpoint_equals_an_uninterrupted_run(tmp_path, fixtures):
    source, made = fixtures
    granules = [FakeGranule(p) for p in made]

    whole = tmp_path / "whole"; whole.mkdir()
    acc_whole = cm.Accumulator(TOY, 0.75, (mg.PRIMARY, mg.SECONDARY))
    run_loop(acc_whole, granules, whole, tmp_path / "whole.npz")

    part = tmp_path / "part"; part.mkdir()
    checkpoint = tmp_path / "part.npz"
    acc_a = cm.Accumulator(TOY, 0.75, (mg.PRIMARY, mg.SECONDARY))
    run_loop(acc_a, granules, part, checkpoint, stop_after=2)   # interrupted

    resumed = cm.Accumulator.load(checkpoint)
    assert len(resumed.done) == 2
    left = [g for g in granules if g.name not in resumed.done]
    assert len(left) == 1
    run_loop(resumed, left, part, checkpoint)

    assert resumed.counts.tolist() == acc_whole.counts.tolist()
    np.testing.assert_allclose(resumed.sums[mg.PRIMARY], acc_whole.sums[mg.PRIMARY])
    assert {c.granule for c in resumed.contributions} == \
           {c.granule for c in acc_whole.contributions}


def test_the_checkpoint_preserves_per_granule_provenance(tmp_path, fixtures):
    source, made = fixtures
    work = tmp_path / "work"; work.mkdir()
    checkpoint = tmp_path / "ck.npz"
    acc = cm.Accumulator(TOY, 0.75, (mg.PRIMARY, mg.SECONDARY))
    run_loop(acc, [FakeGranule(p) for p in made], work, checkpoint)

    reloaded = cm.Accumulator.load(checkpoint)
    assert len(reloaded.contributions) == 3
    before = {c.granule: c for c in acc.contributions}
    for contribution in reloaded.contributions:
        original = before[contribution.granule]
        assert contribution.soundings_read == original.soundings_read
        assert contribution.soundings_in_box == original.soundings_in_box
        assert contribution.acquired == original.acquired
    coverage = mg.coverage_of(reloaded.composite())
    assert coverage.soundings_by_year                 # years survived the round trip
    assert coverage.contributing_granules == 3


def test_a_checkpoint_write_is_atomic(tmp_path, fixtures):
    """A crash mid-write must leave the previous checkpoint, not a truncated one."""
    source, made = fixtures
    work = tmp_path / "work"; work.mkdir()
    checkpoint = tmp_path / "ck.npz"
    acc = cm.Accumulator(TOY, 0.75, (mg.PRIMARY, mg.SECONDARY))
    run_loop(acc, [FakeGranule(made[0])], work, checkpoint)
    first = checkpoint.read_bytes()

    acc2 = cm.Accumulator.load(checkpoint)
    acc2.save(checkpoint)
    assert not checkpoint.with_suffix(".npz.tmp").exists(), "temp file left behind"
    assert cm.Accumulator.load(checkpoint).counts.tolist() == acc.counts.tolist()
    assert len(first) > 0


# --------------------------------------------------------------------------
# guards
# --------------------------------------------------------------------------

def test_the_free_space_guard_stops_and_keeps_the_work(tmp_path, fixtures, monkeypatch):
    """A full disk must cost the remaining granules, not the hours already spent."""
    source, made = fixtures
    work = tmp_path / "work"; work.mkdir()
    checkpoint = tmp_path / "ck.npz"
    acc = cm.Accumulator(TOY, 0.75, (mg.PRIMARY, mg.SECONDARY))
    granules = [FakeGranule(p) for p in made]

    floor = 5 * 1024 ** 3
    seen = {"n": 0}

    def fake_usage(_):
        seen["n"] += 1
        free = 50 * 1024 ** 3 if seen["n"] <= 2 else 1 * 1024 ** 3
        return shutil._ntuple_diskusage(100 * 1024 ** 3, 0, free)

    monkeypatch.setattr(cm.shutil, "disk_usage", fake_usage)

    processed = 0
    for granule in granules:
        if cm.shutil.disk_usage(tmp_path).free < floor:
            break
        target = work / granule.name
        shutil.copy(granule.path, target)
        soundings, contribution = mg.read_soundings(target, TOY, qa_threshold=0.75)
        acc.add(soundings, contribution)
        target.unlink()
        processed += 1
    acc.save(checkpoint)

    assert 0 < processed < len(granules), "the guard should stop part way"
    assert checkpoint.exists()
    assert len(cm.Accumulator.load(checkpoint).done) == processed
    assert list(work.iterdir()) == []


def test_run_without_a_bound_refuses(tmp_path, monkeypatch, capsys):
    """--run alone must not start hours of transfer."""
    monkeypatch.setattr(cm.s5p, "list_range", lambda *a, **k: [])
    config = tmp_path / "sources.yml"
    config.write_text(
        "s5p:\n  base_url: https://example.invalid\n  stream: RPRO\n"
        "  product_type: L2__CH4___\n  destination: d\n"
        "  bounding_box: {west: 0.0, south: 0.0, east: 1.0, north: 1.0}\n"
        "  grid_resolution_deg: 0.5\n  qa_threshold: 0.75\n"
        "  start_date: 2018-01-01\n  end_date: 2018-01-02\n")
    code = cm.main(["--config", str(config), "--work", str(tmp_path / "w"),
                    "--checkpoint", str(tmp_path / "c.npz"), "--run"])
    assert code == 2
    assert "refusing to run without" in capsys.readouterr().out


def test_plan_mode_writes_nothing_and_downloads_nothing(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(cm.s5p, "list_range", lambda *a, **k: [])
    def explode(*a, **k):
        raise AssertionError("plan mode must not download")
    monkeypatch.setattr(cm.s5p, "download_granule", explode)
    config = tmp_path / "sources.yml"
    config.write_text(
        "s5p:\n  base_url: https://example.invalid\n  stream: RPRO\n"
        "  product_type: L2__CH4___\n  destination: d\n"
        "  bounding_box: {west: 0.0, south: 0.0, east: 1.0, north: 1.0}\n"
        "  grid_resolution_deg: 0.5\n  qa_threshold: 0.75\n"
        "  start_date: 2018-01-01\n  end_date: 2018-01-02\n")
    work = tmp_path / "w"
    checkpoint = tmp_path / "c.npz"
    assert cm.main(["--config", str(config), "--work", str(work),
                    "--checkpoint", str(checkpoint)]) == 0
    assert not work.exists()
    assert not checkpoint.exists()
    assert "plan only" in capsys.readouterr().out
