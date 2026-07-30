# plot.py function coverage gaps vs the source *_plots.py modules

Direct follow-on to **plot-guides-restructure** (complete/2026/07). That task
created the per-dataset `plot.py` family and closed the AG→AL export asymmetry
via PyAutoGalaxy#538. It did **not** audit whether each `plot.py` demonstrates
the full set of plotting functions its dataset/fit type actually has — it
restructured, it did not enumerate. This task closes that.

Two legs: a small **library** export fix in PyAutoLens (the mirror of #538,
which went the other direction), then the **workspace** coverage fill.

## Evidence

Method: enumerate every public function in the source `*_plots.py` modules,
resolve what `aplt` actually exports by **introspecting the installed stack**
(not by reading `__init__.py`), then grep every `aplt.*` call across both
workspaces, bucketed as demoed-in-a-`plot.py` / used-elsewhere / never-used.

Confirmed: `autolens_workspace/scripts/imaging/plot.py` calls
`subplot_fit_imaging` only. `subplot_fit_imaging_log10`,
`subplot_fit_imaging_of_planes` and `subplot_fit_imaging_tracer` appear
**nowhere in the entire workspace**. The file's own `__Visualizer__` section
even names `subplot_of_planes` in prose while never demonstrating it, and
hand-rolls a `fit.model_images_of_planes_list` loop in its place.

## Library leg — PyAutoLens

`autolens/plot/__init__.py` is missing two exports:

- **`subplot_interferometer_dataset`** — `autogalaxy.plot` exports it from
  `autoarray.dataset.plot.interferometer_plots`; `autolens.plot` imports only
  `subplot_interferometer_dirty_images` and `fits_interferometer` from that same
  module and skips it. Consequence: `autolens_workspace/scripts/interferometer/plot.py`
  has **no dataset subplot** while its autogalaxy counterpart does — the
  function is unreachable, so this is not a workspace gap.
- **`subplot_fit_interferometer_combined`** — autolens's own function in
  `autolens/interferometer/plot/fit_interferometer_plots.py`, unexported, while
  the imaging equivalent `subplot_fit_combined` **is** exported.

Verified by import, not by reading source:
`set(dir(autogalaxy.plot)) - set(dir(autolens.plot))` =
`{subplot_fit_imaging_list, subplot_interferometer_dataset}`. (`subplot_fit_imaging_list`
is deliberate — AL uses `subplot_fit_combined` instead.)

Also noted, **not** in scope: `aplt.subplot_fit_dirty_images` and
`aplt.subplot_fit_real_space` resolve to the **autogalaxy** implementations
inside `autolens.plot`, shadowing autolens's own versions which take
lensing-specific `image_plane_lines` / `source_plane_lines` args. Worth a
separate prompt — changing what an existing exported name resolves to is a
behaviour change, not an additive export.

## Workspace leg

Each `plot.py` demonstrates the dataset- and fit-level functions for **its own**
data type, plus a `fits_*` output section. Tracer/galaxy/profile subplots stay
in `guides/` (`guides/tracer.py`, `guides/galaxies.py`,
`guides/plot/start_here.py`) where they are already covered — do not duplicate.

**autolens_workspace**

| File | Add |
|---|---|
| `scripts/imaging/plot.py` | `subplot_fit_imaging_log10`, `subplot_fit_imaging_of_planes`, `subplot_fit_imaging_tracer`, `fits_imaging` |
| `scripts/interferometer/plot.py` | `subplot_interferometer_dataset` (needs the library leg), `subplot_fit_interferometer_real_space`, `subplot_fit_interferometer_tracer`, fit-level `subplot_fit_dirty_images`, `fits_interferometer` |
| `scripts/weak/plot.py` | `plot_data_vs_model`, `plot_residuals`, `plot_chi_squared_map`, `plot_convergence_map` |
| `scripts/cluster/plot.py` | `plot_image_group_zooms`, `plot_critical_curves`, `plot_caustics` |
| `scripts/point_source/plot.py` | `subplot_point_dataset` |

**autogalaxy_workspace**

| File | Add |
|---|---|
| `scripts/imaging/plot.py` | `subplot_fit_imaging_of_galaxy`, `fits_imaging` |
| `scripts/interferometer/plot.py` | `subplot_fit_real_space`, fit-level `subplot_fit_dirty_images`, `fits_interferometer` |

Note the two distinct dirty-image functions: dataset-level
`subplot_interferometer_dirty_images` (already demoed) vs fit-level
`subplot_fit_dirty_images` (missing in both workspaces' `plot.py`).

## Explicitly excluded

- **`subplot_fit_imaging_x1_plane` / `subplot_fit_imaging_log10_x1_plane`** —
  do **not** add as calls. `subplot_fit` dispatches to them itself
  (`fit_imaging_plots.py:214`, `:346`, `:512`) when
  `len(fit.tracer.planes) == 1`. On the two-plane example fits in `plot.py` they
  are unreachable by design; demoing them would teach a wrong idiom. Cover with
  one prose line noting `subplot_fit` auto-switches layout for single-plane
  tracers.
- **`subplot_ellipse_errors`** — needs `fit_pdf_list: List[List[FitEllipse]]`,
  one inner list per posterior sample. A standalone `plot.py` has no search, so
  this needs a real model-fit. File as its own follow-up prompt.
- **Results/search plots** (`subplot_parameters`, `log_likelihood_vs_iteration`,
  `output_figure`, `corner_anesthetic`) — belong to `guides/plot/searches.py`
  and `guides/results/`, not the per-dataset `plot.py`. Several are used
  nowhere; a separate audit.

## Validation

Sequential test-mode runs with visualization on for every touched script (the
restructure task's own bar: 13/13 AL, 10/10 AG). Parallel runs fake failures
through shared state — baseline sequentially.

Re-run the coverage matrix on the **output** to prove the gaps actually closed,
rather than trusting the edit.

## Repos

- @PyAutoLens — `autolens/plot/__init__.py`, two additive exports. Merges first.
- @autolens_workspace — five `plot.py` scripts.
- @autogalaxy_workspace — two `plot.py` scripts.

## Original request (verbatim)

we just finished a task refactoring all the plot.py files in the workspce, but I
think we are missing some plot fuhnctions. For example, imaging/plot.py has
subplot_fit but not subplot_fit_log10, subplot_of_planes, etc. Do a better
comparison of the *_plots.py files in the source code and the plot.py in the
workspace and fill in the gaps across autolens and autogalaxy

Scope decisions taken by the human at intake:

- Library + workspace (fix the two missing PyAutoLens exports, library merges first).
- Also add `fits_*` output sections to each `plot.py`.
- Skip `subplot_ellipse_errors`; file a follow-up.
