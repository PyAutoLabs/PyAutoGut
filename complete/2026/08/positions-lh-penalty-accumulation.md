- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/699 (CLOSED completed)
- pr: https://github.com/PyAutoLabs/PyAutoLens/pull/700 — MERGED 2026-08-17 as `5d55825`, 3 files, +28/-8
- classification: library (PyAutoLens) — bug, severity high; CP-1 of the inference programme (autolens_profiling#134, PROGRAMME.md §2.1)
- branch: `feature/positions-lh-penalty-accumulation`
- worktree: `~/Code/PyAutoLabs-wt/positions-lh-penalty-accumulation` — **release pending** (merge happened from a remote session; free the worktree in the next laptop session or let repo_cleanup flag it)

## What was wrong

`AnalysisLens.log_likelihood_penalty_from` (`autolens/analysis/analysis/lens.py:163-181`)
overwrote its accumulator with each entry's penalty and then added the variable
to itself, so the analysis subtracted **2x the LAST** `PositionsLH` penalty and
silently discarded every earlier entry in `positions_likelihood_list`. With one
entry (every SLaM stage) that is 2x the documented
`1e8 * (max_separation - threshold)` fence; with N entries
(double-source-plane / multi-plane) all but the last were lost. Blocked the
entire PositionsLH benchmarking arc — every positions experiment would have
measured an undocumented target.

## Fix

Accumulation is now a true sum (`x = x + y`, trivially `xp`-safe under `jnp`);
docstring aligned to the actual 0.0-array (not `None`) no-penalty return, kept
for the JAX path. Tests that PINNED the bug repinned: imaging single-penalty
`-44097289521.73` → `-22048644768.18` (exactly half — the 2x), double-plane
`-44097289521.73` → `-44140499627.75` (the true sum, now distinct from the
single-penalty value), interferometer `-44097289569.2` → `-22048644815.85`.
New regression assertions: analysis penalty == sum of each entry's own
`log_likelihood_penalty_from`, the two per-plane penalties genuinely differ,
single-entry == the entry's value exactly (no 2x). Full suite 538/538; PR CI
green (unittest 3.12/3.13 + docs-build).

## Science impact (release-notes item)

Inside the threshold the penalty is exactly 0 either way — converged posteriors
and positions-free results unchanged. Outside it the fence slope **halves**
from the undocumented 2e8/arcsec to the documented 1e8/arcsec, so likelihood
values in penalized regions shift. Multi-plane penalty stacking is corrected —
previously only the last plane counted.

## Traps and findings

- **THE TESTS ENCODED THE BUG, AND ITS SIGNATURE HID THE DISCARD.** The
  double-plane test asserted the SAME value for one and for two penalties —
  under 2x-last, adding a second penalty changes nothing the tolerance could
  see. The corrected two-plane value shows the per-plane penalties genuinely
  differ; the regression test now pins the sum explicitly.
- **CONFLICT OVERRIDE precedent used:** PyAutoLens was co-claimed by
  `version-stamp-sync-guards`; `worktree_check_conflict` exits 1. FILE-DISJOINT
  verified (that branch touches only `autolens/__init__.py` + `release.sh`) and
  a deliberate, human-directed override was recorded in active.md rather than
  blocking.
- **Sizing-proxy miss:** the Brain Bug Agent scored this large(7)/split via the
  prose-length proxy; correctly overridden to small/single-PR — the fix was one
  accumulation line + docstring + test repins. Detailed prompts overcount.
- **Registry-edit trap (same session):** a blanket `sed` status edit briefly
  clobbered the stored-sample task's status line in active.md — caught and
  restored immediately. Scope registry edits to the task's own `##` section.

## Original prompt

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
