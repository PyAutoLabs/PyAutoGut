# Hands hygiene: expired announcement dead code, unregistered modules

Type: maintenance
Target: pyautohands
Repos:
- PyAutoHands
Difficulty: small
Autonomy: safe
Priority: low
Status: formalised

Found by the 2026-08-19 release-board census (#239):

- @PyAutoHands/autohands/generate_release_notes.py:23-46 carries an
  ANNOUNCEMENT banner mechanism that expired 2026-07-24 — now dead code.
  Delete it (delete the trap, don't document it).
- Several modules exist but are not registered in the `bin/autohands`
  dispatcher (navigator.py, check_navigator.py, regenerate_navigator.py,
  generate_markdown.py, validate_env_profiles.py, check_search_memory.py,
  check_dataset_allowlist.py). AGENTS.md prose was fixed (#239) to call them
  workflow-invoked modules; decide per module whether it should become a CLI
  verb or stay internal, and make `bin/autohands help` the complete registry.
- ~30 stale remote branches (incl. `origin/master`, `origin/release`,
  near-duplicate feature names) — sweep via /repo_cleanup.
