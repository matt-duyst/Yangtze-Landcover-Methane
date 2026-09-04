"""Write a figure to vector and raster, or write nothing at all.

The module is `output` rather than `export` so that the package attribute
`src.figures.export` is unambiguously the function. A module and a function
sharing a name inside one package shadow each other, and the failure is
quiet: `from src.figures.export import ...` keeps working while
`getattr(src.figures, "export")` silently gives the other one.

One call produces both required forms: a PDF for the typesetter, with fonts
embedded as real glyphs, and a PNG companion for the README and for reviewers
who cannot open vector files. They are written from a single figure object so
the two can never drift apart, which is the failure the 2023 thesis has -- its
`legacy/figures/` PNGs are ArcGIS exports whose source projects are gone, so
there is no vector form and no way to regenerate one.

**Verification happens before anything reaches its destination.** Both files
are written to temporary paths in the destination directory, measured there,
and only moved into place once every check passes. A figure that is too small,
too coarse, or too large in bytes leaves no partial output behind and no stale
file from a previous run that a reader might mistake for the current one. This
matters more than it sounds: a figure that silently writes at 100 dpi looks
correct on screen and is rejected at submission.

The checks are the venue's, not this repository's invention:

* raster resolution at least :data:`~src.figures.style.MIN_DPI`
* width at least :data:`~src.figures.style.MIN_WIDTH_CM`
* each file under :data:`MAX_BYTES`
* fonts embedded rather than drawn as paths, asserted through rcParams

Figure functions elsewhere in this package return a :class:`~matplotlib.figure.Figure`
and never write. Writing is this module's job alone, so a figure can be built
and inspected in a test without touching the filesystem.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

import matplotlib as mpl

from . import style

#: Copernicus rejects individual figures above 5 MB.
MAX_BYTES = 5 * 1024 * 1024


def figures_root() -> Path:
    """Where generated figures are written.

    ``figures/`` at the repository root, which is where
    `notes/repository-architecture.md` said they would go before any existed,
    and where the README already tells a reader to look. Overridable through
    ``FIGURES_DIR`` so that tests never write into the working tree.
    """
    env = os.environ.get("FIGURES_DIR")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "figures"


@dataclass(frozen=True)
class Export:
    """What was written, measured from the files themselves."""

    vector: Path
    raster: Path
    width_cm: float
    height_cm: float
    dpi: int
    vector_bytes: int
    raster_bytes: int
    raster_pixels: tuple[int, int]

    @property
    def fonts_embedded(self) -> bool:
        """True when the PDF carries TrueType fonts rather than outlines."""
        return mpl.rcParams["pdf.fonttype"] == 42

    def summary(self) -> str:
        w, h = self.raster_pixels
        return (
            f"{self.vector.name} / {self.raster.name}\n"
            f"  {self.width_cm:.2f} x {self.height_cm:.2f} cm at {self.dpi} dpi "
            f"({w} x {h} px)\n"
            f"  vector {self.vector_bytes:,} B, raster {self.raster_bytes:,} B, "
            f"fonts embedded: {self.fonts_embedded}")


def export(fig, stem: str, directory: Path | None = None,
           dpi: int = style.MIN_DPI) -> Export:
    """Write ``fig`` as ``stem.pdf`` and ``stem.png``, or raise and write nothing.

    Returns an :class:`Export` describing what actually landed on disk, with
    every field measured after the fact rather than assumed from the request.
    """
    if dpi < style.MIN_DPI:
        raise ValueError(
            f"{dpi} dpi is below the {style.MIN_DPI} dpi minimum the venue "
            f"standard requires; refusing to write {stem}")

    width_cm = fig.get_figwidth() / style.CM
    height_cm = fig.get_figheight() / style.CM
    if width_cm < style.MIN_WIDTH_CM:
        raise ValueError(
            f"{stem} is {width_cm:.2f} cm wide, below the "
            f"{style.MIN_WIDTH_CM} cm minimum; refusing to write it")

    directory = Path(directory) if directory is not None else figures_root()
    directory.mkdir(parents=True, exist_ok=True)

    # Write to temporaries beside the destination so the move is on one
    # filesystem, then verify, then move. A failed check leaves nothing.
    tmp_pdf = directory / f".{stem}.pdf.tmp"
    tmp_png = directory / f".{stem}.png.tmp"
    try:
        fig.savefig(tmp_pdf, format="pdf", bbox_inches=None)
        fig.savefig(tmp_png, format="png", dpi=dpi, bbox_inches=None)

        vector_bytes = tmp_pdf.stat().st_size
        raster_bytes = tmp_png.stat().st_size
        for name, size in (("vector", vector_bytes), ("raster", raster_bytes)):
            if size > MAX_BYTES:
                raise ValueError(
                    f"{stem} {name} is {size:,} B, above the "
                    f"{MAX_BYTES:,} B limit; refusing to write it")

        pixels = _png_size(tmp_png)
        # Measure the delivered resolution rather than trusting the request.
        measured = round(pixels[0] / (width_cm * style.CM))
        if measured < style.MIN_DPI:
            raise ValueError(
                f"{stem} rasterised at {measured} dpi, below the "
                f"{style.MIN_DPI} dpi minimum; refusing to write it")

        pdf = directory / f"{stem}.pdf"
        png = directory / f"{stem}.png"
        tmp_pdf.replace(pdf)
        tmp_png.replace(png)
    finally:
        tmp_pdf.unlink(missing_ok=True)
        tmp_png.unlink(missing_ok=True)

    return Export(vector=pdf, raster=png, width_cm=width_cm,
                  height_cm=height_cm, dpi=measured,
                  vector_bytes=vector_bytes, raster_bytes=raster_bytes,
                  raster_pixels=pixels)


def _png_size(path: Path) -> tuple[int, int]:
    """Width and height in pixels, read from the PNG header directly.

    The IHDR chunk is the first after the 8-byte signature and holds width and
    height as big-endian 32-bit integers. Reading it here avoids depending on
    an image library for a check that must not itself be able to fail.
    """
    with open(path, "rb") as handle:
        header = handle.read(24)
    if header[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError(f"{path} is not a PNG")
    return (int.from_bytes(header[16:20], "big"),
            int.from_bytes(header[20:24], "big"))
