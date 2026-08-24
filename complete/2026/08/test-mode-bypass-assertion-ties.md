# test-mode-bypass-assertion-ties

- shipped: 2026-08-24
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1519 (closed)
- repos:
  - PyAutoFit
- PRs:
  - PyAutoFit#1520 `438f56f` (head `d49275c`) — the bypass must evaluate *and store* a point the model's assertions accept

## Summary

The `PYAUTO_TEST_MODE=2/3` bypass has no sampler, so it picked its own evaluation
point: the prior medians. A model whose components share priors and carry an
ordering assertion — the standard exchange-degeneracy idiom, e.g. PyAutoCTI trap
models with `trap_0.release_timescale < trap_1.release_timescale` — ties *exactly*
there, so `check_assertions` rejected it with `FitException` and the run
hard-failed on an artifact of the bypass's own choice of point.

The fix makes the bypass pick its point through a new
`NonLinearSearch._test_mode_valid_parameter_vector` — prior medians first, then
`np.random.default_rng(seed=0)` prior draws, each candidate validated — factored
out of the deterministic search `TEST_MODE=1` recovery already used, so both call
sites share it and smoke runs stay reproducible without touching global RNG state.

## Root cause — three sites, not the one reported

The prompt's own 2026-08-09 note found site 1 and proposed two one-liners. **Neither
would have got a run to completion**, because sites 2 and 3 also derive from the
stored vector:

1. `_fit_bypass_test_mode` instantiated the model *outside* the `try` that catches
   `FitException`, so the assertion rejection escaped that guard.
2. `_build_fake_samples` scales the median vector uniformly (1.001 / 0.999 /
   1.002), and a uniform scale **preserves** an ordering tie — so every stored
   sample failed the same assertion, not just the first.
3. `SamplesSummary.max_log_likelihood` is `@to_instance()` with `recover="raise"`
   (it extends `SamplesInterface` directly, so it does not inherit `Samples`'
   next-valid recovery), and `Result.instance` catches only `AttributeError` — so
   `result.max_log_likelihood_instance` raised `SamplesException`.

## Traps worth keeping

- **`PYAUTO_TEST_MODE=3` was broken too**, which nothing had noticed. It never
  calls the likelihood, so it survived the fit and died later at
  `result.max_log_likelihood_instance`. Reproduced before the fix, verified after.
- **Do not mistake the adjacent `FitException` catch for this fix.** The prompt's
  own note already warned of this: the catch wraps only the *likelihood* call — a
  pathological likelihood is a different contract from an invalid instance. It was
  deliberately left in place; `TestBypassToleratesFitException` still passes.
- **Behaviour change to flag downstream:** mode 3 now instantiates the model once
  (previously zero times). A model whose constructor raises a *non*-`FitException`
  at the medians now fails at fit time rather than at result-access time — same
  failure, surfaced earlier. One instantiation, not one per sample: the
  50,000-sample bypass test is unaffected.
- Mode 1's recovery path was refactored onto the same helper but is
  behaviour-preserving, including its exact failure message.
  `TEST_MODE_REPRESENTATIVE_MAX_ATTEMPTS` keeps its name — an existing test
  monkeypatches it.

## Verification

Reproduced on clean `main` first (mode 2 died *in* the fit; mode 3 died at result
access), then confirmed fixed with both modes selecting the identical vector
(`8.1513753680827, 9.13628021504944`) — cross-mode determinism. All 5 new tests in
`TestBypassToleratesAssertionTies` fail against the un-patched source. Full suite
2016 passed / 34 skipped / 0 failed; CI green on all legs at merge (`Docs`,
`unittest (3.12)`, `unittest (3.13)`, `unittest-nojax`).

**Gate caveat:** `pyauto-heart` was unreachable from the shipping session, so the
readiness gate ran in the WORKFLOW.md fallback form (full library suite as the
gate). CI green on merge is the stronger confirmation, but **no Heart verdict was
recorded for this task**.

## Bookkeeping note

The shipping session (2026-08-24, PyAutoFit issue #1519 → PR #1520, both same day)
never moved the prompt out of `draft/bug/autofit/`, never registered the task in
`active.md`, and left no record here — the Mind leg of the lifecycle was skipped
entirely. This record is the retrospective close-out, written once a later
`/start_dev` on the same draft found the fix already merged in `main`.

## Follow-up (not in this task)

- `autocti_workspace` documents this artifact in its `AGENTS.md` as a workaround.
  That note should now be **deleted** rather than left behind — the
  `testmode-env-drift` precedent, "delete the trap, don't document it". Separate
  task, separate repo.
- Re-enabling `autocti_workspace` smoke coverage of the `modeling/start_here.py`
  class of scripts (CTI resurrection epic, Phase 5) is the downstream unblock this
  frees, and is likewise its own task.

## Original prompt

# TEST_MODE bypass crashes on ordered-parameter assertion ties

Type: bug
Target: PyAutoFit
Repos:
- @PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised — STILL REPRODUCES; see the 2026-08-09 note before grading this against main
Filed: 2026-07-17 (backfilled from git)

## 2026-08-09 — do NOT mistake the adjacent FitException catch for this fix

Checked by the draft/ sweep against PyAutoFit main (`3b960609`). The bypass path
in `abstract_search.py` **now catches `exc.FitException`** and continues with the
`-1e99` sentinel, logging "TEST MODE 2: likelihood verification raised
FitException … treating as a resample-rejected instance". That reads exactly like
this prompt's suggested fix. **It is not.** The bug below still reproduces.

The catch wraps only the likelihood call. The model instantiation is on the line
*before* the `try`:

```python
if call_likelihood:
    instance = model.instance_from_vector(vector=parameter_vector)   # <-- outside
    try:
        log_likelihood = float(analysis.log_likelihood_function(instance))
    except exc.FitException as e:
        ...
```

and `instance_from_vector` → `instance_for_arguments` → `check_assertions`
(`autofit/mapper/prior_model/abstract.py:193`) is precisely what raises
`exc.FitException("N assertions failed!")` when an ordering assertion ties at the
prior medians. `ignore_assertions` defaults to `False` and the bypass does not
pass it. So the assertion exception escapes the guard entirely and still
hard-fails the run.

The upside: the fix is now a one-liner rather than the "catch and retry with a
perturbation" design sketched below. Two options, both cheap and both
deterministic:

- move the `instance_from_vector` call inside the existing `try` — the sentinel
  path already does the right thing for a rejected instance; or
- pass `ignore_assertions=True` at the bypass instantiation, on the grounds that
  a verification eval at the medians is not a sampled point and assertions exist
  to steer sampling.

The second is probably the better semantics (a tied median is not a pathological
model), but it changes what the verification eval attests to — pick deliberately.
Prefer either over adding perturbation logic.

`Difficulty:` stays small. The § Blocks note below still holds.

---

Found during the CTI resurrection epic (Phase 4, 2026-07-17). `PYAUTO_TEST_MODE=2/3`
bypass evaluates the model at the **prior medians**. A model whose components have
identical priors plus an ordering assertion (the standard idiom for breaking
exchange degeneracy, e.g. PyAutoCTI trap models with
`model.add_assertion(trap_0.release_timescale < trap_1.release_timescale)`)
ties exactly at the medians, so the bypass evaluation raises
`autofit.exc.FitException: GreaterThanLessThanAssertion` and the script crashes.

Real samplers resample assertion-failing points gracefully — this is purely a
bypass-path artifact, and it makes every ordered-trap CTI workspace script
un-smokeable at TEST_MODE=2 (reproduced with a bare
`model.instance_from_prior_medians()`; TEST_MODE=1 passes).

Suggested fix: at the bypass evaluation, catch `FitException` from assertions
and retry with a small deterministic perturbation of the unit-cube point (or a
seeded random draw), mirroring what a real sampler does. Keep it deterministic
so smoke runs stay reproducible.

Blocks: autocti_workspace smoke coverage of `modeling/start_here.py`-class
scripts (CTI epic Phase 5); the workspace documents the artifact in its
AGENTS.md meanwhile.
