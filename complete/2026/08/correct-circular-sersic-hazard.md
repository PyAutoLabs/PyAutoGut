## correct-circular-sersic-hazard
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/121
- completed: 2026-08-14
- workspace-pr: https://github.com/PyAutoLabs/autolens_profiling/pull/122
- merge-commit: dfa47a1d0f16653daf36dc33549c9fcee2214ff3
- summary: Corrected the circular Sersic hazard in the actual fitted ell_comps coordinates. The q-angle structural finding was a sampler-parameterization false positive; the exact Cartesian origin instead has a finite likelihood and non-finite JAX gradient while its bounded neighbourhood is finite.
- validation: GitHub Actions lint run 31760350197 succeeded across lint, format, tests, README, links, and smoke; 38 local tests, compile, the three-finding NumPy/JAX scan, README, smoke, and plot review passed; no review threads.
- evidence: q >= 0.99 contains 1.403e-4 of the default two-component Gaussian prior, not 1%; the explicit 1e-8 neighbourhood contains 5.56e-16; the exact origin gradient is [NaN, NaN], versus finite norm ~1.27892 nearby.
- follow-up: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/570
- release: not performed; the merged workspace PR remains in the pending-release queue.

## Original prompt

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

