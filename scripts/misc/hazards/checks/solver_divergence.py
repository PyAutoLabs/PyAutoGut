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
        native_maximum = max(
            max(curve[quantity])
            for curve in curves.values()
            for quantity in ("figure_of_merit", "reconstruction")
        )
        diagnostic = imaging_pixelization_probe(context)["solver_diagnostic"]
        policy_maxima = {
            policy: {
                "reconstruction_relative_error_to_numpy_solver": max(
                    row.reconstruction_relative_error_to_numpy_solver
                    for row in diagnostic
                    if row.solver_policy == policy
                ),
                "objective_relative_gap_to_numpy_solver": max(
                    abs(row.objective_relative_gap_to_numpy_solver)
                    for row in diagnostic
                    if row.solver_policy == policy
                ),
                "complementarity": max(
                    row.complementarity for row in diagnostic if row.solver_policy == policy
                ),
            }
            for policy in ("jax_default", "jax_tight", "jax_relaxed")
        }
        system_matrix_maximum = max(row.system_matrix_relative_error_to_numpy for row in diagnostic)
        system_vector_maximum = max(
            row.system_data_vector_relative_error_to_numpy for row in diagnostic
        )
        native_reconstruction_maximum = max(
            row.native_fit_reconstruction_relative_error_to_numpy for row in diagnostic
        )
        support_boundary = [
            {
                "parameter": row.parameter,
                "parameter_hex": row.parameter_hex,
                "system_backend": row.system_backend,
                "native_fit_support": list(row.native_fit_support),
                "numpy_fit_support": list(row.numpy_fit_support),
                "system_matrix_relative_error_to_numpy": (
                    row.system_matrix_relative_error_to_numpy
                ),
            }
            for row in diagnostic
            if row.solver_policy == "numpy_active_set"
        ]
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
                title="Measured backend divergence originates before the positive solver",
                summary=(
                    f"The native likelihood paths differ by up to {native_reconstruction_maximum:.3e} "
                    "over a one-ULP neighbourhood, but the default solvers agree to "
                    f"{policy_maxima['jax_default']['reconstruction_relative_error_to_numpy_solver']:.3e} "
                    "when given the same system. Backend-built matrices differ by up to "
                    f"{system_matrix_maximum:.3e}."
                ),
                hazard_class="solver_divergence",
                tier=2,
                subject="likelihood",
                subject_name="imaging_pixelization",
                backends=("numpy", "jax"),
                measurements=(
                    Measurement(
                        basis="error_curve",
                        value=native_maximum,
                        unit="relative_error",
                        details={"reference": "numpy_fnnls", "curves": curves},
                    ),
                    Measurement(
                        basis="error_curve",
                        value=policy_maxima["jax_default"][
                            "reconstruction_relative_error_to_numpy_solver"
                        ],
                        unit="same_system_solver_relative_error",
                        details={"policy_maxima": policy_maxima},
                    ),
                    Measurement(
                        basis="error_curve",
                        value=system_matrix_maximum,
                        unit="backend_system_relative_error",
                        details={
                            "curvature_regularization_matrix": system_matrix_maximum,
                            "data_vector": system_vector_maximum,
                            "ulp_neighbourhood": support_boundary,
                        },
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
                    "numpy": {
                        "algorithm": "active-set FNNLS",
                        "same_system_diagnosis": "agrees with JAX",
                    },
                    "jax": {
                        "algorithm": "PDIP with Jacobi preconditioning",
                        "same_system_diagnosis": "agrees with NumPy",
                    },
                },
                reproducer={
                    "parameter": "einstein_radius",
                    "curves": curves,
                    "same_system_reconstruction_error_max": {
                        policy: values["reconstruction_relative_error_to_numpy_solver"]
                        for policy, values in policy_maxima.items()
                    },
                    "system_matrix_relative_error_max": system_matrix_maximum,
                    "system_data_vector_relative_error_max": system_vector_maximum,
                    "native_fit_reconstruction_relative_error_max": (native_reconstruction_maximum),
                    "ulp_neighbourhood": support_boundary,
                    "recommendation": (
                        "Do not open a positive-solver source task from this finding. "
                        "The solvers agree on identical systems; isolate the backend "
                        "system-construction discontinuity instead."
                    ),
                },
            )
        ]
