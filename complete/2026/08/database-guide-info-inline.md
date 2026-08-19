## database-guide-info-inline
- issue: https://github.com/PyAutoLabs/autocti_workspace/issues/20 (closed)
- completed: 2026-08-19
- workspace-pr: https://github.com/PyAutoLabs/autocti_workspace/pull/21 (merged)
- summary: the dataset_1d database guide chain failed on any fresh checkout —
  `database/start_here.py` read `dataset/.../norm_*/info.json` which no simulator writes.
  Replaced the file-read loop with an inline (hypothetical) charge-injection `info` dict,
  mirroring the autolens database guide; dropped the dead `info_list` loop and the unused
  `import json`. Notebook twin left to release-time regeneration.
- validation: full generated-state wipe (dataset/, output/, database.sqlite), then
  `PYAUTO_TEST_MODE=1 python scripts/dataset_1d/advanced/database/start_here.py` — exit 0
  with zero info.json files present.
- trap: stale output/ from a prior same-identifier run makes the guide's second section
  (build-database-from-output-folder) fail with `UNIQUE constraint failed: fit.id` —
  identifier ignores info content, so wipe output/ before before/after comparisons.
- origin: found 2026-08-19 validating PyAutoFit#1504; filed via intake from
  [[stored-sample-reconstruction-guard]] follow-ups.

## Original prompt

# Bug in autocti_workspace: the database guide chain cannot run from

Type: bug
Target: workspaces
Repos:
- autocti_workspace
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

Bug in autocti_workspace: the database guide chain cannot run from a fresh checkout. scripts/dataset_1d/advanced/database/start_here.py line ~165 reads dataset/dataset_1d/simple/norm_*/info.json for every norm, but no simulator under scripts/dataset_1d/simulators/ ever writes info.json, so a fresh run raises FileNotFoundError before any model-fit starts. The repo has no CI, which is why it went unnoticed (found 2026-08-19 during downstream validation of a library change). Fix in autocti_workspace only: write info.json in the dataset_1d simulators, or drop the info.json read from the database scripts.

<!-- formalised by the Intake (Conception) Agent on 2026-08-19 from user-intake -->
