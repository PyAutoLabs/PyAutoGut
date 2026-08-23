# Phase 2: are the SLOW-marked jax_likelihood/jax_grad entries slow, or is this stall wearing a different label?

Type: bug
Target: ci
Repos:
- @autogalaxy_workspace_test
- @autolens_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised
Epic: jax-compile-stall
Phase: 2
Campaign: bug/ci/jax_vmap_jit_compile_stall.md (Phase 2 — the classification; consumes phase 1's evidence)
Filed: 2026-08-23

## The question

Step 1 of the campaign, on its own. Eight entries — six
`interferometer/jax_likelihood/*` and two `jax_grad/*` — were SLOW-skipped on
2026-07-14 for "flaking at the 1800s cap" (PyAutoHeart#74). A **SLOW** marker
says *make it faster*. A **stall** says *it never finishes*. Those route to
completely different places, and the Profiling Agent has been handed the first
description for a set that may partly belong to the second.

Nothing in the current markers distinguishes them, because nothing measured the
distribution — a single observation at a cap looks the same either way.

## Method

A slow script has a **tight timing distribution**. A stalling one is
**bimodal**: tens of seconds when it completes, the full cap when it does not.
That is the discriminator, and it needs repeats, not one more run.

1. Re-time each entry against the cap that actually applies to it (300s smoke,
   1800s release), N repeats each, both Python versions in the matrix. The
   `rectangular_mge.py` result that passed on 3.13 and stalled on 3.12 **on the
   same commit** shows one run per entry settles nothing.
2. Where phase 1's watchdog fires, keep the traceback — a stalled entry
   identifies itself directly and does not need the distribution argument.
3. Classify each entry: genuinely slow, this stall mislabelled, or still
   ambiguous after N runs.

## Entries in scope

The eight SLOW entries above, plus the three already carrying the stall
signature, so the whole set is classified by one consistent method:

| Entry | Repo | Current marker |
|---|---|---|
| `multi_dataset/jax_likelihood/rectangular.py` | autogalaxy_workspace_test | NEEDS_FIX 2026-08-01 |
| `imaging/jax_likelihood/mge_group.py` | autogalaxy_workspace_test | NEEDS_FIX 2026-08-23 |
| `multi_dataset/jax_likelihood/delaunay.py` | autolens_workspace_test | NEEDS_FIX 2026-08-01 (#245) |
| six `interferometer/jax_likelihood/*` | both | SLOW 2026-07-14 |
| two `jax_grad/*` | both | SLOW 2026-07-14 |

`imaging/jax_likelihood/rectangular_mge.py` (stalled on 3.12, passed on 3.13,
same commit) and `delaunay_mge.py` (disabled outright — `jax 0.7` removed
`jax.interpreters.xla.pytype_aval_mappings`, a genuinely different cause) are
reference points, not entries to re-time.

## Acceptance

- Every entry above classified, with the timing distribution that supports the
  classification recorded — not asserted.
- Every marker in the `no_run.yaml` files and `smoke_tests.txt` rewritten to
  carry its real reason, so a SLOW marker means slow and nothing else.
- The answer written down somewhere the Profiling Agent reads, so it stops
  chasing speedups on scripts that are hanging.
- No script is un-quarantined by this phase — restoring coverage is phase 3,
  and depends on the fix.
