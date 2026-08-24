# interferometer/jax_grad/gradient.py: eager and jitted likelihoods diverge ~5e-7 on Python 3.13 only

Type: bug
Target: autolens_workspace_test
Repos:
- @autolens_workspace_test
- @PyAutoArray
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Filed: 2026-08-24

## The failure

`@autolens_workspace_test/scripts/interferometer/jax_grad/gradient.py` runs three
`util.assert_eager_jit_consistent` checks. The third — Variant B,
`RectangularRTUAdaptDensity` mesh + `reg.Adapt()` on the sparse-operator path
(`dataset.apply_sparse_operator(use_jax=True)`) — fails on **Python 3.13 only**:

```
eager   -3164.0196392095145
jitted  -3164.021216643465
```

That is ~5e-7 relative, against the guard's `rtol=1e-10`
(`@autolens_workspace_test/scripts/misc/util.py:185`). The guard exists precisely
for this: its message reads *"possible `pure_callback` constant-folding; do not
trust jitted gradients"*, and it is the gate that must pass before the variant's
finite-difference/AD gradient comparison means anything.

## Measurement

2026-08-24 retime sweep, 5 repeats per Python leg, 300 s cap
(run 32741386752; see autolens_workspace_test#274):

- **3.13: deterministic failure, 5/5**, same two values every repeat.
- **3.12: fully green, 61.2 s** — 7% of its 900 s cap.
- The *eager* value is identical on both legs. Only the **jitted** value moves,
  and only on 3.13.
- Not a timeout and not performance. The script's old
  `# SLOW 2026-07-14 - flakes at the 1800s cap (PyAutoHeart#74)` marker was a
  misdiagnosis; it has been rewritten to `NEEDS_FIX 2026-08-24` in
  `@autolens_workspace_test/config/build/no_run.yaml` pointing here.

Eager agreeing across legs while jitted does not is the informative part: the
Python-version-dependent behaviour is inside compilation, not in the model, the
dataset, or the mesh.

## Task

1. **Localise the divergence inside the jitted graph.** Variants A and C pass on
   both legs, so it is not the sparse operator or `assert_eager_jit_consistent`
   in general — it is specific to `RectangularRTUAdaptDensity` + `reg.Adapt` on
   the sparse path. Bisect within that variant (regularization matrix, mesh
   density/CDF transform, the linear solve) to find which sub-computation's
   jitted value moves on 3.13.
2. **Test the `pure_callback` constant-folding hypothesis the guard names.** Any
   `pure_callback` boundary in this path is a prime suspect: if XLA folds a
   callback result on one leg and not the other, the jitted graph is evaluating
   something the eager path is not. If confirmed, the fix is library-side —
   pin/annotate the callback so it cannot be constant-folded — not a tolerance
   change in the script.
3. **Rule the alternative in or out**: the same jaxlib/XLA version compiling
   differently under 3.13 (fastmath/fusion or reduction-order differences),
   making this a genuine ~5e-7 numerical difference in a solve rather than a
   correctness bug. Compare the jaxlib/XLA versions actually installed on each
   leg first — if they differ, that is the likelier story and this becomes an
   environment-pinning task.
4. **Only then decide about the tolerance.** A ~5e-7 disagreement in a linear
   solve may be legitimate, but `rtol=1e-10` is a deliberate constant-folding
   tripwire; loosening it to make the script green would disarm the guard for
   every variant that uses it. If the conclusion really is "this magnitude is
   expected here", the tolerance change must be argued in the commit and scoped
   to this variant, not applied to `util.assert_eager_jit_consistent` wholesale.

## Why it matters

The variant's whole purpose is that this mesh must carry live, strictly
FD-matched gradients on the sparse path, which has no over-sampling to fall back
on. While the eager/jit guard fails, the jitted gradients it protects cannot be
trusted, and the script stays out of coverage on 3.13 — the leg where the problem
lives.

## Acceptance

- A named cause: `pure_callback` constant-folding, an XLA/jaxlib compilation
  difference, or a genuine numerical property of the solve — with evidence, not
  a tolerance bump standing in for a diagnosis.
- `scripts/interferometer/jax_grad/gradient.py` green on **both** 3.12 and 3.13.
- `assert_eager_jit_consistent` still able to catch the constant-folding it was
  written to catch.
- The `interferometer/jax_grad/gradient.py` `NEEDS_FIX` entry is removed from
  `@autolens_workspace_test/config/build/no_run.yaml`, restoring mega-run
  coverage on 3.13.
