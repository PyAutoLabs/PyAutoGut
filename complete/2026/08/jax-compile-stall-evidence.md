# Make a stalled JAX compile report itself (jax-compile-stall phase 1)

- **Issue:** PyAutoFit#1516 (closed) · **PR:** PyAutoFit#1517 (merged 2026-08-23)
- **Repos:** PyAutoFit (`autofit/non_linear/jax_compile.py`, `test_autofit/non_linear/test_jax_compile.py`)
- **Epic:** `jax-compile-stall` phase 1 of 3 — ledger `draft/bug/ci/jax_vmap_jit_compile_stall.md`. Phase 2 is autolens_workspace_test#271.
- **What:** `log_on_first_compile` gained a heartbeat (`still compiling <desc>, Ns elapsed`; `PYAUTOFIT_JAX_COMPILE_HEARTBEAT_SECS`, default 30, 0 disables), a `faulthandler` watchdog dumping the process's own traceback on overrun (`PYAUTOFIT_JAX_COMPILE_DUMP_SECS`, defaulting to 300 **when `CI` is set** and 0 otherwise), and separate timings for the trace/lower/compile wait vs the `jax.block_until_ready` execution wait. Existing `complete in {n} seconds` summary line unchanged. All four call sites inherit it (`Fitness._vmap/_jit/_grad`, `analysis/latent.py`). No workspace script and no CI runner touched.
- **Why:** the same intermittent XLA compile stall had been quarantined three times (autolens_workspace_test#245; ag_test `multi_dataset/.../rectangular.py` 2026-08-01; ag_test `imaging/.../mge_group.py` 2026-08-23) and diagnosed zero times, because a stalled run emitted the "compiling..." line and then nothing until the cap killed it.
- **Key traps recorded:**
  - **The silence spanned two different waits.** The wrapper called `func(...)` (trace/lower/XLA compile) and then `jax.block_until_ready(result)` (execution) under **one** log line, so a captured tail could not say which half was stuck — or whether the process was alive at all. That ambiguity, not the stall itself, is what defeated three investigations.
  - **`Fitness._vmap` is `jax.vmap(jax.jit(self.call))`** — `vmap` *of* `jit`, the inverted ordering — while `analysis/latent.py` uses `jax.jit(jax.vmap(...))`. The stalling path is exactly the `vmap` path; `_jit`-only scripts in the same directories do not stall. **Deliberately not changed here**: altering the transform while trying to observe the stall would destroy the thing being observed. First A/B for phase 3.
  - **The CI-conditional default avoids a second repo touch.** Defaulting the dump on when `CI` is set makes the next stall self-diagnosing without threading an env var through every workspace's `config/build/env_vars_*.yaml`.
  - **A traceback during XLA compile parks at the pybind boundary** and shows no XLA internals. It still separates *in compile* / *in execution* / *blocked on a Python-level lock* (e.g. the persistent compile cache, on by default since PyAutoConf#128) — which is the three-way fork phase 3 needs.
  - **Diagnostics must never break a fit.** An unstartable heartbeat thread (`RuntimeError` from `Thread.start`), an unarmable dump (a capturing harness can leave stderr without a real fd) and a malformed or negative interval all fall back and continue. The heartbeat-start guard was added on an adversarial re-read before pushing — it was originally outside the `try`, where it could have killed a fit.
- **Tests/verification:** full PyAutoFit suite 2008 passed / 34 skipped (3.12); `test_jax_compile.py` 16 passed, 12 new. CI green on 3.12, 3.13 and **unittest-nojax** — the new tests need no JAX import. End-to-end: a simulated stall in a fresh process (`CI=true`, heartbeat 2s, dump 5s) emitted heartbeats and two repeating tracebacks before SIGKILL at 12s, exactly as a CI cap would kill it.
- **Heart:** **NOT consulted** — `pyauto-heart` was unreachable from the `web-github` session that opened and merged this. Flagged in the PR body and in `active.md`; merge was a human instruction ("merge when green").
- **Provenance:** started, implemented, shipped and merged by one `web-github` session 2026-08-23 (`claude/jax-vmap-jit-stall-swz2tc`), against a direct PyAutoFit clone rather than a worktree. Filed prompt lived on an unmerged branch (`claude/backport-per-script-timeout-r3w1sv`) and was brought onto the task branch at `/start_dev`.

## Original prompt

# Phase 1: make a stalled JAX compile report itself (heartbeat + faulthandler + compile/execute split)

Type: bug
Target: ci
Repos:
- @PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised
Epic: jax-compile-stall
Phase: 1
Campaign: bug/ci/jax_vmap_jit_compile_stall.md (Phase 1 — the enabler; phases 2 and 3 are blocked on this)
Filed: 2026-08-23
Issued: 2026-08-23

## Why this is phase 1

The stall's whole cost is that it produces **no evidence**. The last line any
killed run emits is

```
autofit.non_linear.jax_compile - INFO - JAX jit compiling vectorized (vmap)
    likelihood function, could take seconds or minutes...
```

and then silence until the cap kills it. Three separate quarantines
(`autolens_workspace_test` delaunay #245, `autogalaxy_workspace_test`
`multi_dataset/.../rectangular.py` 2026-08-01, `imaging/.../mge_group.py`
2026-08-23) produced no diagnosis between them, because there was nothing to
diagnose *from*. Phases 2 and 3 of this campaign both consume evidence this
phase creates.

## What is wrong with the current instrumentation

`log_on_first_compile(func, description)` in
`autofit/non_linear/jax_compile.py` wraps the `jax.jit` / `jax.vmap` /
`jax.grad` callables so the "this is compiling" line lands where the user
actually waits — on the first call. Inside that first call it does two very
different things under one log line:

1. `result = func(*args, **kwargs)` — tracing, lowering and XLA compilation;
2. `jax.block_until_ready(result)` — execution, because JAX dispatches
   asynchronously.

Then it logs one `complete in {n} seconds` summary. So a hang anywhere in
either half looks identical from the outside, and a compile that is merely
*slow* looks identical to one that has stopped. Nothing reports liveness in
between.

## Task

All of this is library-side in @PyAutoFit. **Do not touch the workspace
scripts** — they are user-facing documentation, and a per-script workaround is
the quarantine pattern this campaign exists to stop.

1. **Heartbeat.** While the first call is in flight, log
   `still compiling {description}, {n}s elapsed` on an interval. Daemon thread,
   stopped in the existing `finally` so it can never hold the process open.
   Interval from `PYAUTOFIT_JAX_COMPILE_HEARTBEAT_SECS`, default `30`, `0`
   disables.
2. **Watchdog.** Arm `faulthandler.dump_traceback_later(secs, repeat=True,
   exit=False)` before the first call and `cancel_dump_traceback_later()` in the
   `finally`, so a compile that overruns dumps its own traceback to stderr
   before anything kills it. Threshold from `PYAUTOFIT_JAX_COMPILE_DUMP_SECS`.
3. **Default it on under CI.** Default the threshold to `300` when the `CI`
   environment variable is set and `0` (off) otherwise, both overridable. This
   is what makes the *next* CI stall self-diagnosing with no workspace edit and
   no runner edit — the alternative, wiring an env var into each workspace's
   `config/build/env_vars_*.yaml`, is a second repo touch for the same effect.
4. **Split the timing.** Time `func(...)` and `jax.block_until_ready(result)`
   separately and log both, so the record says which half is stuck. Keep the
   existing single `complete in {n} seconds` summary line unchanged.

Applies automatically to all four call sites: `Fitness._vmap`, `Fitness._jit`,
`Fitness._grad` (`autofit/non_linear/fitness.py`) and the batched latent
computation in `autofit/non_linear/analysis/latent.py`.

## Known limitation, to be stated in the PR

A Python traceback taken during XLA compilation parks at the pybind boundary —
it will not show XLA internals. It still separates *in compile* from *in
execution* from *blocked on a Python-level lock* (for instance the persistent
compilation cache, `JAX_COMPILATION_CACHE_DIR`, on by default since
PyAutoConf#128). That three-way split is exactly the fork phase 3 needs, so the
limitation does not undermine the phase.

## Acceptance

- A stalled first compile emits periodic liveness lines with elapsed time.
- A stalled first compile leaves a traceback behind in CI without any workspace
  or runner change.
- The log distinguishes the compile wait from the execution wait.
- Covered by tests in `test_autofit/non_linear/test_jax_compile.py` that need no
  JAX import: heartbeat fires, watchdog is armed and cancelled, env defaults
  including the `CI` branch.
- No workspace script and no CI runner is modified by this phase.
