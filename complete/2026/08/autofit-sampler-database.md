# autofit-sampler-database — release-run Emcee NaN + database regressions

**Date:** 2026-08-21
**Issue:** [PyAutoFit#1508](https://github.com/PyAutoLabs/PyAutoFit/issues/1508) (closed)
**PRs:** none — **no code was changed in any repo**
**Outcome:** investigated to a definitive verdict; no defect exists to fix.

## What this task was

Release run `28784914443` (PyAutoHeart#27, the first real release-profile validation) reported 42
script failures, split across seven prompts in `PyAutoMind/draft/bug/health_fixes/`. This task owned
nine: two `autofit_workspace` cookbooks failing with emcee's
`ValueError: Probability function returned NaN` on a bounded `LogUniformPrior`, and seven
`autofit_workspace_test` database/output scripts reporting empty aggregators, stale scraped search
metadata, and changed likelihood assertions.

Brain sized it `too-large` (score 12), fix-locus "library source", strategy "split into phases".

## What was actually done

The task was deliberately **reproduction-gated** rather than started as the prescribed repair,
because the premise was six weeks old and independently suspect: the sibling prompt from the same
release run (`samples_parameter_paths`, PyAutoFit#1327) had already been parked as not-reproducing,
a second sibling had shipped, and PyAutoFit had since merged #1413, `9f887a9b1`, `8f6f4ef7d`,
#1377, #1401, #1422, #1470, #1486 and #1391 into the exact scrape/aggregator/emcee machinery the
prompt blamed.

All nine scripts were re-run on `main` (PyAutoFit `248ca971f`, Release 2026.8.20.1), each from a
**moved-aside** `output/` under its workspace's `config/build/profile_release.yaml`, with env
resolved by `autohands.env_config.build_env_for_script` at workspace CWD.

## Result: 0 / 9 reproduce

The passes were audited rather than inferred from exit codes:

- **20 searches started fresh**; zero stale-output resumes. The single `Fit Already Completed` was
  `minimal_output.py`'s own deliberate second call after a fresh first run.
- The database scripts' `assert len(agg) > 0` **executed and held**, and the aggregator loop bodies
  ran — the aggregators were populated, not empty.
- **4 Emcee searches ran**; no `Probability function returned NaN` and no `ValueError` anywhere.
- Env resolution was verified first: the five scripts carrying `ENV: real_search` correctly had
  `PYAUTO_TEST_MODE` released (absent == off == `"0"`), so all seven `autofit_workspace_test`
  scripts ran real full searches.

## What this does NOT establish

1. The cookbooks ran at `PYAUTO_TEST_MODE=1` — what their release profile pins, and what the
   prompt itself describes — but reduced iterations mean fewer emcee proposals, so a NaN needing a
   long walk could be missed. The Emcee leg's refutation is weaker than the database legs'.
2. This was a **source-tree** run, not the TestPyPI wheels the release run installed. A wheel-only
   packaging defect would not appear.

## Why the issue was closed rather than parked open

Unlike its sibling #1327, the re-validation this was blocked on happens **automatically**: none of
the nine scripts is in either workspace's `config/build/no_run.yaml`, so every `mode=release` run
re-executes all nine under exactly this profile. A surviving wheel-path defect fails the next
release run loudly and earns a fresh issue with fresh evidence. There is no human reminder to lose.

## Incidental finding (not fixed, no issue filed)

`autofit/database/aggregator/scrape.py:150-158` — `_add_files_fit`'s bare `except AttributeError`
logs `Failed to load latent variables` for essentially every scraped fit. Probing a fit's zip shows
`files/samples.csv`, `samples_info.json`, `samples_summary.json` and **no latent file at all**, so
the guard is warning about legitimate absence. The same guard silently warns `Failed to load
samples` for multi-analysis child fits. Plus 6x `Could not save covariance matrix`. CLI-noise
hygiene, not a regression — route via `/hygiene` if wanted.

## Follow-on work this triggered

The same gate was then run across the four remaining `health_fixes` siblings (17 scripts):
**25 of 26 measured scripts across the whole cluster pass on current `main`**. Those four prompts
stay in `draft/` with dated gate annotations — they are *not* complete, because their SLOW/NEEDS_FIX
parkings describe *intermittent* failures that a single green run cannot clear, and the wheel path
remains unverified. Details in `draft/bug/health_fixes/README.md`.
