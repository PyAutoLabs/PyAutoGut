# point-source-dataset-cap-guard

Shipped 2026-08-23. Issue [PyAutoLens#710](https://github.com/PyAutoLabs/PyAutoLens/issues/710).

## PRs

- [PyAutoLens#711](https://github.com/PyAutoLabs/PyAutoLens/pull/711) — merged `27126fb`
- [autolens_workspace_test#265](https://github.com/PyAutoLabs/autolens_workspace_test/pull/265) — merged `051b051`

Library-first order held: #711 merged before #265.

## Summary

The intake prompt reported `point.py`'s JAX-vmap parity assert failing with a
*different* value on every run (`-1e99` sentinel in a parallel batch, a finite-but-wrong
`16.131221` serially) and asked whether the triangle solve was non-deterministic.

It is not. There is **no library numerical bug**. The mechanism is on-disk dataset
poisoning: `dataset/point_source/simple` is committed, gitignore-allowlisted and
JSON-only, and `should_simulate()` `rmtree`s it whenever `PYAUTO_SMALL_DATASETS=1`
is in force. With no `data.fits` there is no `SMALLDAT` stamp for PyAutoArray#471's
guard to read, so the delete fires and the degenerate replacement survives into the
next full-regime run — one run poisons the next, which is precisely the
parallel-vs-serial value difference.

The prompt's own leading hypothesis was right: under the cap `PointSolver.solve`
short-circuits to a fixed pair unrelated to the lens model, so the parity assert is
structurally meaningless in that regime.

`autolens_workspace_test#264` (2026-08-22) had root-caused this a day earlier and
fixed the one site its sweep found. This task closed the two gaps that remained.

## Key findings / traps

- **`should_simulate` is destructive, and the library guard cannot see JSON datasets.**
  PyAutoArray#471's `_is_capped_at_the_current_cap` keys off a `SMALLDAT` header card in
  `<dataset>/data.fits`. A JSON-only dataset has no such file, so the guard returns
  False and the delete proceeds. Any committed JSON dataset is structurally unprotected
  by it — the workspace-side `ENV: full_datasets` declaration is the only defence.
- **`real_output` and `real_plots` do NOT release the dataset cap.** Only
  `full_datasets` does. Two scripts have now been caught claiming full-resolution data
  in prose while declaring a marker that leaves the cap in force (`visualization.py` in
  #264, `modeling_visualization_jit.py` here). When auditing, read the `ENV:` line, never
  the `__Env__` prose.
- **#264's "only at-risk site in the organism" sweep was wrong** — it missed a site in
  its own repo. The corrected sweep (every `!dataset/**` allowlist entry vs every
  `should_simulate` call site lacking `full_datasets`) now reports clean for
  autolens_workspace_test. **The other workspaces remain unaudited** — worth a task.
- **A guard on geometry does not generalise.** `interferometer/nufft.py` asserts its mask
  shape, which works only because it owns a FITS dataset with detectable capped geometry.
  For JSON data the guard must read the env var directly.
- **The prompt's repro command was invalid** and could never have passed: it hand-set
  `PYAUTO_SMALL_DATASETS=1`, overriding the script's own `ENV: jax full_datasets`
  declaration. A failing repro is not automatically evidence of a bug — check whether the
  invocation contradicts the script's declared environment first.

## Verification

Done in-session (cloud), against libraries 2026.8.23.1 + PyAutoLens main. The prior
prompt asserted a cloud session could not settle this; installing the stack made it
possible, and the mechanism was decided by direct A/B rather than a run tally.

| Check | Result |
|---|---|
| `should_simulate('dataset/point_source/simple')`, cap on | `True`, directory deleted |
| same, cap off | `False`, intact |
| `PointSolver.solve` at einstein_radius 1.0 / 1.6 / 2.5 under cap | identical `[(1.0,0.0),(0.0,1.0)]`, silent at DEBUG |
| `point.py` on main, correct profile | PASS — `-83.38049778`, `-82.33883111`, pins exact |
| `point.py` with the cap set, post-fix | fails on the guard, dataset untouched |
| `test_autolens/` | 541 passed |
| CI | PyAutoLens 4/4 green (incl. `unittest-nojax`); workspace 3/3 smoke green |

The workspace smoke run also confirmed what could not be checked locally: the harness
accepts the previously-unused `full_datasets real_output` marker combination.

## Registry reconciliation

Three prompts described this one surface; folded to one line of truth.

- `planned.md` → `jax-point-source-point-smoke-sentinel` marked superseded. Its `-1e99`
  symptom was the same poisoning; `point.py` passes on main. Retire the entry and its
  prompt `draft/bug/autolens/jax_point_source_point_smoke_sentinel.md`.
- `draft/bug/autolens/point_solver_error_bisect_health.md` no longer absorbs this task —
  the "same investigation surface" premise was false (workspace env-declaration defect,
  not triangle-solve accuracy). Its stale `point_solver.py:111` reference corrected to `:119`.

## Follow-ups worth filing

1. Audit the remaining workspaces' `!dataset/**` allowlists against their `should_simulate`
   call sites — #264's organism-wide claim is still unverified.
2. Consider a `SMALLDAT`-equivalent stamp for JSON datasets, or make `should_simulate`
   refuse to delete a git-tracked path outright. The current protection is per-script
   discipline, and it has now failed twice.

## Original prompt

# point.py JAX-vmap parity assert is non-deterministic under the smoke env

Type: bug
Target: autolens
Repos:
- autolens_workspace_test
- PyAutoLens
Difficulty: small
Autonomy: supervised
Priority: normal
Status: issued — PyAutoLens#710 (2026-08-23)

## 2026-08-23 — DIAGNOSED. Root cause found; scope changed. Read this before the body below.

The body below is the original intake prompt, kept verbatim. Two of its claims are now known
to be wrong, and its leading hypothesis is confirmed. Tracked as
[PyAutoLens#710](https://github.com/PyAutoLabs/PyAutoLens/issues/710).

**The mechanism is on-disk dataset poisoning, not a numerical bug.** `dataset/point_source/simple/`
is committed, gitignore-allowlisted and JSON-only. Under `PYAUTO_SMALL_DATASETS=1`,
`al.util.dataset.should_simulate()` returns `True` and `rmtree`s it, re-simulating under the cap.
With no `data.fits` there is no `SMALLDAT` stamp for PyAutoArray#471's guard to read, so the
delete fires and the degenerate replacement survives into the next full-regime run. Locally, one
run poisons the next — which is the reported parallel-vs-serial value difference.

Verified directly (2026-08-23, cloud session, libraries at 2026.8.23.1 + PyAutoLens main):

| call | result | directory after |
|---|---|---|
| `should_simulate('dataset/point_source/simple')`, `PYAUTO_SMALL_DATASETS=1` | `True` | **deleted** |
| same call, cap unset | `False` | intact |

**The prompt's leading hypothesis was right.** `PointSolver.solve` short-circuits under the cap
and returns `[(1.0, 0.0), (0.0, 1.0)]` for *every* lens model — verified identical at
`einstein_radius` 1.0 / 1.6 / 2.5 — and does so with no warning at DEBUG level. The parity assert
is structurally meaningless in that regime.

**Two corrections to the body below.**

1. **The paths are stale.** The script is now `scripts/point_source/jax_likelihood/point.py`;
   the solver short-circuit is at `point_solver.py:119`, not `:111`. There is no
   `config/build/env_vars.yaml` — the profiles are `config/build/profile_smoke.yaml` and
   `profile_release.yaml`.
2. **The repro command is invalid.** It hand-sets `PYAUTO_SMALL_DATASETS=1`, overriding the
   `ENV: jax full_datasets` declaration the script carries at line 21. That invocation cannot
   pass and never could. It is operator error in the repro, not evidence of a live bug.

**Prior art.** autolens_workspace_test#264 (2026-08-22) root-caused this and fixed the one
at-risk site its sweep found. That sweep missed
`scripts/point_source/visualization/modeling_visualization_jit.py` (declares `ENV: real_output`,
which does not release the cap, while its own prose claims full-resolution data), and it left
the five parity scripts themselves unguarded. Those are this task's scope.


`autolens_workspace_test/scripts/jax_likelihood_functions/point_source/point.py` fails its
JAX-vs-numpy parity assert under the smoke env, and **fails differently between runs**:

```
AssertionError: point: JAX vmap likelihood mismatch
  run A (parallel batch):  ACTUAL [-1.e+99]     DESIRED -83.380498
  run B/C/D (serial):      ACTUAL [16.131221]   DESIRED -83.380498
```

`-1e+99` is the failed-fit sentinel; `16.131221` is a finite but wrong value. Same script,
same env, same commit — so the assert is not measuring what it intends to.

Observed while smoke-gating PyAutoArray#398 (convolver-gaussian-small-datasets-cap, merged
2026-07-22). **Confirmed unrelated to that change**: A/B'd by checking out the pre-fix
`autoarray/operators/convolver.py` and re-running — identical failure and identical value.
The script also contains no `Convolver` / `from_gaussian` / PSF usage at all, so a
convolution change cannot reach it. It is one of the ~10 already-failing workspace scripts
Heart reported on 2026-07-20, i.e. it pre-dates that work.

Lead worth checking first: `PointSolver` has its own `PYAUTO_SMALL_DATASETS` short-circuit
at `PyAutoLens/autolens/point/solver/point_solver.py:111` that skips the triangle-tiling
solve entirely under the smoke flag. If the parity assert runs against that short-circuited
solve, the comparison may be structurally meaningless in smoke mode — in which case the fix
is either to unset the flag for this script (`config/build/env_vars.yaml` override) or to
skip the assert when the short-circuit is active, rather than to chase a numerical bug.

Second possibility to rule out: genuine non-determinism in the triangle solve (ordering /
tie-breaking) that the parity tolerance `rtol=1e-4` cannot absorb.

Repro (from `autolens_workspace_test/`):

```
PYAUTO_TEST_MODE=2 PYAUTO_SMALL_DATASETS=1 PYAUTO_SKIP_FIT_OUTPUT=1 \
PYAUTO_SKIP_VISUALIZATION=1 PYAUTO_SKIP_CHECKS=1 PYAUTO_FAST_PLOTS=1 JAX_ENABLE_X64=True \
NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib \
python scripts/jax_likelihood_functions/point_source/point.py
```

Run it several times, and once inside a parallel batch — the failure value changes. Per
`feedback_flaky_test_sample_size`, a few passing runs will not settle this; decide on the
mechanism, not on a run tally.
