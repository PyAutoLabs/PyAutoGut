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
