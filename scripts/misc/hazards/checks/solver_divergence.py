"""Compare the algorithmically distinct NumPy and JAX positive solvers."""

from __future__ import annotations

from hazards._anchor import maybe_anchor_from_pattern
from hazards._likelihood import backend_error_curves, imaging_pixelization_probe
from hazards._measure import Measurement, reachability_measurement
from hazards._record import Finding
from hazards.checks._base import HazardCheck, ScanContext


class SolverDivergenceCheck(HazardCheck):
    name = "solver_divergence"
    subject = "likelihood"

    def run(self, context: ScanContext) -> list[Finding]:
        rows = [
            row
            for row in imaging_pixelization_probe(context)["inversion"]
            if row.noise_scale == 1.0
        ]
        curves = backend_error_curves(rows)
        if not curves:
            return []
        maximum = max(
            max(curve[quantity])
            for curve in curves.values()
            for quantity in ("figure_of_merit", "reconstruction")
        )
        numpy_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/util/fnnls.py",
            pattern="def fnnls_cholesky(",
            after=18,
            symbol="autoarray.util.fnnls.fnnls_cholesky",
        )
        jax_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/util/jax_nnls.py",
            pattern="def solve_nnls_primal(",
            after=18,
            symbol="autoarray.util.jax_nnls.solve_nnls_primal",
        )
        dispatch_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/inversion/inversion/inversion_util.py",
            pattern='if xp.__name__.startswith("jax"):',
            after=28,
            symbol="autoarray.inversion.inversion.inversion_util.reconstruction_positive_only_from",
        )
        return [
            Finding(
                finding_id="likelihood.imaging-pixelization.positive-solver-backend-divergence",
                title="Positive solvers are backend-dependent algorithms",
                summary=(
                    "A full FitImaging grid compares active-set FNNLS with the JAX "
                    f"interior-point path; maximum measured relative output error is {maximum:.3e}."
                ),
                hazard_class="solver_divergence",
                tier=2,
                subject="likelihood",
                subject_name="imaging_pixelization",
                backends=("numpy", "jax"),
                measurements=(
                    Measurement(
                        basis="error_curve",
                        value=maximum,
                        unit="relative_error",
                        details={"reference": "numpy_fnnls", "curves": curves},
                    ),
                    reachability_measurement(
                        reachable_via=(
                            "FitImaging.numpy.active-set-fnnls",
                            "FitImaging.jax.pdip-jacobi",
                        )
                    ),
                ),
                anchors=tuple(
                    anchor
                    for anchor in (numpy_anchor, jax_anchor, dispatch_anchor)
                    if anchor is not None
                ),
                code_exists=True,
                reachable_via=(
                    "FitImaging.numpy.active-set-fnnls",
                    "FitImaging.jax.pdip-jacobi",
                ),
                blocked_by=(),
                affects_science=None,
                backend_reachability={
                    "numpy": {"algorithm": "active-set FNNLS"},
                    "jax": {"algorithm": "PDIP with Jacobi preconditioning"},
                },
                reproducer={"parameter": "einstein_radius", "curves": curves},
            )
        ]
