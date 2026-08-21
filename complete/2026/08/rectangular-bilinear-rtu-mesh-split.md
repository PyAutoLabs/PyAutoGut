Split the rectangular adaptive mesh family into **Bilinear** (empirical
rank-CDF — sort + cumsum, no hyperparameters, fast CPU default) and **RTU**
(kernel-CDF, Enzi et al. arXiv:2606.30620 — advanced option for GPU /
gradient samplers / interferometer gradient fitting). Conceived, reviewed,
implemented, fanned out across seven repos and human-merged in one day
(2026-08-21). Resolves autolens_profiling PROGRAMME Phase 14 (issue
autolens_profiling#153, option 2).

## Shipped

- **PyAutoArray#462** (issue #461): `create_transforms_rank` recovered
  verbatim from `22b28463^` behind a `transform="rank"|"kernel"` seam
  (interpolator + mesh geometry share it, so areas/edges always match the
  mapper); `RectangularBilinearAdaptDensity(shape)` /
  `RectangularBilinearAdaptImage(shape, weight_power, weight_floor)` added
  (clean signatures — no bandwidth/n_knots); kernel-CDF classes pure-renamed
  to `RectangularRTUAdaptDensity/Image`; `RectangularUniform` untouched.
  1114 unit tests + CI 3.12/3.13/nojax green.
- **autolens_workspace#495 / autogalaxy_workspace#221**: Bilinear default
  in EVERY example — including interferometer, per the follow-up human
  decision that no normal workspace uses RTU; RTU documentation-only, with
  the Enzi citation folded in from the queued Mind docs draft (retired with
  this record); prior yamls split; navigator catalogues regenerated (the
  staleness CI check regenerates per-PR — not release-only).
- **PyAutoGalaxy#579 / PyAutoLens#707**: packaged default prior yamls
  (PyAutoGalaxy ships them — discovered via workspace-impact analysis),
  docs/exc updates, and a fix for genuinely stale `rectangular.<Class>`
  JSON/YAML prior keys (verified: autonerves matches the real module path
  via endswith — the old keys never resolved).
- **autolens_workspace_test#259**: Bilinear pins regenerated under
  JAX_ENABLE_X64=1 (imaging -651692.997799, imaging-mge -85.41696632,
  imaging-dspl -3695.93899659 with the bandwidth kwarg dropped,
  multi -12932.06852498, multi-mge -6157.55707862); RTU pin scripts kept as
  `rectangular*_rtu.py` pure renames (values unchanged); all seven verified
  locally end-to-end.
- **autolens_profiling#155** + PROGRAMME/DECISIONS update on main: both
  meshes explicit via `--rect-mesh {bilinear,rtu}` +
  `_profile_cli.rect_mesh_classes`, `rect_mesh` in result JSONs, `_rtu`
  filename suffix; sampler benchmark surfaces pinned to RTU (truth bars
  valid). Phase 14 flipped to adjudicated+shipped.

## Key traps / findings

- **x64 pins:** the `_test` vmap pins require `JAX_ENABLE_X64=1` — a bare
  container's float32 vmap returns `-inf` even for the unchanged kernel-CDF
  scripts (pre-existing environment trait, not the mesh split). Diagnosed
  via an RTU control script whose historical pin also failed.
- **Stale prior keys:** `module.Class`-style JSON/YAML prior keys must use
  the real module name (`rectangular_rtu_adapt_density.RectangularRTU...`);
  the legacy `rectangular.<Class>` keys silently never matched.
- **Navigator catalogue is a per-PR CI gate** (PyAutoHands
  `regenerate_navigator.py`), not release-regenerated as assumed.
- Bilinear classes subclass the RTU ones with narrowed `__init__`
  signatures, so autofit model introspection sees only real parameters.
- Gradient guidance encoded everywhere: Bilinear likelihood is exactly
  piecewise-constant at os_pix=1 (zero gradients; certified July audit);
  imaging gradient users set os_pix>=4 or use RTU; interferometer gradient
  fitting must use RTU (no over-sampling escape hatch).

## Follow-ups

- Versioned Bilinear-vs-RTU CPU measurement in the `pixelization_numba`
  cells (`--rect-mesh bilinear` / `rtu`) — tracked on autolens_profiling#153
  and PROGRAMME Phase 14's outstanding tail.
- autolens_profiling#152 (in-flight numba-profiling branch) may need a
  trivial rename/flag reconciliation in `pixelization_numba.py` on merge.
- Notebooks + workspace_index regenerate at next release (autohands).

## Session

Web session https://claude.ai/code/session_01WtMqU3JfmyJh8GvB7jT4Et; Mind
state on branch claude/bilinear-rtu-mesh-docs-pbhsxg.

## Original prompt

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
