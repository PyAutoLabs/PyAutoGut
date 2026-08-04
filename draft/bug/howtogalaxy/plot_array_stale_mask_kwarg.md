# HowToGalaxy chapter_4 TypeError: plot_array() unexpected kwarg 'mask'

Type: bug
Target: howtogalaxy
Repos:
- HowToGalaxy
- autolens_workspace_developer
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

## Original request (verbatim)

> In the PyAutoLabs workspace, HowToGalaxy chapter_4_pixelizations fails in
> PyAutoHeart's workspace-smoke with:
>
>   TypeError: plot_array() got an unexpected keyword argument 'mask'
>
> Evidence: PyAutoHeart workspace-smoke run 30858578587, job
> "smoke / run_notebooks (3.12, howtogalaxy, chapter_4_pixelizations)",
> 2026-08-03T22:49:33Z. That run installed released autolens 2026.7.29.2;
> 2026.8.4.1 has since published, so first confirm whether the release
> already fixes it before assuming it's live.
>
> This is a public teaching notebook so it's user-facing. Find whether the
> caller or the plot_array signature is wrong, check for sibling call sites
> with the same kwarg across HowToGalaxy/HowToLens/HowToFit and the
> workspaces, and fix them all. Route through start_dev.

## Triage already done (grounded, pre-plan)

**Still live in 2026.8.4.1.** `PyAutoGalaxy` main is at the 2026.8.4.1 release
commit (`bf91c570`) and the wrapper still rejects `mask`. Verified by
introspection of the installed stack:

```
autogalaxy.util.plot_utils.plot_array params:
  array, title, output_path, output_filename, output_format, colormap,
  use_log10, vmin, vmax, symmetric, positions, lines, line_colors, grid,
  cb_unit, ax
mask   -> REJECTED (TypeError)
output -> REJECTED (TypeError)
```

**The caller is wrong, not the signature.** `aplt.plot_array` resolves to
`autogalaxy/util/plot_utils.py:plot_array` (re-exported by both
`autogalaxy/plot/__init__.py` and `autolens/plot/__init__.py`). That wrapper
deliberately owns all preprocessing — its docstring states "All array
preprocessing (zoom, mask-edge extraction, native/extent unpacking) is handled
internally so callers never need to duplicate it". It derives the mask overlay
from `array.mask` via `auto_mask_edge` and passes it down to the lower-level
`autoarray.plot.array.plot_array`, which *does* take a `mask` parameter — but
as `(N, 2)` mask-edge coordinates, not a `Mask2D`. So `mask=` was never part of
the `aplt` API; it belongs to the private layer below it.

**Sibling sweep — AST scan of every `.py` and `.ipynb` in the workspace** (all
~25 repos, matching `plot_array` calls whose kwargs fall outside the wrapper
signature). Complete result set:

| Site | Bad kwarg | Note |
|------|-----------|------|
| `HowToGalaxy/scripts/chapter_4_pixelizations/tutorial_3_inversions.py:70` | `mask` | the CI failure |
| `HowToGalaxy/notebooks/chapter_4_pixelizations/tutorial_3_inversions.ipynb` cell 9 | `mask` | generated from the script above |
| `autolens_workspace_developer/plotting_alignment/imaging_delaunay.py:261,267` | `output` | |
| `autolens_workspace_developer/plotting_alignment/imaging_rectangular.py:279,283` | `output` | |
| `autolens_workspace_developer/plotting_alignment/imaging_rectangular_no_interp.py:255,261` | `output` | |
| `autolens_workspace_developer/plotting_alignment/plot/imaging/orientation/simulator.py:136` | `output` | |
| `autolens_workspace_developer/plotting_alignment/plot/interferometer/orientation/simulator.py:137` | `output` | |
| `autolens_workspace_developer/scaling_relation_agg/error_make.py:55` | `output` | |

`mask=` appears at exactly **one** logical site (script + its generated
notebook) — HowToLens and HowToFit are clean. The `output=aplt.Output(...)`
sites are a second, independent stale-API drift against the same wrapper
(current API is `output_path` / `output_filename` / `output_format`); they live
in a developer repo that is not smoke-tested, which is why they never surfaced.
The `plot_array(name=...)` hits in
`autofit_workspace_developer/projects/cosmology/src/analysis.py` are a **false
positive** — a local nested `def plot_array(array, name, ...)` at line 134,
unrelated to `aplt`.

**Not parked.** `HowToGalaxy/config/build/no_run.yaml` has no entry for
`chapter_4_pixelizations` — the tutorial genuinely executes in CI and fails, so
this is a real user-facing break in a public teaching notebook.

## Fix direction

Canonical idiom, from the direct sibling `HowToLens/scripts/chapter_4_pixelizations/tutorial_3_inversions.py:76`
and from `autogalaxy_workspace` (e.g. `markdown/ellipse/fit.md:158`): plot the
data with no `mask=` kwarg, and if the mask overlay is wanted, plot *after*
`apply_mask` so the wrapper derives the edge from `array.mask` itself. The
HowToGalaxy call sits immediately before `dataset.apply_mask(mask=mask)`, so
preserving the author's intent (show the mask over the data) means moving the
plot below that line rather than merely deleting the kwarg — decide during
planning which reads better in the tutorial narrative.

Also update the 7 `output=` sites in `autolens_workspace_developer` to the
`output_path`/`output_filename`/`output_format` triple.

Notebooks are **generated** — edit `scripts/` only, then regenerate
`notebooks/`; never hand-edit the `.ipynb`.

## Sibling prompt

`draft/bug/howtogalaxy/small_api_drift_ellipse_and_plot_grid_lines.md` is the
same class of bug (stale plotter kwargs in HowToGalaxy, incl. a
`plot_grid() got an unexpected kwarg 'plot_grid_lines'`). Different call sites,
but consider whether they should ship together — the fix pattern and the
notebook-regeneration step are identical.
