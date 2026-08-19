- issue: https://github.com/PyAutoLabs/PyAutoHands/issues/235 (closed by the 2026-08-19 reconcile sweep — see traps)
- prs: PyAutoNerves#148 (`e9f7c11`), PyAutoArray#447 (`7d1906e`), PyAutoFit#1488 (`fe9f813`), PyAutoGalaxy#573 (`49115ad`), PyAutoLens#698, PyAutoHands#236 — **all six MERGED 2026-08-17T22:03Z**, within 16 seconds of each other
- classification: maintenance (libraries + Hands) — version-stamp sync + release-sed hardening
- branch: `feature/version-stamp-sync-guards` (all six repos; remote branches may still exist — repo_cleanup territory)
- worktree: `~/Code/PyAutoLabs-wt/version-stamp-sync-guards` — release pending; free it in the next laptop session or let repo_cleanup flag it

## What shipped

The three-part package PyAutoHands#235 planned, verified merged on every main:

1. **Stamp sync** — the five frozen `__version__` literals synced
   `2026.7.23.1` → `2026.8.17.1` (verified on main: `autofit/__init__.py:167`
   reads `2026.8.17.1`), each with the freeze design documented in-line
   (git tag / stamped wheel = release truth; literal = last manual sync,
   deliberately NOT bumped per release — PyAutoBuild#118/#120).
2. **Dead stampers deleted** — the three unreferenced legacy `release.sh`
   scripts removed from PyAutoLens / PyAutoArray / PyAutoFit.
3. **Release-sed guards** — `PyAutoHands/.github/workflows/release.yml` now
   refuses an empty `$VERSION` in the live step and, after each stamp sed in
   both build jobs, `ast.parse`s the stamped `__init__.py` and asserts the
   exact `__version__ = "$VERSION"` line — the empirically-shown
   silent-SyntaxError-wheel failure mode is now loud.

Test evidence at ship (from the issue's 2026-08-17T22:04Z "Shipped" comment):
full library suites green (155/1058/1852/1111/538/314 passed, 0 failures);
smoke euclid 6/6 and HowToLens 50/50 passed.

## Traps and findings

- **THE WRAP-UP TAIL WAS DROPPED — this record is 2 days late.** The shipping
  session merged all six PRs and posted the "Shipped" comment on #235 at
  22:04Z, promised the re-run smoke result ("autofit/autogalaxy/autolens/
  autolens_test legs are re-running — result will be posted here"), and then
  died. The smoke result was never posted, #235 was never closed, no record
  was written, and the active.md entry went stale. Found and reconciled by
  the 2026-08-19 completed-tasks sweep. The close rests on the six merged
  PRs + the green suites; reopen #235 if the lost smoke legs turn out to have
  found something real.
- **Wrong-PR pointer in active.md.** The stale entry's status line read
  `pr-open (PyAutoLens/pull/700)` — but #700 is the
  positions-lh-penalty-accumulation PR (a different task shipped the same
  evening from the same session). Consistent with that record's
  "registry-edit trap": a blanket `sed` status edit across active.md sections.
  Scope registry edits to the task's own `##` section.
- **Detection gap (now closed by this sweep's follow-up):** `lifecycle.py
  issues` only flags entries whose tracking ISSUE is closed. In this failure
  mode the dying session never closes the issue, so the drift was invisible
  to the only reconciliation check that existed — and that check needs `gh`,
  so it never runs in CI or cloud sessions anyway.
- Behavioral note from the ship comment (still true until acted on): the
  synced stamp is >30 days past the workspace floors (2026.7.9.1), so source
  checkouts running workspace scripts see the `check_version` staleness
  warning pip users already see. Remedy when it becomes noise: bump
  `version.minimum_library_version` in the workspace configs or set
  `PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`.

## Original prompt

# Version-stamp sync to 2026.8.17.1 + release-sed guards

Type: maintenance
Target: libraries
Repos:
- @PyAutoNerves
- @PyAutoArray
- @PyAutoFit
- @PyAutoGalaxy
- @PyAutoLens
- @PyAutoHands
Difficulty: small
Autonomy: safe
Priority: medium
Status: draft

Original request (verbatim): "should we even bother with having these versions?
I think we should but if so they should update?" → "ok do it but do a bit more
deep research on the source code first to make sure its the right approach".

In-session research (2026-08-17, full readers/writers map + handshake
mechanics) concluded the derive-from-`importlib.metadata` migration is
net-negative for this stack: local dev resolves libs via `PYTHONPATH` (no dist
metadata → fallback always taken → per-run `check_version` UserWarning), the
release stamp sed would corrupt a `try/except` block into SyntaxError wheels,
assistant chat-bundle regeneration would publish dev stamps to users, and
per-release bump commits to library mains are the documented cause of the
June/July 2026 accidental-release cascade (PyAutoBuild#118/#120). Human chose
the manual-sync-plus-guards package instead:

1. **Sync the five frozen `__version__` literals** from `2026.7.23.1` to the
   latest release `2026.8.17.1` (same deliberate manual sync that produced
   7.23): `autonerves/__init__.py:119`, `autoarray/__init__.py:110`,
   `autofit/__init__.py:163`, `autogalaxy/__init__.py:134`,
   `autolens/__init__.py:154`. Add a one-line comment at each stamp site
   documenting the freeze design (git tag / stamped wheel = release truth;
   this literal = last manual sync, deliberately NOT bumped per release).
2. **Delete the three dead legacy stampers** — `PyAutoLens/release.sh`,
   `PyAutoArray/files/release.sh`, `PyAutoFit/files/release.sh` — unreferenced,
   and their `grep -v __version__` rewrite would mangle any future refactor of
   the stamp lines.
3. **Guard the live release seds** in
   `PyAutoHands/.github/workflows/release.yml` (~136 rehearsal build, ~431 live
   build): after each `sed`, verify the stamped `__init__.py` still parses
   (`python3 -c "import ast; ast.parse(...)"`) and contains the exact
   `__version__ = "$VERSION"` line, failing the job loudly otherwise. The sed's
   unanchored zero-or-more pattern was empirically shown to be able to ship a
   SyntaxError wheel silently.

Supersedes `nerves_version_stamp_behind_consensus.md` (its drift already
resolved — all five stamps read 2026.7.23.1; the pre_build stamp-sweep question
it raised is moot since pre_build no longer stamps versions). While in
`version_drift.sh` territory: no change needed there — literal date stamps
remain grep-able after this task.
