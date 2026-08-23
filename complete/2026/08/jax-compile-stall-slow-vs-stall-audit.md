# JAX vmap compile stall — instrumented, measured, partially explained (jax-compile-stall epic)

- **Issues:** PyAutoFit#1516 (closed) · autolens_workspace_test#271 (closed) · **PRs:** PyAutoFit#1517, PyAutoFit#1518, PyAutoHeart#161, autolens_workspace_test#272, autogalaxy_workspace_test#110 — all merged 2026-08-23
- **Repos:** PyAutoFit (`non_linear/jax_compile.py`, tests), PyAutoHeart (`.github/workflows/smoke-tests.yml`), autolens_workspace_test + autogalaxy_workspace_test (`.github/scripts/retime.py`, `.github/workflows/retime.yml`)
- **Epic:** `jax-compile-stall`, 3 phases. Phase 1 shipped in full; phases 2 and 3 taken to a deliberate stopping point (James, 2026-08-23) — **the remaining breadth moves to `draft/research/ci/smoke_timing_and_profiling.md`**, where this record is meant to be dug up.
- **Status: CLOSED AS PARTIAL.** The stall is instrumented and characterised but **not root-caused**. Nothing was un-quarantined.

## What shipped

1. **A stalled JAX compile now reports itself** (#1517, #1518). `log_on_first_compile` gained a heartbeat (`still compiling <desc>, Ns elapsed`), a `faulthandler` watchdog, and separate timings for the trace/lower/compile wait vs the `block_until_ready` execution wait. All four call sites inherit it. No workspace script or CI runner touched.
2. **A re-timing harness** (Heart#161 + the two workspace PRs). `retime.yml` (`workflow_dispatch`: scripts, repeats, script-timeout) → `retime.py`, which reuses `run_smoke.py`'s `run_one` so it cannot disagree with the PR gate about a script's environment. Heart's reusable workflow gained `runner` / `runner-args` / `script-timeout` inputs, all defaulting to prior behaviour, so the ceremony is shared rather than copied.

## What was measured (60 script executions, all on hosted runners)

| Entry | Verdict | Evidence |
|---|---|---|
| `interferometer/datacube/shared_preloads.py` (al) | **NEITHER** | 10/10 completed, worst 34.0s = **1.9%** of the 1800s cap its SLOW marker claims it flakes at |
| `imaging/jax_likelihood/rectangular_mge.py` (ag) | **STALL** | 4/5 capped on *both* legs, completions ~22s (7% of cap) |
| `imaging/jax_likelihood/mge_group.py` (ag) | **AMBIGUOUS** | 5/5 capped both legs, no completion |
| `multi_dataset/jax_likelihood/mge.py` (al) | **AMBIGUOUS** | 5/5 capped both legs, though its own marker records 32s standalone |

## Key findings — the part worth digging up

- **A SLOW marker is not evidence of slowness.** Every 2026-07-14 marker reads "flakes at the 1800s cap" and records *no timing at all*. The first one measured was wrong by ~50x. Do not trust the remaining 17 without re-measuring.
- **The stall is a >100x bimodality inside one step.** A healthy compile of `rectangular_mge.py` is **3.1s** (trace/lower/compile) + 0.5s (materialize); a stalled one exceeds 300s. Same commit, same runner image.
- **`vmap(jit)` ordering is contributory, not causal.** `Fitness._vmap` builds `jax.vmap(jax.jit(self.call))` while `analysis/latent.py` builds the conventional `jax.jit(jax.vmap(...))`. A/B on `rectangular_mge.py`: control **8/10 stalls (80%)** vs experiment **3/10 (30%)**, Fisher exact two-tailed **p = 0.070**. The stall SURVIVES the swap, so the ordering is not necessary for it, and n=10/arm is not significant. Branch `experiment/jax-vmap-jit-ordering` exists in PyAutoFit and autogalaxy_workspace_test, unmerged, for whoever resumes.
- **Untested hypothesis, still live:** the persistent compilation cache (`JAX_COMPILATION_CACHE_DIR`, default-on since PyAutoConf#128, 2026-07-17). Both NEEDS_FIX stalls post-date it; the SLOW batch predates it. A/B with the cache disabled is the obvious next experiment and was never run.

## Traps recorded

- **A watchdog whose threshold equals the cap never fires.** #1517 defaulted the `faulthandler` dump to 300s under CI; the smoke cap is also 300s, so the runner's SIGKILL beat the dump in all 20 stalled runs — heartbeats, no stacks. #1518 derives it from `BUILD_SCRIPT_TIMEOUT` at 80%. Its tests assert the *relationship* (`dump < cap` for every cap), not today's numbers, because nothing in #1517's own tests could have caught a collision between two independently-correct timeouts owned by different repos.
- **A Python traceback during XLA compile parks at the pybind boundary** — it separates *in compile* / *in execution* / *blocked on a Python lock*, but shows no XLA internals.
- **The compile/execute split does not localise a stall.** It only prints once *both* halves finish, so it characterises the healthy case only. Only the stack does.
- **Testing a library change through workspace CI:** the reusable workflow clones the dependency chain at the **matching branch name**, so an identically-named branch in the workspace repo makes its CI pick up an experimental library branch. That is how the ordering A/B was run.
- Diagnostics must never break a fit: unstartable heartbeat thread, unarmable dump, malformed interval all fall back and continue.

## Left undone, deliberately

- No root cause. No marker rewritten. **Nothing un-quarantined** — all five stall quarantines and all 21 SLOW markers stand as they were.
- The two 1800s runs dispatched at 21:37 (ag_test run 32668061785, al_test run 32668067325; `mge_group.py` and `multi_dataset/jax_likelihood/mge.py`, 2 repeats) were still in flight at close-out and should carry the first `faulthandler` stack at 1440s. **Read those two runs first when resuming** — they are the only pending evidence.
- **Heart:** never consulted this session — `pyauto-heart` unreachable from the `web-github` environment. Every merge was on an explicit human instruction ("merge when green").
- Merged branches could not be deleted: this session's git proxy refuses ref deletions. `feature/jax-compile-stall-evidence`, `feature/jax-compile-dump-below-cap` (PyAutoFit), `feature/reusable-smoke-runner-input` (PyAutoHeart), `feature/jax-stall-retime-harness` (both workspaces), plus the two `experiment/jax-vmap-jit-ordering` branches. All need a local `/repo_cleanup`.

## Original prompt

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
