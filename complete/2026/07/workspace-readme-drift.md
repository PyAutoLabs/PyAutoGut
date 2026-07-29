Fixed 62 dead README references across autolens_workspace and
autogalaxy_workspace — the drift the widened hygiene `refs` scanner
([[hygiene-refs-readme-drift]], PyAutoBrain#178/#180) made visible.

- autolens_workspace#372 (34 findings) — MERGED, 4/4 green
- autogalaxy_workspace#179 (28 findings) — MERGED, 4/4 green

`hygiene refs` reports zero README findings for both repos; `check_navigator.py`
passes on both.

## What was wrong

- **Root structure lists.** `slam_pipeline` had not existed for a long time
  (SLaM is `scripts/guides/modeling/slam_start_here.py` + `features/slam/`
  folders, as `AGENTS.md` already said correctly). `skills` is `.claude/skills`.
  `multi`/`weak` (autolens) and `ellipse` (autogalaxy) existed but were omitted.
  `simulators` never existed — the scripts are singular `simulator.py`.
- **Reversed and typo'd paths.** `data_preparation/imaging` is really
  `imaging/data_preparation`; `modeling/features` is just `features`;
  `sdvanced/modeling`, `guide/advanced`.
- **Renamed targets.** `galaxies_fit`→`galaxies_fits`, `image`→`data`,
  `stellar_dark_mass`→`mass_stellar_dark`,
  `operated_light_profiles`→`operated_light_profile`.
- **Config inventories** listing YAML that no longer ships: `non_linear/` has
  only `GridSearch.yaml` (not mcmc/nest/mle); `visualize/` has
  general/plots/plots_search (not include/mat_wrap*); `config/README.md` listed
  `grids` (gone) and `non-linear` (it is `non_linear`).
- **Clone residue.** `generag.yaml` — a corrupted `general.yaml` from a blind
  `al`→`ag` substitution. Also a **PyAutoGalaxy** mention inside
  autolens_workspace, and lensing prose ("lensed source", "mass models") in
  autogalaxy's interferometer data-prep README.
- **A link that never resolved.** autogalaxy linked
  `PyAutoLabs/autogalaxy_assistant` twice; that repo has never existed.
  Repointed to `autolens_assistant` with a lensing-focused caveat, matching that
  repo's own `AGENTS.md`. Flagged to the human as the one content judgement.

## Traps

- **A worktree branches from `origin/main` at creation.** `check_navigator.py`
  passed in the worktree and failed in CI: `ba12e177` had landed meanwhile,
  moving the `potential_correction` examples **without regenerating the
  navigator catalogue**, so the check failed on unmodified `main`. Rebase and
  re-run before claiming a check passes. Fixed here by regenerating
  (`regenerate_navigator.py` — lightweight, pyyaml only) in `4ebfa39b`.
- **Audit names as files, not just directories.** `source_science` was flagged
  as drift from a `-type d` search; `source_science.py` exists in every dataset
  package. The scanner disproved the audit. Left alone.
- `gh pr create` fails on these remotes — used `gh api repos/.../pulls`.

## Not done (filed)

`draft/docs/workspaces/script_prose_and_howto_ref_drift.md` — 92 findings in
these repos' `scripts/**/*.py` docstrings plus 64 across autofit_workspace and
HowToFit/Galaxy/Lens (HowToGalaxy carries the same `generag.yaml` corruption).
That is a prerequisite for
`draft/feature/pyautohands/navigator_check_readme_ref_shapes.md`, since all six
repos run the gate that phase widens. Corpus went 218 → 156 on main.

## Original prompt

# Sweep README drift across autolens and autogalaxy workspaces

Type: docs
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Both workspaces' `README.md` files describe a repository layout that no longer
matches the tree. Driven by the widened hygiene `refs` scanner (see
`draft/feature/pyautobrain/hygiene_refs_readme_drift_class.md`, which must land
first so the fix list is machine-generated rather than hand-curated).

Audited classes:

**Root README structure lists.** autolens lists `slam_pipeline` (gone — SLaM is
under `features/slam/`, as `AGENTS.md` already states correctly) and `skills`
(actually `.claude/skills`); omits `multi` and `weak`, both of which exist; lists
`source_science` as a dataset-package example type with no such directory
anywhere; and has a typo, "many strong nses". autogalaxy omits `ellipse` and
links `PyAutoLabs/autogalaxy_assistant` twice — that repository does not exist.

**Stale / reversed relative paths** (~20 files). `data_preparation/imaging` →
`imaging/data_preparation`; `modeling/features` → `features`;
`imaging/advanced/subhalo/detect` → `imaging/features/advanced/subhalo/detect`;
`detect/database.py` (deleted, only `start_here.py` remains);
`point_source/data_preparation` (never existed); `README.rst` → `README.md`.

**Rename-sweep corruption.** `generag.yaml` → `general.yaml` in autogalaxy
`config/README.md` and `config/visualize/README.md` — residue of the
autolens→autogalaxy clone. Also `sdvanced/modeling` → `advanced/modeling` and
`guide/advanced` → `guides/advanced`.

**Config README inventories** listing YAML the workspace no longer ships:
`config/non_linear/README.md` lists `mcmc.yaml`/`nest.yaml`/`mle.yaml` when only
`GridSearch.yaml` exists; `config/visualize/README.md` lists
`include.yaml`/`mat_wrap*.yaml` when the actual files are
`general.yaml`/`plots.yaml`/`plots_search.yaml`; `config/priors/README.md`
references deleted templates and a dead `examples/complex/linking` path.

Edit `scripts/**/README.md` and the root/config READMEs only —
`notebooks/**/README.md` are byte-identical committed mirrors and are refreshed
by the workspace `generate_and_merge` skill. Judge each reference's intended
target; several are re-points to a moved file, not restores. Do not "fix" the
runtime-generated targets (`main_lens_centres.json`, `dataset/imaging/clumpy`,
`search_internal/`) — their absence from a checkout proves nothing.

Acceptance: `pyauto-brain hygiene refs` reports clean for both repos and the
notebook README mirrors stay byte-identical to their `scripts/` sources.

## Original request

> the autolens workspacde readme has API drift (e.g. it refers to slam_pipeline).
> Can you do a sweep of this over autolens_workspaceand gaalxy and then put the
> thing in the hygeine agent?
