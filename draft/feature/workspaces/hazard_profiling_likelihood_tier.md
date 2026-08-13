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

The one tier-1 check deferred from phase 1: **`PowerLaw` backend divergence** —
JAX uses a 20-term series `omega` (`PyAutoGalaxy/autogalaxy/profiles/mass/total/jax_utils.py:14`)
where numpy uses exact `scipy.special.hyp2f1`
(`profiles/mass/total/power_law.py:123-143`). Series convergence degrades as
`factor = (1-q)/(1+q)` approaches 1 — i.e. exactly where the tier-1 `ell_comps`
clamp is pushing the sampler. `PowerLaw` is the base class of `Isothermal`, so
every SIE/EPL fit is affected. This check belongs in `scripts/misc/hazards/` with
the other tier-1 checks.

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
