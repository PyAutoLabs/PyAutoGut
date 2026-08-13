"""Detect positive-solver support changes inside a complete likelihood."""

from __future__ import annotations

import numpy as np

from hazards._anchor import maybe_anchor_from_pattern
from hazards._likelihood import (
    epsilon_neighbourhood_mass,
    imaging_pixelization_probe,
    support_mask,
    support_transition_locations,
)
from hazards._measure import Measurement, epsilon_neighbourhood_measurement
from hazards._record import Finding
from hazards.checks._base import HazardCheck, ScanContext


class ActiveSetCheck(HazardCheck):
    name = "active_set"
    subject = "likelihood"

    def run(self, context: ScanContext) -> list[Finding]:
        rows = [
            row
            for row in imaging_pixelization_probe(context)["inversion"]
            if row.backend == "numpy" and row.noise_scale == 1.0
        ]
        transitions = support_transition_locations(rows)
        if not transitions:
            return []
        ordered = sorted(rows, key=lambda row: row.parameter)
        lower, upper = ordered[0].parameter, ordered[-1].parameter
        spacing = min(right.parameter - left.parameter for left, right in zip(ordered, ordered[1:]))
        epsilon = 0.5 * spacing
        mass = epsilon_neighbourhood_mass(
            transitions,
            epsilon=epsilon,
            lower=lower,
            upper=upper,
        )
        relative_steps = []
        for left, right in zip(ordered, ordered[1:]):
            if support_mask(left.reconstruction) == support_mask(right.reconstruction):
                continue
            left_array = np.asarray(left.reconstruction)
            right_array = np.asarray(right.reconstruction)
            relative_steps.append(
                float(
                    np.linalg.norm(right_array - left_array)
                    / max(np.linalg.norm(left_array), 1.0e-14)
                )
            )

        active_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/util/fnnls.py",
            pattern="def fnnls_cholesky(",
            after=18,
            symbol="autoarray.util.fnnls.fnnls_cholesky",
        )
        dispatch_anchor = maybe_anchor_from_pattern(
            context.workspace_root,
            repo="PyAutoArray",
            path="autoarray/inversion/inversion/inversion_util.py",
            pattern="def reconstruction_positive_only_from(",
            after=18,
            symbol="autoarray.inversion.inversion.inversion_util.reconstruction_positive_only_from",
        )
        measurement = epsilon_neighbourhood_measurement(
            epsilon=epsilon,
            mass=mass,
            domain={"parameter": "einstein_radius", "lower": lower, "upper": upper},
            centre=transitions,
        )
        continuity = Measurement(
            basis="error_curve",
            value=max(relative_steps),
            unit="adjacent_relative_reconstruction_step",
            details={
                "interpretation": (
                    "support and derivative are nonsmooth; this finite grid does not show "
                    "a discontinuous well-posed reconstruction"
                ),
                "grid_spacing": spacing,
                "relative_steps_at_support_changes": relative_steps,
                "support": [list(support_mask(row.reconstruction)) for row in ordered],
            },
        )
        return [
            Finding(
                finding_id="likelihood.imaging-pixelization.nnls-active-set-kinks",
                title="NNLS support changes create likelihood kinks",
                summary=(
                    f"The NumPy full-likelihood scan changes active support at "
                    f"{len(transitions)} bounded Einstein-radius location(s). The report "
                    "measures explicit epsilon-neighbourhood mass, not exact-kink prior mass."
                ),
                hazard_class="active_set",
                tier=2,
                subject="likelihood",
                subject_name="imaging_pixelization",
                backends=("numpy",),
                measurements=(measurement, continuity),
                anchors=tuple(
                    anchor for anchor in (active_anchor, dispatch_anchor) if anchor is not None
                ),
                code_exists=True,
                reachable_via=("FitImaging.RectangularUniform.Constant.numpy",),
                blocked_by=(),
                affects_science=None,
                backend_reachability={"numpy": {"full_likelihood": "reachable"}},
                reproducer={
                    "parameter": [row.parameter for row in ordered],
                    "transition_locations": transitions,
                    "epsilon": epsilon,
                },
            )
        ]
