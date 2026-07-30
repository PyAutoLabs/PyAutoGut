# Python 3.12 floor — Phase 4B: PyAutoReduce

Type: feature
Target: PyAutoReduce
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Parent: `python_312_floor_phase_4_independent.md`

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

## Scope

Raise @PyAutoReduce package metadata, classifiers, tests, contributor contract,
and living documentation to Python 3.12/3.13. Remove only support machinery
made obsolete by the floor, preserving scientific behavior and independent
dependency constraints. Validate the full suite on both supported versions.

## Gates

- Built metadata reports `Requires-Python: >=3.12` with 3.12/3.13 classifiers.
- The full @PyAutoReduce suite passes on Python 3.12 and 3.13.
- Any release remains independent of the core stack and human/readiness gated.
