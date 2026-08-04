# _test_mode_samples_info is opt-in, but its docstring reads as an obligation

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
`self._test_mode_samples_info()` returns (merged at line 947). The base hook
(line 979) returns `{}` and tells subclasses to override it "so that tutorial
scripts and downstream code can access those keys without `KeyError`".

Nine search modules write `samples_info` in their real path (nautilus, dynesty,
emcee, zeus, bfgs, drawer, blackjax nuts, multi_start_gradient, abstract).
**Exactly one overrides the hook: `BlackJAXNUTS`.** Read against that docstring,
the other eight look like they are missing an override.

## Investigation — the asymmetry is correct, the docstring is wrong

**Reachability.** No *library* path reads these diagnostic keys under bypass. The
properties that read them — `SamplesMCMC.total_steps` (`samples/mcmc.py:200`),
`SamplesNest.number_live_points` / `total_samples` / `log_evidence`
(`samples/nest.py:77-92`) — live on Samples subclasses the bypass never
constructs; `_fit_bypass_test_mode` always builds a `SamplesPDF`. The only
possible consumers are workspace scripts reading `samples_info[...]` directly.

**Consumer sweep** across all eleven workspace/tutorial repos finds exactly two
such sites:

- `autofit_workspace/scripts/searches/mcmc.py:335` — prints `ess_min`,
  `num_samples`, `mean_acceptance`, `n_divergent`, `n_logl_evals`, and has **no**
  `__Env__` declaration, so it runs bypassed under smoke. This is the reason the
  NUTS override exists: commit `5d175ebcc` (#1260, May 2026) added the hook and
  that single override to stop this tutorial crashing.
- `autofit_workspace_test/scripts/jax_assertions/multi_start_gradient_auto_convergence.py:130`
  — *asserts* on `total_steps`; fixed on the workspace side with
  `ENV: real_search jax` (wst#83 / PR#84, merged `f4c45c1`).

Nautilus, Dynesty, Emcee and Zeus have no bypassed consumer either — which is why
none of them override the hook. `autofit_workspace/scripts/searches/mle.py` uses
`MultiStartAdam` but never touches `samples_info`, so MultiStartGradient has no
bypassed consumer at all.

So the hook is **opt-in**, and the rule the two live decisions actually follow is:

> **Prints → placeholders. Asserts → real search.** A tutorial that only
> *displays* diagnostics may legitimately run bypassed, so its search needs the
> override with honest empties. A script that *asserts* on diagnostics must not
> run bypassed at all — it declares `ENV: real_search`, and no override is wanted.

That rule is written down nowhere, which is why the gap reads as an oversight.

## Task (human-decided 2026-08-04: document the rule)

Rewrite the `_test_mode_samples_info` docstring in
`autofit/non_linear/search/abstract_search.py` to state that the hook is opt-in
rather than a per-sampler obligation, carry the print-vs-assert test, and cite
both live precedents (BlackJAXNUTS #1260; AbstractMultiStartGradient's deliberate
non-override + wst#83).

Do **not** add an `AbstractMultiStartGradient` override: it serves no existing
consumer, and a placeholder `total_steps` would let a future
`assert total_steps < n_steps` silently pass on a stub `0` — the exact failure
mode avoided in wst#83.

No unit test: a test can pin `BlackJAXNUTS`'s keys but cannot express "and the
others deliberately have none" without freezing the sampler roster.

## Acceptance

The base hook's docstring states the opt-in rule and the print-vs-assert test
explicitly, so the next person hitting a bypass `KeyError` knows which of the two
fixes applies. Docstring-only — no behaviour change, no new override.
