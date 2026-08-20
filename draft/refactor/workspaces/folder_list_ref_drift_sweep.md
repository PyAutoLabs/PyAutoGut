# Fix folder-list drift in workspace/HowTo prose (hygiene refs sweep)

Type: refactor
Target: workspaces
Repos:
- autocti_workspace
- autofit_workspace
- autogalaxy_workspace
- HowToGalaxy
- HowToLens
Difficulty: easy
Autonomy: safe
Priority: low
Status: formalised

The 2026-08-19 `hygiene refs` scan found 18 folder-list defects (10 dead
references, 8 undocumented folders) in 11 files across 5 repos. Prose-only:
no code path, output, or public API changes.

Dead references (`->` = the reference as written; judge the intended target —
a moved file, a file that became a directory, or a sibling-repo reference —
before re-pointing):

- @autocti_workspace `scripts/dataset_1d/modeling/start_here.py:363` and
  `scripts/imaging_ci/modeling/start_here.py:387` -> `autoCTI_workspace/output`
  (casing drift — the repo folder is `autocti_workspace`).
- @HowToLens `scripts/chapter_4_scaling_up_lensing/tutorial_3_scaling_relation.py:575`
  -> `imaging/features/scaling_relation` (autolens_workspace restructure).
- @HowToLens `scripts/chapter_4_scaling_up_lensing/tutorial_6_weak_lensing.py:412-415`
  -> `weak/start_here.py`, `weak/fit.py`, `weak/modeling.py`,
  `weak/simulator.py`, `weak/likelihood_function.py` (weak-lensing folder
  restructure).
- @HowToLens `scripts/simulator/cluster.py:77` and `:528`
  -> `howtolens/dataset/cluster/simple`.

Undocumented folders (`!!` = folder exists, its README folder list never names
it; the fix is a new entry describing it, sourced from that folder's own README
or a script docstring — never inferred from the folder name):

- @autofit_workspace `scripts/README.md` !! `cookbooks/`
- @autogalaxy_workspace `scripts/guides/results/README.md` !! `aggregator/`, `workflow/`
- @autogalaxy_workspace `scripts/imaging/data_preparation/README.md` !! `gui/`, `manual/`
- @autogalaxy_workspace `scripts/imaging/features/README.md` !! `point_source/`
- @HowToGalaxy `scripts/README.md` !! `simulators/`
- @HowToLens `scripts/README.md` !! `simulator/`

Behaviour-preservation invariant: `.py` edits touch only module-level
triple-quoted docstring prose (and `README.md` files); regenerated notebooks
must show prose-cell diffs only. Witness: re-run
`PyAutoBrain/bin/pyauto-brain hygiene refs` — the 18 findings clear and no new
ones appear; smoke legs for the touched scripts stay green.
