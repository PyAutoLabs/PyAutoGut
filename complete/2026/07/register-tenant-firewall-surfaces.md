## register-tenant-firewall-surfaces
- issue: https://github.com/PyAutoLabs/PyAutoMind/issues/114
- completed: 2026-07-29
- library-pr: https://github.com/PyAutoLabs/PyAutoMind/pull/115
- summary: Registered the exact intentional instance-fact sets for six recent PyAutoBrain/PyAutoHands surfaces in the frozen tenant-firewall baseline, clearing the false manifest drift without changing organ source or detector semantics.
- validation: `python3 scripts/repos_sync.py --check` PASS; `git diff --check` PASS; negative probes confirmed new facts still fail in both unlisted and allowlisted files.
- review: Claude Opus 5 max-effort CLEAN on exact head `6b2583a8a812277eedc4f2d2f84e5b41fc802c85` after one low ordering finding was fixed in a separate non-amended commit.
- merge: PR #115 merged as `2a02a460f6156b5ef9a4363931dd0bbc8b6b392c`; merged `scripts/repos_sync.py` blob `4278273a427e236f2ca11b095d8406f886646233` is byte-identical to the reviewed head and the first-parent merge delta contains only that file.
- workspace-impact: none; this is an internal PyAutoMind manifest table with no package runtime or public API, so workspace smoke tests were not applicable.
- heart-before: YELLOW 80 — workspace validation not passing (13 failed, 2026-07-21T19-05-22Z); 33 stale parked scripts; tenant firewall 6 mismatches. The task directly addresses the third reason.
- notes: Opus identified pre-existing stale allowlist entries and broader checker-coverage opportunities as non-blocking future hygiene; this PR introduced none and deliberately stayed within its corrective scope.

## Original prompt

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
