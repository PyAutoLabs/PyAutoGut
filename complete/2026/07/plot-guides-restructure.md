# plot-guides-restructure

Restructured the plot examples of autolens_workspace and autogalaxy_workspace, removed every
remaining legacy plot-API mention, and re-pointed autolens_assistant. Four phases, all merged
2026-07-30 (same day as issue #400 was filed).

## What shipped

- **PyAutoGalaxy#538** (merged first): 1-line export of `aplt.subplot_fit_imaging_list` so the AG
  multi example uses the public API. 1009 tests passed.
- **autolens_workspace#401** (66 files, +5123/−2242): `guides/plot/` flattened — `start_here.py`
  rewritten (fit plot dropped, `mat_plot.py` absorbed with corrected `config/visualize/general.yaml`
  keys), `plotters.py` reduced to the object-by-object tour, `searches.py` de-legacied
  (`__DynestyPlotter__` headers, wrong prose, 46-line duplicate emcee/zeus block, `search.name`),
  `examples/` + `advanced/` removed. NEW `plot.py` in all 7 dataset packages (imaging,
  interferometer, point_source, cluster, group, multi_galaxy, weak), each ending in a
  `__Visualizer__` section (Analysis-bound class + `plots.yaml` gating). `multi/plot.py` rewritten
  around `aplt.subplot_imaging_dataset_list` + `aplt.subplot_fit_combined(_log10)` — the same calls
  `VisualizerImaging.visualize_combined` makes. Advanced scripts became
  `imaging/features/pixelization/plot.py` and
  `imaging/features/advanced/double_source_plane_lens/plot.py` (prose aligned with what the code
  actually plots; missing auto-sim guard added). Validation: 13/13 sequential test-mode runs with
  visualization on.
- **autogalaxy_workspace#190** (60 files): mirror restructure; additionally deleted ~8 sections
  documenting kwargs `plot_array` does not accept (`figsize`, `xlabel`, `mask=`, `border=`,
  `patches=`, `vector_yx=`, `contours=`) that were prose-only no-ops; `guides/plot/simulator.py`
  kept in place (executable dependency of `data_structures.py` and `imaging/fit.py`); NEW `plot.py`
  in imaging, interferometer, cluster, multi_galaxy, ellipse; `multi/plot.py` on the new export.
  Validation: 10/10 sequential test-mode runs.
- **autolens_assistant#101**: 3 skills re-pointed to the new canonical paths;
  `wiki/core/api/plotting.md` gained the per-dataset `plot.py` family; citation check 413/413 clean
  against the merged workspace mains.

## Traps found and closed

- `config/build/no_run.yaml` excluded the search-running script via the SUFFIX substring
  `examples/searches` — dead after the move in BOTH workspaces; re-pointed to
  `guides/plot/searches`. Pre-move sweeps must grep sidecars by basename, not old directory path
  (memory: no-run-suffix-entries-break-on-moves).
- The legacy API was already gone from all code — every `MatPlot2D`/`Visuals2D`/`*Plotter` mention
  was migration prose, stale filenames/titles, or the `mat_wrap.yaml` config pointer.
- AG's combined-fit subplot existed in source but was not exported; the AL/AG asymmetry is now
  closed via PyAutoGalaxy#538.
- Issue #400 auto-closed when #401 merged ("Closes #400" in the commit body) — one phase early but
  harmless; the final summary comment went to the closed issue.

## State

- Heart YELLOW 70 acknowledged by the human before ship (workspace-validation cloud artifact,
  manifest drift, stale release rehearsal — all unrelated to this docs change).
- Worktree `~/Code/PyAutoLabs-wt/plot-guides-restructure` removed post-merge; feature branches
  merged via merge commits on all four repos.

## Original prompt

# Plot guides: legacy-API removal + restructure to per-dataset plot.py

Restructure the `scripts/guides/plot/` examples in **autolens_workspace** and
**autogalaxy_workspace**: remove all legacy plot-API documentation (Visuals2D,
MatPlot, `mat_plot.py`, `plotters.py`), flatten the `examples/` folder into
`plot/`, and move dataset-specific fit plotting out into per-dataset
`plot.py` example scripts (`scripts/imaging/plot.py`, etc.). Document the
`Visualizer` at the end of each per-dataset `plot.py`. Then update
`autolens_assistant` accordingly.

## Original request (verbatim)

- Remove all mention of legacy API (e.g. Visuals2D, MatPlot, mat_plot.py)
- Keep plot/start_here.py, but dont do a fit plot, as these will move to dataset packages.
- remove examples/mat_plot.py, but any content work documenting move to plot/start_here.py. in style of other scripts, i.e. a bit more detail and explanation.
- mat_plot.py is legacy, as is plotters.py.
- I think we should keep the start_here.py, examples/
- Retain examples/plotters.py, but remove any repetition, but it has important content, also move to just plot folder.
- move searches.py to plot folder.
- retain visuals.py, but move to plot folder.
- We can now remove examples folder.
- For all dataset plots (e.g. FitImaging) we will make a scripts/imaging/plot.py example, same for interferometer, point_source, cluster, etc.
- For advanced, anticipate that pixelization will move to a plot.py example in features/pixelization and same for double_einstein_ring.
- Apply changes over both autolens workspace and autogalaxy workspace.
- for multi, make sure we can plot all datasets in one subplot in plot.py like dont in source code.
- I guess also use this opportunity to document the Visualizer in each plot.py, at the end of each, so users can use that functionality linked to Analysis.
- After all this, update autolens assistant accordingly.
- delegate where possible.

## Repos

- @autolens_workspace — `scripts/guides/plot/` restructure + new per-dataset `plot.py` scripts (imaging, interferometer, point_source, cluster, multi, …) + `features/` plot.py placement for pixelization / double_einstein_ring.
- @autogalaxy_workspace — mirror of the above for its dataset folders.
- @autolens_assistant — update skills/wiki references to the new layout after the workspace changes land.

## Notes

- `.py` scripts are canonical; notebooks are generated. Sweep ALL references
  (READMEs, navigator sidecars, `.script_sizes.json`, docs, assistant) with a
  non-extension-filtered grep before any move — path-keyed sidecars fail open
  on `git mv`.
- The multi `plot.py` must demonstrate plotting all datasets of a multi fit in
  one subplot, matching what the source-code Visualizer does.
