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
Filed: 2026-07-22 (backfilled from git)

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
