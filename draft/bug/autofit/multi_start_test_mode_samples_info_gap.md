# AbstractMultiStartGradient has no _test_mode_samples_info override (NUTS does)

Type: bug
Target: autofit
Repos:
- @PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: low
Status: draft

## Finding (2026-08-04, split out of autofit_workspace_test#83)

`AbstractSearch._fit_bypass_test_mode` (`autofit/non_linear/search/abstract_search.py:864`)
builds `samples_info` from `{total_iterations, time, log_evidence}` plus whatever
the subclass's `_test_mode_samples_info()` hook returns. The hook's own docstring
says it exists "so that tutorial scripts and downstream code can access those keys
without `KeyError`".

`BlackJAXNUTS` overrides it (`.../mcmc/blackjax/nuts/search.py:386`, writing
`total_steps: 0` among others). `AbstractMultiStartGradient` does **not** — so under
`PYAUTO_TEST_MODE=2` / `=3`, every key its real `samples_via_internal_from` writes
(`total_steps`, `n_starts`, `optax_method`, `stop_reason`, `converged`,
`convergence`, `fom_history`, `n_resurrections`, …) is simply absent, and any user
script reading them raises `KeyError`.

This surfaced as autofit_workspace_test#83, where the fix was on the workspace side
(the script must run a real search). The library override was deliberately rejected
there — a placeholder would have converted a loud `KeyError` into a vacuous pass
followed by a confusing truth-recovery failure.

## Task

Decide whether the hook contract is "every sampler with diagnostic `samples_info`
keys must override it" (→ add the MultiStartGradient override with NaN/0/None
placeholders, per the NUTS precedent) or "the hook is opt-in for keys downstream
code genuinely reads under bypass" (→ leave it, and say so in the hook docstring so
the asymmetry stops looking like an oversight).

Weigh against the workspace doctrine that a bypassed run should fail loudly rather
than silently produce placeholder diagnostics.

## Acceptance

Either `AbstractMultiStartGradient._test_mode_samples_info()` exists with
placeholders and a unit test asserting the bypass `samples_info` keys, or the base
hook's docstring states the opt-in rule explicitly. Not both, and not neither.
