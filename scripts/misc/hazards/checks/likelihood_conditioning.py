"""Measure absolute inversion floors against scales from a real imaging fit."""

from __future__ import annotations

from hazards._anchor import maybe_anchor_from_pattern
from hazards._likelihood import floor_fraction, imaging_pixelization_probe
from hazards._measure import Measurement, reachability_measurement
from hazards._record import Finding
from hazards.checks._base import HazardCheck, ScanContext


class LikelihoodConditioningCheck(HazardCheck):
    name = "likelihood_conditioning"
    subject = "likelihood"

    def run(self, context: ScanContext) -> list[Finding]:
        from autoarray.settings import Settings

        rows = [
            row
            for row in imaging_pixelization_probe(context)["inversion"]
            if row.backend == "numpy" and row.parameter == 0.9
        ]
        rows.sort(key=lambda row: row.noise_scale)
        configured_floor = float(Settings().no_regularization_add_to_curvature_diag_value)
        regularization_jitter = 1.0e-8
        curvature_ratios = [
            floor_fraction(configured_floor, row.curvature_diagonal) for row in rows
        ]
        regularization_ratios = [
            floor_fraction(regularization_jitter, row.regularization_diagonal) for row in rows
        ]

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
                    "The complete likelihood expresses curvature and constant-regularization "
                    "floors as fractions of the fitted matrices over a noise-map scaling sweep."
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
                    "regularization_jitter_fraction": regularization_ratios,
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
