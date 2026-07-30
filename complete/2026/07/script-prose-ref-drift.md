Closed the README ref-drift arc's final surface: dead file/folder references in
`scripts/**/*.py` docstrings and comments across **all 7** workspace/HowTo repos.
**129 -> 0** findings. Seven PRs, all merged green.

autolens_workspace#383 (8/8), autogalaxy_workspace#186 (8/8),
autofit_workspace#126 (8/8), autocti_workspace#15 (no CI), HowToFit#38 (10/10),
HowToGalaxy#50 (10/10), HowToLens#61 (10/10). Issue #377 closed.

Verified on merged canonical `main`: `hygiene refs` 0 across 7 repos;
`check_navigator.py --banners=fail` PASS on all 6 gated repos.

## Verified fix classes (113 mechanical re-points)

- `log_likelihood_function` -> `likelihood_function` (scripts drop the `log_`)
- `notation/label.yaml` -> `notation.yaml` (config went folder -> file)
- `config/generag.yaml` -> `config/general.yaml` (autolens->autogalaxy clone
  residue, this time in script prose rather than READMEs)
- `autofit_workspace/*/plots` -> `plot`; `simulators` -> `simulator`
- `feature/pixelization/...` -> `features/`; `subhalo/detection` -> `detect`
- `guides/source_science` -> the topic packages (`source_science.py` lives in
  `imaging/`, `interferometer/`, `group/` -- never `guides/`)
- `preprocess` / `propocess` -> `imaging/data_preparation`
- `modeling/imaging/{customize,searches}` -> `guides/modeling/...`
- `imaging/advanced/database` -> `guides/results/database`
- dataset dirs quoted without their `dataset/` prefix -> qualification, not restore

Eleven needed prose rewriting because no target exists in any form: autogalaxy
has no CPU-fast pixelization example (now cross-references the autolens one);
`point_source` has no likelihood_function walkthrough (-> `cluster/likelihood_function`,
titled "Log Likelihood Function: Cluster Point Source"); no `subhalo/detect/examples`
anywhere; `mat_wrap.yaml` retired for `general.yaml`; `config/priors` has no
`default` subfolder; `z_projects/` is not in this workspace.

## The lesson: re-run the detector on your own output

Two of my 113 re-points were **wrong** -- `point_source/likelihood_function` and
`subhalo/detect/examples` do not exist. A blanket mapping that was right for
`imaging`/`interferometer` was wrong for `point_source`. Caught only by re-running
`hygiene refs` after the bulk pass; no amount of reading the diff would have found
it. Any scripted sweep must end with the detector, not with the edit.

## Trap: generate.py wipes notebooks/ before validating the project

Running `generate.py autocti` **deleted 117 tracked files** under
`autocti_workspace/notebooks/` and *then* aborted -- `autocti` is absent from
`COLAB_PROJECTS` (`build_util.py:37`) and PyAutoNerves `_PROJECTS`. Restored with
`git checkout -- notebooks`; nothing damaged shipped. Filed as
`draft/bug/pyautohands/generate_rejects_autocti_after_deleting_notebooks.md`,
where two other sessions turned out to have hit it independently.

**And do not hand-roll the workaround.** `build_util.py_to_notebook` alone is NOT
equivalent to `generate.py`: control-tested against an *unchanged* script
(`dataset_1d/extract.py`), the committed notebook carries a trailing empty code
cell `py_to_notebook` does not emit (343 vs 336 lines, otherwise identical). So
autocti's 5 script fixes shipped with its notebooks untouched, stated in the PR,
rather than shipping notebooks structurally unlike every other one in the repo.
Control-test any regeneration path against an unchanged file before trusting it.

## Also

Rebasing before starting mattered: the branch was cut before other sessions'
merges, and re-baselining moved the count 116 -> 129. Notebook + catalogue
regeneration is required because docstring text feeds `notebooks/`,
`llms-full.txt` and `workspace_index.json`. Each HowTo repo declares its own
generator project (`howtolens`, not `autolens`).

## Original prompt

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
