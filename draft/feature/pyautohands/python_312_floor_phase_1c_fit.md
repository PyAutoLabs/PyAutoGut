# Python 3.12 floor — Phase 1C: PyAutoFit

Type: feature
Target: PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

Parent: `python_312_floor_phase_1_core.md`
Depends on: `python_312_floor_phase_1b_array.md`

## Scope

In @PyAutoFit, raise metadata/classifiers to 3.12/3.13, remove the now-
tautological optax Python marker and its stale explanatory comment without
loosening the pin, replace the two Python-3.7 `Protocol = ABC` shims with the
direct modern definition, update tests if needed, and update `AGENTS.md`.
