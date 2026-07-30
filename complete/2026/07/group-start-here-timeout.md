Reverted group/start_here.py to Nautilus, clearing the last classified failure
on the release surface.

- issue: autolens_workspace#402 (auto-closed) · pr: autolens_workspace#403
  (`8f81afb57`), merged unchanged; smoke + navigator green.
- measured regression: 217s (Nautilus, green run 30472573498) → 1800s timeout
  after d5c9802d converted the script to MultiStartProdigy; locally the
  converted script exceeded 42 min without completing, the reverted path
  completes in 509s cold. Group-scale models (several lens galaxies + halo)
  hit the same CPU compile/descent wall the conversion commit documented for
  `multi`. group joins the "Why Not MultiStartProdigy?" set with the numbers;
  imaging/interferometer/multi_galaxy keep the optimizer (within budget).
- trap: reverting docstring sections changes the script's contents listing —
  the navigator "Catalogue staleness" gate failed until
  `regenerate_navigator.py autolens` refreshed workspace_index.json.
- bonus live proof: the just-merged docs-only smoke gate classified this .py
  diff as docs_only=false and correctly ran the matrix (fail-closed working).
- perf follow-up routes to the MultiStartProdigy compile-census thread.

## Original prompt

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
