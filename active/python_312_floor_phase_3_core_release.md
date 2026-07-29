# Python 3.12 floor — Phase 3: coordinated core release

Type: feature
Target: PyAutoHands
Difficulty: large
Autonomy: supervised
Priority: high
Status: blocked — Stage 3 install verification failed Check E; live release not dispatched

Parent: `python_312_ecosystem_floor.md`
Depends on: phases 1 and 2

## Scope

Recheck PyPI's last-compatible unyanked versions, obtain the human version
choice, pass fresh Heart/pre-build gates, and release @PyAutoNerves,
@PyAutoArray, @PyAutoFit, @PyAutoGalaxy, and @PyAutoLens coherently. Verify the
published wheels reject Python 3.11 and install on 3.12/3.13. Do not yank usable
historical wheels. Record every unyanked pre-floor fallback that pip can still
select so Phase 6 describes rollback behavior accurately rather than promising
a hard resolution error.

## Release-validation checkpoint — 2026-07-29

- Authorized coordinated version: `2026.7.29.2`.
- TestPyPI rehearsal passed for all five packages at
  `2026.7.29.2.dev68901` (PyAutoHands run `30455540795`).
- Release-profile workspace validation passed all runnable scripts: 588 passed,
  0 failed, 91 deliberately skipped (PyAutoHeart run `30456078786`).
- Install verification A/B/C/D/F passed, including Python 3.12 and 3.13
  installs and the Python 3.11 `Requires-Python >=3.12` rejection.
- Install verification E failed because the workflow's final
  `actions/setup-python` step left unqualified `python3` at Python 3.13. The
  historical `2026.2.26.4` stack caps SciPy at 1.14.0, which has no Python 3.13
  wheel, so pip attempted a source build and failed for missing OpenBLAS.
- A diagnostic Check E run on Python 3.12 passed with all five historical
  packages installed at `2026.2.26.4`, confirming the test-harness boundary.
- The ingested Heart verdict is RED with `install verification FAILED
  (testpypi; checks E)` and `release validation FAILED (stage integrate)`.
- The unchanged-YELLOW authorization condition was not met. No live PyPI
  release, tag, yank, or issue closure was dispatched.
