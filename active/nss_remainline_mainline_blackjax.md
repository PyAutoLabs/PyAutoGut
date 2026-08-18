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
