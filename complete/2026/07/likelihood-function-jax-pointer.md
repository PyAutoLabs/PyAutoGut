## likelihood-function-jax-pointer (six `likelihood_function.py` __JAX__ blocks demoted to a one-line pointer — SHIPPED)
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/368
- completed: 2026-07-29
- workspace-prs: https://github.com/PyAutoLabs/autolens_workspace/pull/375 (MERGED f7d7884d), https://github.com/PyAutoLabs/autogalaxy_workspace/pull/181 (MERGED 1abfc8c8)
- summary: All six `likelihood_function.py` scripts carrying a trailing `__JAX__` block (autolens imaging/interferometer/group/cluster, autogalaxy imaging/interferometer) now carry a one-sentence `__JAX__` pointer at the END of the header docstring, immediately after `__Contents__`, plus a `__JAX__` bullet as the first `__Contents__` entry. The detail moved into `scripts/guides/using_jax.py` in BOTH workspaces as a new `__Custom Likelihood Functions__` section. Smoke: autolens 16/16, autogalaxy 12/12; check_sizes.sh clean; notebooks + llms-full.txt + workspace_index.json regenerated.

  **The headline finding: the recipe in all six deleted blocks did not run.** Two independent failures, reproduced in both workspaces: (1) `register_tracer_classes(tracer)` (autolens) / constructing an `AnalysisImaging` (autogalaxy) does NOT let a `ModelInstance` cross a `@jax.jit` boundary — that needs `autofit.jax.pytrees.enable_pytrees()` + `register_model(model)`, which only `Fitness.__init__` performs (fitness.py:125-130); (2) even past that, a hand-rolled `FitImaging` without `xp=jnp` raises `TracerArrayConversionError`. The autogalaxy blocks additionally asserted that instantiating `AnalysisImaging` runs `_register_fit_imaging_pytrees()` as a side effect — false, it is called from `fit_from`, not `__init__`. Nothing caught any of this because none of the six scripts is in `smoke_tests.txt` and the blocks were prose inside a docstring, so nothing ever executed them. The guide therefore carries a VERIFIED recipe, not a copy: the three published paths (jit-around-Analysis, hand-rolled + `xp=jnp`, `Fitness._vmap`) were each executed verbatim and agree with the eager NumPy log likelihood to ~1e-15.

  `register_tracer_classes` is genuinely needed only when a `Tracer` crosses the jit boundary AS AN ARGUMENT — the `__JIT-ing Library Methods__` case `using_jax.py` already documented correctly.

  Decisions: cluster REDUCED to the pointer, not migrated (its block was `FitPositionsSource`-shaped; `cluster/modeling.py` already carries the `AnalysisPoint(use_jax=True)` path). `__Contents__` bullet added to all six (human call) rather than leaving the new section unlisted. Brain Feature Agent returned too-large (score 13) / split-into-4-phases off its repo-count proxy — overridden to one PR per repo, since the change is 8 docstring-only files of uniform shape.

  Coordination: `multistart-prodigy-start-here` (#366) and `assistant-start-here-scripts` (#367) claimed the same two repos throughout. Proceeded in parallel on human go-ahead — zero source-file overlap (those edit `start_here.py`) — with the generated artifacts (notebooks/, llms-full.txt, workspace_index.json) as the only collision surface.

  Follow-ups spawned: (1) **`worktree_check_conflict` has never fired for any task** — `worktree_list_claimed` (PyAutoBrain/bin/worktree.sh:326-333) parses `  - <repo>: <branch>` but active.md writes `  - <repo> (<branch>)`, so `repo` swallows the branch and the `==` at :346 never matches. It reported "no conflict" on two repos two active tasks both claimed. Filed as draft/bug/pyautobrain/worktree_check_conflict_never_fires.md, NOT started. (2) **autogalaxy had no public counterpart to `autolens.jax.register_tracer_classes`** — became its own task, PyAutoGalaxy#536 / PR#537.

## Original prompt

# likelihood_function.py: demote the trailing `__JAX__` block to a one-line pointer

Type: docs
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: small
Autonomy: supervised
Priority: normal

The user's request, verbatim:

> I just found a likelihood_function.py file which ended with this: __JAX__
>
> [the trailing `__JAX__` section of
> `autolens_workspace/scripts/imaging/likelihood_function.py`]
>
> This is too much detail, can you move the __JAX__ section to the top after
> __Contents__, have it be a single sentense saying "JAX is used for likelihood
> functions" (make it sound clearer though) and then point to
> guides/using_jax.py, which there has an example of a likelihood function being
> JAX'd, both via Fitness but also the Analysis object itself?

## Why

`scripts/guides/using_jax.py` is already the JAX home in both workspaces
(`__Auto-Enabled Modeling__`, `__Disabling JAX__`, `__Writing @jax.jit
Yourself__`, `__JIT-ing Library Methods__`, `__Return-Type Contract__`). The
six `likelihood_function.py` scripts each grew their own trailing `__JAX__`
block with partially divergent recipes — three different pytree-registration
stories, two different validation snippets, an interferometer-only caveat, and
one section that is purely a "see the imaging one" stub. That detail belongs in
the guide, once, not repeated six ways at the bottom of a NumPy walkthrough the
reader has just finished.

## Scope

**In scope — the six scripts carrying a trailing `__JAX__` section:**

- `autolens_workspace/scripts/imaging/likelihood_function.py`
- `autolens_workspace/scripts/interferometer/likelihood_function.py`
- `autolens_workspace/scripts/group/likelihood_function.py`
- `autolens_workspace/scripts/cluster/likelihood_function.py`
- `autogalaxy_workspace/scripts/imaging/likelihood_function.py`
- `autogalaxy_workspace/scripts/interferometer/likelihood_function.py`

In each: delete the trailing `__JAX__` block and add a `__JAX__` heading plus a
**single sentence** at the end of the opening header docstring, immediately
after the `__Contents__` bullet list. The sentence states that model-fits
evaluate this likelihood function through JAX and points at
`scripts/guides/using_jax.py`.

**In scope — the guide, both workspaces:**

- `autolens_workspace/scripts/guides/using_jax.py`
- `autogalaxy_workspace/scripts/guides/using_jax.py`

Expand the thin item 2 of `__Writing @jax.jit Yourself__` ("Custom likelihood
functions … See the per-dataset-type `likelihood_function.py` scripts") into a
worked example carrying the detail being deleted, showing **both** paths:

1. **Via the `Analysis` object** — the short path. `al.AnalysisImaging(dataset=dataset)`
   (`use_jax=True` by default), `@jax.jit` around a call to
   `analysis.log_likelihood_function(instance=instance)`. No hand-built
   `Tracer`/`FitImaging`, no explicit pytree registration (the analysis triggers
   it).
2. **Via `Fitness`** — the production path a search actually runs, and the way
   to validate a hand-rolled JAX likelihood against the NumPy walkthrough:
   `from autofit.non_linear.fitness import Fitness` (it is **not** exported as
   `af.Fitness`), `fitness._vmap(jnp.array([parameters]))[0]`. Keep the reason
   `_vmap` is the validation pattern rather than a single
   `jax.jit(fn)(concrete)`: `vmap(jit(call))` exposes un-threaded `xp` sites
   that a concrete single call hides.

Also carry across, in the guide:

- the hand-rolled `@jax.jit` + `al.Tracer` + `al.FitImaging` pattern, with
  `autolens.jax.register_tracer_classes(tracer)` as the one-time pytree setup
  (autogalaxy: the equivalent is instantiating an `ag.AnalysisImaging`, whose
  init registers the pytrees as a side effect);
- the interferometer caveat — use `TransformerDFT` (the default) under JAX;
  `TransformerNUFFT` is not JAX-traceable.

**Out of scope:**

- The `__JAX Variant__` sections in the `simulator.py` scripts — untouched.
- `weak/likelihood_function.py` and the `features/*/likelihood_function.py`
  scripts — none of them carry a `__JAX__` section today; do not add one.
- Any library source change.
- Rewriting the rest of `using_jax.py` (`__Auto-Enabled Modeling__`,
  `__Disabling JAX__`, `__JIT-ing Library Methods__`, `__Return-Type
  Contract__` stay as they are, beyond adding the new material to the
  `__Contents__` list).

## Notes

- Cluster is the odd one out: its `__JAX__` block shows `FitPositionsSource`,
  not `FitImaging`, and its guide cross-reference is `lens_calc.py`. Its
  one-line pointer should still land on `using_jax.py`; do **not** move the
  point-source-specific `FitPositionsSource` recipe into the imaging-shaped
  guide example — reduce it to the pointer and let `modeling.py` carry the
  `AnalysisPoint(use_jax=True)` path as it already does.
- `group/likelihood_function.py`'s current `__JAX__` block is already only a
  "see imaging" stub, so it loses nothing.
- The `__Contents__` bullet lists in the six scripts do **not** currently list
  `__JAX__`. Human decision 2026-07-29: **add a bullet to all six**, as the
  first entry of the list (the section sits immediately after it), so the
  pointer is discoverable and every section stays listed.
- Verify the guide's snippets against the installed API before shipping
  (`Fitness.__init__` signature, `_vmap` as a `cached_property`,
  `AnalysisImaging(use_jax=...)` default, `log_likelihood_function(instance=...)`).
- Tutorial prose — judgment tier, not execution tier ([[feedback_tutorial_prose_opus]]).
- Regenerate notebooks for both workspaces after the script edits.

## Validation

- `python .github/scripts/run_smoke.py` in each workspace for any affected
  entry (the edits are docstring-only, so this is a structural check).
- `scripts/check_sizes.sh` in `autolens_workspace` — the six scripts shrink by
  ~25-45 lines each, well under the 50% shrink threshold, but run it anyway and
  refresh the snapshot in the same diff if it complains.
