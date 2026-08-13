# Prototype a scale-aware curvature-diagonal floor

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: medium
Autonomy: supervised
Priority: high
Status: issued
Source: autolens_profiling#110 · finding `likelihood.imaging-pixelization.absolute-conditioning-floors`

The tier-2 likelihood hazard scan measured the packaged absolute curvature-diagonal
addition (`1.0e-3`) at 0.7%, 2.9%, and 11.5% of the fitted curvature-diagonal
scale as the noise map was multiplied by 0.5, 1.0, and 2.0. Before changing
PyAutoArray numerics, test a scale-aware counterfactual inside the profiling
workspace.

Use the existing small `FitImaging` pixelization cell. Add a zero-floor control,
the current absolute-floor policy, and a scale-aware candidate calibrated to equal
the current default at noise scale 1.0. Derive the candidate from the unfloored
curvature diagonal, then rerun the actual likelihood at all three noise scales.

Report:
- floor / curvature-diagonal scale for both policies;
- figure-of-merit and reconstruction differences versus the current absolute policy;
- whether the zero-floor control remains solvable;
- a bounded recommendation for a later PyAutoArray source task.

Do not change PyAutoArray or any production default in this task. Preserve the
existing stable finding ID and results schema.
