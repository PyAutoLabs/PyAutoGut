## multi-start-gradient-progress-logging

issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1433
completed: 2026-07-30
library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1435 (MERGED 09a134d8)

Per-step progress logging for the four multi-start gradient MAP searches (`af.MultiStartProdigy` / `MultiStartAdam` / `MultiStartADABelief` / `MultiStartLion`). They previously emitted two log lines for an entire run — "Starting new ..." and, hours later, "... sampling complete" — leaving a user unable to tell a live fit from a hung one. Originated from a user observation on a real 48-start Prodigy run.

### What shipped

- **`iterations_per_log: int = 10`** on `AbstractMultiStartGradient.__init__`, inherited by all four subclasses; dict-serialised so a resumed search keeps the cadence. Rejected at construction via `AbstractSearch._check_step_count` if not a whole number >= 1 (a sub-1 cadence either raises on the modulo or logs every step).
- **Three pure seams** beside the existing `_is_final_boundary` / `_stop_reason_on_resume` pair: `_should_log_progress(total_steps, converged)` (first step always, then cadence, plus the converged step; `silence` suppresses all), `_progress_message(...)` (compact pipe-delimited line), `_compile_message(batched)` (the two one-off XLA notices, full-sentence to match #1434's register).
- **Progress line** reports step/ceiling, best **log posterior** (`-0.5 * best_fom`, the same conversion `samples_via_internal_from` applies), gain since the previous line, live-start count, and — for the learning-rate-free rules — Prodigy's per-start `estim_lr` (`d`) as min/median/max.
- **Two compile notices**, before `_broad_starts` (single-point objective) and before the first `batched_value_and_grad` call (vmapped/chunked, one-shot via an `awaiting_compile` flag set outside the loop so resumed runs get it too).
- **22 NumPy-only unit tests** + a source-level wiring guard pinning all three call sites and the `estim_lr` read.

### Key findings / traps

- **Both standard progress channels are structurally dead here.** `iterations_per_full_update` defaults to the never-sentinel so the whole run is one chunk whose lone `perform_update` is (correctly) suppressed by `_is_final_boundary`; and `Fitness`'s quick-update counter is Python state mutated inside `fitness.call`, which is traced under `jax.jit(jax.vmap(...))` — it runs once at trace time and never again. The samplers dodge this by delegating to their own library's progress bar (emcee `progress=True`, dynesty `print_progress`).
- **These searches bypass `Fitness._jit` / `_vmap` / `_grad` entirely**, building `jax.value_and_grad(fitness.call)` at `search.py:260-261`. Any framework-level JAX-compile notice or per-iteration instrumentation added to those wrappers silently misses all four multi-start searches. This is why the compile notices had to live in `_fit`, and was reported to #1434 (whose `quick_update_message` will otherwise tell these users to set `iterations_per_quick_update` — inert here, since `_fit` constructs `Fitness` without that kwarg, unlike e.g. `nautilus/search.py:195,216`).
- **The smoke test cannot validate this change.** `PYAUTO_DISABLE_JAX=1` + `PYAUTO_TEST_MODE=2` are smoke-profile defaults and `searches/mle.py` has no `ENV: jax` release token, so the sampler is bypassed (`TEST MODE 2 ... Skipping sampler`) and `_fit` never executes. Green smoke proves only that the new kwarg breaks no caller. The step loop needed a real JAX `MultiStartProdigy` run, which was done and pasted into the PR.
- **`optax.tree_utils.tree_get(opt_state, "estim_lr")` reaches through the `apply_if_finite` wrapper** — verified against the installed optax before designing it in: `(n_starts,)` array for prodigy (`ProdigyState.estim_lr`, initialised `1e-6`), `None` for adam. So the Adam family needs no special-casing; the field is omitted by `None`.
- **No new packaged config key**, deliberately. A key in the shared `updates:` block would imply every search honours it (they don't) and would `KeyError` in any workspace shadowing that section — the trap from #1409.
- **Numerically inert.** The loop already forced a device sync every step at `search.py:361` (`np.isfinite(np.asarray(foms))`), so step/fom/alive are free; `estim_lr` is an `(n_starts,)` copy taken only on logging steps. No traced operation added, no XLA recompile.
- **`black` reformats unrelated pre-existing lines.** Running it on the two files collapsed a `jnp.concatenate` call and rewrapped an `_is_final_boundary` condition, and reflowed four aligned trailing comments in the test file. All reverted to keep the diff pure-additions (373 insertions, 0 deletions). Black is advisory in this repo, not gated.
- **The sizing heuristic penalises well-researched prompts.** Brain scored this `large (8)` and wanted a phase split; the entire score came from prompt prose (521 words +3; the words *dynesty/emcee/gradient/jax/sampler* +3; *jax/vmap* +1; memory-context +1) while `repos_affected=1` and `architectural_risk=[]` contributed nothing. Overridden to small/no-split, recorded in `active.md` and on the issue. #1434 hit the identical misfire the same evening — this is systematic, not a one-off.

### Concurrency

Ran in parallel with `sampler-cli-output-numbers` (#1434) under a human-authorized concurrent claim on PyAutoFit. Files disjoint (`mle/multi_start_gradient/search.py` here; `abstract_search.py` + `fitness.py` there), both branched off `a50ba95b0`, which had not moved at merge. `worktree_check_conflict` returned 0 at the first check only because the sibling worktree did not exist yet — the hand-check caught it, consistent with the guard being unreliable in both directions.

### Gate

tests 1614p/1s · CI green both matrix legs (3.12, 3.13) + docs-build · smoke autofit_workspace 8/8 (with the caveat above) · Heart YELLOW score 75, no RED — three pre-existing unrelated reasons (manifest drift tenant firewall; `test run status unknown (no report.json)`; release validation stale across 5 repos) human-acknowledged via AskUserQuestion. PR human-merged.

## Original prompt

# MultiStartGradient runs silently for their whole duration — no per-step progress

Type: feature
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: medium
Status: formalised

## Original request (verbatim)

> might not be feasible but if this could have a verbose update would be nice:
> 2026-07-30 19:45:31,924 - start_here - INFO - Starting new prodigy MultiStartGradient search (48 starts, no previous samples found)
> e.g. can Prodigy display its updates a bit more so a user knows it progressing

## Problem

`AbstractMultiStartGradient._fit` emits exactly two log lines for an entire run:
`"Starting new <rule> MultiStartGradient search (N starts, ...)"` and, however many
hours later, `"<rule> MultiStartGradient sampling complete."` Nothing in between.
A user cannot tell a live 300-step fit from a hung one.

Both of the standard autofit progress channels are inert for this search:

- `iterations_per_full_update` defaults to `1e99` (`autofit/config/general.yaml:3`),
  so `_steps_until_full_update` returns the whole budget — one chunk, one
  `perform_update`, which `_is_final_boundary` then correctly suppresses as
  duplicated work. Zero intermediate output by construction.
- `Fitness.call`'s quick-update counter never fires: `fitness.call` is traced inside
  `jax.jit(jax.vmap(...))` (`search.py:260-261`), so the Python-side counting runs
  once at trace time, never per step.

Other searches sidestep this by delegating to their sampler's own progress bar
(emcee `progress=True`, dynesty `print_progress=not self.silence`). The gradient
searches own their step loop, so they have no such fallback.

## Why it is cheap

The step loop (`search.py:358-400`) is plain Python and **already forces a device
sync every step** at line 361 (`np.isfinite(np.asarray(foms))`). Everything a
progress line wants is already materialised on the host each step — `total_steps`
vs `self.n_steps`, `best_fom` (best log posterior is `-0.5 * best_fom`), this
step's `foms_np[best_index]`, `alive.sum()` live starts, `n_resurrections`. No
extra sync, no recompile, no new device work.

## Ask

Add a cadence-controlled progress log line to `AbstractMultiStartGradient`'s step
loop, gated on the existing `silence` flag.

Prodigy-specific extra: `optax.contrib.prodigy`'s state carries `estim_lr` — its
`d`, the self-estimated step scale — confirmed against the installed optax
(`ProdigyState(exp_avg, exp_avg_sq, grad_sum, params0, estim_lr,
numerator_weighted, count)`). It is reachable through the `apply_if_finite`
wrapper via `optax.tree_utils.tree_get(opt_state, "estim_lr")`, the same helper
the resume path already uses at `search.py:298`. State is vmapped per-start, so
this gives min/median/max across the 48 starts — the one genuinely
Prodigy-specific diagnostic that is currently invisible (has `d` finished ramping,
or is it still climbing?). Adam/ADABelief/Lion have no such field; `tree_get`
returns `None` and they get the generic line.

## Constraints / decisions to make

- **Log line, not a tqdm bar.** tqdm is installed only transitively (not declared
  in `pyproject.toml`), a bar's ETA would mislead because auto-convergence makes
  `n_steps` a ceiling rather than a target, and progress lines survive SLURM/HPC
  log capture where bars do not.
- The knob lands on `AbstractMultiStartGradient`, so it applies to all four
  subclasses (Adam / ADABelief / Lion / Prodigy), not Prodigy alone. That is the
  right scope — the silence is a base-class problem — but it is a shared-search
  change, not a Prodigy-only tweak.
- Must not perturb numerics, add a device sync, or trigger an XLA recompile.
- Cadence default should be sane for both a 300-step CPU run and a long GPU run.
