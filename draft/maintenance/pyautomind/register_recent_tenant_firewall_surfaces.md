# Register recent tenant-firewall surfaces

Type: maintenance
Target: pyautomind
Repos:
- @PyAutoMind
Difficulty: small
Autonomy: supervised
Priority: high
Status: draft

PyAutoHeart's current readiness verdict has one actionable warning: the
`repos_sync.py` tenant firewall reports six file-level mismatches introduced by
recent merged work in PyAutoBrain and PyAutoHands. The other two YELLOW reasons
are standing, accepted first-run gaps.

Audit the six mismatches against the firewall doctrine and register only the
intentional instance facts in `PyAutoMind/scripts/repos_sync.py`'s frozen
`FIREWALL_ALLOWLIST` baseline. The affected files are:

- `PyAutoBrain/agents/conductors/hygiene/_hygiene_optdeps.py`
- `PyAutoBrain/agents/conductors/hygiene/_hygiene_refs.py`
- `PyAutoBrain/bin/clean_slate.sh`
- `PyAutoBrain/tests/test_clean_slate.py`
- `PyAutoBrain/tests/test_hygiene_conductor.py`
- `PyAutoHands/autohands/run_notebook.py`

These facts are intentional policy inventories, test fixtures, or explanatory
examples of the same kind already represented by the baseline. Keep the fix
confined to PyAutoMind; do not weaken the detector, bulk-allow future facts, or
introduce a cross-organ configuration refactor for this maintenance task.

Acceptance:

- `python3 scripts/repos_sync.py --check` reports the tenant firewall clean.
- Existing manifest-sync checks remain green.
- A negative regression check still proves that a new fact in a listed file or
  any fact in an unlisted file is reported as drift.
- Re-run `/health` and record the resulting authoritative Heart verdict without
  attempting to clear the two accepted standing YELLOW reasons.

## Original request

> do the next bit of work
