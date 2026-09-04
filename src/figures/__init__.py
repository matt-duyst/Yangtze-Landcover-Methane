"""Figures, drawn to the target venues' author guidelines.

Three kinds of module, split by what each knows:

* :mod:`~src.figures.style` knows the venue standard and nothing about data.
* :mod:`~src.figures.output` knows how to write and verify, and nothing about
  content or palette.
* one module per figure knows its own data and returns a figure object.

The split is what makes the standard testable. Because no figure module writes
anything, a figure can be built and asserted on in memory; because `output`
knows nothing about content, its refusal to write an out-of-spec figure can be
tested with a blank one.
"""

from .output import Export, export, figures_root
from .style import PALETTE_SOURCE, categories, figure, panel_label, sequential

__all__ = ["Export", "export", "figures_root", "PALETTE_SOURCE",
           "categories", "figure", "panel_label", "sequential"]
