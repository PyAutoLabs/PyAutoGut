## file-path-guard-decision
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/475
- completed: 2026-08-07
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/477, https://github.com/PyAutoLabs/autofit_workspace/pull/134
- summary: The file-path leg split from raw-guard-migration (leg 3 of the dataset-bulk series, autolens_workspace#354). Decision for all 9 live census sites: KEEP the raw file guard, marked with a short intentional-raw-guard comment so future migration sweeps don't re-flag them — no conversion. Rationale, 7 autolens positions.json sites: each sits directly below a dataset-level should_simulate(dataset_path) guard which under PYAUTO_SMALL_DATASETS=1 rmtree's the whole dataset folder (deleting positions.json with it) and re-simulates, so the file guard automatically re-fires and regenerates positions from the fresh reduced-resolution data — raw is CORRECT, not a migration gap; converting on the file crashes (shutil.rmtree on a file → NotADirectoryError), converting on the parent dir would delete the just-simulated dataset a second time and run the positions script against missing data. Rationale, 2 autofit data.json sites (features/graphical_models.py, features/shared_analysis_state.py): the repo has no should_simulate namespace and never sets PYAUTO_SMALL_DATASETS (the recorded leg-3 rejection), so raw + comment. 2 of the census 11 needed nothing by 2026-08-07: interferometer/features/pixelization/many_visibilities_preparation.py:90 was already normalized onto a directory-level guard (autolens_workspace fe9031e "normalise the four hand-rolled auto-simulate guards"), and the guides/plot/examples/plotters.py:351 guard was removed in the plot-guides restructure (a198c7c); the census's multi/ paths now live under multi_dataset/. Validation: py_compile 9/9, check_sizes.sh clean, navigator catalogue unchanged, notebooks regenerated 1:1 for the 9 touched scripts only; none of the touched scripts are in either smoke list, and PR CI (navigator + smoke 3.12/3.13) was green on both PRs before merge. NOTEBOOK TRAP recorded: PyAutoHands 596967e (merged 2026-08-06) makes the generator uncomment "from auto* import setup_notebook; setup_notebook()" in every generated notebook, so a wholesale generate.py run wants to touch ~330 notebooks per repo that predate the fix — this task committed only its 9 paired notebooks (which carry the activation as canonical output) and left the repo-wide setup_notebook sweep to the next wholesale regeneration; that sweep is outstanding in autolens_workspace and autofit_workspace (and likely the other notebook-bearing workspaces). Environment note: run in a remote web-github session on branch claude/file-path-guard-decision-50mwce (no worktree, no installed stack — ipynb-py-convert won't pip-install under modern setuptools (install_layout AttributeError); worked around by extracting the sdist and shimming the CLI on PATH). Merged 2026-08-07: autolens_workspace f37fc997, autofit_workspace f909cb88; issue #475 auto-closed by the PR merge.

## Original prompt

# Decide the 11 file-path auto-simulate guards

Type: maintenance
Target: workspaces
Repos:
- autolens_workspace
- autofit_workspace
Difficulty: easy
Autonomy: supervised
Priority: low
Status: formalised

Split from the raw-guard migration (dataset-bulk series leg 3): 11 auto-simulate guards
whose guarded path is a **file**, not a directory. They have a paired simulator, but
`should_simulate` calls `shutil.rmtree(path)` → `NotADirectoryError` on a file, and
passing the parent dir instead changes the guard's semantics (dir-exists vs file-exists).
Each needs a per-site call: pass the parent dir, or leave the raw guard with a comment.

Sites (2026-07-27 census):
- autolens_workspace: `multi/features/pixelization/modeling.py:91`,
  `guides/plot/examples/plotters.py:351`, `guides/modeling/customize.py:54`,
  `imaging/features/advanced/shapelets/modeling.py:116`,
  `imaging/features/pixelization/{adaptive.py:101, cpu_fast_modeling.py:94, modeling.py:158, source_science.py:66}`,
  `interferometer/features/pixelization/many_visibilities_preparation.py:90`
- autofit_workspace: `features/graphical_models.py:74`, `features/shared_analysis_state.py:80`
  (both guard `.../dataset_0/data.json`; note autofit_workspace has no should_simulate
  namespace today — see the leg-3 rejection rationale)
