# Intermittent smoke hang on `imaging/jax_likelihood/mge.py` (autogalaxy_workspace_test)

Type: research
Target: workspaces
Repos:
- @autogalaxy_workspace_test
- @autolens_workspace_test
Difficulty: large
Autonomy: supervised
Priority: medium
Status: formalised
Filed: 2026-08-23

Found 2026-08-23 while shipping the `smoke_install.sh` stale-jax-pin fix
(autolens_workspace_test#266 / autogalaxy_workspace_test#107). Not caused by that
change — see "Ruling out the jax bump" below — but surfaced by it, and deliberately
not folded into it.

## The defect

`autogalaxy_workspace_test`'s Smoke Tests suite intermittently **hangs** rather
than failing. Attempt 1 of run 32652329340 (commit `b0bd72d`, python 3.12):

```
16:41:05  Running 37 smoke test script(s) from smoke_tests.txt
          [PASS] misc/aggregator/galaxies.py — 7.2s
          ... 7 more scripts pass ...
16:41:58  [PASS] imaging/jax_likelihood/lp.py — 9.8s
16:41:58  ##[group]imaging/jax_likelihood/mge.py
          <<< 59 minutes, zero output >>>
17:40:36  ##[error]The operation was canceled.
17:40:36  Terminate orphan process: pid (2860) (python)
17:40:36  Terminate orphan process: pid (2986) (python)
```

8 of 37 scripts passed; the 9th opened its group and produced nothing. The two
orphaned python processes at teardown confirm a wedged subprocess, not slowness.

## It is a known, recurring pattern

Against an 11-14 min norm for a completed run on `main`, four prior runs ran to
GitHub's 6-hour ceiling:

| Run | Duration | Conclusion |
|-----|----------|------------|
| 268 | 6h 00m | cancelled |
| 255 | 6h 03m | cancelled |
| 239 | 6h 01m | cancelled |
| 242 | 6h 00m | failure |

Run 266's commit already parks a sibling for the same reason:
"park `multi_dataset/jax_likelihood/rectangular.py` (NEEDS_FIX): intermittent
release-integrate hang (autolens_workspace_test#245)". So the failure mode has
been seen before, on a sibling JAX likelihood script, and was worked around by
parking rather than diagnosed.

## Ruling out the jax bump

The obvious suspect was the concurrent jax move 0.10.2 -> 0.11.1 (the stale-pin
removal). Two pieces of evidence acquit it:

1. `autolens_workspace_test`'s merged run on the same jax 0.11.1 ran the **same**
   `imaging/jax_likelihood/mge.py` and it **passed in 29.7s**, plus
   `interferometer/jax_likelihood/mge.py`; that suite was 23/23. So the
   tfp-nightly Matern-kernel / `bessel_kve` path is not broken by 0.11.1.
2. Re-running the identical commit `b0bd72d` did **not** reproduce the 70-second
   stall — attempt 2 ran the smoke step well past 14 minutes, so the hang is not
   deterministic on this commit.

## Why it matters

A hang is strictly worse than a failure here. It burns up to 6 runner-hours,
reports as `cancelled` — which is in Heart's `FAILURE_CONCLUSIONS`, so a hung run
on `main` reads as red CI to the `ws_ci` gate — and it yields no traceback, so
each occurrence teaches nothing. The current coping strategy (park the script)
removes coverage of exactly the JAX likelihood paths the parking is meant to
protect.

## Suggested scope

1. Reproduce locally against `imaging/jax_likelihood/mge.py`, ideally under load /
   repeated runs, since it is intermittent. Capture `py-spy dump` or `faulthandler`
   output from the wedged process — the missing artifact in every occurrence so far
   is a stack for where it is stuck.
2. Establish whether the two parked/hanging scripts
   (`imaging/jax_likelihood/mge.py`, `multi_dataset/jax_likelihood/rectangular.py`)
   share a mechanism. Both are JAX likelihood paths; the MGE one goes through
   tfp-nightly's `bessel_kve`. Deadlock in a pure_callback, XLA compile lock, or
   thread/fork interaction are the candidates worth eliminating first.
3. Once root-caused, unpark `multi_dataset/jax_likelihood/rectangular.py` and
   restore the lost coverage.

## Split out of this prompt

The per-script timeout for `.github/scripts/run_smoke.py` — the highest-value
change even if this investigation stalls — is now its own task:
`draft/test/workspaces/run_smoke_per_script_timeout.md`. It is bounded and ships
independently; this prompt is the open-ended half and should not gate it.

Sized `large`, not medium: reproducing an *intermittent* wedge has no guaranteed
endpoint. The sizing faculty derived too-large (score 11) against an initial
declared medium, and it was right.

<!-- Filed as a follow-up during the stale-jax-pin ship rather than folded into it:
     the hang predates that change and has its own four-run history. autogalaxy#107
     was merged with its smoke run still in flight, on the strength of the identical
     autolens change being green at 23/23; item 3 is what would make that judgement
     unnecessary next time. -->
