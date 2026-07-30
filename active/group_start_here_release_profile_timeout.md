# group/start_here.py times out at 1800s under the release profile

Type: bug
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

## Symptom

`autolens/scripts/group/start_here.py` hit the 1800s release-profile cap
(`BUILD_SCRIPT_TIMEOUT=1800`) in Heart workspace-validation run cloud#30516167217
(mode=release, 2026-07-30). Smoke mode (test-mode, 300s cap) passes; only the
release-fidelity run (real searches, `PYAUTO_TEST_MODE=1` reduced sampler for user
workspaces) exceeds the cap.

## Scope

Triage, not necessarily a code fix: decide whether to (a) profile and speed the
script's release-profile path, (b) tighten its search settings under the release
profile, or (c) park it via the slow-skip mechanism with a recorded justification.
Do not raise the global timeout for one script. Check whether the duration regressed
recently (compare earlier green mode=release runs, e.g. run 30472573498 on
2026-07-29 where the release surface passed 588/0).
