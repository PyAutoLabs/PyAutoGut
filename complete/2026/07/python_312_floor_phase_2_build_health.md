# Python 3.12 floor — Phase 2: build and health verification

Type: feature
Target: PyAutoHands
Difficulty: large
Autonomy: supervised
Priority: high
Status: merged — PyAutoHands#207 (`1e9ac6d5`), PyAutoHeart#115 (`eda92a6b`); issue PyAutoHands#206 remains open as the campaign record

Parent: `python_312_ecosystem_floor.md`
Depends on: `python_312_floor_phase_1_core.md`

## Scope

Align @PyAutoHands and @PyAutoHeart with the core floor: required 3.12/3.13
coverage, explicit 3.11 install rejection, and a clean isolated non-required
3.14 evidence leg. Remove old 3.9-3.11 success/banner assertions and duplicated
matrix work without weakening release/install gates.

## Gates

Full scheduled matrix and end-to-end install verification pass, and a fresh
Heart verdict contains no new campaign-attributable RED reason.
