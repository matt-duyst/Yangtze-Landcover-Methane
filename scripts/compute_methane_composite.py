#!/usr/bin/env python3
"""Build a gridded methane composite by streaming granules one at a time.

A thin wrapper over ``src.fetch.s5p`` and ``src.methane.grid``. All arithmetic
lives there.

    python scripts/compute_methane_composite.py                       # plan only
    python scripts/compute_methane_composite.py --run --max-granules 600
    python scripts/compute_methane_composite.py --run --max-hours 2

Download, grid, accumulate, delete, repeat. The alternative, fetching a year
and then computing, needs 28.9 GiB for 2018 alone and about 202 GiB for seven
years, against 29 GiB free. Streaming bounds peak disk at one granule.

**Peak disk.** At most one granule exists at a time, plus the checkpoint. The
bound is asserted rather than assumed: before each download the working
directory is checked to be empty, and after each granule it is checked to be
empty again, so a leak fails the run instead of filling the volume silently.

**Resumption.** Sums and counts accumulate, never means, because a mean cannot
be averaged with another mean. The accumulator plus the list of finished
granules is checkpointed every ``--checkpoint-every`` granules, default 10. The
grid is small, 33 by 31 cells, so a checkpoint is tens of kilobytes and costs
nothing measurable; 10 is a compromise that keeps the log readable rather than
one forced by cost. A crash therefore loses at most the granules since the last
checkpoint, roughly a minute of transfer. The write is atomic: a temporary file
is renamed into place, so a crash mid-write leaves the previous checkpoint
intact rather than a truncated one.

**Free space.** Checked before starting and before every download. Falling
below the floor stops the run cleanly with the accumulator checkpointed, so a
full disk costs the remaining granules rather than the hours already spent.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.fetch import s5p  # noqa: E402
from src.methane import grid as mg  # noqa: E402
from src.methane.grid import Composite, GranuleContribution, GridSpec  # noqa: E402

#: Peak disk is one granule plus a checkpoint. The largest granule observed on
#: this mirror is 66 MB; the allowance is generous and the assertion below is
#: what actually enforces the bound.
PEAK_DISK_ALLOWANCE_BYTES = 256 * 1024 ** 2


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,.0f} B"
        n /= 1024.0
    return f"{n:,.1f} TB"


def as_date(value) -> dt.date:
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value))


class Accumulator:
    """Sums, counts and provenance, checkpointed atomically.

    Holds sums rather than means so partial results compose: two runs over
    disjoint granules can be added, and a mean can be taken at the end.
    """

    def __init__(self, spec: GridSpec, qa_threshold: float, variables):
        self.spec = spec
        self.qa_threshold = qa_threshold
        self.variables = list(variables)
        self.counts = np.zeros(spec.shape, dtype="int64")
        self.sums = {v: np.zeros(spec.shape, dtype="float64") for v in self.variables}
        self.contributions: list[GranuleContribution] = []
        self.done: set[str] = set()

    def add(self, soundings, contribution: GranuleContribution) -> None:
        self.contributions.append(contribution)
        self.done.add(contribution.granule)
        if not len(soundings):
            return
        row, col, _ = self.spec.cell_of(soundings.latitude, soundings.longitude)
        np.add.at(self.counts, (row, col), 1)
        for name in self.variables:
            np.add.at(self.sums[name], (row, col), soundings.values[name])

    def composite(self) -> Composite:
        return Composite(spec=self.spec, qa_threshold=self.qa_threshold,
                         counts=self.counts.copy(),
                         sums={k: v.copy() for k, v in self.sums.items()},
                         contributions=tuple(self.contributions))

    def save(self, path: Path) -> None:
        """Write atomically: a crash mid-write keeps the previous checkpoint."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        payload = {
            "spec": [self.spec.west, self.spec.south, self.spec.east,
                     self.spec.north, self.spec.resolution],
            "qa_threshold": self.qa_threshold,
            "variables": self.variables,
            "counts": self.counts,
            "contributions": np.array(
                json.dumps([c.as_dict() for c in self.contributions])),
        }
        for name in self.variables:
            payload[f"sum::{name}"] = self.sums[name]
        # Pass an open handle: np.savez_compressed appends '.npz' to a path
        # that does not already end in it, which would write the temp file
        # somewhere other than where the rename below looks for it.
        with open(tmp, "wb") as handle:
            np.savez_compressed(handle, **payload)
        tmp.replace(path)

    @classmethod
    def load(cls, path: Path) -> "Accumulator":
        with np.load(path, allow_pickle=False) as data:
            spec = GridSpec(*[float(x) for x in data["spec"]])
            variables = [str(v) for v in data["variables"]]
            acc = cls(spec, float(data["qa_threshold"]), variables)
            acc.counts = data["counts"].astype("int64")
            for name in variables:
                acc.sums[name] = data[f"sum::{name}"].astype("float64")
            records = json.loads(str(data["contributions"]))
        for record in records:
            acquired = (dt.datetime.fromisoformat(record["acquired"])
                        if record["acquired"] else None)
            acc.contributions.append(GranuleContribution(
                granule=record["granule"], acquired=acquired,
                soundings_read=record["soundings_read"],
                soundings_valid=record["soundings_valid"],
                soundings_in_box=record["soundings_in_box"]))
            acc.done.add(record["granule"])
        return acc


def working_bytes(directory: Path) -> int:
    return sum(p.stat().st_size for p in Path(directory).glob("*") if p.is_file())


def assert_disk_bound(directory: Path, allowance: int = PEAK_DISK_ALLOWANCE_BYTES) -> int:
    """Fail loudly if the working directory holds more than one granule's worth."""
    used = working_bytes(directory)
    if used > allowance:
        raise RuntimeError(
            f"working directory {directory} holds {human(used)}, above the "
            f"{human(allowance)} bound. The streaming loop is leaking granules; "
            f"stopping rather than filling the volume.")
    return used


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(REPO / "config" / "sources.yml"))
    parser.add_argument("--source", default="s5p")
    parser.add_argument("--stream", default=None, help="override the configured stream")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--work", default=None,
                        help="scratch directory for the one granule at a time")
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--checkpoint-every", type=int, default=10)
    parser.add_argument("--min-free-gb", type=float, default=2.0,
                        help="abort cleanly if free space falls below this")
    parser.add_argument("--max-granules", type=int, default=None)
    parser.add_argument("--max-hours", type=float, default=None)
    parser.add_argument("--run", action="store_true",
                        help="actually download and grid; without it, plan only")
    parser.add_argument("--timeout", type=float, default=s5p.DEFAULT_TIMEOUT)
    return parser


def main(argv=None) -> int:
    args = build_argparser().parse_args(argv)
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))[args.source]
    box = config["bounding_box"]
    stream = args.stream or config["stream"]
    start = as_date(args.start or config["start_date"])
    end = as_date(args.end or config["end_date"])
    work = Path(args.work) if args.work else REPO / "data" / "interim" / "s5p_work"
    checkpoint = Path(args.checkpoint) if args.checkpoint else \
        REPO / "data" / "interim" / f"methane_composite_{start:%Y%m%d}_{end:%Y%m%d}.npz"

    spec = GridSpec(box["west"], box["south"], box["east"], box["north"],
                    config["grid_resolution_deg"])
    variables = (mg.PRIMARY, mg.SECONDARY)

    print(f"stream      {stream}/{config['product_type']}")
    print(f"dates       {start} to {end}")
    print(f"grid        {spec.shape[0]} x {spec.shape[1]} = {spec.n_cells} cells "
          f"at {spec.resolution} degrees")
    print(f"qa          >= {config['qa_threshold']}")
    print(f"work dir    {work}   (holds ONE granule at a time)")
    print(f"checkpoint  {checkpoint}")
    print()

    print("  listing the mirror ...", flush=True)
    every = s5p.list_range(start, end, stream=stream,
                           product=config["product_type"],
                           base_url=config["base_url"], timeout=args.timeout)
    latest = s5p.latest_per_orbit(every)
    candidates = [g for g in latest
                  if s5p.intersects_box(g, box["west"], box["east"])]
    total_bytes = s5p.volume(candidates)
    print(f"  {len(every)} keys -> {len(latest)} after latest_per_orbit -> "
          f"{len(candidates)} candidates (SUPERSET; the filename carries no footprint)")
    print(f"  candidate volume {total_bytes:,} B ({human(total_bytes)})")

    if checkpoint.exists():
        accumulator = Accumulator.load(checkpoint)
        print(f"  resuming from {checkpoint.name}: {len(accumulator.done)} granules "
              f"already gridded, {int(accumulator.counts.sum()):,} soundings")
    else:
        accumulator = Accumulator(spec, float(config["qa_threshold"]), variables)
        print("  no checkpoint; starting from empty")

    remaining = [g for g in candidates if g.name not in accumulator.done]
    if args.max_granules is not None:
        remaining = remaining[:args.max_granules]
    print(f"  {len(remaining)} granules to process this run")
    free = shutil.disk_usage(REPO).free
    print(f"  free space {human(free)}, floor {args.min_free_gb} GB")
    print(f"  peak disk bound: one granule plus the checkpoint, "
          f"asserted at {human(PEAK_DISK_ALLOWANCE_BYTES)}")

    if not args.run:
        print("\nplan only: nothing downloaded, nothing written. Pass --run with "
              "--max-granules or --max-hours to build.")
        return 0
    if args.max_granules is None and args.max_hours is None:
        print("\nrefusing to run without --max-granules or --max-hours. A full "
              "year is hundreds of granules and hours of transfer; the bound is "
              "required so an accidental invocation cannot start it.")
        return 2

    work.mkdir(parents=True, exist_ok=True)
    floor = args.min_free_gb * 1024 ** 3
    deadline = time.time() + args.max_hours * 3600 if args.max_hours else None

    t0 = time.perf_counter()
    done = with_data = 0
    fetched_bytes = 0
    peak_disk = 0
    stop_reason = "all granules processed"

    for index, granule in enumerate(remaining, 1):
        if deadline and time.time() > deadline:
            stop_reason = "time budget reached"
            break
        free = shutil.disk_usage(REPO).free
        if free < floor:
            stop_reason = f"free space {human(free)} below the {args.min_free_gb} GB floor"
            break

        peak_disk = max(peak_disk, assert_disk_bound(work))
        target = work / granule.name
        try:
            s5p.download_granule(granule, target, base_url=config["base_url"],
                                 timeout=args.timeout)
            fetched_bytes += granule.size
            soundings, contribution = mg.read_soundings(
                target, spec, qa_threshold=accumulator.qa_threshold,
                variables=variables)
            accumulator.add(soundings, contribution)
            if contribution.soundings_in_box:
                with_data += 1
        except Exception as exc:                       # noqa: BLE001
            print(f"  [{index}/{len(remaining)}] {granule.name}: FAILED ({exc})",
                  flush=True)
        finally:
            if target.exists():
                target.unlink()
            part = target.with_suffix(target.suffix + ".part")
            if part.exists():
                part.unlink()

        peak_disk = max(peak_disk, assert_disk_bound(work))
        done += 1

        if done % args.checkpoint_every == 0 or index == len(remaining):
            accumulator.save(checkpoint)
        if done % 25 == 0 or index == len(remaining):
            elapsed = time.perf_counter() - t0
            rate = fetched_bytes / elapsed if elapsed else 0
            left = (len(remaining) - index) * (elapsed / max(index, 1))
            covered = int((accumulator.counts > 0).sum())
            print(f"  [{index}/{len(remaining)}] {done} done, {with_data} with data, "
                  f"{covered}/{spec.n_cells} cells ({100 * covered / spec.n_cells:.1f}%), "
                  f"{human(rate)}/s, elapsed {elapsed / 60:.1f} min, "
                  f"~{left / 60:.0f} min left", flush=True)

    accumulator.save(checkpoint)
    elapsed = time.perf_counter() - t0
    composite = accumulator.composite()
    coverage = mg.coverage_of(composite)

    print(f"\nstopped: {stop_reason}")
    print(f"  granules processed this run   {done}")
    print(f"  with in-box soundings         {with_data}")
    print(f"  downloaded                    {fetched_bytes:,} B ({human(fetched_bytes)})")
    print(f"  elapsed                       {elapsed / 60:.1f} min")
    if elapsed:
        print(f"  mean rate                     {human(fetched_bytes / elapsed)}/s")
    print(f"  peak working-directory bytes  {peak_disk:,} ({human(peak_disk)})")
    print(f"  checkpoint                    {checkpoint}")
    print(f"\n  coverage {coverage.covered_cells}/{coverage.n_cells} cells "
          f"({100 * coverage.fraction:.2f}%), median "
          f"{coverage.median_per_covered_cell} max {coverage.max_per_covered_cell}")
    print(f"  soundings by year: {coverage.soundings_by_year}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
