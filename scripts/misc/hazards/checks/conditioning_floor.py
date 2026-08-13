"""Measure an absolute curvature-diagonal floor against synthetic matrix scale."""

from __future__ import annotations

import numpy as np

from hazards._anchor import maybe_anchor_from_pattern
from hazards._measure import Measurement, reachability_measurement
from hazards._record import Finding
from hazards.checks._base import HazardCheck, ScanContext


class ConditioningFloorCheck(HazardCheck):
    name = "conditioning_floor"
    subject = "matrix"

    def run(self, context: ScanContext) -> list[Finding]:
        from autoarray.inversion.inversion.inversion_util import (
            curvature_matrix_with_added_to_diag_from,
        )
        from autoarray.settings import Settings

        code_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/inversion/inversion/inversion_util.py",
            pattern="def curvature_matrix_with_added_to_diag_from(",
            after=12,
            symbol="autoarray.inversion.inversion.inversion_util.curvature_matrix_with_added_to_diag_from",
        )
        config_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/config/general.yaml",
            pattern="no_regularization_add_to_curvature_diag_value :",
            config_key="general.inversion.no_regularization_add_to_curvature_diag_value",
        )

        floor = float(Settings().no_regularization_add_to_curvature_diag_value)
        if floor <= 0.0:
            return []
        scales = np.logspace(-6, 3, 10)
        base = np.asarray(((1.0, 0.999999), (0.999999, 0.999999)), dtype=float)
        rows: dict[str, dict[str, list[float]]] = {}
        indices = np.asarray((0, 1), dtype=int)

        for backend in context.backends:
            if backend == "jax":
                import jax
                import jax.numpy as xp

                jax.config.update("jax_enable_x64", True)
            else:
                xp = np
            ratios = []
            condition_before = []
            condition_after = []
            added_values = []
            for scale in scales:
                original = base * scale
                matrix_scale = float(np.median(np.abs(np.diag(original))))
                condition_before.append(float(np.linalg.cond(original)))
                result = curvature_matrix_with_added_to_diag_from(
                    # The NumPy helper mutates its input; preserve `original`
                    # so every before/after measurement uses the same matrix.
                    curvature_matrix=xp.asarray(original.copy()),
                    value=floor,
                    no_regularization_index_list=indices,
                    xp=xp,
                )
                result_array = np.asarray(result, dtype=float)
                ratios.append(floor / matrix_scale)
                condition_after.append(float(np.linalg.cond(result_array)))
                added_values.append(float(np.mean(np.diag(result_array - original))))
            rows[backend] = {
                "floor_over_matrix_scale": ratios,
                "condition_before": condition_before,
                "condition_after": condition_after,
                "observed_diagonal_add": added_values,
            }

        for curves in rows.values():
            if not np.allclose(curves["observed_diagonal_add"], floor):
                raise RuntimeError(
                    "conditioning-floor reproducer did not observe the configured add"
                )
        if len(rows) > 1:
            first, *rest = rows.values()
            if any(
                not np.allclose(first["floor_over_matrix_scale"], item["floor_over_matrix_scale"])
                for item in rest
            ):
                raise RuntimeError("conditioning-floor scale ratio differs across backends")

        representative = rows[next(iter(rows))]
        measurement = Measurement(
            basis="error_curve",
            value=float(max(representative["floor_over_matrix_scale"])),
            unit="floor_over_matrix_scale",
            details={
                "parameter_name": "matrix_scale",
                "parameter": scales.tolist(),
                "floor": floor,
                "curves": rows,
            },
        )
        reachable_via = [f"{backend}_synthetic_matrix" for backend in context.backends]
        return [
            Finding(
                finding_id="matrix.curvature.absolute-diagonal-floor",
                title="Absolute curvature-diagonal floor is scale dependent",
                summary=(
                    f"The configured {floor:.1e} diagonal add ranges from dominant to "
                    "negligible as synthetic curvature scale changes. Detection needs no "
                    "dataset; judging scientific relevance does."
                ),
                hazard_class="conditioning_floor",
                tier=2,
                subject="matrix",
                subject_name="curvature_matrix",
                backends=tuple(context.backends),
                measurements=(
                    measurement,
                    reachability_measurement(reachable_via=reachable_via),
                ),
                anchors=tuple(
                    anchor for anchor in (code_anchor, config_anchor) if anchor is not None
                ),
                code_exists=True,
                reachable_via=tuple(reachable_via),
                blocked_by=(),
                affects_science=None,
                backend_reachability={
                    backend: {"synthetic_matrix": "reachable"} for backend in context.backends
                },
                reproducer={
                    "matrix_scale": scales.tolist(),
                    "floor": floor,
                    "backends": rows,
                },
            )
        ]
