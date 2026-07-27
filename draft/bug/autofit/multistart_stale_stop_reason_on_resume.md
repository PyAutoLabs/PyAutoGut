# MultiStart keeps a stale stop_reason when a finished search is resumed with a larger n_steps

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: safe
Priority: low
Status: draft

## The bug

`AbstractMultiStartGradient._fit` restores `stop_reason` from the loaded
`search_internal` on the resume path
(`autofit/non_linear/search/mle/multi_start_gradient/search.py:~296`), and only
ever reassigns it inside the loop when one of two conditions fires
(`search.py:413-416`):

```python
if converged:
    stop_reason = "converged"
elif total_steps >= self.n_steps:
    stop_reason = "max_steps"
```

Take a search that finished with `stop_reason="max_steps"`, then resume it with a
larger `n_steps` (the documented way to extend a budget). The `while` guard
allows the loop to continue (`stop_reason != "converged"`), but for every chunk
before the *new* ceiling is reached neither branch fires — so the restored
`"max_steps"` survives and is written into each intermediate `search_internal`
checkpoint.

Effect: a search that is actively still running reports
`samples_info["stop_reason"] == "max_steps"` at every intermediate checkpoint.
Anything reading results mid-run — the aggregator, a results inspector, a
monitoring script — sees a finished-looking search that is not finished. The
final checkpoint does correct itself, so this is a mid-run reporting defect
rather than a wrong final answer, hence the low priority.

## Fix

Reset `stop_reason = None` when entering the loop on a resume that is going to
run further steps (i.e. whenever `total_steps < self.n_steps`), so the value
always describes the *current* run rather than a previous one. The simplest form
is to clear it once before the `while`, since any real stop reason is
re-derived inside the loop anyway.

Check the interaction with the `converged` short-circuit while doing so: a
genuinely converged search must still refuse to resume into more steps (that is
what `stop_reason != "converged"` in the `while` guard is for), so the reset must
not clear a `"converged"` marker.

Add a NumPy-only test over the stop-reason state machine — construct the
`search_internal` dict directly and assert the reported `stop_reason` /
`converged` in `samples_via_internal_from`, rather than running a JAX fit.

## Provenance

Surfaced by an adversarial review (Codex `gpt-5.6-sol`) of PR#1421 and confirmed
by reading the code; it pre-dates that branch and was deliberately left out of it.
