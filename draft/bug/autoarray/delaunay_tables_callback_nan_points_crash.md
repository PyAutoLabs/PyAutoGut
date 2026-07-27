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

Net effect: **Delaunay is currently unusable for broad-start gradient search
with resurrection** — the mesh whose gradients were certified 2026-07-26
(frozen-tables) cannot exploit the NaN-mortality machinery (Fit#1400) that
made pixelized search viable in #101. Campaign fallback is resurrect=False
(latch-and-freeze), which survives only because params then stay at their last
finite values.

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
