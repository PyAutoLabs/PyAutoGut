Unblocked Python 3.14: the factor-graph "'Gaussian' object is not iterable"
failure was Python 3.14's forkserver default start method, fixed by pinning
the pre-3.14 default (`fork` on POSIX) at every PyAutoFit pool/process site.

- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1437 (auto-closed)
- pr: PyAutoFit#1439 (`3467de94a`) — merged; CI green (3.12 + 3.13 + docs);
  shipped under human-authorized Heart-RED override (unrelated nightly
  "release validation FAILED (stage integrate)")
- root cause (single-variable confirmed): Python 3.14 changed the Linux
  default multiprocessing start method fork → forkserver. Unguarded
  workspace scripts + forkserver (which preloads `__main__`) corrupt the
  model instances dynesty pool workers receive; other pool creation
  silently degraded to a misleading "OS does not support multiprocessing"
  single-CPU fallback. In-process + pickle round-trips were CORRECT — the
  prompt's iteration-protocol and model-flattening hypotheses were ruled
  out empirically. Unmodified tutorial fails on 3.14; identical tutorial
  with fork forced completes.
- fix: new `autofit.non_linear.parallel.fork_context()` reproduces the
  pre-3.14 default on every platform (fork on POSIX except macOS — its
  default has been spawn since py3.8 and fork-with-threads can abort in
  ObjC runtimes, so pinning fork there would be NEW behavior; platform
  default on macOS/Windows). Applied at: dynesty pool (subclass — upstream
  hardcodes the default context), `make_pool`, SneakyPool/SneakierPool +
  Process/Queue layer (covers emcee/zeus), parallel EP optimiser, and
  nautilus (handed a managed pool object instead of `pool=<int>` so it no
  longer builds internal default-context pools). Dynesty's no-pool
  fallback log now includes the triggering exception.
- validation: full test_autofit 1641 passed / 2 skipped incl. new
  numpy-only fork-context tests (factor-graph likelihood computed in a
  real fork-pool worker == in-process value); 3.14.4 venv (full editable
  stack — installs cleanly, no dependency blocker) runs
  `overview_1_the_basics.py` end-to-end on the default start method.
- smoke: six workspaces — autofit 7/0, autogalaxy 13/0, autolens 34/0,
  euclid 6/0, HowToLens 6/0; the 11 autolens_workspace_test failures are
  PRE-EXISTING (three clusters controlled bit-identically on unchanged
  main autofit: jax_likelihood vmap mismatches, composition_mge
  prior_count 4≠6, #672 potential-correction dpsi errors; wst is 2 behind
  origin). Two parallel-run autolens_workspace failures vanished
  sequentially (known shared-state artifact).
- also surfaced (pre-existing, py3.13 + unchanged main): multi-core emcee
  (`number_of_cores=2`) hangs on the WSL dev box (nproc=1); single-core
  instant. Not filed — needs proper repro triage first.
- remaining for 3.14 promotion (separate small PRs): re-add 3.14 to
  PyAutoHands `python_matrix.yml`, add 3.14 classifiers to the libraries,
  retarget the PyAutoNerves 3.14 experimental banner.

## Original prompt

# Investigate FactorGraphModel instance shape on Python 3.14

Type: bug
Target: PyAutoFit
Difficulty: too-large
Autonomy: supervised
Priority: normal
Status: formalised

## Problem

`autofit_workspace/scripts/overview/overview_1_the_basics.py` runs cleanly
on Python 3.9–3.13 but fails on Python 3.14 with:

```
TypeError: 'Gaussian' object is not iterable
```

This was surfaced by the `python_matrix.yml` evidence run (issue
`PyAutoLabs/PyAutoBuild#74`, run 25208343008). Same script, same library
code — only the Python version differs.

3.14 was dropped from advertised support (classifiers + `python_matrix.yml`
matrix) until this is understood. `requires-python` still allows `>=3.9`,
so users who install on 3.14 anyway will see the import-time banner warn
that 3.14 isn't first-class.

## Reproducer

Run on Python 3.14 in a venv with the libraries installed editable:

```bash
python3.14 -m venv /tmp/py314
/tmp/py314/bin/pip install -e PyAutoConf -e PyAutoArray -e PyAutoFit \
    -e PyAutoGalaxy -e "PyAutoLens[optional]"
PYAUTO_TEST_MODE=1 PYAUTO_SMALL_DATASETS=1 \
    /tmp/py314/bin/python autofit_workspace/scripts/overview/overview_1_the_basics.py
```

Reproduces immediately when the script reaches the `factor_graph =
af.FactorGraphModel(*analysis_factor_list)` block (~line 545).

## Stack trace (abridged)

```
File "autofit_workspace/scripts/overview/overview_1_the_basics.py", line 813
    [profile_1d.model_data_from(xvalues=xvalues) for profile_1d in instance]
                                                                   ^^^^^^^^
TypeError: 'Gaussian' object is not iterable

The above exception was the direct cause of the following exception:

File "autofit_workspace/scripts/overview/overview_1_the_basics.py", line 563
    result_list = search.fit(model=factor_graph.global_prior_model,
                             analysis=factor_graph)
File "PyAutoFit/autofit/non_linear/search/abstract_search.py", line 668
    search_internal, fitness = self._fit(...)
File "PyAutoFit/autofit/graphical/declarative/collection.py", line 105
    log_likelihood += model_factor.log_likelihood_function(instance_)
File "PyAutoFit/autofit/graphical/declarative/factor/analysis.py", line 189
    return self.analysis.log_likelihood_function(instance)
```

The workspace `Analysis.log_likelihood_function` expects `instance` to be
a `Collection` of profiles (since the model was built as
`af.Collection(gaussian=Gaussian(), exponential=Exponential())`). On
3.9–3.13 it receives a `Collection`; on 3.14 it receives a single
`Gaussian` object directly.

## What we know

- `model = af.Collection(gaussian=Gaussian(), exponential=Exponential())`
- Each `AnalysisFactor` is built with `model.copy()` — so each factor's
  `prior_model` is itself a Collection of two profiles.
- `FactorGraphModel(*analysis_factor_list).global_prior_model` is the
  combined model passed to the search.
- On 3.9–3.13: `zip(self.model_factors, instance)` in
  `collection.py:104` yields `(factor, sub_instance)` pairs where
  `sub_instance` is the per-factor `Collection` instance — iterable.
- On 3.14: the same iteration yields a single `Gaussian` instance — not
  iterable.

So either:

1. `ModelInstance.__iter__` (which falls back to `__getitem__` since
   `ModelInstance` has no explicit `__iter__`) yields different child
   types on 3.14, OR
2. `FactorGraphModel.global_prior_model` constructs a flatter structure
   on 3.14 (collapses nested Collections into scalars), OR
3. dynesty's multiprocessing pickling round-trips the model differently
   on 3.14 (the trace shows `multiprocessing.pool.RemoteTraceback`,
   suggesting the worker process saw a different structure than the
   main process).

## Where to start investigating

1. Print `instance` and `type(instance)` at the top of the workspace
   `Analysis.log_likelihood_function` on a 3.14 venv. Compare against
   3.13. Specifically:
   - Is `instance` a `ModelInstance`, a `Collection`, or a raw
     `Gaussian`?
   - What does `instance.__dict__` look like on each version?
   - What does `list(instance)` do?

2. `autofit/mapper/model.py:385 ModelInstance` has no explicit
   `__iter__` — Python falls back to the legacy sequence protocol via
   `__getitem__`. `ModelInstance.__getitem__(int)` returns
   `list(self.values())[item]`. On 3.14, check whether `values()` and
   the resulting iteration yield different types than on 3.13.

3. `FactorGraphModel.global_prior_model` — trace how the per-factor
   Collection structures get composed into the global model. If 3.14
   flattens `Collection -> [profile_1, profile_2]` into bare profiles
   (because the dict ordering or attribute lookup behaves differently),
   the per-factor `instance_` would be a single profile.

4. Check whether `dynesty.pool` (from the failure trace) round-trips
   the model object correctly on 3.14. The error is wrapped in a
   `multiprocessing.pool.RemoteTraceback`, so the failure is happening
   in a worker process. Try `dynesty(parallel=False)` to isolate.

5. Python 3.14 release notes worth scanning for relevant behavior
   changes:
   - PEP 768: safe external debugger interface
   - PEP 749: late-bound default values (annotations)
   - PEP 765: disallow `return`/`break`/`continue` in `finally`
   - Behavior changes around `dict` ordering, `__init_subclass__`,
     `__set_name__`, descriptor lookup

## Constraints when fixing

- Don't modify the workspace tutorial script just to paper over the
  symptom. The script worked on 3.9–3.13 because the library produced
  the right shape; it should produce that same shape on 3.14.
- Library unit tests must remain numpy-only — don't add jax-dependent
  tests for this.
- If the fix requires a workspace-side change too (e.g. a defensive
  helper), keep it minimal and add a comment pointing back to this
  prompt.

## Done when

- `python3.14 autofit_workspace/scripts/overview/overview_1_the_basics.py`
  runs cleanly under `PYAUTO_TEST_MODE=1`.
- 3.14 can be re-added to PyAutoBuild's `python_matrix.yml` matrix and
  to each library's `pyproject.toml` classifiers.
- The change is unit-tested in `test_autofit/` with a numpy-only
  factor-graph round-trip test that would have caught the 3.14 shape
  collapse on 3.13 too if the structure had been wrong there.

<!-- formalised retroactively by the Intake (Conception) Agent on 2026-07-08 -->
