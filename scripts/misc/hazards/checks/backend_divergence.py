"""Compare the exact NumPy PowerLaw path with JAX's finite omega series."""

from __future__ import annotations

import numpy as np

from hazards._anchor import maybe_anchor_from_pattern
from hazards._measure import error_curve_measurement, reachability_measurement
from hazards._record import Finding
from hazards.checks._base import HazardCheck, ScanContext


class BackendDivergenceCheck(HazardCheck):
    name = "backend_divergence"
    subject = "component"

    def run(self, context: ScanContext) -> list[Finding]:
        import autoarray as aa
        import jax
        import jax.numpy as jnp
        from autogalaxy.profiles.mass.total.power_law import PowerLaw

        jax.config.update("jax_enable_x64", True)
        exact_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoGalaxy",
            path="autogalaxy/profiles/mass/total/power_law.py",
            pattern="* special.hyp2f1(1.0, 0.5 * slope",
            before=7,
            after=1,
            symbol="autogalaxy.profiles.mass.total.power_law.PowerLaw.deflections_yx_2d_from",
        )
        series_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoGalaxy",
            path="autogalaxy/profiles/mass/total/jax_utils.py",
            pattern="def omega(eiphi, slope, factor, n_terms=20, xp=np):",
            after=6,
            symbol="autogalaxy.profiles.mass.total.jax_utils.omega",
        )

        factors = np.asarray((0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99))
        coordinates = np.asarray(((0.3, 0.7), (-0.4, 0.6), (0.8, -0.2), (-0.7, -0.3)), dtype=float)
        numpy_rows = []
        jax_rows = []
        for factor in factors:
            profile = PowerLaw(ell_comps=(float(factor), 0.0), einstein_radius=1.0, slope=2.2)
            numpy_rows.append(
                np.asarray(
                    profile.deflections_yx_2d_from(
                        grid=aa.Grid2DIrregular(values=coordinates), xp=np
                    ).array,
                    dtype=float,
                )
            )
            jax_rows.append(
                np.asarray(
                    profile.deflections_yx_2d_from(
                        grid=aa.Grid2DIrregular(values=jnp.asarray(coordinates)),
                        xp=jnp,
                    ).array,
                    dtype=float,
                )
            )
        numpy_values = np.asarray(numpy_rows)
        jax_values = np.asarray(jax_rows)
        measurement = error_curve_measurement(
            factors,
            numpy_values,
            jax_values,
            parameter_name="factor=(1-q)/(1+q)",
        )
        if measurement.value is None or measurement.value <= 1.0e-12:
            return []
        return [
            Finding(
                finding_id="component.power-law.series-vs-hyp2f1-divergence",
                title="PowerLaw's 20-term JAX series diverges from hyp2f1 at high ellipticity",
                summary=(
                    "The JAX backend replaces the exact SciPy hyp2f1 angular factor "
                    "with a fixed 20-term omega series. Relative deflection error grows "
                    f"continuously to {measurement.value:.3g} over the measured factor curve."
                ),
                hazard_class="backend_divergence",
                tier=1,
                subject="component",
                subject_name="power_law",
                backends=("numpy", "jax"),
                measurements=(
                    measurement,
                    reachability_measurement(
                        reachable_via=["numpy_deflections", "jax_deflections"]
                    ),
                ),
                anchors=tuple(
                    anchor for anchor in (exact_anchor, series_anchor) if anchor is not None
                ),
                code_exists=True,
                reachable_via=("numpy_deflections", "jax_deflections"),
                blocked_by=(),
                affects_science=True,
                backend_reachability={
                    "numpy": {"implementation": "scipy.special.hyp2f1"},
                    "jax": {"implementation": "omega series", "n_terms": 20},
                },
                reproducer={
                    "slope": 2.2,
                    "coordinates": coordinates.tolist(),
                    "factor": factors.tolist(),
                    "relative_error": measurement.details["relative_error"],
                },
            )
        ]
