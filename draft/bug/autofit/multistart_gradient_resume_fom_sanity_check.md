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
