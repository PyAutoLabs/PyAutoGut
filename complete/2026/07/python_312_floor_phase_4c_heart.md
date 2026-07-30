# Python 3.12 floor — Phase 4C: PyAutoHeart

Type: feature
Target: PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Parent: `python_312_floor_phase_4_independent.md`

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

## Scope

Raise @PyAutoHeart's own package metadata, classifiers, contributor contract,
and living documentation to Python 3.12/3.13. Keep the core release/install
matrix rewrite in campaign Phase 2; this slice only updates Heart's package and
direct development surface, with tests on both supported Python versions.

## Gates

- Built metadata reports `Requires-Python: >=3.12` with 3.12/3.13 classifiers.
- The full @PyAutoHeart suite passes on Python 3.12 and 3.13.
- No release-verification behavior from Phase 2 is duplicated or weakened.
