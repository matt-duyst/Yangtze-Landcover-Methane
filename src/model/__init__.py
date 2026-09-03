"""Baselines the eventual model has to beat.

Nothing here is the model. This package exists so that when a network is
fitted there is already a published number it has to clear, established before
anyone had an interest in where the bar sat.

Three bars, in increasing order of difficulty. A constant predictor says what
the variance of the target is. A per-province constant says how much of that is
just the difference between provinces, which is available for free from a
boundary file. A spatial null predicts each cell from its neighbours, and is the
one that matters: the methane field is spatially autocorrelated by transport, so
a model that only reproduces smoothness has learned nothing about land cover. A
linear model on the two fractions sits between them and answers the question the
study actually asks, which is whether land cover explains the field at all. If
a linear model on impervious and rice fraction does as well as a segmentation
network, the network contributed nothing, and that is the honest finding.
"""

from src.model.baselines import (  # noqa: F401
    BaselineResult,
    ConstantFit,
    GlobalMean,
    LinearFit,
    LinearModel,
    Metrics,
    MissingPredictor,
    NeighbourMean,
    ProvinceMean,
    Table,
    evaluate,
    leave_one_province_out,
    join_column,
    join_covariates,
    load_table,
    r2,
    rmse,
    spatial_blocks,
    weighted_mean,
)

from src.model.association import (  # noqa: F401
    Association,
    Sensitivity,
    correlate,
    paired,
    partial_correlation,
    sensitivity,
)
