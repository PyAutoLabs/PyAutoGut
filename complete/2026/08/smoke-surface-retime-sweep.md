# The smoke-surface retime sweep — every SLOW marker measured; none were slow

autolens_workspace_test#274, shipped 2026-08-24 in one day, end to end:
autolens_workspace_test#275 + #276, autogalaxy_workspace_test#112 + #113,
PyAutoMind#289. Items 1–3 of the prompt; item 4 (routine per-script timings)
had shipped that morning as `complete/2026/08/smoke-timings-dataset.md`.

## What shipped

- **The retime harness repaired first** (#275/#112): the 01:21 runner collapse
  (PyAutoHands#260 phase 1) had silently broken `retime.py` in both test
  workspaces — `from run_smoke import SCRIPTS_DIR, load_cfg, run_one` against a
  77-line shim defining none of them, and `run_one` existing nowhere in
  PyAutoHands. Every dispatch died at ImportError. `retime.py` now takes
  `timeout_for` / `kill_group` / `build_env_for_script` straight from the same
  PyAutoHands modules the mega-run uses (invariant preserved through shared
  code, not shared prose), with a faithful local `run_one` — own session,
  parent-side wall clock, group kill, 124-never-the-signal. Deliberately no
  degraded local fallbacks: absent Hands it fails at import rather than risk
  disagreeing with the gate it exists to explain.
- **The sweep** (item 1 decision recorded on the issue: wall-clock
  classification now, intra-script phase profiling deferred): 19 SLOW-marked
  JAX entries × 5 repeats × both Python legs at the 300 s cap — runs
  32741371308, 32741386752, 32755481885 (autolens), 32741366534, 32755485754
  (autogalaxy). **Not one entry is slow or stalling.** 16 of 19 NEITHER on both
  legs, slowest completion 18% of cap, against markers claiming "flakes at the
  1800s cap" — wrong by factors of ~30–90×.
- **Marker rewrite** (item 3, #276/#113): 18 refuted markers deleted (scripts
  restored to mega-run coverage, including the `#72` `delaunay_mge` pair at
  22.5–36.4 s); `imaging/jax_likelihood/mge_group` kept SLOW with its honest
  phase-2 measurement (AMBIGUOUS — capped 5/5, no completion time known); two
  entries converted to NEEDS_FIX because their markers were hiding
  deterministic bugs, each filed as a Mind bug prompt (PyAutoMind#289):
  - `interferometer/jax_likelihood/delaunay.py` (both legs): the NaN-poisoning
    probe at line ~330 now trips autogalaxy `validate_ell_comps` →
    `ModelParameterException` before testing JAX NaN-lane isolation
    (`draft/bug/autolens_workspace_test/delaunay_nan_probe_ell_comps_validator.md`).
  - `interferometer/jax_grad/gradient.py` (3.13 only; 3.12 green at 61.2 s):
    eager (-3164.0196392095145) vs jitted (-3164.021216643465) disagree ~5e-7 —
    suspected `pure_callback` constant-folding difference in XLA on 3.13
    (`draft/bug/autolens_workspace_test/gradient_eager_jit_divergence_py313.md`).

## Key traps / findings

- **A harness that only runs on dispatch breaks silently.** `retime.py` was
  green-by-absence for the ~13 hours after the collapse; only preparing a
  dispatch exposed the ImportError. Anything reachable solely via
  `workflow_dispatch` needs an import-level check in the PR gate, or it rots.
- **The 17 count was not 21 − 4.** The `#74` "flakes" family was 19; only 2 of
  the 4 phase-2-audited entries were actually in the SLOW set
  (`rectangular_mge` was NEEDS_FIX, `multi_dataset/mge` unlisted). Marker
  vocabulary, not arithmetic, decides membership.
- **ERROR is the interesting verdict.** Both real failures had been invisible
  precisely because a SLOW marker kept the script out of every run — a parked
  script cannot report its own rot. Refuting a marker is also a bug-discovery
  mechanism.
- **The stall family remains real but rare — and now measured around.** During
  this same day the intermittent XLA/`block_until_ready` stall hit main gates
  twice (multi_dataset `mge.py` 01:45, `rectangular_mge.py` 15:07, each
  passing everywhere else, each 34/35) — logged in
  `draft/bug/ci/jax_vmap_jit_compile_stall.md`. The sweep's 190 executions hit
  it zero times; it lives in the full-suite gate context, not the scripts.
- Shallow (`--depth 1`) clones cannot prove branch ancestry — `merge-base
  --is-ancestor` false-negatives; the PR-state API is the merge receipt in
  cloud sessions.
- The retime runs upload `smoke-timings-*` artifacts only via the PR-gate
  path's report dir; retime's own `retime_results.json` is step-summary +
  log only. The gate runs during the day produced the first real
  `smoke-timings-*` artifacts (e.g. run 32740209424).

## Follow-ups

- `mge_group` higher-cap retime (the one surviving SLOW marker).
- The two filed bug prompts above.
- ~~Trim the 900 s `jax_grad/` cap override in autolens `profile_smoke.yaml`
  (measured worst case 61 s; ~15× oversized).~~ **Withdrawn 2026-08-24 (same
  day):** the 61 s figure was one script; the cap's measured basis is the
  weekly workspace-smoke channel, where `point_source/jax_grad/gradient.py`
  runs at 568.2 s (63 % of the budget, run 30938311069) and two more family
  members exceed 250 s — all live and unskipped. The cap stays.
- `draft/maintenance/pyautoheart/weekly_smoke_timings_artifact_naming.md` —
  the weekly validation legs' timings land only inside `results-*` zips.

## Original prompt

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
