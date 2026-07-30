# guides/*.py: consolidate the four trailing `__JAX__` sections into `guides/using_jax.py`

Type: docs
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Model: Fable (human decision 2026-07-30 — execute this task with Fable)

The user's request, verbatim:

> This is in guides/data_structures.py, move to using_jax.py and put pointed in
> data_structures.py, look at recent isue moving jax stuff for advise, __JAX__
>
> [the ~90-line trailing `__JAX__` section of
> `autolens_workspace/scripts/guides/data_structures.py`]

and, on reviewing the sibling guides:

> ok so galaxies.py, lens_calc.py, tracer.py all have similar ending sections. I
> think we should move them all to using_jax.py, write a prompt for doign this
> but we'll do the work with Fable so dont start it

## Why

`scripts/guides/using_jax.py` is the declared JAX home in both workspaces. It is
not: **six** trailing `__JAX__` sections across four guides carry ~536 lines of
JAX prose between them, and they cross-reference each other in a ring —
`data_structures` → `lens_calc`; `galaxies` → `lens_calc` + `data_structures`;
`tracer` → `lens_calc` + `galaxies` + `data_structures`; `lens_calc` declares
itself "the canonical home for the JIT-it-yourself advanced path"; and
`using_jax.py` in turn forwards its `__JIT-ing Library Methods__` and
`__Return-Type Contract__` sections *back* to `lens_calc.py` and
`data_structures.py`. A reader entering at any node is sent to two others, and
no file is the answer.

This is the same shape as `likelihood-function-jax-pointer` (#368, shipped
2026-07-29) and should be executed the same way: one pointer sentence at the
top of each host guide, the substance consolidated into `using_jax.py`.

**And the same headline risk applies — see "Verified findings" below. Three of
the published recipes do not run on the installed stack.** Do not copy prose
across; execute each recipe and publish what actually happens.

## Scope

### In scope — the six host sections, demoted to a pointer

| File | `__JAX__` section | ~lines |
|---|---|---|
| `autolens_workspace/scripts/guides/data_structures.py` | L411-501 | 91 |
| `autolens_workspace/scripts/guides/galaxies.py` | L204-278 | 75 |
| `autolens_workspace/scripts/guides/lens_calc.py` (`__JAX (JIT-it-yourself)__`) | L432-590 | 159 |
| `autolens_workspace/scripts/guides/tracer.py` | L523-600 | 78 |
| `autogalaxy_workspace/scripts/guides/data_structures.py` | L374-443 | 70 |
| `autogalaxy_workspace/scripts/guides/galaxies.py` | L453-514 | 62 |

Line numbers are as of `main` @ 2026-07-30 and will drift — locate by heading.
`autogalaxy_workspace` has no `lens_calc.py` or `tracer.py` (lensing-only
guides); its two sections already forward *cross-workspace* to
`autolens_workspace/scripts/guides/lens_calc.py`, which this task removes.

In each host file: delete the trailing `__JAX__` block; add a `__JAX__` heading
plus a **single sentence** at the end of the opening header docstring,
immediately after the `__Contents__` bullet list, pointing at
`scripts/guides/using_jax.py`; add a `__JAX__` bullet as the **first** entry of
that `__Contents__` list. This is exactly the placement
`scripts/imaging/likelihood_function.py` now uses — read it and mirror it.

Each pointer sentence should be specific to its host, not boilerplate — e.g.
`tracer.py`'s says ray-tracing is JAX-accelerated automatically inside a
model-fit; `data_structures.py`'s says these structures are backend-polymorphic
and `.array` is the raw backing.

Note `tracer.py` ends its section with a stray `Fin.` and `data_structures.py`
with `Finish.` — both are the removed docstring crutch (see coordination note).

### In scope — the guide, both workspaces

- `autolens_workspace/scripts/guides/using_jax.py` (195 lines today)
- `autogalaxy_workspace/scripts/guides/using_jax.py` (188 lines today)

The guide's existing sections are `__Auto-Enabled Modeling__`, `__Disabling
JAX__`, `__Writing @jax.jit Yourself__`, `__Custom Likelihood Functions__`,
`__JIT-ing Library Methods__`, `__Return-Type Contract__`. Fold the incoming
material into that spine rather than appending four new sections — the point of
the task is one coherent guide, not a stapled anthology. Suggested mapping:

- **`__JIT-ing Library Methods__`** (today: three lines forwarding to
  `lens_calc.py`) absorbs the `lens_calc.py` body — the `@jax.jit` + `xp=jnp`
  pairing rule, the forgot-`xp=jnp` footgun and the `ValueError` the library
  raises, decorator-on-def vs `jax.jit(bound_method)`, the fresh-bound-method
  cache-miss footgun, closure-captured `self` vs traced argument, and the
  three-rule summary. This is the largest single migration.
- **A pytree-registration subsection** absorbs `galaxies.py` (both workspaces) —
  what `Analysis(use_jax=True)` / `Simulator(use_jax=True)` register as a side
  effect, the "no Analysis or Simulator handy" case, and
  `autolens.jax.register_tracer_classes`. Note `using_jax.py` already states the
  registration rule in two places (`__Writing @jax.jit Yourself__` item 1 and
  `__JIT-ing Library Methods__`); reconcile into one statement, do not add a
  third.
- **`__Return-Type Contract__`** absorbs `data_structures.py` (both workspaces) —
  backend-polymorphic wrappers, `.array`, the three situations that switch the
  backing, host transfer, the not-pytree rule, and the backing-type summary
  table.
- **`tracer.py`**'s implicit-vs-explicit framing is largely already covered by
  `__Auto-Enabled Modeling__`; what is genuinely new is the multi-plane note and
  the measured speedup figures. Judgment call on whether the speedup numbers
  belong in the guide at all — see Notes.

Update the guide's `__Contents__` bullet list to match whatever sections result.

### Out of scope

- The `__JAX__` / `__JAX Variant (Advanced)__` sections in the `simulator.py`
  scripts — those are executable code cells under CI (#381), leave them.
- The `likelihood_function.py` pointers — already done (#368).
- `start_here.py` JAX sections — already reduced (#336).
- Any library source change. If a recipe is found to be broken (see below), the
  fix is to publish the working recipe, not to change the library; file a
  separate prompt if a library-side fix looks warranted.
- Rewriting `using_jax.py`'s `__Auto-Enabled Modeling__`, `__Disabling JAX__` or
  `__Custom Likelihood Functions__` sections beyond reconciling duplication.

## Verified findings (probed against the installed stack, 2026-07-30)

These were executed against `autolens` @ 2026.7.23.1 / `jax` 0.10.2. **They are
ground truth for the rewrite; they contradict the shipped prose.**

1. **Returning a wrapper from inside `@jax.jit` always fails — it does not "may
   fail".** Both `data_structures.py` ("the JIT boundary *may* fail") and
   `tracer.py` ("aren't *reliably* pytree") hedge. Reality:

   ```
   TypeError: function f traced for jit returned a value of type
   <class 'autoarray.structures.arrays.uniform_2d.Array2D'>, which is not a
   valid JAX type
   ```

   Same for `Grid2DIrregular`. State it as a hard rule.

2. **The `.array`-unwrap-then-rewrap workaround is correct.** Returning
   `....array` from inside the jit and rewrapping with
   `al.Array2D(values=arr, mask=grid.mask)` on the host works, and the rewrapped
   object's `.array` is a `jax.Array` (`ArrayImpl`).

3. **`Grid2D` is not a pytree, so the recipe published in `tracer.py` and both
   `galaxies.py` files does not run.** All three publish a jitted function
   taking the grid as a *traced argument*:

   ```python
   @jax.jit
   def image_fn(tracer, grid):                 # tracer.py
       return tracer.image_2d_from(grid=grid, xp=jnp).array

   @jax.jit
   def galaxy_image(galaxy, grid):             # galaxies.py, both workspaces
       return galaxy.image_2d_from(grid=grid, xp=jnp).array
   ```

   Called as published — *even after* `register_tracer_classes(tracer)` — these
   raise `AttributeError: DynamicJaxprTracer has no attribute array` and
   `AttributeError: ... has no attribute over_sampled` respectively. The grid
   flattens to a bare tracer because `Grid2D` is not registered; registration
   covers `Tracer` / `Galaxy` / profile classes, not the grid.

   **The same function with the grid closed over instead of passed works.** So
   the correct published recipe is `@jax.jit def image_fn(tracer): ... grid
   closed over ...`, or an explicit statement that the grid must be passed as
   `grid.slim` / a raw array. Determine which the library intends and publish
   that — this is the single most important thing to get right in the rewrite.

4. `lens_calc.py`'s claim that `LensCalc` methods implement an `if xp is np:`
   guard returning raw `jax.Array` under `xp=jnp` was **not** probed. Verify
   before carrying it across.

Probe scripts used are throwaway; re-derive rather than trusting this summary
blind, but do not silently drop a finding that reproduces.

## Notes

- **Execute with Fable** (human decision 2026-07-30). Note this is tutorial
  prose, which normally stays on the judgment tier
  ([[feedback_tutorial_prose_opus]]) — the model choice here is a deliberate
  human override of that default, not an oversight.
- **Brain override:** the Feature Agent scored this `too-large (score 11)` and
  recommended a 4-phase split (`_phase_1_design` … `_phase_4_docs`). That score
  is its repo-count proxy ([[feedback_brain_repo_count_difficulty_proxy]]).
  Overridden to **one task, one PR per repo**, as `#368` did for the same shape
  — this is docstring-only prose in 8 files. Recorded here per the memory note
  that overrides must be written down.
- **The precedent is [[project_likelihood_function_jax_pointer]] / #368.** Read
  its completion record before starting — its headline finding was that all six
  deleted blocks contained recipes that had never been executed, because prose
  inside a docstring is never run by CI and none of the host scripts were in
  `smoke_tests.txt`. Finding 3 above is that same failure recurring in a
  different set of files.
- Do not carry the cross-workspace pointer
  (`autogalaxy` → `autolens_workspace/scripts/guides/lens_calc.py`) across. Each
  workspace's guides point at their own `scripts/guides/using_jax.py`.
- `tracer.py`'s speedup figures (10-30× galaxy-scale, 30-100× cluster-scale on
  GPU) are unattributed. `autolens_workspace_developer/jax_profiling/` is cited
  as carrying measured numbers — either ground the figures in that data or drop
  them rather than migrating an unsourced claim into the canonical guide.
- The two `using_jax.py` files have diverged slightly already; keep them in
  step where the API is the same, and keep the autogalaxy one in autogalaxy
  vocabulary (`ag.`, `Galaxy`/`Galaxies`, no `Tracer`/`LensCalc`).
- Regenerate notebooks in both workspaces after the script edits
  (`generate.py autolens` / `generate.py autogalaxy`).

## Coordination

`autolens_workspace` and `autogalaxy_workspace` each carry several live claims
in `active.md`. Direct file overlap known at 2026-07-30:

- **`remove-finish-docstring-hack`** — `autolens_workspace` PR#384 (OPEN,
  pending-release) edits `scripts/guides/data_structures.py`, deleting the
  `Finish.` line two lines below the `__JAX__` block this task removes. It also
  removes `tracer.py`'s `Fin.`. Adjacent-line collision; **check whether #384
  merged before branching** and rebase rather than hand-resolving.
  `autogalaxy_workspace` PR#187 does not touch these guides.
- Several other open PRs touch the generated artifacts (`notebooks/`,
  `llms-full.txt`, `workspace_index.json`) in both repos — whichever merges last
  re-runs `generate.py` rather than hand-resolving.

## Validation

- `python .github/scripts/run_smoke.py` in each workspace for the affected
  entries (docstring-only edits, so this is a structural check).
- `scripts/check_sizes.sh` in both workspaces. `data_structures.py`,
  `galaxies.py` and `tracer.py` each shrink by 60-91 lines and `lens_calc.py` by
  ~159 — all well under the 50% threshold, but run it and refresh the snapshot
  in the same diff if it complains.
- Every code snippet published in `using_jax.py` must have been **executed**
  against the installed stack, not transcribed. This is the whole lesson of
  #368.
