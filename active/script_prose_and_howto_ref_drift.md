# Sweep dead internal references in script prose and the HowTo/autofit repos

Type: docs
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
- autofit_workspace
- HowToFit
- HowToGalaxy
- HowToLens
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

The widened hygiene `refs` scanner (PyAutoBrain#178, #180) reports **218** dead
internal references across 7 repos. The README half of the two named workspaces
was fixed in autolens_workspace#372 / autogalaxy_workspace#179. This prompt
covers the remainder, which was explicitly out of that task's scope.

Two distinct groups:

**1. Script-docstring prose in the two swept workspaces (~100 findings).**
Same drift class, different file surface: `scripts/**/*.py` docstrings and
comments quoting sibling paths that have since moved. Examples seen in the scan:
`feature/pixelization/many_visibilities_preparation` (should be `features/`),
`subhalo/detection/examples` (the package is `detect`),
`autolens_workspace/interferometer/extra_galaxies` (the real path inserts
`features/`), and dataset paths written without their `dataset/` prefix.

**2. The four repos the README sweep did not touch (~64 findings).**
`autofit_workspace`, `HowToFit`, `HowToGalaxy`, `HowToLens`. HowToGalaxy in
particular carries the same `generag.yaml` corruption and the same stale
`config/**/README.md` inventories that were just fixed in autogalaxy_workspace —
strong evidence these repos were cloned from the same source. This group is a
**prerequisite for PyAutoHands' `check_navigator.py` gate widening**
(`draft/feature/pyautohands/navigator_check_readme_ref_shapes.md`): all six
repos run that gate, so either these are swept or their findings are
grandfathered into `.navigator_check_ignore`.

Drive the fix list from `pyauto-brain hygiene refs --json`, not by hand. Judge
each reference's intended target — the residual false-positive classes are
documented in `_hygiene_refs.py`'s module docstring (dataset paths missing their
prefix; extension-less pairs whose tail coincidentally names a real directory).

Known scanner recall limit worth a second pass by eye: the structure-list quorum
skips a bullet block when fewer than two of its extension-less names resolve, so
a *small* block where everything is dead is reported as nothing. Two real cases
were found by hand during the README sweep (`casa_to_autogalaxy`, `profiling` in
`interferometer/data_preparation`).

## Original request

> the autolens workspacde readme has API drift (e.g. it refers to slam_pipeline).
> Can you do a sweep of this over autolens_workspaceand gaalxy and then put the
> thing in the hygeine agent?

(Filed as the explicit out-of-scope remainder of that sweep, which was
README-scoped for the two named repos.)
