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
Issued: 2026-08-23

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

## Corrected census (read off the marker files 2026-08-23, at /start_dev)

The parent prompt's "eight entries SLOW-skipped on 2026-07-14" undercounts by
more than 2x, and it missed a fifth stall quarantine filed the same day. Read
from `config/build/no_run.yaml` in both repos plus `autolens_workspace_test/smoke_tests.txt`:

**SLOW-marked JAX entries — 21, not 8.**

| autogalaxy_workspace_test (9) | autolens_workspace_test (12) |
|---|---|
| `multi_dataset/jax_likelihood/delaunay_mge` (#72) | `imaging/jax_likelihood/delaunay_mge` |
| `imaging/jax_likelihood/delaunay_mge.py` | `imaging/jax_likelihood/mge_group` |
| `interferometer/jax_likelihood/mge.py` | `multi_dataset/jax_likelihood/delaunay_mge` (#72) |
| `interferometer/jax_likelihood/mge_group.py` | `multi_dataset/jax_likelihood/shared_preloads.py` |
| `interferometer/jax_likelihood/delaunay.py` | `interferometer/datacube/delaunay.py` |
| `interferometer/jax_likelihood/delaunay_mge.py` | `interferometer/datacube/shared_preloads.py` |
| `interferometer/jax_likelihood/rectangular_mge.py` | `interferometer/jax_likelihood/mge.py` |
| `interferometer/jax_grad/mge.py` | `interferometer/jax_likelihood/mge_group.py` |
| `multi_dataset/jax_grad/mge.py` | `interferometer/jax_likelihood/delaunay.py` |
| | `interferometer/jax_likelihood/delaunay_mge.py` |
| | `interferometer/jax_likelihood/rectangular_mge.py` |
| | `interferometer/jax_grad/gradient.py` |

**Quarantined for the stall signature — 5, not 3.**

| Entry | Repo | Marker |
|---|---|---|
| `multi_dataset/jax_likelihood/rectangular.py` | ag_test | NEEDS_FIX 2026-08-01 |
| `imaging/jax_likelihood/mge_group.py` | ag_test | NEEDS_FIX 2026-08-23 |
| `imaging/jax_likelihood/rectangular_mge.py` | ag_test | NEEDS_FIX 2026-08-23 |
| `multi_dataset/jax_likelihood/delaunay.py` | al_test | NEEDS_FIX 2026-08-01 (#245) |
| `multi_dataset/jax_likelihood/mge.py` | al_test | disabled in `smoke_tests.txt` 2026-08-22 |

`imaging/jax_likelihood/rectangular_mge.py` was quarantined in ag_test on
2026-08-23, so the parent prompt's "passed on 3.13, stalled on 3.12" reference
point is now a quarantine in its own right. 26 entries in scope, not 11.

## Three things the marker text already establishes, before any re-timing

**1. A 27.8s script is SLOW-marked for "flaking" at a 1800s cap.**
`interferometer/datacube/shared_preloads.py` is SLOW-marked in
`autolens_workspace_test`'s `no_run.yaml` — *"flakes at the 1800s cap
(PyAutoHeart#74)"* — while the `smoke_tests.txt` comment on a sibling records it
running the PR gate in **27.8s**, and it is still enabled there. A script that
completes in 27.8s does not intermittently exceed 1800s by being slow: that is a
65x gap. Whatever is happening to it, slowness is not it.

**2. The same script path is SLOW in one repo and a stall in the other.**
`imaging/jax_likelihood/mge_group` is SLOW-marked in `autolens_workspace_test`
(2026-07-21, *"flakes at the 1800s cap"*) and NEEDS_FIX-quarantined for the
stall in `autogalaxy_workspace_test` (2026-08-23, *"silence for the full 300s"*).
Same tier, same path, two labels. The label recorded which repo noticed it, not
what it was doing.

**3. "Flakes" is bimodal language wearing a unimodal label.**
Every 2026-07-14 SLOW marker reads *"flakes at the 1800s cap"* and records **no
timing at all**. A genuinely slow script does not flake — it exceeds the cap
consistently. Compare the markers this repo writes when it has actually
measured something: `misc/database/scrape/*` say *"re-measured: times out at the
real 300s cap"*, and the stall quarantines say *"18s when it passes"*,
*"passes ~19s otherwise"*, *"runs green in 32s standalone"*. The batch that
carries the SLOW label is the batch with no measurement behind it.

None of this is proof — it is three strong priors that make the re-timing a
confirmation rather than an exploration, and it means the burden now sits on
"these are slow", not on "these are stalls".

## Entries in scope

All 26 above. The method applies uniformly: an entry is classified from its own
distribution, not from which marker it happens to carry today.

`imaging/jax_likelihood/delaunay_mge.py` (al_test) carries **two** unrelated
markers — SLOW in `no_run.yaml` and disabled in `smoke_tests.txt` for `jax 0.7`
removing `jax.interpreters.xla.pytype_aval_mappings`. The API removal is a real,
different cause; re-time it anyway, but do not let the SLOW marker's removal
imply the API one is resolved.

## Acceptance

- Every entry above classified, with the timing distribution that supports the
  classification recorded — not asserted.
- Every marker in the `no_run.yaml` files and `smoke_tests.txt` rewritten to
  carry its real reason, so a SLOW marker means slow and nothing else.
- The answer written down somewhere the Profiling Agent reads, so it stops
  chasing speedups on scripts that are hanging.
- No script is un-quarantined by this phase — restoring coverage is phase 3,
  and depends on the fix.
