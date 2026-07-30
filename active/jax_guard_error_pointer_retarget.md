# Retarget the xp=np guard's ValueError pointer from lens_calc.py to using_jax.py

Type: docs
Target: autoarray
Repos:
- PyAutoArray
Difficulty: small
Autonomy: safe
Priority: normal

## Context

`PyAutoArray/autoarray/structures/decorators/abstract.py` (~line 55) raises the
JAX pairing-rule guard:

```
ValueError: Called {func} with xp=np but the input grid is JAX-backed
(grid.use_jax=True). Inside @jax.jit, pass xp=jnp explicitly to the library
call. See the autolens_workspace `scripts/guides/lens_calc.py` `__JAX__`
section (Phase 5d) for the JIT-it-yourself pattern.
```

The `guides-jax-to-using-jax` task (autolens_workspace#412, PRs
autolens_workspace#415 + autogalaxy_workspace#195, 2026-07-30) deleted
`lens_calc.py`'s `__JAX (JIT-it-yourself)__` section and consolidated the
JIT-it-yourself pattern into `scripts/guides/using_jax.py` (now a runnable,
smoke-tested script). Once those PRs merge, this error message points at a
section that no longer exists.

## Scope

Change the final sentence of the guard message to point at
`autolens_workspace/scripts/guides/using_jax.py` (drop the "(Phase 5d)"
internal-phase reference — it should never have shipped in a user-facing
error). One-line library docs fix; no behaviour change. Check for any sibling
copies of the message (grep `Phase 5d` and `lens_calc.py` across PyAutoArray)
and sweep them in the same diff.

## Coordination

Gate on autolens_workspace#415 merging first, so the pointer's target exists
on main before the message changes.
