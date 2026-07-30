# data_structures.py: move the `__JAX__` block to `guides/using_jax.py`, leave a pointer

Type: docs
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: small
Autonomy: supervised
Priority: normal

The user's request, verbatim:

> This is in guides/data_structures.py, move to using_jax.py and put pointed in
> data_structures.py, look at recent isue moving jax stuff for advise, __JAX__
>
> [the ~90-line trailing `__JAX__` section of
> `autolens_workspace/scripts/guides/data_structures.py`, covering
> backend-polymorphic structures, `.array`, when the backing becomes
> `jax.Array`, host transfer, the not-pytree rule, and the backing-type summary
> table]

## Why

This is the same shape as `likelihood-function-jax-pointer` (#368, shipped
2026-07-29): a NumPy-focused walkthrough grew a long trailing `__JAX__` block
that duplicates material already owned by `scripts/guides/using_jax.py`. The
guide's `__Return-Type Contract__` section already states the wrapper-vs-raw
distinction, the host-transfer rule, and points back at `data_structures.py` —
so the two files currently cover the same ground twice, in different words, and
`using_jax.py` is the file that will drift out of date.

## Scope

**In scope — the two `data_structures.py` scripts:**

- `autolens_workspace/scripts/guides/data_structures.py` (`__JAX__` at L411-501)
- `autogalaxy_workspace/scripts/guides/data_structures.py` (`__JAX__` at L374-443)

In each: delete the trailing `__JAX__` block and put a `__JAX__` heading plus a
**single sentence** at the end of the opening header docstring, immediately
after the `__Contents__` bullet list, pointing at `scripts/guides/using_jax.py`.
Add a `__JAX__` bullet as the first entry of the `__Contents__` list. This is
exactly the placement `likelihood_function.py` now uses — mirror it.

**In scope — the guide, both workspaces:**

- `autolens_workspace/scripts/guides/using_jax.py`
- `autogalaxy_workspace/scripts/guides/using_jax.py`

Fold the deleted substance into the existing `__Return-Type Contract__` section
rather than appending a new parallel section — that section already carries the
thin version of it. What must survive the move:

1. **Backend-polymorphic wrappers + `.array`.** The wrapper type is the same
   `aa.Array2D` / `aa.Grid2D` on either backend; only the backing changes.
2. **The three situations that switch the backing to `jax.Array`** — analysis
   with `use_jax=True`, simulator with `use_jax=True`, construction inside a
   traced function with `xp=jnp`.
3. **Host transfer** — plotting, `.fits` writing, `.copy()`, `.tolist()` convert
   transparently; direct NumPy arithmetic host-transfers off the GPU.
4. **The not-pytree rule** — returning an `aa.Array2D` / `aa.Grid2DIrregular`
   from inside your own `@jax.jit` may fail at the boundary; return the raw
   `.array` and rewrap on the host. This is the one genuinely new fact the guide
   does not already carry, and the reason the move is worth doing rather than
   just deleting.
5. **The backing-type summary table.**

Add a `__Return-Type Contract__`-adjacent line to the guide's `__Contents__`
bullet list only if the section title changes; otherwise leave the list alone.

**Out of scope:**

- The `__JAX__` / `__JAX Variant__` sections in `simulator.py`, `lens_calc.py`,
  `tracer.py`, `galaxies.py` — untouched.
- Any library source change.
- Rewriting the rest of `using_jax.py`.

## Notes

- The two blocks have **diverged**: the autolens version cites
  `scripts/imaging/simulator.py __JAX Variant (Advanced)__` and
  `scripts/guides/lens_calc.py`; the autogalaxy version cross-references
  `autolens_workspace/scripts/guides/lens_calc.py` (a cross-*workspace* pointer)
  and has no `Finish.`/simulator citation. Both cross-references should land on
  the in-repo `scripts/guides/using_jax.py`, which then forwards to `lens_calc.py`
  for the JIT-it-yourself deep dive. Do not carry the cross-workspace pointer
  across.
- **Verify the not-pytree claim before publishing it.** The deleted block hedges
  ("may fail"), and the precedent task found every recipe in the six deleted
  `likelihood_function.py` blocks was untested prose that did not run
  ([[project_likelihood_function_jax_pointer]] — the headline finding). Execute
  the return-an-`Array2D`-from-jit case against the installed stack and state
  what actually happens, or drop the claim.
- **File-overlap coordination:** `autolens_workspace` PR#384
  (`remove-finish-docstring-hack`, OPEN pending-release) edits
  `scripts/guides/data_structures.py` — it deletes the `Finish.` line two lines
  below the `__JAX__` block this task removes. Adjacent-line collision in the
  same file; whichever merges second must rebase.
  `autogalaxy_workspace` PR#187 does not touch `data_structures.py`.
  Both repos also carry several other live claims — see `active.md`.
- Tutorial prose — judgment tier, not execution tier ([[feedback_tutorial_prose_opus]]).
- Regenerate notebooks for both workspaces after the script edits.

## Validation

- `python .github/scripts/run_smoke.py` in each workspace for the affected entry
  (docstring-only edits, so this is a structural check).
- `scripts/check_sizes.sh` in both workspaces — `data_structures.py` shrinks by
  ~90 (autolens) / ~70 (autogalaxy) lines, well under the 50% threshold, but run
  it and refresh the snapshot in the same diff if it complains.
