# Properly time and profile the smoke/release script surface

Type: research
Target: ci
Repos:
- @autolens_workspace_test
- @autogalaxy_workspace_test
- @PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-23
Issued: 2026-08-24

Filed 2026-08-23 at James's direction, to hold the timing/profiling work that
the `jax-compile-stall` epic's phase 2 kept pulling in. Phase 2 asked one narrow
question — *is this entry slow, or is it stalling?* — and answering it for four
entries was enough to prove the SLOW markers are unreliable. Sweeping the
remaining seventeen one at a time was not the best use of the runner budget, and
the real want is broader than the epic: **a proper timing and profiling picture
of the whole smoke surface**, not an entry-by-entry audit driven by a bug hunt.

## What is already known (do not re-measure)

From the phase-2 dispatch, 40 executions at the 300s cap over both Python legs
(`autogalaxy_workspace_test` run 32664679042, `autolens_workspace_test` run
32664682689) — full detail on autolens_workspace_test#271:

| Entry | Verdict | Evidence |
|---|---|---|
| `interferometer/datacube/shared_preloads.py` | NEITHER | 10/10 completed, worst 34.0s — **1.9%** of the 1800s cap its SLOW marker claims it flakes at |
| `imaging/jax_likelihood/rectangular_mge.py` | STALL | 4/5 capped + one ~22s completion, same split on 3.12 and 3.13 |
| `imaging/jax_likelihood/mge_group.py` | AMBIGUOUS | 5/5 capped, both legs |
| `multi_dataset/jax_likelihood/mge.py` | AMBIGUOUS | 5/5 capped, both legs |

The headline for this task: **a SLOW marker is not evidence of slowness.** Every
2026-07-14 marker reads "flakes at the 1800s cap" and records no timing at all;
the one entry measured so far was wrong by a factor of ~50.

## Before you start: the "compile stall" is a misnomer

The stalled entries above were captured mid-hang on 2026-08-23 and the stack
puts them in `jax.block_until_ready`, not in compilation. If any of this work
touches those entries, do not carry the "XLA compile stall" framing over — it
predates the evidence. Detail in
[`../../../complete/2026/08/jax-compile-stall-slow-vs-stall-audit.md`](../../../complete/2026/08/jax-compile-stall-slow-vs-stall-audit.md).

## The harness exists

`.github/workflows/retime.yml` + `.github/scripts/retime.py` in both test
workspaces (merged 2026-08-23), reached through PyAutoHeart's reusable
`smoke-tests.yml` `runner` input. Inputs: `scripts`, `repeats`,
`script-timeout`. Emits per-run timings, a per-script verdict
(STALL/SLOW/NEITHER/AMBIGUOUS/ERROR) and `retime_results.json`. Reuses
`run_smoke.py`'s `run_one`, so it cannot disagree with the PR gate or the
release runner about a script's environment.

It is a *classifier*, deliberately narrow. This task is where a real profile
belongs.

## Task

1. Decide what the useful picture actually is — per-script wall clock across the
   whole surface, where the time goes inside a script (import, dataset
   simulation, compile, sample), or which entries dominate the mega-run. Those
   want different instrumentation; pick before spending runner hours.
2. Re-time the 17 SLOW-marked JAX entries not yet covered, in one batched sweep
   rather than one dispatch at a time.
3. Rewrite every marker to carry its measured reason, and delete the ones the
   measurement refutes.
4. Consider whether the runner should record per-script timings routinely, so
   this is a standing dataset rather than a periodic archaeology exercise.
   *(Shipped 2026-08-24 ahead of this task — PyAutoHands d2a22f4 +
   PyAutoHeart#167; record in `complete/2026/08/smoke-timings-dataset.md`.
   Items 1–3 remain.)*

## Acceptance

- Every SLOW marker in both test workspaces carries a measurement, or is gone.
- A stated view on whether routine per-script timing should be collected.
- The Profiling Agent has real numbers instead of the word "flakes".
