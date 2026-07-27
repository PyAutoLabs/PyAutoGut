## delaunay-nan-callback
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/410
- completed: 2026-07-27
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/411
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace_test/pull/226
- summary: Invalid per-lane Delaunay mesh points are intercepted at the sequential host callback without invoking qhull, while downstream JAX weights deliberately preserve a NaN figure of merit for only the poisoned lane. Dense and sparse production regressions cover all-NaN and partial poisoning, raw NaN likelihood propagation, Fitness resampling, and bit-identical finite-lane values and gradients. PyAutoArray merged as 8c5e28e and the workspace regression merged as f96aed1 after all required CI checks passed.

### Session Notes

- The callback guard alone was unsafe because sentinel tables could be laundered into finite pixel-0 mappings. The walk now refuses padded simplices as a successful result and the JAX weight boundary explicitly encodes invalid mesh state as NaN.
- The NumPy path remains unchanged to preserve its diagnostic exception behavior.
- The unchanged finite-difference Delaunay certification passed; finite sibling lanes remained bitwise identical under production vmap and direct value-and-gradient tests.
- The same callback boundary covers the sparse interferometer path associated with the intermittent qhull-NaN report.
- No RAL mirror was pulled or modified. The campaign rerun remains the external integration check.

## Original prompt

# Delaunay tables callback crashes the whole JAX run when traced points contain NaN

Type: bug
Target: autoarray
Repos:
- PyAutoArray
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft

## The bug (hit live on RAL, 2026-07-27, wsdev#117 campaign)

Under broad-start multi-start gradient descent (`af.MultiStartProdigy`,
`resurrect=True`), a start's parameter vector can go non-finite mid-trajectory.
For the pure-JAX meshes (rectangular kernel-CDF, KNN) that propagates as NaN
through the likelihood — `optax.apply_if_finite` / resurrection then handle it,
by design. For the **Delaunay mesh** the NaN-traced mesh points reach the host
qhull `pure_callback` (`_jax_delaunay_tables`), where
`scipy.spatial._qhull` raises

```
ValueError: Points cannot contain NaN
-> jax.errors.JaxRuntimeError: INTERNAL: CpuCallback error calling callback
```

and the **entire vmapped batch / process dies** — one poisoned lane kills all
16 starts. Worse, the search's persisted checkpoint holds the NaN params, so
every resume crashes instantly (RAL jobs 331197/331198/331199; logs
`/mnt/ral/jnightin/pixgrad_logs/pix_prod_delaunay-33119[7-9].err`).

**UPDATE (same day, ~14:20): the crash is NOT resurrection-specific.** The
resurrect=False retry (RAL jobs 331202/331203) died identically, before the
first 50-step checkpoint. The NaN points do not come from resurrected params —
ordinary descent trajectories reach mass configurations whose deflections (and
hence traced mesh points) are non-finite, and the callback converts what
should be a NaN log-likelihood into a process-fatal exception. The
`Fitness` where-guard cannot intervene: the exception fires DURING the forward
evaluation. Note the crash requires a batch: single-point evals at sane
parameters (truth-bar scans, the FD certification harness) never see it.

Net effect: **Delaunay is currently unusable for ANY broad-start gradient
search** — the mesh whose gradients were certified 2026-07-26 (frozen-tables)
crashes under the exact search machinery (Fit#1398/#1400) that made pixelized
search viable in #101. There is no campaign-side workaround; wsdev#117 records
the mesh as BLOCKED pending this fix.

## Fix sketch

Harden the tables callback: detect non-finite input points inside the callback
(cheap `np.isfinite` check) and return degenerate/sentinel int32 tables instead
of calling qhull, such that the downstream likelihood evaluates to NaN for that
lane — restoring the "NaN propagates, guard handles it" contract the pure-JAX
meshes obey. A lane-level guard matters: with `vmap_method="sequential"` one
bad lane must not take down the finite lanes. Add a jax_grad-style regression
(NaN param vector → finite process, NaN logL, other lanes unaffected).

Related: `active/interferometer_delaunay_intermittent_qhull_nan.md` (the
intermittent qhull NaN on interferometer) — likely the same missing guard
surfacing under a different trigger; coordinate the fix.
