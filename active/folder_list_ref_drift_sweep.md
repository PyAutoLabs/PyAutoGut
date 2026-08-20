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

Dead references — adjudicated 2026-08-19 (each `->` finding judged against the
repo the surrounding sentence names, per the known sibling-repo false-positive
mode of the scanner):

REAL (fix):
- @autocti_workspace `scripts/dataset_1d/modeling/start_here.py:363` and
  `scripts/imaging_ci/modeling/start_here.py:387`: `autoCTI_workspace/output`
  -> `autocti_workspace/output` (casing drift; the lowercase form is the one
  used everywhere else in the repo's prose).
- @HowToLens `scripts/simulator/cluster.py:77` and `:528`:
  `howtolens/dataset/cluster/simple` -> `dataset/cluster/simple` (the script
  writes to `Path("dataset", "cluster", "simple")`; sibling simulators
  `group.py`/`interferometer.py`/`weak_lensing.py` all use the bare
  repo-relative form).

FALSE POSITIVES (no edit — correct as written, targets exist in
autolens_workspace which the prose names explicitly):
- @HowToLens `tutorial_3_scaling_relation.py:575` `imaging/features/scaling_relation`
  (exists: `autolens_workspace/scripts/imaging/features/scaling_relation/`).
- @HowToLens `tutorial_6_weak_lensing.py:412-415` `weak/{start_here,fit,modeling,simulator,likelihood_function}.py`
  (all exist under `autolens_workspace/scripts/weak/`; same adjudication as the
  2026-08-06 hygiene pass).

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
`PyAutoBrain/bin/pyauto-brain hygiene refs` — the 12 real findings clear and no
new ones appear (the 6 sibling-repo false positives above will still be
reported by the scanner until it learns cross-repo resolution); smoke legs for
the touched scripts stay green. Notebook-regen convention is per-workspace —
check each repo's own AGENTS.md before opening its PR.
