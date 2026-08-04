# multi_start_gradient_auto_convergence.py KeyError: 'total_steps' in workspace-smoke

Type: bug
Target: autofit_workspace_test
Repos:
- @autofit_workspace_test
Difficulty: small
Autonomy: supervised
Priority: medium
Status: draft

## Original request (verbatim)

> 2. multi_start_gradient_auto_convergence.py KeyError
>
> In the PyAutoLabs workspace, this script fails in workspace-smoke:
>
>   autofit_workspace_test scripts/jax_assertions/multi_start_gradient_auto_convergence.py
>   KeyError: 'total_steps'   (FAIL after 4.7s)
>
> Evidence: PyAutoHeart workspace-smoke run 30858578587, job
> "smoke / run_scripts (3.12, autofit_test, jax_assertions)",
> 2026-08-03T22:28:40Z. Ran against released autofit 2026.7.29.2.
>
> Fails fast (4.7s), so it looks like a plain contract break between the
> script and whatever dict it reads 'total_steps' from — likely a
> MultiStartGradient progress/result structure that changed. Find who
> writes that key, decide whether the library or the script is wrong, and
> fix the owning side. Route through start_dev.

## Root cause (reproduced locally 2026-08-04)

Not a library contract break — the script runs with the **sampler bypassed**.

- The script's `__Env__` section declares `ENV: jax`, which releases only
  `PYAUTO_DISABLE_JAX`. `profile_smoke.yaml`'s default `PYAUTO_TEST_MODE: "2"`
  therefore still applies.
- Under `PYAUTO_TEST_MODE=2`, `AbstractSearch._fit_bypass_test_mode` skips
  `_fit` entirely and builds `samples_info` from
  `{total_iterations, time, log_evidence}` + `_test_mode_samples_info()`.
  `AbstractMultiStartGradient` does not override that hook (only BlackJAX NUTS
  does), so `total_steps` is absent.
- Script line 123 `result.samples.samples_info["total_steps"]` → KeyError.

Reproduced verbatim with `PYAUTO_TEST_MODE=2` + JAX enabled: KeyError at
line 123, ~4.5 s — matching CI.

`samples_via_internal_from` has always written `total_steps` into
`samples_info` (since 63cd4e222, the original multi-start commit), and the
released 2026.7.29.2 has it. The library never changed.

The bypass can never satisfy this script: it asserts truth recovery
(`normalization ≈ 25`), and the bypass returns the prior median, which for
`LogUniformPrior(1e-2, 1e2)` is 1.0. This is a real-inference assertion script
and must run the real search — exactly like its siblings
`scripts/searches/MultiStartAdam.py` / `MultiStartProdigy.py` /
`BlackJAXNUTS.py`, which all declare `ENV: real_search jax`.

Not a regression: the same failure appears in the previous workspace-smoke run
(30790463134, 2026-08-03T06:33Z). `jax_assertions/` only ever had
`unset: [PYAUTO_DISABLE_JAX]` in the pre-migration profile, so the
declaration migration (#187/#189) was a no-op — the script has been broken
under the smoke profile since it was authored. It is not in `smoke_tests.txt`,
so the per-PR gate is unaffected; only the full-profile sweep runs it.

## Task

1. Change the script's declaration to `ENV: real_search jax` (releasing
   `PYAUTO_TEST_MODE` as well), with the rationale comment beside it in the
   `__Env__` section, mirroring `scripts/searches/MultiStartAdam.py`.
2. Fix the module-docstring reference `af.AbstractMultiStartGradient` — that
   symbol is not exported on `af` (the class lives in
   `autofit.non_linear.search.mle.multi_start_gradient`). The stale `af.`
   prefix trips the PyAuto API gate on any local run of the script.

Library side considered and rejected for this fix: adding a
`_test_mode_samples_info()` override to `AbstractMultiStartGradient` (as
BlackJAX NUTS has) would supply a placeholder `total_steps` but would only
convert a loud KeyError into a vacuous pass followed by a confusing
truth-recovery failure. Worth raising separately as a consistency question,
not as the repair here.

## Acceptance

`scripts/jax_assertions/multi_start_gradient_auto_convergence.py` passes under
the resolved smoke env (`build_env_for_script` with
`config/build/profile_smoke.yaml`), running the real search.

Verified pre-fix by running it with `PYAUTO_TEST_MODE` unset: parts A/B/C all
pass — "Auto-convergence stopped after 158 / 300 steps", recovered
`centre=50.156, normalization=25.197, sigma=9.858`, HLO byte-identical across
builds, results-DB round-trip `converged=True, stop_reason=converged`,
`fom_history` length 158. Wall time ~60 s (vs 4.7 s bypassed) — acceptable for
the full-profile sweep, which is the only place this script runs.
