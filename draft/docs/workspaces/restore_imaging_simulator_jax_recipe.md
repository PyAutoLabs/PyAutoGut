# Restore the imaging simulator `@jax.jit` recipe — and put it under CI

Type: docs
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: small
Autonomy: supervised
Priority: normal

PyAutoArray#421 (merged `e994485c`) fixed the imaging simulator's `@jax.jit` path.
The docs still say it "does not currently work" — true when autolens_workspace#379
shipped, false now. This restores the recipe and, crucially, **puts it under CI**.

## Why the CI part is the point

This is the fourth task in one arc (autolens_workspace#368 → PyAutoGalaxy#536 →
autolens_workspace#379 → PyAutoArray#421). Every generation traced to the same
root cause: **a documented JAX recipe that no script executes will be wrong.**

The imaging `__JAX Variant__` sections had the call commented out
(`# dataset_jax = simulate(tracer)`) or inside a ```` ```python ```` fence, so nothing
ever ran them — which is exactly how the claim stayed false for months. Restoring
the recipe without executing it would re-create the trap.

**Neither workspace has any `simulator.py` in `smoke_tests.txt`** (verified
2026-07-30), so uncommenting alone gives zero CI coverage. The imaging simulator
scripts must be added to the smoke list for CI to actually prove the recipe.

## Scope

**Restore the recipe, as executed code:**

- `autolens_workspace/scripts/imaging/simulator.py` — restore the `@jax.jit`
  `simulate` cell and **uncomment `dataset_jax = simulate(tracer)`**, keeping the
  `register_tracer_classes(tracer)` setup line (still required — that half of
  autolens_workspace#379 remains true).
- `autogalaxy_workspace/scripts/imaging/simulator.py` — same, using
  `register_galaxies_classes(galaxies)` (PyAutoGalaxy#537). This section is
  currently fenced prose; convert to **real cells** so it executes.
- `autolens_workspace/scripts/guides/using_jax.py` and
  `autogalaxy_workspace/scripts/guides/using_jax.py` — `__Writing @jax.jit
  Yourself__` item 1: the jitted wrap works for imaging; keep the registration
  requirement and its trace-time reason.
- `autolens_workspace/scripts/{group,multi_galaxy}/simulator.py` — the stubs say
  the jitted wrap "does not currently work"; update to match imaging.

**Add to CI:**

- `autolens_workspace/smoke_tests.txt` — add `scripts/imaging/simulator.py`
- `autogalaxy_workspace/smoke_tests.txt` — add `scripts/imaging/simulator.py`

This adds two entries to the per-PR gate. Deliberate: it is the only mechanism
that makes CI execute the recipe. Both scripts already run clean under the smoke
profile (measured during autolens_workspace#379).

**Must NOT change — still accurate:**

- The **interferometer** sections in both workspaces. PyAutoArray#421 explicitly
  excluded that path: `TransformerDFT` fails at the jit boundary
  (`Interferometer` needs its own pytree registration) and `TransformerNUFFT`
  fails at `operators/transformer.py:660`. Tracked in
  `draft/bug/autoarray/interferometer_simulator_jax_jit.md`. Leave the
  not-supported wording and the issue pointer.
- `point_source/simulator.py` and `cluster/simulator.py` — already correct.
- Do not claim eager `use_jax=True` returns JAX-backed data on its own; that was
  a separate false claim fixed in autolens_workspace#379 and is unrelated to the
  jitted path.

## What the restored recipe must say

Registration stays the caller's responsibility, with the reason (JAX flattens a
jitted function's arguments at trace time, so a callee that registers internally
is already too late). PyAutoArray#421 changed only what happens *after*
registration — it did not make registration automatic, and cannot.

## Validation

- Run both edited `imaging/simulator.py` scripts end-to-end — the uncommented
  jitted call must actually execute.
- `python .github/scripts/run_smoke.py` in both workspaces; the two new entries
  must pass, and confirm the summary count rises accordingly.
- `scripts/check_sizes.sh` in autolens_workspace.
- Regenerate notebooks in both workspaces.
- Confirm the jitted call returns `jax.Array`-backed data, so the section's own
  claim is exercised rather than merely present.

## Note

`autogalaxy_workspace` PR #184 (`feature/extra-galaxies-multi-galaxy`) is open and
touches the generated artifacts (`llms-full.txt`, `workspace_index.json`). No
source overlap; whichever merges last re-runs `generate.py`.
