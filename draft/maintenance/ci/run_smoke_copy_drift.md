# run_smoke.py: 9 per-repo copies, 5 drifted revisions, no sync mechanism

Type: maintenance
Target: ci
Repos:
- @PyAutoHands
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

## Finding (2026-07-25, during the notebook skip-guard fix)

Every workspace's PR smoke gate runs its own copy of
`.github/scripts/run_smoke.py`. There are **9 copies across the workspace
repos in 5 distinct revisions** — they have already drifted:
autofit_workspace + autolens_workspace share one revision; HowToLens +
HowToGalaxy + autofit_workspace_test share another; autogalaxy_workspace,
autogalaxy_workspace_test, autolens_workspace_test and autocti_workspace_test
are each unique. PyAutoHeart's reusable smoke-tests.yml deliberately leaves
the runner in the workspace, but nothing keeps the copies aligned.

Immediate consequence: PyAutoHands#198 taught the authoritative executor
(`autohands/build_util.py::execute_notebook`) to treat a clean `SystemExit: 0`
notebook exit as a PASS (the optional-dep skip-guard idiom), but the 9 smoke
copies still carry their own `execute_notebook` and keep reporting the
spurious FAIL until each adopts it. Adoption is ~2 lines per repo (they
already import `env_config` and `build_util.py_to_notebook` from PyAutoHands);
the exact snippet + full copy inventory is documented in
PyAutoHands `docs/internals.md`.

## Task

1. Short term: roll the 2-line adoption across the 9 copies (one PR per repo,
   mechanical).
2. Structural: decide whether `run_smoke.py` should become a PyAutoHands-owned
   module that the per-repo copies thin-wrap — the `env_config.py` precedent
   exists precisely because a local copy drifted. If yes, implement the shared
   module and reduce each repo's script to the wrapper.

## Acceptance

- A notebook exiting via the skip-guard passes every workspace's PR smoke gate.
- Either all copies are byte-identical thin wrappers, or a documented reason
  why per-repo divergence is intentional.
