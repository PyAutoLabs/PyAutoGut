# Python 3.12 floor — Phase 4D: Euclid assistant

Type: feature
Target: euclid_assistant
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Parent: `python_312_floor_phase_4_independent.md`

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

## Scope

Raise @euclid_assistant package metadata, classifiers, test/development
configuration, and living setup documentation to Python 3.12/3.13. Preserve
historical/provenance material and keep assistant-content updates scoped to
live support claims.

## Gates

- Built metadata reports `Requires-Python: >=3.12` with 3.12/3.13 classifiers.
- The assistant's validation/test suite passes on Python 3.12 and 3.13.
- No generated or historical content changes outside the intended support
  claims.
