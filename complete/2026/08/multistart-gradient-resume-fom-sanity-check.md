## multistart-gradient-resume-fom-sanity-check
- issue: none — shipped straight from `draft/` in a single remote session; no tracking issue was opened (the human asked for "pr and merge" directly). Recorded here so the ledger still carries it.
- completed: 2026-08-15
- library-pr: PyAutoFit#1474 (merged a0af8574 -> main)
- workspace-pr: https://github.com/PyAutoLabs/autofit_workspace_test/pull/85 (merged 69ee1305 -> main)
- what shipped: `Fitness.check_log_likelihood` compared the log likelihood stored in a previous run's samples summary against `fitness(parameters)` — the figure of merit in the search's **own** convention. Those agree only when `fom_is_log_likelihood=True` and `convert_to_chi_squared=False`, so resuming any other search failed its sanity check on a completely unchanged likelihood function. New `Fitness.log_likelihood_from` helper applies the exact inverse of the FoM mapping; `check_log_likelihood` converts before comparing, and `call_wrap` (which already needed that identical inverse for quick-update/history bookkeeping) now shares it instead of duplicating it.
- **not multi-start specific** — `LBFGS`, `Emcee`, `Zeus`, `NUTS` and `Drawer` all build `Fitness` with `fom_is_log_likelihood=False` and carried the same mismatch. `MultiStartAdam`/`MultiStartProdigy` is simply where it surfaced, being the search whose resume path gets exercised by long pixelized campaigns.
- which side was wrong (the prompt explicitly asked to verify before fixing): the **comparison** side. The persisted side is correct and was left alone — `MultiStartGradient.samples_via_internal_from` explicitly stores `-0.5 * best_fom - log_prior`, a genuine log likelihood, and every downstream consumer (aggregator, database, results) reads `Sample.log_likelihood` as one. Fixing the persistence side instead would have corrupted all of them.
- the reported ratio decomposes exactly: `5390.281 = -2 x (-2692.955 + (-2.186))` — the `-2` is `convert_to_chi_squared`, the residual is the folded-in log prior. The "-2.0000x" in the field report is `convert_to_chi_squared` alone; the small excess is the log prior, so **both** legs of the conversion were implicated, not just the factor of 2.
- incidental bug found and fixed: the log-prior subtraction was an in-place `-=`. When `convert_to_chi_squared` is `False`, `log_likelihood` **is** `figure_of_merit` (same object), so `call_wrap` over a NumPy array mutated the value it was about to return — handing the search a log likelihood where it asked for a log posterior. Now out-of-place, with a regression test.
- test placement — **diverged from the prompt's scope note**, deliberately. The prompt expected the regression test in `autofit_workspace_test` with a subprocess kill/resume, assuming the fix needed `_fit` (jax + optax). It does not: the defect is entirely inside `Fitness`, which is pure NumPy. Test lives in the library unit suite instead — `test_autofit/non_linear/test_fitness_check_log_likelihood.py`, 10 tests, 0.16s, no jax, no subprocess.
- **trap for later: `test_autofit/config/general.yaml` sets `check_likelihood_function: false`.** That is why the library suite never caught this and cannot catch a regression of it by default — any test touching the resume sanity check must flip the flag on via fixture and restore it. Worth remembering before assuming "the unit suite covers resume".
- second trap: a `GaussianPrior` has log prior exactly 0.0 **at its mean**. A test parametrised over FoM conventions that evaluates at the prior means collapses the log-posterior conventions onto the log-likelihood one and passes against the *unfixed* code. Parameters must sit off the means for the log-prior leg to be exercised at all — the first draft of the test made precisely this mistake.
- validation: 10 new tests parametrised over all three FoM conventions (log-likelihood / log-posterior / chi-squared), asserting both that an unchanged likelihood resumes cleanly **and** that a genuinely changed one still raises — the guard's original purpose is preserved. With the fix reverted, the log-posterior and chi-squared resume cases fail while the log-likelihood case passes either way. Full suite under CI conditions (jax installed, `JAX_ENABLE_X64=True`, coverage): 1754 passed; sole failure `test_nautilus::test__single_core_builds_no_pool`, confirmed pre-existing on unmodified `main`. CI green on 3.12, 3.13 and docs.
- end-to-end verification (the actual reported scenario, not just the unit fix): `MultiStartAdam`, `iterations_per_full_update=2`, `kill -9` mid-run leaving `search_internal.dill` and no `.completed`. Before: `Old = -56.3875 / New = 112.7750`, exit 1. After: resume runs to completion, exit 0, continuing from the checkpointed step rather than restarting.
- CI/tooling trap (cost ~40 min this session): the GitHub `get_check_runs` API serves **stale cached data** — it froze all three jobs at `in_progress` long after they had finished (the docs job had actually succeeded 96s in). Acting on that reading, a healthy mid-suite Tests run was cancelled and had to be re-run. `list_workflow_jobs` and `get_workflow_run` report accurately; `get_workflow_run_usage` gaining a `run_duration_ms` key is a reliable completion signal. Do not trust `get_check_runs` for liveness.
- follow-up **done** (same session): PyAutoFit#1472's `n_value_nan_lane_steps` / `n_grad_nan_lane_steps` counters restore via `search_internal.get(..., 0)` and are designed to keep accumulating across a resume — not demonstrable end-to-end until this bug was fixed. Now verified and covered permanently by `autofit_workspace_test/scripts/searches/MultiStartResumeNaNCounters.py`. **No bug — the counters accumulate correctly.**
- how that follow-up was verified, and the trap in doing it: `_broad_starts` **rejects any draw whose objective or gradient is non-finite**, so every lane begins healthy by construction and a NaN trap placed at the edges of the prior is never reached — three runs reported counters of exactly 0 before this was spotted. Both traps must sit **on the descent path** (which is also the realistic case: a pixelized likelihood going degenerate near its solution). Gradient-NaN uses the `where`/`sqrt` pattern from the `Fitness.call` docstring — inside the band the selected branch is a finite `0.0` while the unselected `sqrt` of a negative is NaN, and reverse-mode gives `0 * NaN = NaN`, so the value stays finite and only the gradient dies.
- assertion design worth reusing: the load-bearing invariant is **equality with an uninterrupted reference run** (the search is deterministic), not "the counters went up". Injecting the regression (resetting both counters on resume) yields 402 against the reference's 403 — a `>=` assertion accepts that happily, equality catches it. A separate decisive check also ran: stamping sentinel values (7000/9000) into the live checkpoint and resuming gave 7045/9008, so the restored totals are provably carried rather than recounted.
- also confirmed while doing it: a resumed run's final counters are independent of *where* the kill landed (killed at step 72 and at step 74 both finished at the reference totals), i.e. the checkpoint captures the full accumulator state.

## Correction (2026-08-22) — the `test_nautilus` failure

`test_nautilus.py::test__single_core_builds_no_pool` is **not** a failure on
clean `main`. It is a **missing optional dependency**: the test runs a real
`search.fit`, which reaches `from nautilus import Sampler`, and
`nautilus-sampler` ships only in the `[optional]` extra. CI installs
`[optional]` and the test passes there — latest main CI is 2024 passed,
3 skipped, 0 failed. Sandboxes and local venvs without the extras get a hard
`ModuleNotFoundError`.

The validation bullet above says "confirmed pre-existing on unmodified
`main`". "Not caused by this work" was right; "pre-existing on `main`" is the
wrong gloss — read it as environment-specific.

Fixed by PyAutoFit#1511 / PR #1512 (skip-if-missing guards, also covering the
`astropy` collection errors and aggregator errors from the same cause). Full
investigation: `active/17_optional_dependency_skip_guards.md`.

## Original prompt

# MultiStartGradient cannot resume a killed mid-run search — FoM sanity check compares log-likelihood against chi-squared

Type: bug
Target: PyAutoFit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

`MultiStartGradient` (`af.MultiStartAdam` / `af.MultiStartProdigy`) raises
`SearchException` when resuming a search that was killed mid-run, so the resume
path is unusable. Long pixelized campaigns are exactly the runs that get
interrupted, and this is the mechanism meant to recover them.

## Reproduce

Confirmed on `main` (PyAutoFit `39a187b2d`), with the **stock** `af.ex.Analysis`
— no custom analysis needed.

1. Run a named `af.MultiStartAdam` with `iterations_per_full_update=2` so
   checkpoints are written during the run (the default single-chunk cadence only
   checkpoints at the end, so a mid-run kill leaves nothing to resume from).
2. `kill -9` it around step 10 of 400. This leaves
   `files/search_internal/search_internal.dill` and **no** `.completed` marker —
   the only state a real resume starts from, since a search that finishes
   deletes its checkpoint.
3. Re-run the identical script. It fails:

```
autofit.exc.SearchException:
    Figure of merit sanity check failed.
    Old Figure of Merit = -2692.9547224874896
    New Figure of Merit = 5390.281252235021
```

Reproduced twice, with matching structure:

| analysis | old FoM | new FoM | ratio |
|---|---|---|---|
| stock `af.ex.Analysis` | -2692.9547224874896 | 5390.281252235021 | -2.0000x |
| a custom analysis | -2915.2793638973044 | 5834.81444744653 | -2.0006x |

## Diagnosis (starting point, not a conclusion)

The consistent **-2x** relationship points at a units mismatch rather than a
genuine likelihood change. `MultiStartGradient` builds its `Fitness` with
`fom_is_log_likelihood=False` and `convert_to_chi_squared=True`, i.e. its
figure-of-merit is `-2 * log_posterior` (a chi-squared). The stored "old" value
looks like a **log-likelihood** while the freshly computed "new" value looks
like the **chi-squared**, so `Fitness.check_log_likelihood`
(`autofit/non_linear/fitness.py:614`, called from `__init__` at line 171)
appears to be comparing a stored log-likelihood against a value in the
multi-start FoM convention.

Verify that before fixing — the fix is either at the point the old value is
persisted or at the point the comparison converts, and picking the wrong one
would paper over a real check. Note `check_log_likelihood` exists to catch a
genuinely changed likelihood function between runs (the documented
"multi-start resume chains do not survive library upgrades that touch FoM
bookkeeping" behaviour in `autolens_profiling/scripts/misc/searches/README.md`).
The fix must keep that guard working for the case it was built for; the bug is
that it fires on an **unchanged** likelihood in the same process generation.

## Scope

- Confirm which side carries the wrong convention, with a test that resumes a
  killed run and asserts it continues rather than raising.
- The library unit suite is NumPy-only and `_fit` needs jax + optax, so the
  regression test likely belongs in `autofit_workspace_test` alongside
  `scripts/searches/MultiStartResurrect.py` (`ENV: real_search jax`), with the
  kill/resume driven as a subprocess.

## Provenance

Found while verifying the resume path of the value-NaN / gradient-NaN step
counters added in PyAutoFit#1472. Those counters restore via
`search_internal.get(..., 0)` and are designed to keep accumulating across a
resume; that behaviour **cannot be demonstrated end-to-end until this is
fixed**, so #1472 ships with the resume accumulation covered only by unit tests
over hand-built `search_internal` dicts. Re-check it here once resume works.

This bug is independent of #1472 — reproduced on `main` without those changes.
