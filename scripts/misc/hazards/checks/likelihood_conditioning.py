"""Measure inversion floors and a scale-aware counterfactual in a real fit."""

from __future__ import annotations

from hazards._anchor import maybe_anchor_from_pattern
from hazards._likelihood import (
    conditioning_policy_metrics,
    floor_fraction,
    imaging_pixelization_probe,
)
from hazards._measure import Measurement, reachability_measurement
from hazards._record import Finding
from hazards.checks._base import HazardCheck, ScanContext


class LikelihoodConditioningCheck(HazardCheck):
    name = "likelihood_conditioning"
    subject = "likelihood"

    def run(self, context: ScanContext) -> list[Finding]:
        from autoarray.settings import Settings

        probe = imaging_pixelization_probe(context)
        rows = sorted(
            (row for row in probe["inversion"] if row.backend == "numpy" and row.parameter == 0.9),
            key=lambda row: row.noise_scale,
        )
        configured_floor = float(Settings().no_regularization_add_to_curvature_diag_value)
        regularization_jitter = 1.0e-8
        policy_metrics = conditioning_policy_metrics(probe["conditioning"])
        absolute = policy_metrics["absolute"]
        scale_aware = policy_metrics["scale_aware"]
        no_floor = policy_metrics["none"]
        curvature_ratios = absolute["floor_fraction"]
        regularization_ratios = [
            floor_fraction(regularization_jitter, row.regularization_diagonal) for row in rows
        ]
        scale_aware_span = max(scale_aware["floor_fraction"]) - min(scale_aware["floor_fraction"])
        scale_aware_output_error = max(
            scale_aware["figure_of_merit_relative_error"]
            + scale_aware["reconstruction_relative_error"]
        )

        curvature_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/inversion/inversion/inversion_util.py",
            pattern="def curvature_matrix_with_added_to_diag_from(",
            after=18,
            symbol="autoarray.inversion.inversion.inversion_util.curvature_matrix_with_added_to_diag_from",
        )
        config_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/config/general.yaml",
            pattern="no_regularization_add_to_curvature_diag_value :",
            config_key="general.inversion.no_regularization_add_to_curvature_diag_value",
        )
        constant_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/inversion/regularization/constant.py",
            pattern="diag_vals = 1e-8 +",
            after=3,
            symbol="autoarray.inversion.regularization.constant.constant_regularization_matrix_from",
        )
        gaussian_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/inversion/regularization/gaussian_kernel.py",
            pattern="h_jitter = 1e-8 * xp.abs(diag_mean)",
            after=3,
            symbol="autoarray.inversion.regularization.gaussian_kernel.GaussianKernel.regularization_matrix_from",
        )
        reachability = reachability_measurement(
            reachable_via=["FitImaging.linear-light-plus-RectangularUniform.Constant"]
        )
        return [
            Finding(
                finding_id="likelihood.imaging-pixelization.absolute-conditioning-floors",
                title="Absolute inversion floors move with dataset scale",
                summary=(
                    "Using only the diagonal entries the policy actually touches, the "
                    f"absolute floor reaches {max(curvature_ratios):.3e} of their scale. "
                    "A reference-calibrated scale-aware counterfactual holds its fraction "
                    f"fixed with maximum relative output error {scale_aware_output_error:.3e}."
                ),
                hazard_class="conditioning_floor",
                tier=2,
                subject="likelihood",
                subject_name="imaging_pixelization",
                backends=("numpy",),
                measurements=(
                    Measurement(
                        basis="error_curve",
                        value=max(curvature_ratios),
                        unit="curvature_floor_over_diagonal_scale",
                        details={
                            "noise_scale": [row.noise_scale for row in rows],
                            "fraction": curvature_ratios,
                            "absolute_floor": configured_floor,
                            "conditioned_indices": rows[0].metadata["conditioned_indices"],
                            "denominator": (
                                "median absolute curvature diagonal at no_regularization_index_list"
                            ),
                        },
                    ),
                    Measurement(
                        basis="error_curve",
                        value=max(regularization_ratios),
                        unit="regularization_jitter_over_diagonal_scale",
                        details={
                            "noise_scale": [row.noise_scale for row in rows],
                            "fraction": regularization_ratios,
                            "absolute_jitter": regularization_jitter,
                            "scale_free_counterexample": "GaussianKernel trace-scaled h_jitter",
                        },
                    ),
                    Measurement(
                        basis="error_curve",
                        value=scale_aware_span,
                        unit="scale_aware_curvature_floor_fraction_span",
                        details={
                            "noise_scale": scale_aware["noise_scale"],
                            "fraction": scale_aware["floor_fraction"],
                            "floor_value": scale_aware["floor_value"],
                            "calibration": "matches absolute default at noise_scale=1.0",
                        },
                    ),
                    Measurement(
                        basis="error_curve",
                        value=scale_aware_output_error,
                        unit="max_relative_output_error_vs_absolute_policy",
                        details={
                            "scale_aware": scale_aware,
                            "zero_floor_control": no_floor,
                        },
                    ),
                    reachability,
                ),
                anchors=tuple(
                    anchor
                    for anchor in (
                        curvature_anchor,
                        config_anchor,
                        constant_anchor,
                        gaussian_anchor,
                    )
                    if anchor is not None
                ),
                code_exists=True,
                reachable_via=("FitImaging.linear-light-plus-RectangularUniform.Constant",),
                blocked_by=(),
                affects_science=None,
                backend_reachability={"numpy": {"full_likelihood": "reachable"}},
                reproducer={
                    "noise_scale": [row.noise_scale for row in rows],
                    "curvature_floor_fraction": curvature_ratios,
                    "scale_aware_curvature_floor_fraction": scale_aware["floor_fraction"],
                    "regularization_jitter_fraction": regularization_ratios,
                    "conditioning_policies": policy_metrics,
                    "zero_floor_solvable": True,
                    "phase_2_denominator_correction": (
                        "The earlier 11.5% headline used the median of the full "
                        "matrix. The floor only touches no_regularization_index_list; "
                        "this record measures those affected entries."
                    ),
                    "recommendation": (
                        "Do not change the PyAutoArray default from this fixture. "
                        "Scale dependence is real, but the maximum affected-entry "
                        "fraction is small; require representative workspace evidence "
                        "before opening a source-numerics task."
                    ),
                },
            ),
            Finding(
                finding_id="likelihood.imaging-pixelization.curvature-floor-doc-config-drift",
                title="Curvature-floor documentation trails the live default",
                summary=(
                    f"The helper docstring names 1e-8 while live configuration supplies "
                    f"{configured_floor:.1e}, a {configured_floor / 1.0e-8:.0e} ratio."
                ),
                hazard_class="documentation_drift",
                tier=2,
                subject="likelihood",
                subject_name="imaging_pixelization",
                backends=tuple(context.backends),
                measurements=(
                    Measurement(
                        basis="error_curve",
                        value=configured_floor / 1.0e-8,
                        unit="configured_over_documented",
                        details={"documented": 1.0e-8, "configured": configured_floor},
                    ),
                ),
                anchors=tuple(
                    anchor for anchor in (curvature_anchor, config_anchor) if anchor is not None
                ),
                code_exists=True,
                reachable_via=("FitImaging.linear-light-inversion",),
                blocked_by=(),
                affects_science=None,
                reproducer={"documented": 1.0e-8, "configured": configured_floor},
            ),
        ]
