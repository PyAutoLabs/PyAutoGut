## test-mode-bypass-assertion-ties
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1519 (closed)
- completed: 2026-08-24
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1520 (merged 438f56fac)
- summary: The PYAUTO_TEST_MODE=2/3 bypass evaluated the model at the prior
  medians, so a model with identical priors plus an ordering assertion (the
  exchange-degeneracy idiom, e.g. PyAutoCTI trap models) tied exactly there and
  check_assertions hard-failed the run. The bypass now picks its point through a
  shared `_test_mode_valid_parameter_vector` — prior medians first, then
  `default_rng(seed=0)` prior draws, each candidate validated — so the vector it
  evaluates AND stores satisfies the assertions.
- key-finding: **the prompt's own suggested fix would not have worked.** The
  2026-08-09 note had narrowed this to a one-liner (move `instance_from_vector`
  inside the existing try, or pass `ignore_assertions=True`). Reading main
  d3625a8 found THREE sites, and both one-liners fix only the first:
  1. `abstract_search.py:1007` — instantiation outside the FitException guard;
  2. `_build_fake_samples:1112` — the perturbed samples are the median vector
     scaled UNIFORMLY (1.001/0.999/1.002), and a uniform scale preserves an
     ordering tie, so every stored sample fails the same assertion;
  3. `SamplesSummary.max_log_likelihood` (`interface.py:122`) is `@to_instance()`
     with `recover="raise"` — it extends SamplesInterface directly so it does NOT
     inherit Samples' next-valid recovery — so `result.max_log_likelihood_instance`
     raises SamplesException, and `Result.instance` catches only AttributeError.
- key-finding: **TEST_MODE=3 was broken too and nobody had noticed.** It never
  calls instance_from_vector in the bypass, so it survived the fit and died at
  the first `result.max_log_likelihood_instance`. Confirmed by reproduction, not
  just by reading. Fixing the stored vector fixes modes 2 and 3 together.
- trap: do NOT re-run a bypass reproduction without clearing `output/` first. A
  bypassed fit calls `paths.completed()`, so a second run with the same
  unique_tag takes `result_via_completed_fit` and replays the OLD (broken)
  samples — which reads exactly like "the fix didn't work". Cost one false
  negative during verification.
- trap: `af.m.MockAnalysis` maps its likelihood over the model and returns a
  LIST for an `af.Collection`, which the bypass's `float()` rejects. Regression
  tests needed a small float-returning analysis instead.
- behaviour-change: mode 3 now instantiates the model once (previously zero
  times). A model whose constructor raises a non-FitException at the medians now
  fails at fit time rather than result time — same failure, surfaced earlier.
  Flagged in the PR body for downstream repos.
- verification: reproduced on clean main first (mode 2 raised FitException in the
  fit; mode 3 raised SamplesException at result access), then both modes complete
  and select the identical vector after. All 5 new tests in
  `TestBypassToleratesAssertionTies` fail against the un-patched source. Full
  suite 2016 passed / 34 skipped / 0 failed; CI green on all three legs
  (unittest 3.12, unittest 3.13, unittest-nojax) plus Docs.
- gate-caveat: shipped from a web-github session where `pyauto-heart` is
  unreachable, so the readiness gate ran in the WORKFLOW.md fallback form (full
  library suite as the gate). No Heart verdict was recorded for this task; CI
  green at merge is the stronger confirmation that stands in its place. The
  workspace-impact grep was likewise not run (workspace clones absent) — API
  Changes are "none, internal", so option (iii) was inferred, not measured.
- follow-up: `autocti_workspace` documents this artifact in its AGENTS.md as a
  workaround. Delete that note now the fix has shipped — the testmode-env-drift
  precedent ("delete the trap, don't document it"). Separate repo, separate task.
- follow-up: re-enable autocti_workspace smoke coverage of the
  `modeling/start_here.py`-class scripts (CTI epic Phase 5) that this unblocks.
- environment: web-github; no worktree was ever created, so there is none to
  remove. PyAutoFit was worked in a session clone at /home/user/pyautofit.

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
Issued: 2026-08-24

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
