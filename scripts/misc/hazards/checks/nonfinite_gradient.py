"""Detect finite values with non-finite derivatives at measure-zero sites."""

from __future__ import annotations

import math

import numpy as np

from hazards._anchor import maybe_anchor_from_pattern
from hazards._measure import (
    epsilon_neighbourhood_measurement,
    reachability_measurement,
)
from hazards._record import Finding
from hazards.checks._base import HazardCheck, ScanContext


class NonFiniteGradientCheck(HazardCheck):
    name = "nonfinite_gradient"
    subject = "component"

    def run(self, context: ScanContext) -> list[Finding]:
        import autoarray as aa
        from autogalaxy.profiles.geometry_profiles import SphProfile

        anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoGalaxy",
            path="autogalaxy/profiles/geometry_profiles.py",
            pattern="return xp.sqrt(xp.add(xp.square(grid.array[:, 0])",
            after=1,
            symbol="autogalaxy.profiles.geometry_profiles.SphProfile.radial_grid_from",
        )

        profile = SphProfile()
        numpy_value = float(
            profile.radial_grid_from(
                grid=aa.Grid2DIrregular(values=np.asarray([[0.0, 0.0]])), xp=np
            ).array[0]
        )
        radii = np.asarray((0.0, 1.0e-12, 1.0e-10, 1.0e-8, 1.0e-6, 1.0e-4))
        gradient_norm: list[float | None] = [None] * len(radii)
        jax_value = None
        jax_gradient = None
        hazard_persists = True  # A NumPy-only run cannot adjudicate an AD hazard.
        reachable_via = ["grid_alignment"]
        backend_reachability = {"numpy": {"value_at_r=0": "finite"}}
        if "jax" in context.backends:
            import jax
            import jax.numpy as jnp

            def radial(coordinate):
                grid = aa.Grid2DIrregular(values=coordinate.reshape(1, 2))
                return jnp.sum(SphProfile().radial_grid_from(grid=grid, xp=jnp).array)

            coordinate = jnp.asarray([0.0, 0.0])
            jax_value = float(radial(coordinate))
            jax_gradient_array = np.asarray(jax.grad(radial)(coordinate), dtype=float)
            jax_gradient = [
                float(value) if np.isfinite(value) else None for value in jax_gradient_array
            ]
            hazard_persists = not np.all(np.isfinite(jax_gradient_array))
            for index, radius in enumerate(radii):
                gradient = np.asarray(jax.grad(radial)(jnp.asarray([radius, 0.0])), dtype=float)
                norm = float(np.linalg.norm(gradient))
                gradient_norm[index] = norm if np.isfinite(norm) else None
            reachable_via.append("jax_autodiff")
            backend_reachability["jax"] = {
                "value_at_r=0": "finite",
                "gradient_at_r=0": "non_finite",
            }

        epsilon = 1.0e-6
        epsilon_mass = math.pi * epsilon**2 / 4.0
        measurement = epsilon_neighbourhood_measurement(
            epsilon=epsilon,
            mass=epsilon_mass,
            centre=(0.0, 0.0),
            domain={
                "type": "uniform_coordinate_window",
                "lower": [-1.0, -1.0],
                "upper": [1.0, 1.0],
                "dimensions": 2,
                "note": "coordinate measure, not a model-parameter prior",
            },
        )
        if not hazard_persists:
            return []
        return [
            Finding(
                finding_id="component.spherical-geometry.radial-sqrt-gradient-at-zero",
                title="Radial sqrt has a non-finite gradient at r=0",
                summary=(
                    "The spherical radial coordinate returns the correct finite value zero "
                    "at the profile centre, but JAX differentiation of sqrt(y^2+x^2) "
                    "returns a non-finite gradient there."
                ),
                hazard_class="nonfinite_gradient",
                tier=1,
                subject="component",
                subject_name="spherical_geometry",
                backends=("jax",),
                measurements=(
                    measurement,
                    reachability_measurement(reachable_via=reachable_via),
                ),
                anchors=tuple(item for item in (anchor,) if item is not None),
                code_exists=True,
                reachable_via=tuple(reachable_via),
                blocked_by=(),
                affects_science=False,
                backend_reachability=backend_reachability,
                reproducer={
                    "numpy_value_at_zero": numpy_value,
                    "jax_value_at_zero": jax_value,
                    "jax_gradient_at_zero": jax_gradient,
                    "radius": radii.tolist(),
                    "gradient_norm": gradient_norm,
                },
            )
        ]
