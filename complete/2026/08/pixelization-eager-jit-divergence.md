## pixelization-eager-jit-divergence

- issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/580
- completed: 2026-08-21
- library-pr: https://github.com/PyAutoLabs/PyAutoGalaxy/pull/581 (merged d1b46b9)
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace_developer/pull/127 (merged 77ca9d3)

Investigated the reported eager-vs-JIT log-evidence divergence in
`jax_profiling/jit/imaging/pixelization.py`. **Verdict: not a library bug** —
but chasing it surfaced a real library bug, a broken script, and a silent
transform swap that a stale regression pin had been masking for a month.

**Library fix (PyAutoGalaxy#581).** `Basis.image_2d_list_from` built the
zero placeholder for its `LightProfileLinear` members as
`Array2D(values=..., mask=grid.mask)`, assuming a masked `Grid2D`. Evaluating a
basis containing a linear light profile on a `Grid2DIrregular` — the grid type
JIT-traced likelihood paths use — raised `AttributeError: Grid2DIrregular does
not have attribute mask`, making any such path with an MGE lens light
unreachable. Now dispatches on grid type (`ArrayIrregular` vs `Array2D`),
mirroring `ArrayMaker.via_grid_2d` / `via_grid_2d_irr`. 1113 tests pass.

**The reported divergence — two causes, both settled, neither a bug.**
(1) The script fed the step-11 mapper-only H (1225) into an evidence whose D and
F span every linear object (1285 = source pixels + 60 linear MGE Gaussians) — a
hard shape error on current main. The MGE columns are unregularized, so the full
H is singular and `slogdet(H)` is `-inf`; `Inversion.log_det_*` evaluates both
log-det terms on the *reduced* (mapper-only) matrices, and the script now
mirrors that. Rebuild matches `figure_of_merit` to 13 s.f.
(2) The residual step-by-step gap is the fnnls non-negative active set (362 of
1285 pinned at exactly zero; 777 negative under an unconstrained solve), not
"floating-point drift" as the old comment claimed. Comment corrected; the
step-by-step value, previously printed and never asserted, now carries its own
pin. Prompt suspects 1/2/4 falsified — `FitDataset.figure_of_merit` uses exactly
the five-term formula the script implements.

**The constant was RESTORED, not re-pinned.** My first pass re-pinned to the
kernel value and blamed accumulated library drift — inferred from a commit
message, not measured. The user challenged it and the measurement falsified me.
PyAutoArray `22b28463` (#402, 2026-07-23) gave the unchanged class name
`RectangularAdaptDensity` the kernel-CDF transform; it had meant rank-CDF when
the constant was pinned 2026-05-11. Naming `RectangularBilinearAdaptDensity`
explicitly reproduces `24746.105672366088` **bit-for-bit**, preserving the pin's
pre-#402 history. Four independent lines agree: cross-split measurement
(pre-split `RectangularAdaptDensity` == post-split RTU == 25004.71903495436, so
RTU really is a pure rename); `git log -S` showing the kernel value was NEVER
pinned in the script's history; era artifacts
`results/jit/imaging/pixelization/{hpc_a100,local_gpu,local_cpu}_fp64.json` (two
GPUs + CPU, two library versions) all bit-identical to the constant; and code
identity — May-era `create_transforms` is line-for-line identical to today's
`create_transforms_rank`.

**TRAPS**
- A **bit-identical** match across months is strong evidence *against* generic
  drift: any other change touching the value would break exactness. Check
  `.hex()`, not printed precision.
- Never attribute a constant's movement from commit messages — build the old
  checkout and measure (`git worktree add <scratch> <sha>^ --detach` + a
  PYTHONPATH substitution of the one repo is minutes, and decisive).
- A stale pin can **hide** a silent semantic change. Ask what the *name* meant
  when it was pinned. Restoring the fiducial beats re-pinning, which launders the
  change away.
- **Never blanket-rename these mesh symbols — relabel by DATE.** I made this
  mistake mid-task on `gradient/README.md` and had to fix it (`08d5d86`): that
  file is mixed, carrying 2026-07-09 rank rows and a 2026-07-26 kernel section,
  and states the distinction itself. ≤2026-07-09 → Bilinear; ≥2026-07-26 → RTU.
- The transform lives in `mesh/interpolator/rectangular.py`, **not** the mesh
  class — grep the interpolator to identify which CDF a mesh uses.

**Carried forward** into
`draft/feature/autoarray/rectangular_bilinear_rtu_mesh_split.md` (that campaign
owns the remaining ~40 files): the two `misc/pixelization_spline_*.py` scripts
broken on the deleted `RectangularSplineAdaptDensity`; the three renamed sibling
scripts that are symbol-verified but never executed; the dated-relabel trap; and
a caution on Goal 3 — check whether each `_test` pin's fiducial actually changed
before overwriting it, since an unchanged fiducial should reproduce its
pre-#402 value exactly and that match is a free correctness check.

## Original prompt

# Investigate eager `FitImaging.figure_of_merit` vs JIT/step-by-step divergence in rectangular pixelization

Type: bug
Target: PyAutoLens
Difficulty: too-large
Autonomy: supervised
Priority: high
Status: formalised

## Context

Surfaced by the eager-numpy regression assertions added in
`jax_profiling/imaging/pixelization.py` (PR from
`PyAutoPrompt/issued/eager_numpy_regression_assertions.md`).

When the rectangular pixelization script runs, it computes the same
`log_evidence` via three supposedly-equivalent numpy/JAX paths and gets two
different answers:

```
figure_of_merit (log_evidence) = -1338814172.1831784   ← eager FitImaging
log_evidence (step-by-step)    = -1338521802.3596904   ← JIT-equivalent numpy rebuild
log_evidence (inv matrices)    = -1338814172.1831782   ← numpy rebuild from eager matrices
log_evidence (reference)       = -1338814172.1831784   ← same as figure_of_merit
full log_likelihood (JIT)      = -1338521802.3596945   ← JIT full pipeline
```

The split is:

- **Cluster A (eager):** `FitImaging.figure_of_merit`, `log_evidence (reference)`,
  and `log_evidence (inv matrices)` all agree on `-1338814172.18`.
- **Cluster B (JIT / step-by-step):** `log_evidence (step-by-step)` and
  `full log_likelihood (JIT full pipeline)` agree on `-1338521802.36`.

The two clusters differ by ~292k in absolute value (~0.02% relative) — well
above float64 round-off and well above the `rtol=1e-4` used in the regression
assertions. The script's own internal assertion

```
Assertion PASSED: inversion-matrix log_evidence matches FitImaging.log_evidence
```

confirms the eager and "inv matrices" numpy rebuilds agree with each other.
The JIT-style rebuild (`step-by-step`) disagrees with that pair and instead
matches the JIT full-pipeline result.

So something is happening in `FitImaging`-eager that is **not** the same as
re-running the same math in a JIT-style numpy pipeline. Currently the
pixelization script pins two separate regression constants — the original
`EXPECTED_LOG_EVIDENCE_HST` for the JIT path, and a new
`EXPECTED_LOG_EVIDENCE_HST_EAGER` for the eager path (with a FIXME pointing
at this prompt).

## Task

Identify which cluster is correct (or whether they're both reasonable results
of a numerically-legitimate-but-subtle difference in accumulation order /
regularization), then either:

1. **Fix the divergent path** so both clusters converge, and collapse the two
   constants back into one.
2. **Document the divergence as genuine** (e.g. one path includes a term the
   other legitimately omits), update code comments accordingly, and keep the
   two constants but remove the FIXME framing.

Either outcome is fine — the goal is to understand *why* the two numpy
computations of the same quantity disagree and to make the code's treatment
of them honest.

## Where to look

The disagreement is specifically in the **rectangular pixelization** log-evidence
stack. Likely suspects (in rough order of plausibility):

1. **`FitImaging.figure_of_merit` for `Inversion`-based fits** — does it use a
   different formulation (Bayesian evidence with full regularization term)
   than the step-by-step reconstruction in the script does?
   - `PyAutoLens/autolens/imaging/fit_imaging.py`
   - `PyAutoArray/autoarray/inversion/inversion/abstract.py::log_evidence`
     and related helper properties.

2. **Regularization matrix handling** — the eager path may be building the
   full regularization contribution via `log_det_regularization_matrix_term`
   whereas the step-by-step may be using a shortcut that agrees with what
   the JIT path does.

3. **Mapping matrix numerical accumulation order** — check whether
   `mapping_matrix` and `blurred_mapping_matrix` are computed with different
   intermediate dtypes or summation orders in the eager vs step-by-step
   pipelines.

4. **`inversion.log_evidence` vs `fit.figure_of_merit`** — check whether
   `FitImaging.figure_of_merit` returns
   `inversion.log_evidence_with_regularization` or just
   `inversion.log_likelihood`. The script's "step-by-step" may be comparing
   against a different decomposition.

Not suspected:

- The simulator is deterministic (seeded), and `imaging/delaunay.py` (using
  a different mesh but same overall fit pattern) does NOT show this
  divergence — its eager `figure_of_merit` matches its `EXPECTED_LOG_EVIDENCE_HST`
  bit-for-bit. So the bug is specifically in the rectangular-pixelization
  code path, not in the general `FitImaging` + `Inversion` framework.

- The interferometer pixelization script (`jax_profiling/interferometer/pixelization.py`)
  also passes the eager assertion cleanly — `figure_of_merit_ref ≈
  EXPECTED_LOG_EVIDENCE_SMA`. So it's not a universal pixelization issue,
  it's imaging + rectangular specifically.

## Verification

After fixing:

```bash
source ~/Code/PyAutoLabs-wt/<task-name>/activate.sh
cd autolens_workspace_developer
python jax_profiling/imaging/pixelization.py
```

Expect:

- `figure_of_merit (log_evidence)` == `log_evidence (step-by-step)` to within
  float64 round-off (or a documented, justified gap).
- `EXPECTED_LOG_EVIDENCE_HST_EAGER` can be removed and the eager assertion
  can revert to using `EXPECTED_LOG_EVIDENCE_HST` alongside the JIT/vmap
  assertions.
- Delete the FIXME comment block.

## Affected repos

- `PyAutoLens` and/or `PyAutoArray` (library — most likely `PyAutoArray`
  inversion code, possibly `PyAutoLens/fit_imaging.py`)
- `autolens_workspace_developer` (script — remove the FIXME and the second
  constant once the library fix lands)

## Suggested branch

`feature/pixelization-eager-jit-divergence`

## Notes

- Don't start by bumping either constant. The script's internal
  "inv matrices vs step-by-step" split is the debugging starting point —
  narrow down which numpy computation is authoritative, then fix the other.
- The divergence is ~0.02%, which is well within the regime where Bayesian
  model comparison decisions could flip, so treat this as a real bug until
  proven otherwise (not just a rounding artefact).

<!-- formalised retroactively by the Intake (Conception) Agent on 2026-07-08 -->
