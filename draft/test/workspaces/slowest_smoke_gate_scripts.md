# Speed up the three slowest autolens_workspace_test smoke-gate scripts

Type: test
Target: workspaces
Repos:
- autolens_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

The per-PR smoke gate in `autolens_workspace_test` costs ~11m20s wall-clock, of
which ~9m13s is script execution. Three entries are 42% of that. This prompt is
the *make them cheaper* half; cutting how often the gate runs at all is the
sibling prompt `draft/test/pyautoheart/smoke_relevance_gate.md`. Do not merge
the two — one edits scripts, the other edits a workflow, and they land in
different repos.

## Measured

CI run 32605025472 (2026-08-22, `main`), py3.12 leg (the critical path; py3.13
is ~6% faster). 23 entries, 23/23 pass, **553.0s** total — which reconciles to
the step wall-clock exactly, so the runner adds no measurable overhead and the
scripts *are* the cost.

| py3.12 | share | script |
|-------:|------:|--------|
| 120.7s | 21.8% | `imaging/subhalo_recovery.py` |
|  63.4s | 11.5% | `misc/database/scrape/general.py` |
|  47.7s |  8.6% | `point_source/jax_likelihood/point.py` |
|  33.9s |  6.1% | `imaging/jax_likelihood/rectangular.py` |
|  31.5s |  5.7% | `misc/jax_assertions/delaunay_nn.py` |
|  30.2s |  5.5% | `imaging/jax_likelihood/mge.py` |

The remaining 17 entries are 4.5–29.2s each and are not in scope. Reproduce
with `gh api` on the job log and grep the runner's `[PASS] <name> — <n>s`
lines; the runner prints one per entry.

Note the tail is short: after these three the curve flattens, so this prompt
can win ~4 minutes and no more. Do not chase entries below ~30s.

## Task

Per script, either make it materially faster or demote it — both are
acceptable outcomes, and the choice is per script, not global.

1. **`imaging/subhalo_recovery.py` (120.7s).** Already the subject of one
   speed-up pass: `complete/2026/08/potential-correction-validation.md` leg 1
   recorded it at 232s/224s against the 300s cap, and it now runs at 120.7s, so
   half the work is done and the *why* is documented there — read it before
   re-deriving. It asserts end-to-end `dkappa` recovery of a simulated 1e10
   Msun subhalo for both the one-shot and iterative engines. Ask whether the
   PR gate needs both engines or whether one belongs on the weekly channel.
2. **`misc/database/scrape/general.py` (63.4s).** Un-parked on 2026-07-21
   (`chore(no_run): un-park database/scrape/general`, autolens_workspace_test#192).
   A database-scrape regression is the least likely of the three to be broken
   by a typical lens-modelling PR, so it is the strongest demotion candidate —
   check what it uniquely covers before deciding.
3. **`point_source/jax_likelihood/point.py` (47.7s).** Check whether the cost
   is `PointSolver` iterations or JAX compile time; if compile-dominated, the
   lever is problem size, not sample count.

## Constraints

- **A faster script that no longer tests anything is a regression, not a win.**
  This repo has three recorded instances of exactly that failure mode: the
  vacuous JAX assertions (`complete/2026/07/vacuous-jax-assertions.md`), the
  NUFFT parity legs that compared nufftax against itself and reported
  `max |Δ| = 0.0000e+00`, and `latent/latent_nan_robustness` passing vacuously
  under the smoke profile (see `planned.md`). For every reduction, state what
  the assertion still discriminates against and show it failing when the thing
  it guards is broken.
- Coverage given up is not coverage lost. Heart's weekly `workspace-smoke.yml`
  (Mondays 03:00 UTC) already runs *every* script in this repo against library
  `main` under the same `profile_smoke.yaml`, and `release-integrate` re-runs
  the matrix at `PYAUTO_TEST_MODE=0`, full resolution. The curated PR list is a
  strict subset of both. Demotion = removing the entry from `smoke_tests.txt`
  with a comment saying which channel still covers it.
- Do not raise `BUILD_SCRIPT_TIMEOUT` for these. The 300s smoke cap is a
  runaway detector; three entries sitting under it is the problem, not the cap.
- Keep the entries that stay inside the cap with real margin — 120.7s against
  300s already flaked into timeout historically under sweep-load contention
  (`planned.md` records 252s uncontended vs a 300s timeout under load).

## Acceptance

- Smoke step wall-clock for the py3.12 leg drops below ~6 minutes.
- 23/23 still pass, and every touched script has a stated, demonstrated
  discriminating assertion.
- Any demoted entry is commented in `smoke_tests.txt` naming the channel that
  still runs it.

<!-- formalised by the Intake (Conception) Agent on 2026-08-23 from user-intake -->
