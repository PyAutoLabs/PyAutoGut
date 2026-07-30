# Clear the standing "tenant firewall" manifest drift (autocti_workspace)

Type: maintenance
Target: pyautohands
Repos:
- PyAutoHands
- PyAutoMind
Difficulty: small
Autonomy: safe
Priority: normal
Status: draft

## Problem

Heart readiness carries a permanent YELLOW:
`manifest drift: tenant firewall (organ code) — 2 mismatch(es) vs PyAutoMind/repos.yaml`.
The two problems are `PyAutoHands/autohands/generate.py:66` and
`tests/test_generate_validates_project.py:6` — both mention `autocti_workspace`,
which the firewall check flags as instance facts in unlisted files (the known
"autocti still unregistered" gap from generate.py PR#216).

## Scope

Pick the consistent resolution and apply it: either register `autocti_workspace`
properly (PyAutoMind/repos.yaml + whatever allowlist `heart/checks/manifest_drift.py`
reads, then `repos_sync.py --write`), or remove/parameterise the hard-coded
references in generate.py and its test. Verify with a local
`python3 heart/checks/manifest_drift.py` run showing 0 mismatches.
