"""Coverage saturation and monthly yield for the 2018 composite.

The figure exists to make one argument visible: **coverage is a union
statistic, so it saturates, and a number measured from a small sample of
granules describes the sample rather than the year.** The reconnaissance put
2018 coverage far below what the full year turned out to be, and no amount of
care in choosing granules would have fixed it, because the shortfall is a
property of the statistic and not of the sample.

The second panel carries the other half of the sampling caution. Soundings do
not arrive evenly through the year. They arrive when the sky is clear, which in
the Yangtze Delta means not during the monsoon, which is also when the rice is
flooded. Any annual mean over these cells is therefore weighted away from
exactly the season the study is about.

Structure follows the package convention: :func:`from_checkpoint` reads, and
:func:`coverage_figure` draws from an in-memory record and returns a figure
without writing. The two are separate so the drawing can be tested on
constructed data with no checkpoint present, and so the figure is never a side
effect of loading.

**Months with no record are drawn as absent, not as zero.** The 2018 stream
begins on 30 April, so January through March have no granules at all, which is
a different fact from a month in which the instrument looked and saw nothing. A
zero-height bar is indistinguishable from a missing bar, so absence is marked
by a shaded span with its own legend key. The same distinction will be needed
for the 96 cells the composite never covered.
"""

from __future__ import annotations

import datetime as dt
import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import style

#: Cells in the 0.25 degree analysis grid, 33 rows by 31 columns.
GRID_CELLS = 1023

#: The reconnaissance sample size, marked on the saturation curve.
RECONNAISSANCE_GRANULES = 36

MONTH_INITIALS = "JFMAMJJASOND"


@dataclass(frozen=True)
class MonthlyYield:
    """One month's contribution, or its absence.

    `acquired` and `granules` are deliberately separate. A month in which the
    satellite passed overhead and returned nothing usable is not the same fact
    as a month it never sampled, and only the second is an absence. The 2018
    record happens to contain no month of the first kind, so the distinction
    costs nothing here and is kept because the next year processed may differ.
    """

    month: int
    soundings: int
    granules: int
    acquired: int

    @property
    def observed(self) -> bool:
        """Whether any granule was acquired this month, productive or not."""
        return self.acquired > 0

    @property
    def per_granule(self) -> float:
        return self.soundings / self.granules if self.granules else float("nan")


@dataclass(frozen=True)
class CoverageRecord:
    """Everything the figure needs, with no file handle attached."""

    cumulative_cells: np.ndarray
    monthly: tuple[MonthlyYield, ...]
    total_cells: int = GRID_CELLS

    @property
    def granules_processed(self) -> int:
        return int(self.cumulative_cells.size)

    @property
    def productive_granules(self) -> int:
        return sum(m.granules for m in self.monthly)

    @property
    def granules_acquired(self) -> int:
        return sum(m.acquired for m in self.monthly)

    @property
    def total_soundings(self) -> int:
        return sum(m.soundings for m in self.monthly)

    def fraction_at(self, granule: int) -> float:
        """Covered fraction after ``granule`` granules, one-based."""
        return float(self.cumulative_cells[granule - 1]) / self.total_cells

    @property
    def final_fraction(self) -> float:
        return self.fraction_at(self.granules_processed)


def from_checkpoint(path: Path | str, total_cells: int = GRID_CELLS) -> CoverageRecord:
    """Read the saturation curve and the monthly aggregation from a checkpoint.

    The monthly numbers are derived here from the per-granule `contributions`
    record rather than stored separately, so they cannot disagree with the
    granule-level history they come from.
    """
    with np.load(path, allow_pickle=False) as data:
        saturation = np.asarray(data["saturation"])
        contributions = json.loads(str(data["contributions"]))

    cumulative = saturation[:, 1].astype(np.int64)

    # soundings, productive granules, granules acquired
    tally: dict[int, list[int]] = defaultdict(lambda: [0, 0, 0])
    for record in contributions:
        month = dt.datetime.fromisoformat(record["acquired"]).month
        tally[month][2] += 1
        soundings = int(record["soundings_in_box"])
        if soundings <= 0:
            continue  # acquired, but it intersected nothing in the box
        tally[month][0] += soundings
        tally[month][1] += 1

    monthly = tuple(
        MonthlyYield(month=m, soundings=tally[m][0], granules=tally[m][1],
                     acquired=tally[m][2])
        for m in range(1, 13))

    return CoverageRecord(cumulative_cells=cumulative, monthly=monthly,
                          total_cells=total_cells)


def coverage_figure(record: CoverageRecord):
    """Build and return the two-part coverage figure. Writes nothing."""
    colours = style.categories(4)
    curve_colour, soundings_colour, granule_colour = colours[0], colours[1], colours[2]
    absent_colour = "0.88"

    fig = style.figure(width_cm=style.DOUBLE_COLUMN_CM, height_cm=8.2)
    grid = fig.add_gridspec(
        2, 2, width_ratios=(1.0, 1.06), height_ratios=(1.0, 0.78),
        wspace=0.30, hspace=0.20, left=0.075, right=0.985, top=0.90, bottom=0.12)

    ax_sat = fig.add_subplot(grid[:, 0])
    ax_snd = fig.add_subplot(grid[0, 1])
    ax_gran = fig.add_subplot(grid[1, 1], sharex=ax_snd)

    _draw_saturation(ax_sat, record, curve_colour)
    _draw_monthly(ax_snd, ax_gran, record, soundings_colour, granule_colour,
                  absent_colour)

    style.panel_label(ax_sat, "a", dx=-0.11)
    style.panel_label(ax_snd, "b", dx=-0.13)
    style.panel_label(ax_gran, "c", dx=-0.13)
    return fig


def _draw_saturation(ax, record: CoverageRecord, colour) -> None:
    n = record.granules_processed
    x = np.arange(1, n + 1)
    y = 100.0 * record.cumulative_cells / record.total_cells

    ax.plot(x, y, color=colour, linewidth=1.4, solid_joinstyle="round",
            label="cumulative coverage")

    recon = min(RECONNAISSANCE_GRANULES, n)
    recon_y = 100.0 * record.fraction_at(recon)
    final_y = 100.0 * record.final_fraction

    ax.plot([recon], [recon_y], marker="o", markersize=4.5, color=colour,
            markerfacecolor="white", markeredgewidth=1.2, linestyle="none",
            label=f"{recon} granules, {recon_y:.1f} %", zorder=5)
    ax.plot([n], [final_y], marker="s", markersize=4.5, color=colour,
            linestyle="none",
            label=f"{n} granules, {final_y:.1f} %", zorder=5)

    ax.set_xlim(0, n * 1.02)
    ax.set_ylim(0, 100)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("Granules processed (count)")
    ax.set_ylabel(f"Grid cells covered (% of {record.total_cells})")
    ax.legend(loc="lower right", handlelength=1.4, borderpad=0.4, labelcolor="black")


def _draw_monthly(ax_snd, ax_gran, record: CoverageRecord, snd_colour,
                  gran_colour, absent_colour) -> None:
    """Two stacked axes sharing one month axis.

    Stacked rather than twin axes. Twin axes put two scales on one frame, and a
    reader has to be told which curve belongs to which side before the panel
    can be read at all; worse, the relative height of the two series then
    depends on limits chosen by whoever drew it. Stacking costs vertical space
    and buys an unambiguous comparison, since both series share the month axis
    by construction and neither can be made to look larger than the other.
    """
    months = np.arange(1, 13)
    observed = np.array([m.observed for m in record.monthly])
    soundings = np.array([m.soundings for m in record.monthly], dtype=float)
    granules = np.array([m.granules for m in record.monthly], dtype=float)

    absent = months[~observed]
    for ax in (ax_snd, ax_gran):
        if absent.size:
            ax.axvspan(absent.min() - 0.5, absent.max() + 0.5,
                       color=absent_colour, linewidth=0, zorder=0)

    ax_snd.bar(months[observed], soundings[observed] / 1000.0, width=0.68,
               color=snd_colour, linewidth=0, label="soundings")
    ax_gran.bar(months[observed], granules[observed], width=0.68,
                color=gran_colour, linewidth=0, label="productive granules")

    # April is a single granule and its bar is a fraction of a millimetre.
    # Left unlabelled it reads as absent, which is the one thing this panel
    # must not let happen, so the count is written next to it.
    first = record.monthly[int(np.argmax(observed))]
    ax_snd.annotate(f"{first.soundings:,}", xy=(first.month, first.soundings / 1000.0),
                    xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=style.TICK_SIZE - 0.5)

    ax_snd.set_ylabel("Soundings in box\n(thousands)")
    ax_gran.set_ylabel("Productive granules\n(count)")
    ax_gran.set_xlabel("Month (2018)")

    ax_snd.tick_params(labelbottom=False)
    ax_gran.set_xticks(months)
    ax_gran.set_xticklabels(list(MONTH_INITIALS))
    ax_gran.set_xlim(0.4, 12.6)

    # The shaded span is labelled in place rather than through a legend. A
    # legend key for it would be a grey swatch sitting on the grey span, which
    # is invisible by construction; text on the thing it describes is not.
    if absent.size:
        ax_snd.text(float(absent.mean()), 0.5, "no granules\nacquired",
                    transform=ax_snd.get_xaxis_transform(),
                    ha="center", va="center", color="black",
                    fontsize=style.TICK_SIZE)
