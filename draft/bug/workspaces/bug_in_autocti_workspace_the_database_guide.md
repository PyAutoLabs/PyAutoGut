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
