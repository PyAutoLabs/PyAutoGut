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
