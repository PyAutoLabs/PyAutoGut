"""Pure analysis helpers shared by likelihood-tier hazard cells and checks."""

from __future__ import annotations

import importlib.util
from dataclasses import dataclass, field
from pathlib import Path
from types import ModuleType

import numpy as np


@dataclass(frozen=True)
class LikelihoodProbeRow:
    """One complete-likelihood evaluation and its inversion diagnostics."""

    parameter: float
    parameter_name: str
    backend: str
    figure_of_merit: float
    reconstruction: tuple[float, ...] = ()
    curvature_diagonal: tuple[float, ...] = ()
    regularization_diagonal: tuple[float, ...] = ()
    noise_scale: float = 1.0
    metadata: dict = field(default_factory=dict)


def support_mask(
    values: tuple[float, ...], *, relative_tolerance: float = 1.0e-8
) -> tuple[bool, ...]:
    """Return the numerical NNLS support without baking in an absolute flux scale."""

    array = np.asarray(values, dtype=float)
    if not array.size:
        return ()
    threshold = max(float(np.max(np.abs(array))) * relative_tolerance, np.finfo(float).eps)
    return tuple(bool(value > threshold) for value in array)


def support_transition_locations(rows: list[LikelihoodProbeRow]) -> list[float]:
    """Midpoints where adjacent evaluations change active NNLS support."""

    ordered = sorted(rows, key=lambda row: row.parameter)
    locations: list[float] = []
    for left, right in zip(ordered, ordered[1:]):
        if support_mask(left.reconstruction) != support_mask(right.reconstruction):
            locations.append(0.5 * (left.parameter + right.parameter))
    return locations


def epsilon_neighbourhood_mass(
    centres: list[float], *, epsilon: float, lower: float, upper: float
) -> float:
    """Uniform prior mass of the union of clipped epsilon-neighbourhoods."""

    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    if upper <= lower:
        raise ValueError("upper must be greater than lower")
    intervals = sorted(
        (max(lower, centre - epsilon), min(upper, centre + epsilon))
        for centre in centres
        if lower - epsilon <= centre <= upper + epsilon
    )
    merged: list[list[float]] = []
    for start, end in intervals:
        if end <= start:
            continue
        if not merged or start > merged[-1][1]:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return sum(end - start for start, end in merged) / (upper - lower)


def diagonal_scale(diagonal: tuple[float, ...]) -> float:
    """Robust positive scale for a matrix represented by its diagonal."""

    values = np.abs(np.asarray(diagonal, dtype=float))
    positive = values[np.isfinite(values) & (values > 0.0)]
    return float(np.median(positive)) if positive.size else 0.0


def floor_fraction(floor: float, diagonal: tuple[float, ...]) -> float:
    scale = diagonal_scale(diagonal)
    return float(floor / scale) if scale else float("inf")


def backend_error_curves(
    rows: list[LikelihoodProbeRow], *, reference_backend: str = "numpy"
) -> dict[str, dict[str, list[float]]]:
    """Align backends by parameter and report FoM and reconstruction errors."""

    reference = {
        (row.parameter_name, row.parameter, row.noise_scale): row
        for row in rows
        if row.backend == reference_backend
    }
    curves: dict[str, dict[str, list[float]]] = {}
    for row in rows:
        if row.backend == reference_backend:
            continue
        key = (row.parameter_name, row.parameter, row.noise_scale)
        target = reference.get(key)
        if target is None:
            continue
        fom_scale = max(abs(target.figure_of_merit), 1.0)
        fom_error = abs(row.figure_of_merit - target.figure_of_merit) / fom_scale
        candidate = np.asarray(row.reconstruction, dtype=float)
        expected = np.asarray(target.reconstruction, dtype=float)
        if candidate.shape != expected.shape:
            reconstruction_error = float("inf")
        else:
            reconstruction_error = float(
                np.linalg.norm(candidate - expected) / max(float(np.linalg.norm(expected)), 1.0e-14)
            )
        curve = curves.setdefault(
            row.backend,
            {"parameter": [], "figure_of_merit": [], "reconstruction": []},
        )
        curve["parameter"].append(row.parameter)
        curve["figure_of_merit"].append(float(fom_error))
        curve["reconstruction"].append(reconstruction_error)
    return curves


def orientation_spans(rows: list[LikelihoodProbeRow]) -> dict[float, float]:
    """Figure-of-merit span over orientation at every axis ratio."""

    grouped: dict[float, list[float]] = {}
    for row in rows:
        axis_ratio = float(row.metadata["axis_ratio"])
        grouped.setdefault(axis_ratio, []).append(row.figure_of_merit)
    return {
        axis_ratio: float(max(values) - min(values))
        for axis_ratio, values in sorted(grouped.items())
    }


def _load_cell(path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location("autolens_hazard_pixelization", path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load hazard cell: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def imaging_pixelization_probe(context) -> dict[str, list[LikelihoodProbeRow]]:
    """Load and cache the small imaging cell; four checks share this one run."""

    key = "imaging_pixelization_probe"
    cached = context.cache.get(key)
    if cached is None:
        path = context.repo_root / "scripts" / "imaging" / "hazards" / "pixelization.py"
        cached = _load_cell(path).run_probe(backends=context.backends)
        context.cache[key] = cached
    return cached
