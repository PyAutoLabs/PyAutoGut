# Python 3.12 floor — Phase 3: coordinated core release

Type: feature
Target: PyAutoHands
Difficulty: large
Autonomy: supervised
Priority: high
Status: formalised

Parent: `python_312_ecosystem_floor.md`
Depends on: phases 1 and 2

## Scope

Recheck PyPI's last-compatible unyanked versions, obtain the human version
choice, pass fresh Heart/pre-build gates, and release @PyAutoNerves,
@PyAutoArray, @PyAutoFit, @PyAutoGalaxy, and @PyAutoLens coherently. Verify the
published wheels reject Python 3.11 and install on 3.12/3.13. Do not yank usable
historical wheels.
