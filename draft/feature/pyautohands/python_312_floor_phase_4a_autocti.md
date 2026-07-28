# Python 3.12 floor — Phase 4A: PyAutoCTI

Type: feature
Target: PyAutoCTI
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Parent: `python_312_floor_phase_4_independent.md`

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

## Scope

Raise PyAutoCTI package metadata and classifiers to Python 3.12/3.13 and update
its living installation claim. Preserve the archival JOSS paper and historical
traceback examples. Validate the full suite on both supported Python versions,
including the repository's documented `arcticpy==2.6` installation constraint.

## Gates

- Built metadata reports `Requires-Python: >=3.12` and only 3.12/3.13 Python
  classifiers.
- The full PyAutoCTI suite passes on Python 3.12 and 3.13.
- The release stays independent of the five-package core release and remains
  behind PyAutoCTI's resurrection/readiness gate.

