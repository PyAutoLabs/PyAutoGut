# Correct the circular Sersic hazard parameterization

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: medium
Autonomy: supervised
Priority: high
Status: issued
Source: autolens_profiling finding `likelihood.imaging-sersic.circular-orientation-degeneracy`

The structural finding currently measures a uniform physical
`(axis_ratio, angle)` grid, but Sersic models are sampled in two Cartesian
`ell_comps` Gaussian priors. At the circular point, angle is a derived,
undefined quantity rather than an independent sampler coordinate.

Measure the circular neighbourhood in the actual two-dimensional default prior
and correct the finding's reachability, prior mass, and science semantics. Add
an off-grid-centre full-likelihood JAX gradient probe that isolates the
`ell_comps=(0, 0)` origin from the existing radial-grid-centre hazard. Persist
a separate stable non-finite-gradient finding if the exact origin returns
non-finite derivatives while its bounded neighbourhood has finite continuous
limits.

Do not modify PyAutoGalaxy or its priors in this task. Open a bounded source task
only if the profiling evidence isolates a removable implementation singularity.
