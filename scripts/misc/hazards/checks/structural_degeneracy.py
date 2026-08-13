"""Measure a parameter direction that vanishes at the circular-profile edge."""

from __future__ import annotations

from hazards._likelihood import imaging_pixelization_probe, orientation_spans
from hazards._measure import Measurement, epsilon_neighbourhood_measurement
from hazards._record import Finding
from hazards.checks._base import HazardCheck, ScanContext


class StructuralDegeneracyCheck(HazardCheck):
    name = "structural_degeneracy"
    subject = "likelihood"

    def run(self, context: ScanContext) -> list[Finding]:
        rows = [
            row
            for row in imaging_pixelization_probe(context)["structural"]
            if row.backend == "numpy"
        ]
        spans = orientation_spans(rows)
        circular_span = spans.get(1.0, float("inf"))
        reference_span = spans.get(min(spans), 0.0)
        relative = circular_span / max(reference_span, 1.0e-14)
        return [
            Finding(
                finding_id="likelihood.imaging-sersic.circular-orientation-degeneracy",
                title="Orientation vanishes at the circular profile boundary",
                summary=(
                    "A complete imaging likelihood loses sensitivity to position angle as "
                    "the Sersic axis ratio reaches one."
                ),
                hazard_class="structural_degeneracy",
                tier=2,
                subject="likelihood",
                subject_name="imaging_sersic",
                backends=("numpy",),
                measurements=(
                    Measurement(
                        basis="error_curve",
                        value=relative,
                        unit="circular_over_elliptical_orientation_span",
                        details={
                            "axis_ratio_to_figure_of_merit_span": {
                                str(axis_ratio): span for axis_ratio, span in spans.items()
                            }
                        },
                    ),
                    epsilon_neighbourhood_measurement(
                        epsilon=0.01,
                        mass=0.01,
                        domain={"parameter": "axis_ratio", "lower": 0.0, "upper": 1.0},
                        centre=(1.0,),
                    ),
                ),
                anchors=(),
                code_exists=True,
                reachable_via=("FitImaging.Sersic.axis-ratio-angle-grid",),
                blocked_by=(),
                affects_science=True,
                backend_reachability={"numpy": {"full_likelihood": "reachable"}},
                reproducer={"axis_ratio_to_figure_of_merit_span": spans},
            )
        ]
