Filled the per-file plotting-function coverage gaps between the source `*_plots.py`
modules and the workspace `plot.py` family, and closed two PyAutoLens export
asymmetries found on the way. Three PRs, all merged 2026-07-30.

## What shipped

- **PyAutoLens#668** (`45ac1dbaf`, merged first): two additive exports in
  `autolens/plot/__init__.py` — `subplot_interferometer_dataset` (exported by
  `autogalaxy.plot` from the same autoarray module, skipped by autolens) and
  `subplot_fit_interferometer_combined` (autolens's own function, unexported while
  the imaging equivalent `subplot_fit_combined` was exported). Plus the two names
  in `docs/api/plot.rst`. 488 tests passed; CI 5/5.
- **autolens_workspace#404** (`5b558f5c2`, 5 scripts +233): `imaging` gained
  `subplot_fit_imaging_of_planes` / `_log10` / `_tracer` / `fits_imaging`;
  `interferometer` gained `subplot_interferometer_dataset`, fit-level
  `subplot_fit_dirty_images`, `_real_space`, `_tracer`, `fits_interferometer`;
  `weak` gained `plot_convergence_map`, `plot_data_vs_model`, `plot_residuals`,
  `plot_chi_squared_map`; `cluster` gained `plot_image_group_zooms`,
  `plot_critical_curves`, `plot_caustics`; `point_source` gained
  `subplot_point_dataset`. CI 10/10.
- **autogalaxy_workspace#191** (`6ca53f89c`, 2 scripts +69): `imaging` gained
  `subplot_fit_imaging_of_galaxy` + a `use_log10` variant + `fits_imaging`;
  `interferometer` gained fit-level `subplot_fit_dirty_images`,
  `subplot_fit_real_space`, `fits_interferometer`. CI 10/10.

Coverage in `plot.py` files: **18 → 36** of 63 exported symbols
(autolens_workspace), **11 → 14** of 28 (autogalaxy_workspace).

## The gap this closed

`plot-guides-restructure` (same day) built the per-dataset `plot.py` family but
**restructured without enumerating**. `imaging/plot.py` called
`subplot_fit_imaging` and nothing else; `subplot_fit_imaging_log10`,
`_of_planes` and `_tracer` appeared nowhere in the entire workspace. That file's
own `__Visualizer__` prose named `subplot_of_planes` while never demonstrating
it, hand-rolling a `model_images_of_planes_list` loop in its place.

Two of the "workspace gaps" were not workspace gaps at all: the functions were
**unreachable**. That only surfaced because the audit resolved the API by
introspecting the *installed stack* (`set(dir(agplt)) - set(dir(aplt))`) instead
of reading `__init__.py`.

## Traps found and closed

- **`subplot_fit_imaging_x1_plane` / `_log10_x1_plane` must NOT be called.**
  `subplot_fit` dispatches to them itself (`fit_imaging_plots.py:214`, `:346`,
  `:512`) when `len(fit.tracer.planes) == 1`. On the two-plane example fits they
  are unreachable by design — a call would teach a wrong idiom. Covered with one
  prose line. Same reasoning kept `subplot_fit_interferometer_combined` out of the
  single-fit interferometer script (it takes a `fit_list`; `[fit, fit]` would be
  fake).
- **A cluster tracer is cheap, contrary to first appearance.** Critical curves and
  caustics need a `Tracer`, and reproducing `start_here.py`'s model composition
  looked like scope creep — but the dataset's `mass.csv`/`point.csv` models have
  `prior_count == 0` (every value a fixed default), so
  `instance_from_prior_medians()` returns the exact truth galaxies in ~6 lines,
  no fitting. Probing beat assuming.
- **`generate.py` resolves from `Path.cwd()` and takes a SHORT project key.** Run
  from the workspace/worktree root it prints `(0 scripts)` and silently changes
  nothing — a zero-diff that reads as "notebooks already current". Must be run
  from inside the repo, with `autolens` / `autogalaxy`, not `autolens_workspace`.
  Prove it by the script count (al=308, ag=132). Recorded as a memory.
- **The PyAuto API gate false-positives with a RecursionError** when introspecting
  a namespace that legitimately does not yet contain the symbol under test.
  `PYAUTO_SKIP_API_GATE=1` is the right bypass when verifying newly-added exports.
- **`worktree_check_conflict` was wrong in both directions in one session** — it
  flagged PyAutoLens (stale `python-312-floor` completion record, hand-cleared via
  `git worktree list` + 3 commits past the claimed sha) and *failed* to flag
  `group-start-here-timeout`'s live claim on autolens_workspace. Hand-check both ways.
- **A concurrent Mind session swept this task's `active.md` edit into its own
  commit** (`git add -A`), confirming the commit-explicit-paths rule.

## Verification

All 7 touched scripts executed sequentially in test mode with visualization on
against the branch build (7/7), then the coverage matrix re-run against the
**edited files** — 22/22 planned gaps closed, `*_x1_plane` exclusion confirmed.
Post-merge, the merge-order-critical `interferometer/plot.py` was re-run against
the **canonical merged mains** (asserting `autolens.__file__` was outside the
worktree) — exit 0 in both workspaces, both checkouts clean afterwards.

Leak control: the new `fits_*` sections write into `output/plot/`, verified
gitignored with `git check-ignore` before any commit; the written FITS was opened
and confirmed to carry `MASK`/`DATA`/`PSF`/`NOISE_MAP`. Notebook regeneration
touched exactly the 7 notebooks plus the two tracked catalogue files, with no
foreign drift swept in.

## State

- Brain scored this `too-large (15)` with a 4-phase split (design/core_api/
  workspace_examples/docs); **overridden** to one combined library→workspace task —
  it scored 3 repos, not the work (2 import lines + 7 files). Precedents:
  `vacuous-jax-assertions`, `multiband-pyloop-batching`.
- Heart at ship: `verdict: stale`, score 75, with `red_reasons` and
  `yellow_reasons` both **empty** — out-of-date evidence, not failure. Human
  acknowledged before the library ship.
- Workspace mains now call an unreleased symbol; both workspace PRs carried
  `pending-release`, so this resolves at the next release.
- PyAutoLens#667 left **open** for follow-up 4 below.

## Follow-ups

`draft/docs/workspaces/plot_coverage_followups.md` (four independent items, not
bulk-issued):

1. Demo `subplot_fit_interferometer_combined` in a multi-dataset interferometer
   example — exported here, demonstrated nowhere.
2. Demo `subplot_ellipse_errors` — needs a real posterior `fit_pdf_list`.
3. `docs/api/plot.rst` omits 6 already-exported symbols and has no dataset heading.
4. **Live API defect:** `aplt.subplot_fit_dirty_images` resolves to *autogalaxy's*
   implementation inside `autolens.plot`, so autolens's own version — the one
   accepting `image_plane_lines` for critical-curve overlays — is reachable under
   no exported name. Left out of #668 because rebinding an exported name is a
   behaviour change, not an additive export.

## Original prompt

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
