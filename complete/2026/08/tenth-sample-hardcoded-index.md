## tenth-sample-hardcoded-index
- issue: https://github.com/PyAutoLabs/autofit_workspace/issues/140 (closed)
- completed: 2026-08-19
- workspace-prs: autofit_workspace#141, autogalaxy_workspace#213, autolens_workspace#487,
  autocti_workspace#22 (all merged)
- notebook-regen-prs: autofit_workspace#142, autogalaxy_workspace#214, autolens_workspace#488
  (all merged) — those three workspaces' AGENTS.md require committing regenerated .ipynb twins
  alongside script changes; autocti_workspace's says release-time regeneration, so it has none.
  See [[feedback_notebook_regen_convention_differs_per_workspace]].
- summary: results/database/aggregator tutorials hardcoded stored-sample index 9 ("the tenth
  sample") in `parameter_lists[9][k]` and the four figure-of-merit `[9]` prints — IndexError
  for any stored run with <10 samples (test-mode sweeps). Unified the family to the final
  sample (`[-1]`) with matching prose across 10 scripts in 4 repos. autogalaxy's two
  aggregator guides had been part-fixed to `[0]` with stale "tenth sample" prose — realigned.
  autolens `galaxies_fits.py`'s two `from_sample_index(-10)` near-best demos clamped with
  `max(-10, -len(parameter_lists))` to preserve teaching intent.
- validation: direct regression proof — autocti database example under PYAUTO_TEST_MODE=1
  (<10 stored samples) crashed at `[9]` before, executes all fixed prints after; 8/8 touched
  guides PASS under CI env profiles (real_search); autofit/autogalaxy/autolens PR smoke green.
- traps: (1) a naive CI poll that greps `gh pr checks` output faked ALL-GREEN when gh returned
  EMPTY output (rate limit) — treat empty as pending, fail-closed; (2) two more pre-existing
  autocti drift sites found beyond this fix (FactorGraph `.cti` attribute, stale
  `aplt.subplot_fit_dataset_1d`) — filed as `draft/triage/bug_in_autocti_workspace_the_dataset_1d.md`.
- origin: found 2026-08-19 validating PyAutoFit#1504; sibling of [[database-guide-info-inline]],
  follow-up of [[stored-sample-reconstruction-guard]].

## Original prompt

# Bug in the workspaces: tutorial scripts hardcode stored-sample index 9

Type: bug
Target: workspaces
Repos:
- autocti_workspace
- autolens_workspace
- workspaces
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Bug in the workspaces: tutorial scripts hardcode stored-sample index 9 and crash under low-sample profiles. autocti_workspace scripts/dataset_1d/advanced/database/examples/samples.py:103 prints samples.parameter_lists[9][2]; autolens_workspace scripts/guides/results/aggregator/samples.py:200 and samples_via_aggregator.py:146 print samples.parameter_lists[9]. Any stored run with fewer than 10 samples (e.g. test-mode fake searches) raises IndexError; real-search runs pass, so this is latent in CI but breaks local/test-mode validation sweeps (found 2026-08-19). Fix: derive the index from len(samples.parameter_lists) or guard the print, in both workspaces (one PR per repo).

<!-- formalised by the Intake (Conception) Agent on 2026-08-19 from user-intake -->
