# Count frozen lanes in the multi-start gradient search

Type: feature
Target: PyAutoFit
Repos:
- PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

@PyAutoFit

Add a third lane counter to `AbstractMultiStartGradient._nan_lane_counts`
(`autofit/non_linear/search/mle/multi_start_gradient/search.py:219-255`).

It counts two disjoint failure modes today — **value-NaN** (likelihood
undefined; the death `resurrect` triggers on) and **gradient-NaN** (defined but
not differentiable; `apply_if_finite` zeroes the update). A third mode escapes
both: a lane whose value is finite and whose gradient is finite but **exactly
zero**, sitting on a saturating plateau.

## Why it matters

The reference case is the ellipticity magnitude clamp `jax.lax.min(fac, 0.999)`
in PyAutoGalaxy's `convert.py:71-77`. Past `|ell_comps| >= 0.999` the axis ratio
pins at `q = 5.0025e-4` and the derivative w.r.t. both components is exactly
zero. For a multi-start gradient search that is an absorbing trap:

- Starts are safe: `_broad_starts` draws in the unit cube at `(0.15, 0.85)`,
  capping start magnitude near 0.44 under the default `TruncatedGaussian(0, 0.3)`.
- But `optax.apply_updates(params, updates)` (`search.py:743`) steps the physical
  vector with no re-projection into prior limits, so trajectories can walk in.
- Once inside there is no restoring force, so the lane cannot leave.
- `apply_if_finite` and `resurrect` are both no-ops here — value and gradient are
  finite.
- `multi_start_prodigy_autoconv` runs `check_for_convergence=True`, so frozen
  lanes flatten the figure of merit and can false-trigger early stopping.

A frozen lane is therefore indistinguishable from a converged one in the
figure-of-merit trace, which is exactly the hazard `_nan_lane_counts` was
written to expose for the gradient-NaN case.

## Scope

Instrumentation only. Add the count alongside the existing two, accumulate it
across steps, record it into `search_internal`, restore it on resume, and report
it on the progress line — mirroring `n_value_nan_lane_steps` and
`n_grad_nan_lane_steps` exactly. Keep it pure-NumPy and free of search state so
it stays directly testable like its two siblings.

The search must produce identical results with the counter present. Do not add a
penalty term, and do not touch `resurrect`, `apply_if_finite`, the convergence
check, stepping behaviour, or the clamp itself.

## Decisions to make

- Keep the buckets disjoint: a lane already counted as value-NaN or gradient-NaN
  must not also count as frozen.
- Define "exactly zero" — all coordinates versus any coordinate, and exact `== 0`
  versus a threshold. An exact test is the honest default for a `lax.min`
  plateau, but the realistic case is a partially frozen lane (ellipticity dead,
  other coordinates live), which is the more useful signal.
- Do not force a per-step device sync if it costs measurable run time. The
  existing NaN accounting measured 0.0004% of step time; stay in that class.

<!-- formalised by the Intake (Conception) Agent on 2026-08-15 from file:/tmp/claude-0/-home-user/ef0adef1-5fcd-5111-9cdf-bcb1014fc23d/scratchpad/frozen_lane_counter.md -->
