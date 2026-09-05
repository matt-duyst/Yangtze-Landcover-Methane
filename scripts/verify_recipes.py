#!/usr/bin/env python
"""Run the documented regeneration recipes and diff against the committed files.

    python scripts/verify_recipes.py                  # every runnable recipe
    python scripts/verify_recipes.py --tier committed # only fresh-clone ones
    python scripts/verify_recipes.py --readme         # print the README table
    python scripts/verify_recipes.py --update-readme  # write it into README.md

Every recipe lives in `config/recipes.yml`, not in prose. Two drifts got into
this repository because the commands were documented only in a README that a
human maintained beside the code: one command could not produce the committed
file at all, and another produced a different one without saying so. Neither
made a test fail.

Nothing here writes into the working tree. Each recipe is redirected to a
temporary directory and the result compared there, so a verification run can
never be the thing that overwrites a committed artefact.
"""

from __future__ import annotations

import argparse
import csv
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
REGISTRY = REPO / "config" / "recipes.yml"
BEGIN = "<!-- BEGIN GENERATED RECIPE TABLE -->"
END = "<!-- END GENERATED RECIPE TABLE -->"


def recipes() -> list[dict]:
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8"))["recipes"]


def readme_table(entries: list[dict] | None = None) -> str:
    """The regeneration table, generated from the registry.

    Generated rather than written, so the README cannot claim a command the
    registry does not hold. A test asserts the committed README contains
    exactly this.
    """
    entries = recipes() if entries is None else entries
    seen, rows = set(), []
    for entry in entries:
        if entry["label"] in seen or entry["verified"] == "unregenerable":
            continue
        seen.add(entry["label"])
        command = (entry["command"] or "").replace("python scripts/", "")
        rows.append(f"| {entry['label']} | `{command}` | {entry['cost']} | "
                    f"{entry['verified'].replace('_', ' ')} |")
    head = ("| result | command | cost | verified |\n|---|---|---|---|")
    return "\n".join([head, *rows])


def missing_inputs(entry: dict) -> list[str]:
    """Inputs the command needs that are not present."""
    wanted = re.findall(r"(?:data|figures|config)/[\w./-]+", entry["command"] or "")
    return [w for w in wanted if not (REPO / w).exists()
            and not w.startswith("data/processed") and not w.startswith("figures")]


def run_one(entry: dict, keep: Path) -> tuple[str, str]:
    """Run one recipe into ``keep`` and compare. Returns (status, detail)."""
    artefact = REPO / entry["artefact"]
    produced = keep / Path(entry["artefact"]).name

    command = entry["command"]
    if command is None:
        return "skipped", "no command; registered as unregenerable"
    if entry["inputs"] == "network":
        return "skipped", "expensive tier; verified on demand"
    absent = missing_inputs(entry)
    if absent:
        return "skipped", f"inputs absent: {', '.join(absent[:2])}"

    argv = command.split()
    argv[0] = sys.executable
    argv = _redirect(argv, entry, keep)
    result = subprocess.run(argv, cwd=REPO, capture_output=True, text=True,
                            env=_env(keep))
    if result.returncode != 0:
        return "FAILED", (result.stderr or result.stdout).strip().splitlines()[-1:][0] \
            if (result.stderr or result.stdout).strip() else "non-zero exit"
    if not produced.exists():
        return "FAILED", f"command produced no {produced.name}"

    if entry["compare"] == "bytes":
        if produced.read_bytes() == artefact.read_bytes():
            return "identical", ""
        return "DIFFERS", _describe(produced, artefact)
    return _subset(produced, artefact)


def _env(keep: Path) -> dict:
    import os
    env = dict(os.environ)
    env["FIGURES_DIR"] = str(keep)
    env["MPLBACKEND"] = "Agg"
    return env


def _redirect(argv: list[str], entry: dict, keep: Path) -> list[str]:
    """Point the command's output at ``keep`` instead of the working tree."""
    name = Path(entry["artefact"]).name
    flags = {"--out", "--out-baselines", "--out-comparison", "--export-csv"}
    out = []
    skip = False
    for i, token in enumerate(argv):
        if skip:
            skip = False
            continue
        if token in flags:
            out += [token, str(keep / Path(argv[i + 1]).name)]
            skip = True
        elif token in {"--export", "--export-covariates", "--export-deseasonalised"}:
            out += [token, str(keep / Path(argv[i + 1]).name)]
            skip = True
        else:
            out.append(token)
    if not any(f in out for f in flags) and entry["artefact"].startswith("data/"):
        # A script that writes more than one artefact has no bare --out, so the
        # registry names the flag rather than the runner guessing it.
        out += [entry.get("out_flag", "--out"), str(keep / name)]
    return out


def _describe(produced: Path, artefact: Path) -> str:
    if produced.suffix != ".csv":
        return f"{produced.stat().st_size:,} B vs {artefact.stat().st_size:,} B"
    a = list(csv.DictReader(produced.open(newline="")))
    b = list(csv.DictReader(artefact.open(newline="")))
    if not a or not b:
        return "one side is empty"
    if set(a[0]) != set(b[0]):
        return f"columns {len(a[0])} vs {len(b[0])}"
    if len(a) != len(b):
        return f"rows {len(a)} vs {len(b)}"
    from collections import Counter
    per = Counter(k for x, y in zip(a, b) for k in x if x[k] != y[k])
    return ", ".join(f"{k}:{n}" for k, n in per.most_common(3))


def _subset(produced: Path, artefact: Path) -> tuple[str, str]:
    """The recipe reproduces some rows exactly and cannot produce the rest."""
    a = list(csv.DictReader(produced.open(newline="")))
    b = list(csv.DictReader(artefact.open(newline="")))
    keys = list(a[0])[:4]
    index = {tuple(r[k] for k in keys): r for r in b}
    shared = [r for r in a if tuple(r[k] for k in keys) in index]
    bad = [r for r in shared
           if any(r[k] != index[tuple(r[k] for k in keys)][k] for k in r)]
    if bad:
        return "DIFFERS", f"{len(bad)} of {len(shared)} shared rows differ"
    return "identical", f"{len(shared)} of {len(b)} rows reproduced exactly"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--tier", choices=("all", "committed", "local"), default="all")
    parser.add_argument("--readme", action="store_true", help="print the table")
    parser.add_argument("--update-readme", action="store_true")
    args = parser.parse_args(argv)

    if args.readme:
        print(readme_table())
        return 0
    if args.update_readme:
        path = REPO / "README.md"
        text = path.read_text(encoding="utf-8")
        block = f"{BEGIN}\n{readme_table()}\n{END}"
        path.write_text(re.sub(f"{re.escape(BEGIN)}.*?{re.escape(END)}", block,
                               text, flags=re.S), encoding="utf-8")
        print(f"  updated the recipe table in {path}")
        return 0

    entries = recipes()
    if args.tier == "committed":
        entries = [e for e in entries if e["inputs"] == "committed"]
    elif args.tier == "local":
        entries = [e for e in entries if e["inputs"] in ("committed", "local")]

    failures = 0
    with tempfile.TemporaryDirectory() as tmp:
        keep = Path(tmp)
        for entry in entries:
            status, detail = run_one(entry, keep)
            failures += status in ("FAILED", "DIFFERS")
            print(f"  {status:<10} {entry['artefact']:<52}{detail}")
    print(f"\n  {failures} recipe(s) failed or drifted")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
