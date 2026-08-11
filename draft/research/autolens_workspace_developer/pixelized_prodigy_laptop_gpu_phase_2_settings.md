# Optimize pixelized Prodigy settings on the laptop GPU

Type: research
Target: autolens_workspace_developer
Repos:
- @autolens_workspace_developer
Difficulty: medium
Autonomy: human-required
Priority: high
Status: blocked
Blocked-by: `pixelized_prodigy_laptop_gpu_phase_1_compatibility.md`
Parent: `pixelized_prodigy_laptop_gpu.md`

Consume the phase-1 four-mesh compatibility results and determine the
`af.MultiStartProdigy` settings that reach the best supported likelihood in
the fewest optimizer steps and shortest wall time on the laptop RTX 2060
Max-Q. Cover rectangular, KNN, Delaunay, and DelaunayNN without repeating
settled CPU arms unnecessarily.

Compare useful `n_starts` values (starting at 4 and escalating through 8/16
only when they add basin coverage), memory-tiling `batch_size` values that fit
6 GB VRAM, and fixed/inherited versus free Matérn and free AdaptSplit
regularization where scientifically relevant. Keep the validated broad start
band unless evidence demands otherwise. Use full FoM histories to report
steps-to-bar rather than launching redundant step-ceiling runs.

Produce a four-mesh recommendation table with maximum likelihood, recovered
mass parameters, steps-to-bar, wall-to-bar, per-step time, resurrection rate,
and VRAM/overflow constraints. Clearly distinguish highest-likelihood,
fewest-step, and shortest-wall winners when they differ, and document every
configuration that fails within its tested budget.

## Original request

> Then work out what settings infer the max Lh modle I fewest steps e.g.
> perform best.
