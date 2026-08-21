# Rectangular mesh split: Bilinear (fast CPU default) vs RTU (advanced/GPU)

Type: feature
Target: autoarray
Repos:
- @PyAutoArray
- @autolens_workspace
- @autogalaxy_workspace
- @autolens_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: high

## Original request (verbatim, 2026-08-21)

> Ok, I think we want RectangularBilinearAdaptDensity (workspace default)
> RectangularBilinearAdaptImage, RectangularRTUAdaptDensity and
> RectangularRTUAdaptImage. Confirm RectangularBilinearAdaptDensity is CPU fast
> and gradient robust. Thsi will prob means we need to again updated all _test
> workspace likelihood values in certain scripts, see if history has them but
> over write if not (and keep RTU files somewhere)? make prompt to hand off to
> mobile

Preceding context (same conversation): the RTU kernel-CDF transform dominates
the numba CPU likelihood (55% of a euclid eval, 89% at hst; O(M_sub x N_data)
erf sum), making the workspace-default rectangular mesh slow on CPU and on the
interferometer path. Proposal: a simpler/faster rectangular mesh becomes the
workspace default; RTU is documented separately as the recommended option for
advanced modeling, especially on GPU. This subsumes option (2) of the Phase 14
default-mesh decision (`autolens_profiling` PROGRAMME.md Phase 14, issue
autolens_profiling#153) — resolve/update that issue as part of this work.

## Grounding (verified 2026-08-21, this session)

- Current classes (`PyAutoArray autoarray/inversion/mesh/mesh/__init__.py`):
  `RectangularAdaptDensity` / `RectangularAdaptImage` (RTU kernel-CDF,
  Enzi et al. arXiv:2606.30620) and `RectangularUniform` (plain uniform
  lattice + bilinear, no transform). There is no bare `Rectangular`.
- **Naming caveat:** BOTH the RTU meshes and every historical adaptive variant
  use the same 4-pixel bilinear interpolation on the warped lattice
  (`interpolator/rectangular.py:435-442`). What "Bilinear vs RTU" actually
  distinguishes is the lattice transform: the resurrect candidate is the
  **empirical rank-CDF** adaptive transform (sort + cumsum), deleted in
  PyAutoArray `22b28463` (#402, 2026-07-23, -3738 lines) when kernel-CDF took
  the plain names. Recover its implementation from that commit
  (`create_transforms` with `argsort`/`cumsum`) — do NOT reinvent it.
- **CPU fast: YES.** The rank-CDF transform is O(N log N) sort/cumsum and
  eliminates the erf sum that is 55-89% of the numba CPU eval (post-#458 the
  RTU eval is euclid 1.17 s / hst 10.1 s on a 4-core container). Measure the
  new class in the existing `autolens_profiling` cells
  (`scripts/imaging/likelihood_runtime/pixelization_numba.py` etc.) and record
  a versioned result.
- **Gradient robust: CONDITIONALLY.** Certified evidence from the July
  gradient audit (`autolens_workspace_developer/jax_profiling/gradient/README.md`):
  - os_pix=1 (the current default): rank-CDF likelihood is *exactly
    piecewise-constant* in mass/shear — gradients exactly zero. Unusable.
  - over_sample_size_pixelization=4: full FD sweeps validate both adaptive
    meshes — AdaptImage production shape <=~1% on mass, AdaptDensity <=~3%.
    Acceptable for most JAX gradient samplers.
  - Interferometer sparse path: no over-sampling exists — the staircase with
    no escape hatch. RTU (and RectangularUniform) are the only certified
    gradient meshes there.
  So docs MUST say: gradient inference on the Bilinear default needs
  os_pix>=4 (imaging); interferometer gradient work needs RTU. Sampler-level
  mesh-family ranking is already PROGRAMME Phase 5 — do not duplicate it here.
- Alternative implementation considered: interpolated-kernel-CDF forward
  (K=8192 -> dlnL <= +4e-3, 18-55x on the step, measured in #151/#153 work).
  Rejected for the *Bilinear* pair (it is still RTU with a bandwidth
  hyperparameter, defeating "conceptually simple"); it remains #153's lever
  for making RTU itself faster on CPU.

## Goal

1. **PyAutoArray**: four adaptive classes —
   `RectangularBilinearAdaptDensity` (resurrected rank-CDF transform +
   bilinear) and `RectangularBilinearAdaptImage`;
   `RectangularRTUAdaptDensity` / `RectangularRTUAdaptImage` (pure renames of
   the current kernel-CDF classes, values unchanged). `RectangularUniform`
   stays as-is (library-test baseline; certified interferometer gradient
   mesh). **Never delete the RTU implementation.** Breaking rename → release
   notes need the `## API Changes` heading.
2. **Workspaces** (`autolens_workspace` ~224 uses, `autogalaxy_workspace`,
   HowToLens ~42): default examples switch to
   `RectangularBilinearAdaptDensity`; RTU documented separately as the
   recommended advanced option (GPU / gradient samplers / interferometer),
   folding in the queued Enzi-citation docs draft
   (`draft/docs/workspaces/rectangular_mesh_enzi_citation_examples.md`).
   Prior configs: add `mesh/rectangular_bilinear_adapt_*.yaml`, rename the
   RTU yamls to match the new class names (autoconf lowercases keys).
3. **_test workspace**: likelihood pin scripts
   (`scripts/{imaging,multi_dataset,interferometer}/jax_likelihood/rectangular*.py`
   and siblings) — keep RTU pin scripts alive under the renamed classes
   (values unchanged by a pure rename), add/switch default-mesh scripts to
   Bilinear and **regenerate pins, overwriting**. History does hold
   pre-consolidation (empirical-CDF era) values but under older paths/configs
   (over-sampling changed since: `3b4156e`, `602ffce`) — not reusable.
4. Update autolens_profiling#153 / PROGRAMME Phase 14 with the decision.

Library first, workspace follow-up once the API lands (standard both-routing).
