## hazard-profiling-likelihood-tier
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/109
- completed: 2026-08-13
- workspace-pr: https://github.com/PyAutoLabs/autolens_profiling/pull/110
- merge-commit: 60b8eef67582a0d305788e5640e9093ef94f72fb
- summary: Tier-2 likelihood profiling landed with five persistent findings and corrected NNLS continuity semantics.
- validation: 22 local tests, Ruff, compile, smoke, and the full NumPy/JAX scan passed; GitHub lint run 31740669618 succeeded.
- findings:
  - NNLS support transitions create active-set and derivative kinks, while the well-posed convex reconstruction remains continuous.
  - Absolute conditioning floors are dataset-scale-sensitive; the measured curvature floor was about 0.115 of the fitted diagonal scale.
  - The curvature helper documentation says 1e-8 while the configured default is 1e-3, a 1e5 ratio.
  - NumPy active-set and JAX interior-point positive solvers diverged by about 8.99e-3 in the measured case.
  - Circular Sersic orientation is structurally degenerate, with zero likelihood span.
- boundary: profiling only; no source-library numerical behavior was changed. Each corrective is a separate task.

## Original prompt

# Hazard profiling — the likelihood tier (tier 2)

Type: feature
Target: workspaces
Repos:
- autolens_profiling
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

Phase 2 of the numerical-hazard profiling package. Phase 1
(`add_a_numerical_hazard_profiling_package_to.md`) builds the framework in
`scripts/misc/hazards/` and the tier-1 component checks. This prompt adds the
**tier-2 likelihood cell** under `scripts/imaging/hazards/`, which runs the same
hazard analysis on components *encased in a full likelihood function*.

Do not start this before phase 1 has merged — it consumes phase 1's check API,
record schema and results convention.

## Why tier 2 is separate

Tier-1 hazards live in a profile evaluated with no data. Tier-2 hazards only
exist once a likelihood wraps that profile: the linear algebra (inversion, NNLS,
regularization), the residuals and the chi-squared. They are dataset-specific,
which is why they live under `scripts/<dataset>/hazards/` rather than `misc/`.

This is forced, not stylistic. The conditioning floors are absolute constants
added to matrices whose entries scale as (flux/noise)² — halve the noise map and
the effective regularization strength changes fourfold. There is no
dataset-independent number to report.

## Hazard classes to implement

- **Active-set kinks.** `reconstruction_positive_only_from`
  (`PyAutoArray/autoarray/inversion/inversion/inversion_util.py:285-370`) forks by
  backend. The numpy path is a true active-set solver — `fnnls_cholesky`
  (`autoarray/util/fnnls.py:21`), with pinning in `fix_constraint_cholesky`
  (`:135-172`, note `s_chol[~P] = 0.0` at `:170`) and a ratio test at `:148-149`.
  The active set — and therefore the reconstruction — is a discontinuous function
  of the model at every sign flip of the warm-start solve (`inversion_util.py:363`).
  Report where kinks occur and how much prior volume sits near one.
- **Conditioning floors.** Three families, all absolute:
  - curvature-diagonal add, `curvature_matrix_with_added_to_diag_from`
    (`inversion_util.py:39-66`). **Note a live docstring/config drift**: the
    docstring at `:49` says `1.0e-8`, but the actual default is `1.0e-3`
    (`PyAutoArray/autoarray/config/general.yaml:7`). Five orders of magnitude.
    Report the drift as a finding in its own right.
  - regularization jitter `1e-8`, repeated across ~8 modules
    (`regularization/constant.py:53`, `adapt.py:103-108`, and the kernel
    regularizations' `jitter` knob). `matern_adapt_kernel.py:80` already
    documents that `1e-8` "can reach 100% of a faint pixel's variance".
  - the scale-free counter-example to contrast against:
    `gaussian_kernel.py:173`, `h_jitter = 1e-8 * xp.abs(diag_mean)`.
  Express each as a fraction of the matrix scale it perturbs, so the number means
  something for a given dataset.
- **Structural degeneracies.** Directions in which a parameter stops affecting the
  likelihood as another approaches a prior edge.
- **Solver backend divergence.** The numpy and JAX paths are *different
  algorithms*, not different array libraries: active-set FNNLS (tolerance
  `eps * n`, iteration cap 10000 that raises) versus interior-point PDIP
  (`autoarray/util/jax_nnls.py:33,111`, `max_iter=50` with silent truncation,
  relaxed-KKT custom VJP, plus Jacobi preconditioning applied on the JAX side only
  at `inversion_util.py:326-345`). Same input, structurally different output.

## Also in scope

**Breadth across the profile registry.** Phase 1 is deliberately one case per
subject shape; this phase widens the `component` subject across the light and mass
profiles, reusing the phase-1 detectors rather than writing new ones.

**A named first consumer.** Phase 1 emits `results/hazards/hazards_index.json`
keyed by stable finding ID. This phase must wire at least one existing profiling
report to cross-reference it for the cells it profiles, so the index has a reader
rather than existing on principle. Pick the consumer explicitly when planning —
an index nothing reads is the main way this package dies.

Note: the `PowerLaw` backend-divergence check (`hyp2f1` vs the 20-term `omega`
series — `jax_utils.py:14`, `power_law.py:123-143`) was **pulled forward into
phase 1** as its `error_curve` reference case, so it is no longer owed here.

## Layout

```
scripts/imaging/hazards/       # tier-2 cells, one per model as the repo does elsewhere
results/hazards/imaging/...    # mirrors the scripts layout
```

Extend `scripts/misc/hazards/` only where the framework needs a genuine
generalisation to host tier-2 checks — the check API should already fit.

## Boundary

All work lands in `@autolens_profiling`. This does not fix any finding in the
source libraries; each of those is its own task. The source-library paths above
are anchors to measure, not work to be done here. Do not run the full
`component x backend` matrix — the package is the deliverable, not the corpus.
