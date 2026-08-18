Re-mainlined `af.NSS` (nested slice sampling) into PyAutoFit as a proper
first-class search on **mainline blackjax ≥1.6**, with integration-test
coverage restored — human-directed 2026-08-18, executed entirely from a
mobile/cloud session on CPU.

- **PRs (both merged):** PyAutoFit#1492 (`401e666`, closes #1491) — the
  search, tests, `__init__` export, optional-extra blackjax floor
  ≥1.2.0 → ≥1.6.2; autofit_workspace_test#86 (`12da16d`) —
  `scripts/searches/NSS.py` integration script.
- **Why now:** the search was removed in PyAutoFit#1356/#1357 solely because
  its dependencies were unshippable git-fork pins; nested sampling merged
  into mainline blackjax 1.6, so the removal reason vanished. Implementation
  restored verbatim from the `autofit_workspace_developer/searches/nss/`
  stash (whose README's re-mainlining checklist this executes).
- **The mainline port (3 diffs):** `from nss.ns import log_weights, finalise`
  → `blackjax.ns.utils`; `SliceInfo.num_steps` → `num_expansions` (eval
  counter); the chunked GPU-memory builder recomposed from mainline public
  helpers (`build_slice_kernel`/`slice_constrained_step`/
  `build_adaptive_kernel`/`live_covariance`) since mainline `build_kernel`
  dropped the fork's `update_strategy=` seam. `_chunked_update.py` needed no
  logic change (byte-equivalent to mainline's `update_with_mcmc_take_last`
  bar the vmap→lax.map swap).
- **Validation:** port proven on a 2D analytic toy BEFORE any source change
  (logZ −4.558 ± 0.078 vs analytic −4.605; **chunked bit-identical to
  unchunked at fixed seed**); 17/17 restored unit tests + full CI green
  (3.12/3.13/docs); integration script validated in direct and
  PYAUTO_TEST_MODE=1 runs against the PR branch (logZ −72.16 ± 0.42, ESS
  417, chunked ≡ unchunked) — merged after #1492 per the library-first gate.
- **Traps for the record:** (1) a quick-update Fitness-wiring convention test
  added after the removal (`test_quick_update_wiring.py`) tripped on the
  restored search — NSS never samples through Fitness, so the fix is an
  EXEMPT entry with reason, not forwarding the kwarg to a dead path.
  (2) PyAutoFit#1494 (clipper identifiers) landed on main mid-PR — its
  nested-sampler identifier tripwire pins a fixed search list, so NSS is
  unaffected; verified by merging main locally and running all 55 affected
  tests before pressing merge. (3) blackjax is an optional extra, not a hard
  autofit dep — environments must install/upgrade it explicitly.
- **Programme tie-in:** scope-change entry in the inference DECISIONS.md
  (autolens_profiling#144): re-mainlined ahead of Gate A per human direction;
  Gate A still decides GPU-baseline adoption. Phase 2 can now drive `af.NSS`
  directly (the "profiling-local runner first" hedge is obsolete).
- **Follow-ups:** restore the `Search: NSS` tutorial section in
  `autofit_workspace/scripts/searches/nest.py` (stash checklist item 5,
  user-facing docs); blackjax ≥1.6.2 upgrades in the local venvs + RAL stack
  (re-run `autolens_profiling/scripts/misc/searches/nss_smoke.py` there);
  Phase 2 GPU re-benchmarking campaign.

## Original prompt

# Re-mainline af.NSS as a proper PyAutoFit search on mainline blackjax ≥1.6

Type: feature
Target: autofit
Repos:
- @PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: high

Human-directed 2026-08-18 (mobile session): the parked `af.NSS` nested slice
sampler — removed from PyAutoFit on 2026-07-11 (PyAutoFit#1356/#1357) solely
because its dependencies were unshippable git-fork pins — should be
reimplemented as a proper first-class search now that nested sampling is in
**mainline blackjax 1.6** (the whole removal reason is gone). The full
working implementation is preserved verbatim at
`autofit_workspace_developer/searches/nss/` with a re-mainlining checklist
in its README.

Port surface (validated on CPU 2026-08-18 in the cloud session before any
source change; see autolens_profiling#142 for the environment validation):

- `from nss.ns import log_weights, finalise` → `blackjax.ns.utils`.
- SliceInfo eval counter: fork `num_steps` → mainline `num_expansions`.
- Chunked GPU-memory path: the fork's `build_kernel(update_strategy=)` seam
  is gone — recompose from mainline public helpers (`build_slice_kernel`,
  `slice_constrained_step`, `build_adaptive_kernel`, `live_covariance`);
  `_chunked_update.py` is already byte-equivalent to mainline's
  `update_with_mcmc_take_last` bar the vmap→lax.map swap.
- End-to-end validation on a 2D analytic toy through the full search
  pipeline: logZ −4.558 ± 0.078 vs analytic −4.605; **chunked path
  bit-identical to unchunked** (same logZ/evals/ESS at fixed seed).

Task (stash README checklist, PyAutoFit side):
1. Restore `autofit/non_linear/search/nest/nss/` (search.py, samples.py,
   _chunked_nss.py, _chunked_update.py, __init__.py) with the mainline port
   and fork-era prose removed.
2. Restore `test_autofit/non_linear/search/nest/nss/` (kept verbatim against
   library import paths; one ImportError match-string update).
3. `autofit/__init__.py`: re-export `NSS`.
4. `pyproject.toml`: bump the `optional` extra's blackjax floor to ≥1.6.2
   (no cap exists).
5. Run the nss test subset + smoke the search end-to-end from the checkout.

Note the programme-plan interaction: PROGRAMME §7 gated "af.NSS re-mainlined
on blackjax.nss" behind Gate A — the human has directed early re-mainlining;
Gate A still decides whether NSS becomes the GPU nested-sampling *baseline*.
Record the scope change in the inference DECISIONS.md. The workspace
tutorial restoration (checklist item 5) is a separate follow-up task.
