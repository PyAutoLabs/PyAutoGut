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
