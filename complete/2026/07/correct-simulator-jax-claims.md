## correct-simulator-jax-claims (four false simulator-JAX claims corrected across both workspaces + one library docstring — SHIPPED)
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/379 (CLOSED)
- completed: 2026-07-30
- library-pr: https://github.com/PyAutoLabs/PyAutoLens/pull/665 (MERGED d53bfcc0)
- workspace-prs: https://github.com/PyAutoLabs/autolens_workspace/pull/380 (MERGED 5ebc1594), https://github.com/PyAutoLabs/autogalaxy_workspace/pull/183 (MERGED 21c17ce1)
- summary: Four claims were false, all measured against the installed stack. (1) "The simulator handles pytree registration internally" — ZERO `register` hits in any simulator (autolens, autogalaxy, both autoarray bases), so the documented `@jax.jit` wrap fails with `TypeError ... value is of type Tracer/Galaxies`; also UNIMPLEMENTABLE as worded, since JAX flattens jitted arguments at trace time before entering the callee (PointSolver.solve_triangles already documents exactly this). (2) "eager use_jax=True already runs on JAX" — returns numpy.ndarray-backed data in BOTH libraries. (3) The `@jax.jit` recipe fails even WITH correct registration, inside autoarray. (4) "`TransformerNUFFT` is not JAX-traceable" — BACKWARDS.

  **Claim (4) was self-inflicted, same day.** It was shipped hours earlier in PR#375/#181 (the likelihood-function-jax-pointer task), carried over from the old `__JAX__` blocks while removing them, without checking. `autolens_workspace/scripts/interferometer/simulator.py` had it right the whole time, so #375 briefly contradicted a sibling script. Per autoarray's own error text `TransformerNUFFT` IS the default JAX-native nufftax-backed transformer (nufftax 0.3.1 installed) and `TransformerNUFFTPyNUFFT` is the legacy pynufft one. Defaults differ BY CLASS: `SimulatorInterferometer`→`TransformerDFT` (simulator.py:16), `Interferometer` (what a fit uses)→`TransformerNUFFT` (dataset.py:34).

  Two scripts were ALREADY correct and were mirrored rather than rewritten — `point_source/simulator.py` and `cluster/simulator.py` state the setup, actually call `register_tracer_classes(tracer)`, and give the trace-time reason. Left untouched. Dead cells were REMOVED rather than corrected in autolens imaging/ + interferometer/simulator.py: they held live `@jax.jit def simulate(...)` cells whose call was commented out — a decorated function never invoked, which is exactly why the claim survived. The working `use_jax=True` constructor stays a live cell.

  Validation: PyAutoLens 488 passed; autolens smoke 17/17; autogalaxy smoke 12/12; all 6 edited simulator scripts run end-to-end; check_sizes.sh clean; post-merge grep zero hits for all four claims.

- detour-1-conflict: #380 went CONFLICTING mid-flight — `#378 multi-galaxy-imaging-parity` merged and touched the same `multi_galaxy/simulator.py`. Merged main in: script + notebook auto-merged, `workspace_index.json`/`llms-full.txt` REGENERATED rather than hand-resolved. #378 had independently adopted the #375 `__JAX__` pointer text verbatim for its new `multi_galaxy/likelihood_function.py`, so the two are consistent.
- detour-2-navigator: #183 was blocked by a gate armed 7 MINUTES before its run. PyAutoHands#213 ("gate relative folder references in README prose") merged 08:28:46Z; autogalaxy_workspace main last passed Navigator Check at 08:21:38Z. `navigator_check.yml` is consumed @main, so #183 was the FIRST PR to run under the widened gate, and it flagged 5 pre-existing README refs the PR never touched. **First read ("the checker over-reaches") was WRONG** — `autolens_workspace` words the same sentences repo-relative ("The `scripts` folder") and passes the identical gate; autogalaxy used the repo-name-prefixed form, which cannot resolve from the repo root because the root IS autogalaxy_workspace. Genuine drift. Fixed the 5 flagged folder refs; generate.py propagated them to the notebooks/ mirrors.
- navigator-scope-left: refs to `autogalaxy_workspace/README.md` (a FILE — the gate covers folder refs only, and autolens keeps that form) and the trailing-slash prefixed refs in `extra_galaxies/README.md` (not flagged) were deliberately left. autogalaxy still carries some prefixed refs — a full alignment sweep is its own task.
- open-followup: draft/bug/autoarray/simulator_jax_jit_path_broken.md — the real library defect behind claim (3), NOT started. At least two un-threaded xp sites (`preprocess.py:153` `noise_map_via_data_eps_and_exposure_time_map_from` takes NO xp param at all; then `array_2d_util.py` via the `Array2D.full` else-branch), depth beyond that unmeasured. Once fixed, the @jax.jit simulator recipe can be restored to the docs AND uncommented so CI proves it.
- lesson: third generation of one root cause, starting at autolens_workspace#368 → PyAutoGalaxy#536 → here. **A documented JAX recipe that no script executes will be wrong.** Where a section keeps a runnable snippet, let CI run it rather than asserting in prose that it works.

## Original prompt

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
