## Outcome

Both `scripts/guides/modeling/searches.py` guides now lead with **Nautilus**, then **MultiStartProdigy**:

```
Nautilus → MultiStartProdigy → Dynesty → Emcee → Zeus → LBFGS → Start Point → Search Cookbook
```

- autolens_workspace#388 MERGED (`f5d03984`)
- autogalaxy_workspace#188 MERGED (`78aff831`)
- Issue PyAutoLabs/autolens_workspace#386 CLOSED

## The finding the prompt did not anticipate

**Neither file had a Nautilus section to move.** Both opened on Dynesty and never documented Nautilus anywhere — despite naming it repeatedly in their own intros and in the Dynesty / Zeus / LBFGS sections as *the* recommended search. The request said "move a section on Nautilus up to the top"; there was no such section, so it was written fresh. A reader following either guide top-to-bottom met four searches they are told not to use before reaching either of the two that are actually recommended.

The guides had also drifted from the scripts they document: `imaging/modeling.py` fits with `af.Nautilus` and `imaging/start_here.py` fits with `af.MultiStartProdigy` in both repos, yet both intros still claimed Nautilus was "the default search used throughout all modeling examples".

## The JAX claim was verified, not assumed

The user's framing — full posterior sampling, no JAX gradients, but does exploit the JAX GPU — was checked against the installed `autofit` before being written as prose:

- `autofit/non_linear/search/nest/nautilus/search.py:196-199` — builds the `Fitness` with `use_jax_vmap=self.use_jax_vmap` (default `True`) and `batch_size=self.n_batch` whenever `analysis._use_jax`.
- `:291` — passes `vectorized=fitness.use_jax_vmap` to the nautilus sampler.
- `autofit/non_linear/fitness.py:509` — `jax.vmap(jax.jit(self.call))`.

So `n_batch` proposals per step are fitted **simultaneously in one GPU call**, and no `_grad` is ever built for this search. The GPU speed-up is real and comes from batched likelihood evaluation, not gradient descent. `n_batch` doubles as the VRAM control.

Deliberately **no `n_live` default value is quoted** in the new section: `autofit`'s signature default is `3000`, while `imaging/modeling.py`'s prose claims "the default value of 200 is sufficient". That contradiction is real and still unreconciled — left out of scope here rather than propagated into two more files.

## autogalaxy carried a stale section

`autogalaxy_workspace`'s guide documented `MultiStartAdam` with a hand-tuned `learning_rate=0.01`, while that repo's own `imaging/start_here.py` already fits with `af.MultiStartProdigy`. Retitled to `__MultiStartProdigy__` and the cell switched (no `learning_rate`), with Adam / ADABelief / Lion listed as alternatives. Kept short-form per human decision — autolens's `__Pixelized sources__` subsection (`resurrect=True`, regularization-scheme choice, `n_steps`/`batch_size`, kernel-CDF `bandwidth`) was **not** ported, since that material was validated on lens likelihoods.

## The reorder broke a cross-reference

The multi-start prose in both files described LBFGS's weakness as "noted above" — false once the section sits *above* LBFGS. Fixed to "described below", and its closing line to "`Nautilus` above". Worth remembering as a general hazard: **moving a docstring section silently invalidates every positional reference inside it and pointing at it.** A grep for `noted above` / `described next` / `described below` was run over both files afterwards to confirm none survived.

## Brain override (recorded)

`pyauto-brain feature` scored this `too-large (10)` and proposed a four-phase split (`design` / `core_api` / `workspace_examples` / `docs`). That is the known repo-count difficulty proxy misfiring — two prose files, zero library API change, so a `core_api` phase was vacuous. Overridden to small, single pair of PRs. Same misfire pattern as `scaling-relation-bgc-anchored` and `vacuous-jax-assertions`.

## Concurrency

Three separate collisions, all cleared without blocking:

1. `remove-finish-docstring-hack` and `script-prose-ref-drift` both claimed these repos in `active.md`. Hand-verified disjoint (`git diff --name-only origin/main...origin/<branch>` showed neither touched `guides/modeling/searches.py` **or** `searches.ipynb`); both then MERGED as PR#383/#384 mid-session.
2. `scaling-relation-bgc-anchored` also claims `autolens_workspace` but is confined to `scripts/*/features/scaling_relation/` — disjoint.
3. A **live concurrent session** was mid-commit in PyAutoMind during issue creation (`active.md` + `complete/index.md` dirty, files touched seconds earlier). Committed only explicit paths rather than `git add -A`; their `prompt_sync_push` then swept the prompt-file rename into their own commit, which was harmless. Confirms the existing guidance: on the shared Mind index, never stage broadly.

## Gate

Heart **YELLOW**, human-acknowledged. Reasons recorded verbatim in `active.md`: `workspace validation not passing (0 failed, cloud#30516167217)` and `release validation stale: source moved since rehearsal (PyAutoFit, PyAutoArray, PyAutoGalaxy, PyAutoLens)`. `red_reasons: []`, score 70. Neither related to this change — the first reported **0 failed** (a cloud run still in flight, not real failures).

## Validation

- Both scripts executed directly — exit 0 in each workspace. The guide is **not** in either `smoke_tests.txt`, so the per-PR smoke gate does not cover it; it was run by hand under its declared `ENV: full_datasets`.
- `scripts/check_sizes.sh` — `OK: all scripts within size tolerance` in both (files grew, so no shrink risk).
- Notebooks + `llms-full.txt` + `workspace_index.json` regenerated via PyAutoHands `generate.py`; diff confined to `guides/modeling/searches` entries.
- CI: 16/16 green across both PRs — `smoke (3.12)`, `smoke (3.13)`, `navigator / paths + banner lint`, `navigator / Catalogue staleness`.

## Original prompt

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
