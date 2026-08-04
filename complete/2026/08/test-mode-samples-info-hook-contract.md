## test-mode-samples-info-hook-contract
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1448
- completed: 2026-08-04
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1449 (MERGED as 8f706c51)
- summary: `NonLinearSearch._test_mode_samples_info()`'s docstring told subclasses
  to override it "so that tutorial scripts and downstream code can access those
  keys without KeyError", which reads as a per-sampler obligation — so the fact
  that only 1 of 9 searches writing `samples_info` overrides it looked like an
  oversight in the other 8. Investigation showed the asymmetry is CORRECT and the
  docstring wrong. Rewrote it to state the opt-in rule. Docstring-only: no
  behaviour change, no new override, no new test.
- reachability (the deciding evidence): no LIBRARY path reads these diagnostic
  keys under bypass. `SamplesMCMC.total_steps` (samples/mcmc.py:200) and
  `SamplesNest.number_live_points`/`total_samples`/`log_evidence`
  (samples/nest.py:77-92) live on Samples subclasses the bypass never constructs
  — `_fit_bypass_test_mode` (abstract_search.py:864) ALWAYS builds a SamplesPDF.
  Only workspace scripts reading `samples_info[...]` directly can be affected.
- consumer sweep (all 11 workspace/tutorial repos): exactly TWO direct-read sites.
  (1) autofit_workspace/scripts/searches/mcmc.py:335 PRINTS ess_min/num_samples/
  mean_acceptance/n_divergent/n_logl_evals, has NO `__Env__` declaration, and is
  LINE 2 of that workspace's smoke_tests.txt — so it runs bypassed on EVERY PR.
  That is why PyAutoFit#1260 (5d175ebcc, May 2026) added both the hook and the
  BlackJAXNUTS override. (2) autofit_workspace_test jax_assertions/
  multi_start_gradient_auto_convergence.py:130 ASSERTS on total_steps — fixed on
  the workspace side with `ENV: real_search jax` (wst#83 / PR#84, f4c45c1).
  Nautilus/Dynesty/Emcee/Zeus have no bypassed consumer either, hence no override;
  autofit_workspace/scripts/searches/mle.py uses MultiStartAdam but never touches
  samples_info, so MultiStartGradient has no bypassed consumer at all.
- the rule now in the docstring: PRINTS → override with NaN/0 placeholders;
  ASSERTS → the script declares `ENV: real_search` instead. Adding placeholders
  for an asserting reader is WORSE than the KeyError it replaces — the assert then
  silently passes on a stub value.
- rejected (human-decided): an AbstractMultiStartGradient override for surface
  consistency with NUTS (serves no consumer; creates the silent-pass hazard), and
  a unit test pinning the bypass keys (cannot express "the others deliberately
  have none" without freezing the sampler roster).
- validation: pytest test_autofit/non_linear/search 172 passed / 1 skipped;
  docutils RST lint of the docstring 0 warnings; PR CI green on all three checks
  INCLUDING docs/docs-build (the check that catches malformed RST in a docstring);
  diff verified to contain no non-docstring line (28 insertions, 5 deletions, one
  file).
- heart: shipped under human-acknowledged YELLOW — same three reasons as the
  wst#83 ship earlier the same day (workspace validation not passing / tenant
  firewall manifest drift / stale release validation), score 70, no RED.
- correction: the issue body called the class `AbstractSearch`; it is
  `NonLinearSearch` (abstract_search.py:136). Corrected by comment on #1448; the
  PR and docstring use the right name. NOTE a pre-existing stale `AbstractSearch`
  reference survives in a comment at abstract_search.py:1185 — left alone, out of
  scope.
- claim-note: BOTH PyAutoFit claims in active.md were stale and were released to
  clear the conflict guard — point-source-defaults-campaign (#1441 merged
  2026-08-01T12:47:32Z) and nautilus-1core-serial-pool (#1443 merged
  2026-08-01T19:12:47Z, merge commit 5bf32dab on origin/main). The latter task
  looks fully shipped while its status line still says "PR OPEN ... awaiting CI";
  it wants a completion pass of its own.

## Original prompt

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
