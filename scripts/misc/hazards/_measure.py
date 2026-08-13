"""Typed numerical-hazard measurements.

There is deliberately no universal ``is_risky`` predicate.  Finite-volume
regions, measure-zero sites, construction-only paths, and continuous backend
errors require different measurements and must remain distinguishable in the
stored record.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field
from statistics import NormalDist

import numpy as np

RISK_BASES = {
    "prior_mass",
    "epsilon_neighbourhood",
    "reachability",
    "error_curve",
}


@dataclass(frozen=True)
class Measurement:
    """One typed measurement attached to a finding."""

    basis: str
    value: float | None
    unit: str
    details: dict = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.basis not in RISK_BASES:
            raise ValueError(f"unknown risk basis: {self.basis}")

    def to_dict(self) -> dict:
        return asdict(self)


def wilson_interval(
    successes: int, sample_count: int, confidence: float = 0.95
) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion."""

    if sample_count <= 0:
        raise ValueError("sample_count must be positive")
    if not 0 <= successes <= sample_count:
        raise ValueError("successes must be between zero and sample_count")
    if not 0.0 < confidence < 1.0:
        raise ValueError("confidence must be between zero and one")

    z = NormalDist().inv_cdf(0.5 + confidence / 2.0)
    n = float(sample_count)
    p = successes / n
    denominator = 1.0 + z * z / n
    centre = (p + z * z / (2.0 * n)) / denominator
    half_width = z * math.sqrt(p * (1.0 - p) / n + z * z / (4.0 * n * n))
    half_width /= denominator
    return max(0.0, centre - half_width), min(1.0, centre + half_width)


def prior_mass_measurement(
    mask: np.ndarray,
    *,
    sample_count: int,
    seed: int,
    prior: dict,
    confidence: float = 0.95,
) -> Measurement:
    """Measure finite prior mass from a boolean Monte Carlo result."""

    mask = np.asarray(mask, dtype=bool).reshape(-1)
    if mask.size != sample_count:
        raise ValueError("mask size does not match sample_count")
    successes = int(mask.sum())
    estimate = successes / sample_count
    low, high = wilson_interval(successes, sample_count, confidence)
    return Measurement(
        basis="prior_mass",
        value=estimate,
        unit="fraction",
        details={
            "successes": successes,
            "sample_count": sample_count,
            "seed": seed,
            "confidence": confidence,
            "confidence_interval": [low, high],
            "prior": prior,
        },
    )


def epsilon_neighbourhood_measurement(
    *,
    epsilon: float,
    mass: float,
    domain: dict,
    centre: list[float] | tuple[float, ...],
) -> Measurement:
    """Record the mass of an explicit epsilon-ball around a measure-zero site."""

    if epsilon <= 0.0:
        raise ValueError("epsilon must be positive")
    if not 0.0 <= mass <= 1.0:
        raise ValueError("mass must be between zero and one")
    return Measurement(
        basis="epsilon_neighbourhood",
        value=mass,
        unit="fraction",
        details={
            "epsilon": epsilon,
            "centre": list(centre),
            "domain": domain,
        },
    )


def reachability_measurement(
    *, reachable_via: list[str], blocked_paths: dict[str, str] | None = None
) -> Measurement:
    """Record which construction/evaluation paths reach a site."""

    return Measurement(
        basis="reachability",
        value=1.0 if reachable_via else 0.0,
        unit="boolean",
        details={
            "reachable_via": sorted(set(reachable_via)),
            "blocked_paths": blocked_paths or {},
        },
    )


def error_curve_measurement(
    parameter: np.ndarray,
    reference: np.ndarray,
    candidate: np.ndarray,
    *,
    parameter_name: str,
    floor: float = 1.0e-14,
) -> Measurement:
    """Relative-error curve for two implementations of the same quantity."""

    parameter = np.asarray(parameter, dtype=float).reshape(-1)
    reference = np.asarray(reference, dtype=float)
    candidate = np.asarray(candidate, dtype=float)
    if reference.shape != candidate.shape or reference.shape[0] != parameter.size:
        raise ValueError("parameter/reference/candidate shapes do not align")

    difference = candidate - reference
    if reference.ndim == 1:
        denominator = np.maximum(np.abs(reference), floor)
        relative = np.abs(difference) / denominator
    else:
        axes = tuple(range(1, reference.ndim))
        denominator = np.maximum(np.linalg.norm(reference, axis=axes), floor)
        relative = np.linalg.norm(difference, axis=axes) / denominator

    return Measurement(
        basis="error_curve",
        value=float(np.max(relative)),
        unit="relative_error",
        details={
            "parameter_name": parameter_name,
            "parameter": parameter.tolist(),
            "relative_error": relative.tolist(),
            "maximum_parameter": float(parameter[int(np.argmax(relative))]),
        },
    )
