Cleared the standing "manifest drift: tenant firewall — 2 mismatch(es)"
readiness YELLOW without growing the firewall allowlist.

- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/217 (auto-closed)
- prs: PyAutoHands#218 (`c778379e9`) + PyAutoHeart#125 (`f237a08c1`), plus the
  PyAutoMind allowlist rename `d8dc28e` — all merged unchanged.
- resolution: `autocti_workspace` was ALREADY in repos.yaml; the flags were
  incident-narration comments in `autohands/generate.py` + its test (the
  113-notebook deletion story). De-instanced to "an unregistered workspace"
  (specifics live in git history + PyAutoHands#215) — the allowlist doctrine
  says never grow it casually.
- the firewall, re-run over the audit's OWN output, caught two NEW violations
  in the just-merged worktree-drift test file (PyAutoLabs-shaped fixture
  paths) — fixed in Heart#125; the check's allowlist entry renamed .sh→.py to
  follow the #124 refactor.
- verified pre-merge: `repos_sync.check_tenant_firewall` over a symlink farm
  of all edited repos → NONE. The YELLOW clears on the first tick.

## Original prompt

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
