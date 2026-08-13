"""Detect flat regions created by saturating reparametrisations."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np

from hazards._anchor import maybe_anchor_from_pattern
from hazards._measure import (
    epsilon_neighbourhood_measurement,
    prior_mass_measurement,
    reachability_measurement,
)
from hazards._reachability import probe_path
from hazards._record import Finding
from hazards.checks._base import HazardCheck, ScanContext


@dataclass(frozen=True)
class Plateau:
    start: float
    end: float
    value: float
    samples: int


def detect_plateaus(
    parameter: np.ndarray, values: np.ndarray, *, atol: float = 1.0e-12
) -> list[Plateau]:
    """Find contiguous, repeated output values without knowing clamp thresholds."""

    parameter = np.asarray(parameter, dtype=float)
    values = np.asarray(values, dtype=float)
    if parameter.ndim != 1 or parameter.shape != values.shape:
        raise ValueError("parameter and values must be aligned 1D arrays")
    plateaus: list[Plateau] = []
    start = 0
    for index in range(1, len(values) + 1):
        still_flat = index < len(values) and np.isclose(
            values[index], values[index - 1], rtol=0.0, atol=atol
        )
        if still_flat:
            continue
        count = index - start
        if count >= 2:
            plateaus.append(
                Plateau(
                    start=float(parameter[start]),
                    end=float(parameter[index - 1]),
                    value=float(values[start]),
                    samples=count,
                )
            )
        start = index
    return plateaus


def _truncated_normal_pairs(sample_count: int, sigma: float, seed: int) -> np.ndarray:
    from scipy.special import ndtr, ndtri

    rng = np.random.default_rng(seed)
    low = ndtr(-1.0 / sigma)
    high = ndtr(1.0 / sigma)
    return sigma * ndtri(rng.uniform(low, high, size=(sample_count, 2)))


def _prior_measurements(sample_count: int, seed: int):
    measurements = []
    for sigma in (0.3, 0.5):
        samples = _truncated_normal_pairs(sample_count, sigma, seed)
        measurements.append(
            prior_mass_measurement(
                np.sum(samples * samples, axis=1) >= 1.0,
                sample_count=sample_count,
                seed=seed,
                prior={
                    "type": "independent_truncated_gaussian",
                    "mean": 0.0,
                    "sigma": sigma,
                    "lower": -1.0,
                    "upper": 1.0,
                    "dimensions": 2,
                },
            )
        )

    rng = np.random.default_rng(seed)
    samples = rng.uniform(-1.0, 1.0, size=(sample_count, 2))
    measurements.append(
        prior_mass_measurement(
            np.sum(samples * samples, axis=1) >= 1.0,
            sample_count=sample_count,
            seed=seed,
            prior={
                "type": "independent_uniform",
                "lower": -1.0,
                "upper": 1.0,
                "dimensions": 2,
            },
        )
    )
    return measurements


class SaturationCheck(HazardCheck):
    name = "saturation"
    subject = "component"

    def run(self, context: ScanContext) -> list[Finding]:
        from autogalaxy import convert
        from autogalaxy.profiles.mass.total.isothermal import Isothermal
        from autogalaxy.profiles.mass.total.power_law import PowerLaw

        convert_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoGalaxy",
            path="autogalaxy/convert.py",
            pattern="fac = xp.sqrt(ell_comps[1] ** 2 + ell_comps[0] ** 2)",
            after=6,
            symbol="autogalaxy.convert.axis_ratio_and_angle_from",
        )
        guard_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoGalaxy",
            path="autogalaxy/profiles/validate.py",
            pattern="magnitude_squared >= 1.0",
            before=4,
            after=2,
            symbol="autogalaxy.profiles.validate.validate_ell_comps",
        )
        isothermal_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoGalaxy",
            path="autogalaxy/profiles/mass/total/isothermal.py",
            pattern="return xp.minimum(axis_ratio, 0.99999)",
            before=2,
            symbol="autogalaxy.profiles.mass.total.isothermal.Isothermal.axis_ratio",
        )

        high_factors = np.asarray((0.998, 0.999, 0.9995, 0.9999, 1.0, 1.2))
        high_curve: dict[str, list[float]] = {}
        if "numpy" in context.backends:
            high_curve["numpy"] = [
                float(convert.axis_ratio_from((factor, 0.0), xp=np)) for factor in high_factors
            ]
        if "jax" in context.backends:
            import jax.numpy as jnp

            high_curve["jax"] = [
                float(convert.axis_ratio_from((jnp.asarray(factor), jnp.asarray(0.0)), xp=jnp))
                for factor in high_factors
            ]
        representative_high_curve = next(iter(high_curve.values()))
        high_plateaus = detect_plateaus(high_factors, representative_high_curve)
        high_plateau = max(
            high_plateaus,
            key=lambda plateau: plateau.end,
            default=Plateau(0.0, 0.0, float(representative_high_curve[-1]), 0),
        )

        probes = []
        backend_reachability: dict[str, dict] = {}
        reachable_via: list[str] = []
        blocked_by = []
        if "numpy" in context.backends:
            inner = probe_path(
                "numpy_construction_inner_annulus",
                lambda: PowerLaw(ell_comps=(0.9995, 0.0)).axis_ratio(xp=np),
            )
            outside = probe_path(
                "numpy_construction_beyond_unit_circle",
                lambda: PowerLaw(ell_comps=(1.2, 0.0)).axis_ratio(xp=np),
                blocked_by="validate_ell_comps",
            )
            probes.extend((inner, outside))
            if inner.reachable:
                reachable_via.append(inner.path)
            if not outside.reachable:
                if guard_anchor is not None:
                    blocked_by.append(guard_anchor)
            backend_reachability["numpy"] = {
                "0.999 <= magnitude < 1": "reachable",
                "magnitude >= 1": "blocked_by_validate_ell_comps",
                "probes": [inner.to_dict(), outside.to_dict()],
            }
        if "jax" in context.backends:
            import jax
            import jax.numpy as jnp

            construction = probe_path(
                "jax_construction_beyond_unit_circle",
                lambda: PowerLaw(ell_comps=(jnp.asarray(1.2), jnp.asarray(0.0))).axis_ratio(xp=jnp),
            )
            tracing = probe_path(
                "jax_trace_beyond_unit_circle",
                lambda: jax.jit(
                    lambda factor: PowerLaw(ell_comps=(factor, jnp.asarray(0.0))).axis_ratio(xp=jnp)
                )(jnp.asarray(1.2)),
            )
            probes.extend((construction, tracing))
            reachable_via.extend(probe.path for probe in (construction, tracing) if probe.reachable)
            backend_reachability["jax"] = {
                "magnitude >= 0.999": "reachable",
                "probes": [construction.to_dict(), tracing.to_dict()],
            }

        prior_measurements = _prior_measurements(context.sample_count, context.seed)
        prior_measurements.append(
            reachability_measurement(
                reachable_via=reachable_via,
                blocked_paths={
                    "numpy:magnitude>=1": "validate_ell_comps"
                    if "numpy" in context.backends
                    else "not_probed"
                },
            )
        )
        ell_comps_finding = Finding(
            finding_id="component.ell_comps.magnitude-saturation",
            title="ell_comps magnitude saturates at 0.999",
            summary=(
                "The conversion maps every magnitude at or above 0.999 to q="
                f"{high_plateau.value:.15g}. NumPy reaches the thin valid annulus below "
                "one but its constructor guard blocks the beyond-unit region; JAX arrays "
                "and tracers bypass that concrete-scalar guard."
            ),
            hazard_class="saturation",
            tier=1,
            subject="component",
            subject_name="ell_comps",
            backends=tuple(context.backends),
            measurements=tuple(prior_measurements),
            anchors=tuple(
                anchor for anchor in (convert_anchor, guard_anchor) if anchor is not None
            ),
            code_exists=True,
            reachable_via=tuple(sorted(set(reachable_via))),
            blocked_by=tuple(dict.fromkeys(blocked_by)),
            affects_science=True,
            backend_reachability=backend_reachability,
            reproducer={
                "parameter": "ell_comps_magnitude",
                "parameter_values": high_factors.tolist(),
                "axis_ratio": high_curve,
                "detected_plateau": asdict(high_plateau),
                "probes": [probe.to_dict() for probe in probes],
            },
        )

        low_factors = np.asarray((0.0, 1.0e-7, 1.0e-6, 4.0e-6, 5.0e-6, 5.1e-6, 1.0e-5))
        low_curve: dict[str, list[float]] = {}
        if "numpy" in context.backends:
            low_curve["numpy"] = [
                float(Isothermal(ell_comps=(factor, 0.0)).axis_ratio(xp=np))
                for factor in low_factors
            ]
        if "jax" in context.backends:
            import jax.numpy as jnp

            low_curve["jax"] = [
                float(
                    Isothermal(ell_comps=(jnp.asarray(factor), jnp.asarray(0.0))).axis_ratio(xp=jnp)
                )
                for factor in low_factors
            ]
        representative_low_curve = next(iter(low_curve.values()))
        low_plateaus = detect_plateaus(low_factors, representative_low_curve)
        low_plateau = min(
            low_plateaus,
            key=lambda plateau: plateau.start,
            default=Plateau(0.0, 0.0, float(representative_low_curve[0]), 0),
        )
        epsilon = (1.0 - low_plateau.value) / (1.0 + low_plateau.value)
        sigma = 0.3
        truncation_probability_1d = math.erf(1.0 / (sigma * math.sqrt(2.0)))
        epsilon_mass = -math.expm1(-(epsilon**2) / (2.0 * sigma**2))
        epsilon_mass /= truncation_probability_1d**2
        floor_measurement = epsilon_neighbourhood_measurement(
            epsilon=epsilon,
            mass=epsilon_mass,
            centre=(0.0, 0.0),
            domain={
                "type": "independent_truncated_gaussian",
                "sigma": sigma,
                "lower": -1.0,
                "upper": 1.0,
                "dimensions": 2,
            },
        )
        floor_reachability = [
            f"{backend}_construction_near_spherical" for backend in context.backends
        ]
        floor_finding = Finding(
            finding_id="component.isothermal.near-spherical-saturation",
            title="Isothermal caps near-spherical axis ratios at 0.99999",
            summary=(
                "A second, load-bearing saturation prevents the q=1 divisions in the "
                "elliptical Isothermal deflection from becoming 0/0. Its affected "
                "ell_comps disk is too small for prior-sampling discovery."
            ),
            hazard_class="saturation",
            tier=1,
            subject="component",
            subject_name="isothermal",
            backends=tuple(context.backends),
            measurements=(
                floor_measurement,
                reachability_measurement(reachable_via=floor_reachability),
            ),
            anchors=tuple(anchor for anchor in (isothermal_anchor,) if anchor is not None),
            code_exists=True,
            reachable_via=tuple(floor_reachability),
            blocked_by=(),
            affects_science=True,
            backend_reachability={
                backend: {"magnitude <= epsilon": "reachable"} for backend in context.backends
            },
            reproducer={
                "parameter": "ell_comps_magnitude",
                "parameter_values": low_factors.tolist(),
                "axis_ratio": low_curve,
                "detected_plateau": asdict(low_plateau),
                "derived_epsilon": epsilon,
            },
        )
        findings = []
        if high_plateaus:
            findings.append(ell_comps_finding)
        if low_plateaus:
            findings.append(floor_finding)
        return findings
