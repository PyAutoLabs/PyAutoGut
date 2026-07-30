## Summary

Two untrue things the CLI told a user during a non-linear search, plus two real
bugs found while verifying the fix for them.

The workspace scripts printed the literal token `iterations_per_quick_update`
instead of its value. Fixed by moving the message into the library —
`AbstractSearch.quick_update_message`, logged once in `fit()` — so 23 workspace
scripts can drop their hand-written copy (phase 2). The message has two branches
because the packaged default is the inf-like `1e99` never-sentinel: a real
integer cadence, or a plain statement that updates are disabled naming the
config key. Rendering the default as "every 1e+99 iterations" would have been
true and useless.

`jax.jit` / `jax.vmap` / `jax.grad` return instantly — tracing, lowering and XLA
compilation happen on the *first call* to what they return. The old logging sat
at wrapper-construction time, so it announced a wait that had not started and
reported ~0 seconds immediately before an unexplained pause that can run to
minutes. New shared helper `autofit/non_linear/jax_compile.py`
(`log_on_first_compile`) moves the message to the first call and reports honest
elapsed time. `analysis/latent.py` had the identical bug and now shares the
helper rather than duplicating it.

## PRs

- PyAutoFit#1436 — MERGED 2026-07-30 (merge commit `39cbce779`); issue #1434
  auto-closed. CI green on all three legs (unittest 3.12, unittest 3.13,
  docs-build).

## Key findings / traps

**Only Nautilus ever forwarded `iterations_per_quick_update` to `Fitness`.**
Dynesty, Emcee, Zeus, BlackJAX NUTS, BFGS and Drawer all constructed `Fitness`
without it, so `Fitness.iterations_per_quick_update` was `None` and
`manage_quick_update` returned at its first guard (`fitness.py:378`). The search
ran perfectly and simply never updated — setting the knob did nothing at all for
7 of the 8 searches. Control test, same model and cadence of 25 with a fresh
output directory each run: Nautilus produced updates, Dynesty produced none;
after wiring, 0 → 1. **Announcing a cadence without fixing this would have
converted a cosmetic bug into an active lie.**

**The re-run that appeared to show "still 0" was stale output, not a result.**
The probe wrote to `output/probe_cadence_25/`; the second run resumed the
already-complete fit and evaluated nothing. Always `rm -rf` the probe's output
directory between before/after runs — this nearly produced a false "the fix
didn't work" conclusion.

**Wiring the searches up exposed a latent crash.**
`manage_quick_update` called `.tolist()` on the parameter vector, which held only
because Nautilus passes an ndarray. Dynesty's initializer passes a plain Python
list → `AttributeError: 'list' object has no attribute 'tolist'` mid-fit.
Normalized with `np.asarray(...).tolist()`.

**`multi_start_gradient` is deliberately NOT wired.** It differentiates
`fitness.call` inside its own jit/vmap step loop, so the Python-side counter in
`call_wrap` would run once at trace time rather than per step. Its progress
reporting is PyAutoFit#1433 (a genuinely concurrent sibling task in another
session). The exemption is recorded with its reason in the new
`test_quick_update_wiring.py` rather than left implicit.

**Both new detectors were proven to fail on the pre-fix source** before being
trusted — the AST wiring test on all 6 sites, the parameter-container test on
the `list` and `tuple` cases (ndarray passed either way, as expected). A
regression test that cannot fail proves nothing.

**New non-fatal warning as a side effect.** With quick updates live for six more
searches, `_warmup_visualization` becomes reachable for them; an analysis without
`fit_for_visualization` now logs `Visualization warm-up failed (non-fatal)` once
per fit. Harmless but new on simple autofit analyses that enable both JAX and a
finite cadence.

## Concurrency notes

Registered while PyAutoFit was already claimed by `multi-start-gradient-progress-logging`
(#1433, registered minutes earlier). `worktree_check_conflict` returned 0 — but
only because that worktree did not exist on disk yet, so the guard saw nothing.
Hand-checking `active.md` found the claim. Files were disjoint and both tasks
ran in parallel without collision.

The shared Mind index also held another session's staged `git mv` at the moment
of registration, so every Mind commit here used explicit file pathspecs rather
than `prompt_sync_push` (which does `git add -A` and would have swept it).

## Follow-up

Phase 2 — remove the now-duplicated sentence from 23 workspace scripts
(`autolens_workspace` 14+, `autogalaxy_workspace` 3+, `HowToLens` 1) and
regenerate the 23 `.ipynb` / 14 `.md` counterparts. Prompt filed at
`draft/docs/autolens_workspace/sampler_cli_output_workspace_sweep.md`; needs its
own issue via `start_dev`. Also fixes the "cell **with** progress" typo in the
same print block.

## Heart

Shipped on Heart **YELLOW** with explicit human acknowledgement. Reasons were
unrelated to the change: `manifest drift: tenant firewall (organ code) — 1
mismatch(es) vs PyAutoMind/repos.yaml`, plus two stale markers (`test run status
unknown (no report.json)`, `release validation stale: source moved since
rehearsal`). No RED reasons. The manifest drift remains outstanding.

## Original prompt

# Sampler CLI output should state actual numbers and real JAX compile status

## Request (verbatim)

> On-the-fly updates every iterations_per_quick_update is the command line output
> when a sampler runs, the actuallyh number should be printed to the CLI should say
> the actual number

> follow up, when JAX compiles a LH function it should say Should say "JAX jit
> compiling likelihood function, could take seconds or minutes..." in output so user
> knows why theres a small wait so a user knows they are waiting

## Problem

Two defects in what the CLI tells a user while a non-linear search runs.

### 1. Literal variable name printed instead of its value

The workspace scripts print a fixed string containing the *name* of the config
knob rather than its value, e.g. `autolens_workspace/scripts/imaging/start_here.py:340`:

```python
print(
    """
    The non-linear search has begun running.

    This Jupyter notebook cell with progress once the search has completed - this could take a few minutes!

    On-the-fly updates every iterations_per_quick_update are printed to the notebook.
    """
)
```

Occurrences: 23 `.py` scripts (autolens_workspace 14+, autogalaxy_workspace 3+,
HowToLens 1), with 23 generated `.ipynb` and 14 `.md` counterparts.

Complication: `search.iterations_per_quick_update` defaults to `1e99`
(`config/general.yaml` `updates:` block) — quick updates are effectively disabled
unless `hpc_mode` is on (250000). It is stored as a `float`
(`autofit/non_linear/search/abstract_search.py:216`). So a naive f-string would
print `1e+99`, which is worse than the placeholder. The message must branch on
whether the value is a real, finite cadence.

### 2. JAX compile message fires before compilation happens

`autofit/non_linear/fitness.py:508 / 528 / 549` log at *wrapper construction*
time, not compile time:

```python
logger.info("JAX: Applying jit to likelihood function -- may take a few seconds.")
func = jax.jit(self.call)
logger.info(f"JAX: jit applied in {time.time() - start} seconds.")
```

`jax.jit(...)` is instantaneous — it only wraps. Actual tracing/lowering/compilation
happens on the first call to the returned function (`fitness.py:310`,
`figure_of_merit = self._call(parameters)`). The user therefore sees "applied in
0.0001 seconds", then sits through an unexplained wait that can run to minutes.

## Desired behaviour

1. The search-start print states the actual iteration cadence, e.g.
   `On-the-fly updates every 250000 iterations are printed to the notebook.`
   When the value is the disabled sentinel (`1e99` / non-finite), say plainly that
   on-the-fly updates are off and name the config knob that enables them.
2. On the first likelihood evaluation under JAX, log
   `JAX jit compiling likelihood function, could take seconds or minutes...`
   before the call, and the true elapsed compile time after it. Same treatment for
   the `vmap` and `grad` variants.

## Scope

- `PyAutoFit` — `autofit/non_linear/fitness.py` (`_jit`, `_vmap`, `_grad` and the
  first-call path). Note `fitness._jit` is also consumed by
  `autofit/non_linear/search/mle/bfgs/search.py:183` (passed to scipy as `fun=`),
  so any wrapper must stay a plain callable. `__getstate__`/`__setstate__`
  (`fitness.py:474-491`) strip and rebuild these attributes — the one-shot flag
  must survive or reset cleanly across pickling.
- `autolens_workspace`, `autogalaxy_workspace`, `HowToLens` — the 23 `.py`
  scripts, then regenerate `.ipynb` and `.md`.

Library change lands first; the workspace print may want a small helper so the
disabled-vs-enabled wording is not duplicated 23 times.

## Verification

- Run a search with `iterations_per_quick_update` set to a real value and confirm
  the printed number matches the config.
- Run with the default `1e99` and confirm the "updates are off" wording.
- Run a JAX-backed fit and confirm the compile message appears *before* the wait
  and the reported elapsed time reflects the real compile, not ~0s.
- Confirm regenerated notebooks/markdown carry the new text (zero unrelated diff).
