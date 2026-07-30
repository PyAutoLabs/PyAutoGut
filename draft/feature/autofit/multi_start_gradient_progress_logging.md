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
