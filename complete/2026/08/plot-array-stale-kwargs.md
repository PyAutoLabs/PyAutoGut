Fixed the workspace-smoke failure in the public HowToGalaxy teaching notebook
`chapter_4_pixelizations/tutorial_3_inversions`, reported as
`TypeError: plot_array() got an unexpected keyword argument 'mask'`
(PyAutoHeart workspace-smoke cloud#30858578587, 2026-08-03).

## Outcome

| Repo | PR | Merged |
|---|---|---|
| HowToGalaxy | [#57](https://github.com/PyAutoLabs/HowToGalaxy/pull/57) | 2026-08-04T13:41:20Z |
| autolens_workspace_developer | [#124](https://github.com/PyAutoLabs/autolens_workspace_developer/pull/124) | 2026-08-04T13:41:30Z |

## Root cause

**Not a library break, and not fixed by 2026.8.4.1** — PyAutoGalaxy `main` was at
the release commit `bf91c570` and `plot_array` still had no `mask` parameter.
`aplt.plot_array` resolves to `autogalaxy/util/plot_utils.py:124`; the mask
overlay is auto-derived one layer down at `autoarray/plot/array.py:128`
(`if mask is None: mask = auto_mask_edge(array)`), and `auto_mask_edge` returns
`None` for a fully-unmasked array. The call sat *before* `apply_mask`, so it drew
nothing — which is exactly why the author added the kwarg. Measured: unmasked →
`None`; after `apply_mask` → `(156, 2)` edge coords. Moving the call below
`apply_mask` restores the intended boundary with no kwarg.

## The reported error was one of three

Execution stops at the first exception, so CI never showed the other two. Each
was only found by re-running after the previous fix:

1. `plot_array(..., mask=mask)` — kwarg never existed on that wrapper
2. `aplt.subplot_image_and_mapper` — not re-exported by `autogalaxy.plot`; it
   lives in `autoarray.plot`, which `tutorial_2_mappers.py` in the same chapter
   already imports as `aaplt`
3. `inversion.reconstruction_to_native` — attribute gone; the plottable `Array2D`
   is `mapped_reconstructed_operated_data`

A private-path import of `subplot_of_mapper` was also replaced by the public
`aaplt` export.

## Correction worth carrying forward

The first AST sweep **hardcoded the alias `aplt`** and missed a call site written
`aaplt`, reporting a falsely confident "2 hits, contained". Rewritten to resolve
aliases from each file's own imports. A symbol scan also cannot see direct
imports, kwarg drift, or runtime attributes — break 3 above was invisible to it.

## Second repo — scope and honesty

`autolens_workspace_developer`'s whole `aplt.Output` drift was repaired (10
files). `aplt.Output` no longer exists on the autolens/autogalaxy plot namespace
(deliberate removal, documented in `autolens_assistant/AGENTS.md:218`); it
survives only as `autoarray.plot.Output`. Accepted kwargs differ per callee, so
it was not a blanket rename: `plot_array` takes
`output_path`/`output_filename`/`output_format`, the `subplot_*` family only
`output_path`/`output_format`.

That repo has **no CI** and several scripts need FITS data absent from the repo,
so files were compile-checked and `inspect.signature`-bound (112 calls clean),
**not run end-to-end**. Four still do not run — they break earlier on unrelated
stale symbols (`al.Preloads`, `al.mapper_indices_from`, `al.Grid2DIterate`).

## CI coverage gap (important)

HowToGalaxy's own PR CI is **structurally blind to this bug**: `smoke_tests.txt`
lists only 4 chapter-1 tutorials and no workflow runs chapter 4 or notebooks. The
6 green checks proved chapter 1 did not regress and the navigator catalogue is
consistent — nothing about the fix. Actual evidence was a local run of all five
chapter-4 tutorials (5/5 green); the real gate is PyAutoHeart's `run_notebooks`.

## Verification

- Failure reproduced on unchanged input first, matching the CI trace exactly
- All 5 `chapter_4_pixelizations` tutorials green locally
- Detector re-run on own output: 0 (it correctly still flagged the generated
  notebook until regenerated)
- Post-merge on `main`: workspace-wide detector 17 → 6, all 6 being the known
  false positive (a local nested `def plot_array(array, name, ...)` in
  `autofit_workspace_developer/projects/cosmology/src/analysis.py`); zero
  residual `aplt.Output`
- Notebook regenerated via PyAutoHands, confirmed to carry every fix

Shipped under explicit human acknowledgement of Heart YELLOW (score 70, no RED)
for exactly two reasons; the first named cloud#30858578587 — this very run.

## Follow-ups filed (draft/)

- `bug/workspaces/aplt_output_drift_remaining_repos.md` — autocti_workspace_test
  (27 files, flagged **unverified**: different library, may be correct as
  written) + euclid_strong_lens_modeling_pipeline (2 files)
- `maintenance/autolens_workspace_developer/stale_api_rot_audit.md` — 56 stale
  symbols + `al.Pixelization`/`al.Settings` kwarg drift; triage-first, some may
  be dead experiments better condemned than modernised
- `docs/howtolens/ch4_mask_overlay_never_drawn.md` — HowToLens ch4 t3 plots
  before `apply_mask` at lines 76/190, so its mask overlay never draws

## Open, not addressed

`inversion.reconstruction` prints all zeros in this tutorial. Pre-existing (same
before the fix) and outside scope, but worth a look if that reconstruction is
meant to be non-trivial.

## Original prompt

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
`autogalaxy/plot/__init__.py` and `autolens/plot/__init__.py`). The mask
overlay is derived automatically one layer down: the wrapper does **not**
forward any `mask` argument, and `autoarray/plot/array.py:128` does
`if mask is None: mask = auto_mask_edge(array)`. So `mask=` was never part of
the `aplt` API — the lower-level `autoarray.plot.array.plot_array` does take a
`mask` parameter, but as `(N, 2)` edge coordinates, not a `Mask2D`.

**Why the author reached for it, and why moving the call fixes it.**
`auto_mask_edge` returns `None` for a fully-unmasked array, so no overlay is
drawn. The HowToGalaxy call sits *before* `apply_mask`, where `dataset.data` is
still unmasked — hence nothing to see, hence the `mask=mask` kwarg. Verified
empirically on the installed stack:

```
unmasked   -> mask.is_all_false: True  | auto_mask_edge: None
after mask -> mask.is_all_false: False | auto_mask_edge: (156, 2)
```

Moving the plot below `dataset.apply_mask(mask=mask)` therefore restores the
intended mask-boundary overlay with no kwarg at all — a strictly better result
than deleting the kwarg (which would show no mask).

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
Those sites are in fact doubly stale: `aplt.Output` no longer exists either
(`hasattr(aplt, "Output") == False`), so they raise `AttributeError` *before*
ever reaching the `TypeError`.
The `plot_array(name=...)` hits in
`autofit_workspace_developer/projects/cosmology/src/analysis.py` are a **false
positive** — a local nested `def plot_array(array, name, ...)` at line 134,
unrelated to `aplt`.

**Not parked.** `HowToGalaxy/config/build/no_run.yaml` has no entry for
`chapter_4_pixelizations` — the tutorial genuinely executes in CI and fails, so
this is a real user-facing break in a public teaching notebook.

## Fix direction

Canonical idiom, from `autogalaxy_workspace` (`markdown/ellipse/fit.md:158`,
"Image Data With Mask Applied"): plot with **no** `mask=` kwarg, *after*
`apply_mask`, so the overlay is auto-derived. Move the HowToGalaxy call below
`dataset = dataset.apply_mask(mask=mask)` and drop the kwarg — the narrative
already reads "We now create the masked imaging", so the plot lands naturally
after it as the visual confirmation.

Note the direct sibling
`HowToLens/scripts/chapter_4_pixelizations/tutorial_3_inversions.py:76` plots
*before* `apply_mask` with no kwarg, so it draws no mask at all. It does not
crash, so it is out of scope here, but it is the weaker pattern — worth a
follow-up rather than copying.

Also update the 7 `output=aplt.Output(path=…, filename=…, format=…)` sites in
`autolens_workspace_developer` to the flat
`output_path=` / `output_filename=` / `output_format=` triple.

Notebooks are **generated** — edit `scripts/` only, then regenerate
`notebooks/`; never hand-edit the `.ipynb`.

## Sibling prompt

`draft/bug/howtogalaxy/small_api_drift_ellipse_and_plot_grid_lines.md` is the
same class of bug (stale plotter kwargs in HowToGalaxy, incl. a
`plot_grid() got an unexpected kwarg 'plot_grid_lines'`). Different call sites,
but consider whether they should ship together — the fix pattern and the
notebook-regeneration step are identical.
