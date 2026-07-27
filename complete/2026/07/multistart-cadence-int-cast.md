## Shipped

- PR https://github.com/PyAutoLabs/PyAutoFit/pull/1421 **merged** as `e217292`
  (2026-07-27, CI green on Docs + both Tests matrix legs); issue
  https://github.com/PyAutoLabs/PyAutoFit/issues/1420 closed.
- **The fix:** `AbstractMultiStartGradient._steps_in_chunk` casts the per-chunk
  step count to `int` at the consumer. `AbstractSearch.__init__` stores
  `iterations_per_full_update` as a float (`abstract_search.py:219`), and the
  crash was latent for everyone because `min(1e99, steps_remaining)` returns the
  `int` operand — only a real cadence *below* the remaining budget reached
  `range` and raised `TypeError: 'float' object cannot be interpreted as an
  integer`. Killed RAL chain jobs 331182–331190 in the wsdev#117 campaign.
- The helper exists so the test can be NumPy-only: `_fit` needs jax + optax + a
  JAX-traceable `Analysis`, so the library suite cannot drive it.

## What review changed — the interesting part

Three commits, two of them from review:

1. `int(min(...))` at the consumer.
2. **Self-review caught a defect in commit 1.** `int` truncates towards zero, so
   a fractional cadence below 1 gives `range(0)`: no step runs, `total_steps`
   never advances, and the enclosing `while` spins forever re-running
   `perform_update`. Commit 1 alone traded a loud crash for a silent hang that on
   a cluster burns the whole allocation. Floored the chunk at 1.
3. **An independent adversarial review (Codex `gpt-5.6-sol`, xhigh) replaced that
   floor.** `max(1, ...)` silently laundered `-5`, `0.5` and `50.9` into a
   plausible-looking cadence — the silent-guard pattern this workspace removes.
   And "the chunk can never overshoot `steps_remaining`" held *only* because
   `n_steps` is an integer; the loop guard proves `steps_remaining > 0`, not
   `>= 1`, so a float `n_steps=2.5` leaves a 0.5 remainder that truncates to a
   zero-length chunk. Both the cadence and `n_steps` are now validated as whole
   numbers >= 1, raising a `ValueError` that names the bad value; validating
   `n_steps` is what let the floor be removed rather than kept beside the check.

Final: **1541 passed, 1 skipped**. Smoke: no regression (50 pass / 7 fail, all 7
reproduce identically on `main` — the `jax_likelihood` parity scripts, which the
smoke profile runs under `PYAUTO_DISABLE_JAX=1`).

## Corrections the adversarial review forced

- **My sibling list was wrong.** I claimed five searches shared the latent
  defect, derived from reading the call shape. Probing the actual callees gives
  **two**: `mcmc/emcee/search.py:206` (`EnsembleSampler.sample` does
  `range(iterations)`, no cast) and `mcmc/blackjax/nuts/search.py:291`
  (`jax.random.split(key, 50.0)` raises the same `TypeError`). **zeus is safe** —
  it casts internally via `self.nsteps = int(iterations)`; `bfgs`, `dynesty` and
  `nautilus` only use the value in comparisons or arithmetic. Lesson: reading the
  call shape is not verification, probe the third-party callee.
- **My rationale for not touching `abstract_search.py:219` was wrong.** I argued
  the shared `float()` coercion is load-bearing because `1e99` must be
  representable. Python ints represent `1e99` fine. The coercion protects nothing
  and *is* the defect class. Casting at the consumer was still right for a
  hotfix; "fix the producer" is the right framing for the follow-up.
- My tests initially characterised the helper without pinning that `_fit` calls
  it — all of them would have passed if the call site regressed. Added a
  source-level wiring guard.

## Follow-ups filed (PyAutoMind `8a3a4d1`)

Three drafts under `draft/bug/autofit/`, taken up immediately afterwards as one
combined task: the emcee/BlackJAX sibling crashes; the duplicate final
`perform_update` (MultiStart passes `during_analysis=not is_final` at
`search.py:432` while `emcee:238` / `bfgs:219` / `nautilus:438` all pass `True`
unconditionally, so the expensive final update runs twice); and the stale
`stop_reason` when a finished search is resumed with a larger `n_steps`.

Also cleared on merge: the post-construction int overwrite in
`autolens_workspace_developer/searches_minimal/pix_prodigy.py` (branch
`feature/pix-prodigy-cpu`) is now dead — noted on wsdev#117.

## Process notes

- Effective autonomy was **`supervised`**, not the prompt header's `safe`:
  `AUTONOMY.md` caps work-type `bug` at `supervised`, so `--auto` parked at ship
  sign-off rather than opening the PR unattended.
- Start was blocked by a **stale worktree claim** on PyAutoFit from the completed
  `testmode-env-drift` task (both its PRs merged, its issue closed, post-merge
  cleanup never run). Released first, in `3a99904`.
- The parallel smoke runner produced **five false failures** from contention over
  shared `output/`/`dataset/` state; all five pass sequentially on the branch and
  match `main`. Never call a parallel-sweep failure a regression without a
  sequential baseline on both sides.

## Original prompt

# MultiStart gradient step loop crashes when iterations_per_full_update < remaining steps

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: safe
Priority: high
Status: draft

## The bug (hit live on RAL, 2026-07-27, wsdev#117 campaign)

`abstract_search.py:219` unconditionally coerces `iterations_per_full_update`
to **float** (`float(iterations_per_full_update or conf...)`). The multi-start
gradient `_fit` (`autofit/non_linear/search/mle/multi_start_gradient/search.py:284`)
then computes

```python
iterations = min(self.iterations_per_full_update or self.n_steps, steps_remaining)
...
for _ in range(iterations):   # line 298
```

`range(float)` → `TypeError: 'float' object cannot be interpreted as an
integer` — but **only when the cadence is below the remaining budget**, because
`min(float, int)` returns the int operand otherwise. The config default is huge,
so every existing run took the `steps_remaining` branch and the crash never
fired; any user who passes a real checkpoint cadence (e.g.
`iterations_per_full_update=50` with `n_steps=3000`) crashes on step-loop entry.
Six RAL chain jobs (331182-331190) died on it back-to-back.

Evidence: `/mnt/ral/jnightin/pixgrad_logs/pix_prod_*-33118[5-9].err`; workspace
hotfix (post-construction int overwrite) in
`autolens_workspace_developer/searches_minimal/pix_prodigy.py` (branch
`feature/pix-prodigy-cpu`) — remove it when this ships.

## Fix

`iterations = int(min(...))` in `_fit` (the float coercion in abstract_search
serves inf-like config values and is shared by other searches — casting at the
consumer is the minimal, non-regressing change). Add a unit test that runs a
MultiStart search with `iterations_per_full_update` smaller than `n_steps`
(numpy objective — library unit tests stay JAX-free) and asserts the step loop
executes + checkpoints.
