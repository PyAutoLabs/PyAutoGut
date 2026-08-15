# Find what kills MGE multi-start lanes — it is not the ell_comps plateau

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

# Find what kills MGE multi-start lanes — it is not the ell_comps plateau

@autolens_profiling

The frozen-lane counter shipped (PyAutoFit #1475, PyAutoGalaxy #572) and its
first run cleared the ell_comps plateau as a suspect for the MGE cell — and
surfaced a much larger effect nobody has characterised.

Real `imaging/mge` cell (production dataset, model and analysis via
`build_for_cell`; 16 starts x 150 steps, cloud CPU, 352s):

| counter | lane-steps | share |
|---|---:|---:|
| `n_value_nan_lane_steps` | 1498 | **62.42%** |
| `n_grad_nan_lane_steps` | 9 | 0.38% |
| `n_constrained_lane_steps` | 0 | 0.00% |

The population fell from `alive 16/16` to `alive 2/16`. **Roughly seven of every
eight starts die, and the best-fit is being found by two survivors.**

## Why this is worth a task

It contradicts a documented assumption. `AbstractMultiStartGradient`'s
`resurrect` docstring states the default `resurrect=False` is safe because "the
parametric (MGE-class) cell has only the measure-zero singularity, so the
`apply_if_finite` guard suffices". The measurement says otherwise: value-NaN,
not gradient-NaN, dominates at 62% of lane-steps, and `apply_if_finite` does not
rescue a value-NaN lane — it only zeroes the step, so the lane stays dead and
`resurrect=False` never redraws it.

If that holds at production budget, the MGE cell is running at a small fraction
of its nominal start count, and `n_starts` is not buying what it appears to.

## What to establish

- **Where the NaNs come from.** Which parameters/regions produce a non-finite
  likelihood in the MGE cell — the mask edge, a Gaussian `sigma` collapsing, the
  linear inversion, the `sqrt` at r=0, something else. The hazard index in this
  repo is the natural place to look first and to record the answer.
- **When they happen.** Deaths concentrated in the first steps (bad draws that
  `_broad_starts` should have filtered) mean something different from deaths
  accumulating throughout (trajectories walking into a wall).
- **Whether `resurrect=True` recovers the budget** on this cell, and what it
  costs. The docstring says it is for pixelized sources; this evidence suggests
  the parametric cell may need it too.
- **Whether it reproduces at production budget and on GPU**, and across seeds.
  The measurement above is one seed at reduced budget.

## Boundary

Investigation and measurement, in `@autolens_profiling`. Do not change the
`resurrect` default or any search behaviour as part of this — if the evidence
supports a change, that is a separate PyAutoFit task with its own benchmark
impact, since it would shift every existing multi-start result.

## Provenance

Measured 2026-08-15 with the frozen-lane counter; see
`complete/2026/08/frozen-lane-counter.md` for the full run, the positive control
that validates the zero, and the environment notes (`jaxnnls` is a required
extra; the runner writes into `dataset/`).

<!-- formalised by the Intake (Conception) Agent on 2026-08-15 from file:/tmp/claude-0/-home-user/ef0adef1-5fcd-5111-9cdf-bcb1014fc23d/scratchpad/nan_death_prompt.md -->
