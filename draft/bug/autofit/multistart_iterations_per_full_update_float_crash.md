# MultiStart gradient step loop crashes when iterations_per_full_update < remaining steps

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: safe
Priority: high
Status: draft

## The bug (hit live on RAL, 2026-07-27, wsdev#117 campaign)

`abstract_search.py:219` unconditionally coerces `iterations_per_full_update`
to **float** (`float(iterations_per_full_update or conf...)`). The multi-start
gradient `_fit` (`autofit/non_linear/search/mle/multi_start_gradient/search.py:284`)
then computes

```python
iterations = min(self.iterations_per_full_update or self.n_steps, steps_remaining)
...
for _ in range(iterations):   # line 298
```

`range(float)` → `TypeError: 'float' object cannot be interpreted as an
integer` — but **only when the cadence is below the remaining budget**, because
`min(float, int)` returns the int operand otherwise. The config default is huge,
so every existing run took the `steps_remaining` branch and the crash never
fired; any user who passes a real checkpoint cadence (e.g.
`iterations_per_full_update=50` with `n_steps=3000`) crashes on step-loop entry.
Six RAL chain jobs (331182-331190) died on it back-to-back.

Evidence: `/mnt/ral/jnightin/pixgrad_logs/pix_prod_*-33118[5-9].err`; workspace
hotfix (post-construction int overwrite) in
`autolens_workspace_developer/searches_minimal/pix_prodigy.py` (branch
`feature/pix-prodigy-cpu`) — remove it when this ships.

## Fix

`iterations = int(min(...))` in `_fit` (the float coercion in abstract_search
serves inf-like config values and is shared by other searches — casting at the
consumer is the minimal, non-regressing change). Add a unit test that runs a
MultiStart search with `iterations_per_full_update` smaller than `n_steps`
(numpy objective — library unit tests stay JAX-free) and asserts the step loop
executes + checkpoints.
