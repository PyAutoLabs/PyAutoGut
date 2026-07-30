# Stale parked-script sweep: re-measure 11 no_run entries against the real cap

Type: maintenance
Target: workspaces
Repos:
- autogalaxy_workspace
- autolens_workspace
- autolens_workspace_test
Difficulty: small
Autonomy: supervised
Priority: normal
Status: issued — https://github.com/PyAutoLabs/autolens_workspace_test/issues/234

11 stale SLOW entries; seven cite a 60s cap that never existed. Delete, re-run
each directory through run_python.py under profile_smoke (sequential), keep
deletions under cap, restore over-cap with 2026-07-30 dates + corrected reasons.
Filed from the 2026-07-30 CI/release audit follow-on assessment.
