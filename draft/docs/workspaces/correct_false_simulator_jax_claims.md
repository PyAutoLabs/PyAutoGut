# Correct the false simulator-JAX claims in both workspaces (and one stale library docstring)

Type: docs
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
- PyAutoLens
Difficulty: medium
Autonomy: supervised
Priority: high

Companion to `draft/bug/autoarray/simulator_jax_jit_path_broken.md`. That bug may
sit for a while; these claims are false **today** and should not stand while it
waits. Docs-only — no behaviour change.

## The three false claims

Measured 2026-07-29 on the installed stack (see the bug prompt for frame chains):

1. **"The simulator handles pytree registration internally"** — no simulator
   anywhere registers pytrees (autolens, autogalaxy and autoarray bases: zero
   `register` hits). The jitted call fails with `TypeError ... value is of type
   Tracer / Galaxies`. It is also **unimplementable as worded**: per
   `PointSolver.solve_triangles`' own note, JAX flattens function arguments at
   trace time, so registration must run *before* the first jitted call and cannot
   be done inside the callee.
2. **"eager `via_tracer_from(...)` already runs on JAX"** — eager with
   `use_jax=True` succeeds but returns `dataset.data.array` of type
   `numpy.ndarray`, not `jax.Array`, in both libraries.
3. **The `@jax.jit` simulator recipe does not work at all**, even with correct
   registration — it dies in autoarray (`preprocess.py:153`, then
   `array_2d_util.py`). That is the separate bug; docs must stop presenting the
   recipe as working.

Plus one regression this session introduced, and one pre-existing half-truth:

4. **`TransformerNUFFT` is NOT the un-traceable one — I got this backwards.**
   autolens_workspace#375 / autogalaxy_workspace#181 (merged 2026-07-29) shipped
   "`TransformerDFT` (the default). `TransformerNUFFT` is not JAX-traceable." into
   both `using_jax.py` `__Custom Likelihood Functions__` sections. The claim was
   inherited from the old `__JAX__` blocks and is wrong. Per autoarray's own error
   text, `TransformerNUFFT` is "the default **JAX-native**" transformer
   (nufftax-backed, nufftax 0.3.1 installed) and `TransformerNUFFTPyNUFFT` is
   "the legacy pynufft backend". Defaults differ by class:
   `SimulatorInterferometer` defaults to `TransformerDFT`
   (`autoarray/dataset/interferometer/simulator.py:16`) while `Interferometer`
   (what a fit uses) defaults to `TransformerNUFFT`
   (`.../dataset.py:34`). `autolens_workspace/scripts/interferometer/simulator.py`
   already states this correctly — the guides contradict it.
5. **`guides/tracer.py`** says "Pytree registration runs as a side effect of the
   first `fit_from` / `via_tracer_from` call; you write nothing JAX-specific."
   True for `fit_from` (both `Analysis` classes register inline). False for
   `via_tracer_from`.

## Use the two correct exemplars

Do not invent wording. Two scripts already get this right and should be mirrored:

- `autolens_workspace/scripts/point_source/simulator.py` `__JAX Variant (Advanced)__`
  — states the one-time setup, calls `register_tracer_classes(tracer)`, and gives
  the reason ("Inside `@jax.jit`, JAX flattens function arguments at trace time —
  auto-registration inside `solve()` runs too late").
- `autolens_workspace/scripts/cluster/simulator.py` `__JAX JIT__` /
  `__JAX JIT — Point Solver__` — same, and actually calls it.

## Files

**Fix (9 workspace + 1 library):**

| File | What |
|---|---|
| `autolens_workspace/scripts/guides/using_jax.py` | claim 1+2 in `__Writing @jax.jit Yourself__` item 1; **claim 4** in `__Custom Likelihood Functions__` (line ~125) |
| `autogalaxy_workspace/scripts/guides/using_jax.py` | same two (claim 4 at line ~116) |
| `autolens_workspace/scripts/guides/tracer.py` | claim 5 (~line 533-537) — split `fit_from` (true) from `via_tracer_from` (false) |
| `autolens_workspace/scripts/imaging/simulator.py` | claims 1+2+3 (~359-395) |
| `autolens_workspace/scripts/interferometer/simulator.py` | claims 1+2+3 (~336-378); its NUFFT paragraph is already correct — keep it |
| `autolens_workspace/scripts/group/simulator.py` | claim 1 (~339) |
| `autolens_workspace/scripts/multi_galaxy/simulator.py` | claim 1 (~339) |
| `autogalaxy_workspace/scripts/imaging/simulator.py` | claims 1+2+3 (~252-285) |
| `autogalaxy_workspace/scripts/interferometer/simulator.py` | claims 1+2+3 (~191-225) |
| `PyAutoLens/autolens/jax/registration.py` | module docstring claims registration "is called automatically by `PointSolver(use_jax=True).solve(...)` ... and by `Simulator(...).via_tracer_from(...)` once Phase 2 ships". Nothing in autolens calls it. Docstring only |

**Leave alone — already correct:** `point_source/simulator.py`, `cluster/simulator.py`.

## What the corrected text must say

- Registration is the **caller's** responsibility, with the trace-time reason,
  naming `autolens.jax.register_tracer_classes` /
  `autogalaxy.jax.register_galaxies_classes` (the latter added in PyAutoGalaxy#537).
- The `@jax.jit` simulator wrap is **not currently supported** — link the
  autoarray issue — so readers do not burn time on a broken recipe. Keep it short;
  do not turn each simulator script into an essay ([[feedback_docs_minimal_not_maximal]]).
- Do not claim eager `use_jax=True` returns JAX-backed data.
- Interferometer: `TransformerDFT` and the nufftax-backed `TransformerNUFFT` are
  both JAX-traceable; only `TransformerNUFFTPyNUFFT` is not. Name the differing
  simulator-vs-dataset defaults rather than saying "the default".

## Validation

- Docstring-only, so `py_compile` all touched files plus `run_smoke.py` in both
  workspaces for the structural check.
- `scripts/check_sizes.sh` in autolens_workspace; the simulator scripts shrink.
- Regenerate notebooks in both workspaces.
- Re-grep afterwards for `pytree registration internally`, `already runs on JAX`
  and `TransformerNUFFT is not JAX-traceable` — must be zero hits outside the
  corrected/allowed contexts.
- `python -m pytest test_autolens/` for the library docstring change (expected
  no-op; run it anyway).

## Ordering

The library change is docstring-only with **zero API surface**, so the
library-first merge gate is vacuous here — but merge PyAutoLens first anyway
since it is trivial, then the two workspace PRs.

## Governing lesson

From autolens_workspace#368 and this follow-on: **a documented JAX recipe that no
script executes will be wrong.** Where these sections keep a runnable snippet,
prefer letting CI execute it over asserting in prose that it works.
