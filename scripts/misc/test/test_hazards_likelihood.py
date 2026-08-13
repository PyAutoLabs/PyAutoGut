"""Pure likelihood-tier analysis tests; no PyAuto/JAX imports required."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest


def _profiling_root() -> Path:
    for path in Path(__file__).resolve().parents:
        if (path / "ruff.toml").is_file():
            return path
    raise RuntimeError("autolens_profiling root (ruff.toml) not found")


_misc = _profiling_root() / "scripts" / "misc"
if str(_misc) not in sys.path:
    sys.path.insert(0, str(_misc))

from hazards._likelihood import (  # noqa: E402
    LikelihoodProbeRow,
    backend_error_curves,
    epsilon_neighbourhood_mass,
    floor_fraction,
    orientation_spans,
    support_transition_locations,
)


def _row(parameter, reconstruction, *, backend="numpy", figure_of_merit=-10.0, **metadata):
    return LikelihoodProbeRow(
        parameter=parameter,
        parameter_name="einstein_radius",
        backend=backend,
        figure_of_merit=figure_of_merit,
        reconstruction=tuple(reconstruction),
        metadata=metadata,
    )


def test_active_support_transitions_are_midpoints_not_exact_prior_mass():
    rows = [
        _row(0.0, (1.0, 0.0)),
        _row(1.0, (0.8, 0.2)),
        _row(2.0, (0.0, 1.0)),
    ]
    assert support_transition_locations(rows) == [0.5, 1.5]
    assert epsilon_neighbourhood_mass(
        [0.5, 1.5], epsilon=0.25, lower=0.0, upper=2.0
    ) == pytest.approx(0.5)


def test_epsilon_neighbourhood_mass_merges_overlap_and_clips_edges():
    assert epsilon_neighbourhood_mass(
        [0.0, 0.1, 1.0], epsilon=0.2, lower=0.0, upper=1.0
    ) == pytest.approx(0.5)


def test_backend_curves_align_parameters_and_report_both_outputs():
    rows = [
        _row(1.0, (1.0, 2.0), figure_of_merit=-10.0),
        _row(1.0, (1.1, 1.9), backend="jax", figure_of_merit=-9.0),
    ]
    curve = backend_error_curves(rows)["jax"]
    assert curve["parameter"] == [1.0]
    assert curve["figure_of_merit"] == pytest.approx([0.1])
    assert curve["reconstruction"][0] > 0.0


def test_conditioning_and_structural_helpers_use_physical_scales():
    assert floor_fraction(1.0e-3, (1.0, 2.0, 3.0)) == pytest.approx(5.0e-4)
    rows = [
        LikelihoodProbeRow(0.7, "axis_ratio", "numpy", -5.0, metadata={"axis_ratio": 0.7}),
        LikelihoodProbeRow(0.7, "axis_ratio", "numpy", -2.0, metadata={"axis_ratio": 0.7}),
        LikelihoodProbeRow(1.0, "axis_ratio", "numpy", -3.0, metadata={"axis_ratio": 1.0}),
        LikelihoodProbeRow(1.0, "axis_ratio", "numpy", -3.0, metadata={"axis_ratio": 1.0}),
    ]
    assert orientation_spans(rows) == {0.7: 3.0, 1.0: 0.0}
