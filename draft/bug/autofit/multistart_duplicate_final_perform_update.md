# MultiStart gradient runs the expensive final perform_update twice

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: safe
Priority: normal
Status: draft

## The bug

`AbstractMultiStartGradient._fit` performs its own final update with
`during_analysis=False`
(`autofit/non_linear/search/mle/multi_start_gradient/search.py:430-439`):

```python
is_final = converged or total_steps >= self.n_steps
self.perform_update(..., during_analysis=not is_final, ...)
```

`AbstractSearch.start_resume_fit` then **unconditionally** performs the same
final update immediately after `_fit` returns
(`autofit/non_linear/search/abstract_search.py:704-710`, `during_analysis=False`).

So every MultiStart run does the full final update twice: final sample output,
latent-variable computation, visualization and profiling all run a second time.
On a pixelized or GPU fit that is a substantial, entirely wasted cost at the end
of every search — the exact work `during_analysis=False` exists to do once.

## Why this is MultiStart's bug and not the framework's

Every other search calls `perform_update` inside `_fit` with
`during_analysis=True` **unconditionally**, leaving the single `False` call to
`start_resume_fit`. Verified:

- `mcmc/emcee/search.py:238` → `during_analysis=True`
- `mle/bfgs/search.py:219` → `during_analysis=True`
- `nest/nautilus/search.py:438` → `during_analysis=True`

MultiStart's `is_final` branch is the outlier. The house pattern is that `_fit`
only ever emits *intermediate* updates.

## Fix

Pass `during_analysis=True` unconditionally in the MultiStart step-loop update
and delete the `is_final` computation, matching every sibling search — unless
`_fit` genuinely needs a final-flavoured update before returning, in which case
say why and fix the duplication at the other end instead.

Check the convergence/early-stopping path too: when the search stops early, the
last in-loop update is the one carrying `converged`/`stop_reason` into
`samples_info`, so confirm that information still reaches the final samples via
the `search_internal` dict `_fit` returns (it should — `start_resume_fit`'s
update is built from that same dict).

Add a regression test that counts `perform_update` calls with
`during_analysis=False` across one search (NumPy-only — stub or monkeypatch
rather than running a JAX fit; the library suite stays JAX-free).

## Provenance

Surfaced by an adversarial review (Codex `gpt-5.6-sol`) of PR#1421 and confirmed
by reading the call sites; it pre-dates that branch and was deliberately left
out of it.
