# searches.py guide — lead with Nautilus, then MultiStartProdigy

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: active
Issue: https://github.com/PyAutoLabs/autolens_workspace/issues/386

## Verbatim request

> For searches.py in autolens and galaxy workspace, can you move a section on Nautilus up to the
> top, explaining its full posterior sampling but does not use JAX gradients (but does exploit JAX
> GPU). Then put MultiStartProdgy second.

## Scope

`scripts/guides/modeling/searches.py` in **autolens_workspace** and **autogalaxy_workspace**.

## Verified starting state

- **Neither file has a Nautilus section at all.** Both open on Dynesty. Nautilus is named
  repeatedly in the header prose and in the Dynesty / Zeus / LBFGS sections as the recommended
  search, but is never documented or shown as a code cell. So this is an *add* at the top, not a
  literal move of an existing block.
- Current section order in both: Dynesty → Emcee → Zeus → LBFGS → (multi-start) → Start Point →
  Search Cookbook.
- The multi-start section differs between the two repos:
  - autolens: `__MultiStartProdigy__`, long-form (GIGA-Lens + Prodigy citations, the
    `MultiStartAdam` / `MultiStartADABelief` / `MultiStartLion` family, and a `__Pixelized
    sources__` subsection on `resurrect=True`, regularization choice, `n_steps`/`batch_size`,
    kernel-CDF `bandwidth`).
  - autogalaxy: `__MultiStartAdam__`, short-form, `learning_rate=0.01` — **stale**. Its own
    `scripts/imaging/start_here.py` already fits with `af.MultiStartProdigy`.
- Both repos' `imaging/start_here.py` now use `af.MultiStartProdigy`; `imaging/modeling.py` uses
  `af.Nautilus` (`n_live`, `n_batch=50`, `iterations_per_quick_update=10000`,
  `live_visual_update=False`). Those are the canonical prose + settings to anchor on.
- `af.Nautilus`, `af.MultiStartProdigy`, `af.MultiStartAdam`, `af.MultiStartADABelief` all exist in
  the installed `autofit`.

## Work

1. Add a `__Nautilus__` section as the **first** search in both files, covering:
   - nested sampling → the **full posterior**: every parameter's PDF, its errors, and the
     covariances between parameters — the reason it is the default recommendation.
   - it is **gradient-free**: it never differentiates the likelihood, so unlike the multi-start
     optimizers it does not need (and cannot use) JAX gradients.
   - it **does** exploit JAX on GPU: `n_batch` likelihood evaluations are proposed at once and
     evaluated simultaneously through the `vmap`/`jit`-wrapped likelihood, so a GPU run is
     batched even though no gradient is taken.
   - `n_live` as the accuracy/run-time trade-off.
   - a runnable `search = af.Nautilus(...)` cell matching the `modeling.py` settings.
2. Move the multi-start section to **second**, directly after Nautilus and ahead of
   Dynesty/Emcee/Zeus/LBFGS.
3. In autogalaxy, retitle that section `__MultiStartProdigy__` and switch the code cell to
   `af.MultiStartProdigy` (no `learning_rate`), matching autolens's recommendation and that repo's
   own `start_here.py`. Keep it short-form — do not port autolens's pixelized-source subsection.
4. Fix the cross-references the reorder breaks: the multi-start prose says LBFGS's weakness was
   "noted above", which is no longer true once it sits above LBFGS.
5. Update the `__Contents__` list order in both, adding the Nautilus bullet; and adjust the intro
   paragraph so the two recommended searches are framed correctly (Nautilus when you need errors,
   MultiStartProdigy when you want speed) rather than claiming Nautilus is used in every example.

## Out of scope

- The `path_prefix=Path("searches")` vs `Path("imaging", "searches")` inconsistency already present
  between the Dynesty cell and the rest.
- Any other guide or `start_here.py` / `modeling.py` script.
