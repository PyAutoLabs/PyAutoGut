# PositionsLH penalty accumulation returns 2x the LAST penalty, discarding the rest

- Work type: bug
- Target: PyAutoLens
- Sized: small
- Origin: inference-programme planning pass 2026-08-17 (plan §2.1, CP-1); human: "thats
  worrying if theres a bug in soemthing so important so defo check".

## Original request (verbatim, from the programme plan critical path)

> CP-1 · PositionsLH defect verify + fix (hours, laptop). Unblocks the entire positions
> arc; every later positions result depends on it.

## The bug (VERIFIED against main by direct read, 2026-08-17)

`AnalysisLens.log_likelihood_penalty_from` (`autolens/analysis/analysis/lens.py:163-181`):

```python
log_likelihood_penalty = self._xp.array(0.0)
if self.positions_likelihood_list is not None:
    for positions_likelihood in self.positions_likelihood_list:
        if positions_likelihood is not None:
            log_likelihood_penalty = (          # <-- OVERWRITES the accumulator
                positions_likelihood.log_likelihood_penalty_from(...)
            )
            log_likelihood_penalty += log_likelihood_penalty   # <-- doubles itself
    return log_likelihood_penalty
```

- One penalty in the list (the common case, incl. every SLaM stage): returns **2x** the
  documented `1e8 * (max_separation - threshold)` penalty.
- N penalties (double-source-plane / multi-plane usage): returns 2x the **last** entry
  only; all earlier penalties silently discarded.
- Docstring also promises `None` when there is no penalty but the code returns a 0.0
  array (the JAX-safe behaviour) — align the docstring, keep the behaviour.

Existing tests PIN the bug: `test_autolens/imaging/model/test_analysis_imaging.py:101`
and `:126` assert the SAME value (-44097289521.734665) for one and for two penalty
objects — exactly the 2x-last signature. Both expected values need recomputing after
the fix (single: base - p; two-plane: base - (p0 + p1)).

## Fix

Accumulate: `log_likelihood_penalty = log_likelihood_penalty + penalty_i` (JAX-traceable,
no in-place mutation semantics needed). Update the two pinned test values, add a
regression test asserting (a) two penalties = sum of the two individual penalties,
(b) one penalty = exactly the `PositionsLH.log_likelihood_penalty_from` value (no 2x).

## Science impact (record in PR)

Inside threshold the penalty is exactly 0 either way — converged posteriors and all
positions-free results unchanged. Outside threshold the fence slope halves (2e8 -> 1e8
per arcsec): early-search likelihood values in penalized regions change, and
multi-plane penalty stacking is corrected. Classify as bug-fix restoring documented
behaviour; note in release notes that penalized-region likelihood values shift.

## Do-not

- Do not change the penalty formula, threshold semantics, or `PositionsLH` itself.
- Do not return `None` (JAX path needs the 0.0 array); fix the docstring instead.
