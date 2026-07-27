## Shipped

- PR https://github.com/PyAutoLabs/PyAutoFit/pull/1423 **merged** as `c042d72`
  (2026-07-27, CI green on Docs + both Tests matrix legs); issue
  https://github.com/PyAutoLabs/PyAutoFit/issues/1422 closed.
- **Five** bugs fixed, not the three filed — the PR's own adversarial review
  found two more.

## What shipped

**Part 1 — Emcee and BlackJAX NUTS crashed on a real cadence**, the same defect
PR#1421 fixed for MultiStart. `emcee`'s `sample()` does `range(iterations)` with
no cast; `jax.random.split` rejects a float.

**The plan's producer fix was rejected after auditing the consumers.** The issue
said to fix `abstract_search.py:219`'s `float()` coercion because Python ints
hold `1e99` fine. True, but `int(1e99)` is a **99-digit integer**, and it would
land in every saved `search.json` in place of a readable inf-like sentinel. The
conversion moved *up* instead, into one shared validated
`AbstractSearch._steps_until_full_update`, now used by all five chunked searches
(MultiStart, Emcee, Zeus, BFGS, BlackJAX NUTS). Deriving it once beats
re-deriving it per search — re-deriving it is how this class shipped three times.
`AbstractMultiStartGradient._steps_in_chunk` (PR#1421) folded into it.

**Part 2 — MultiStart ran the expensive final pass twice.** `_fit` emitted
`during_analysis=False` on its last chunk while `start_resume_fit` performs the
final update unconditionally anyway.

**Part 3 — a resumed run inherited the previous run's `stop_reason`**, so raising
`n_steps` to extend a finished search left a stale `"max_steps"` in every
intermediate checkpoint and a still-running search reported itself finished.
Cleared on entry, `"converged"` preserved (the loop guard uses it to refuse
resuming a converged search).

## The two extra bugs, and the fix that was cosmetic

Two adversarial Codex `gpt-5.6-sol` passes, both of which changed the code:

- **Zeus was NOT safe — just not crashing.** Cleared on #1420 because it casts
  internally (`self.nsteps = int(iterations)`), but PyAutoFit adds the *uncast*
  float to its own `total_iterations` (`zeus/search.py:261`): `nsteps=100,
  iterations_per_full_update=50.9` draws 50 then 49 — 99 samples — while the
  bookkeeping reaches 100. **Safe-from-crashing is not safe.** BFGS also bypassed
  the validation the helper advertises for `maxiter`.
- **The first Part 2 fix was cosmetic.** Flipping `during_analysis` to `True`
  deduplicates nothing: `SearchUpdater.update` rebuilds the samples, recomputes
  the summary and re-runs likelihood profiling on *every* call regardless of the
  flag, and the visualize gate keys off `paths.is_complete`, which is not written
  until after `_fit` returns. The in-loop update had to be **skipped outright**
  at a terminal boundary.
- **The falsy-cadence branch reintroduced the silent behaviour the validation
  existed to remove**: a stored `0` meant "never checkpoint", reachable through
  the HPC override (which assigns the config value with no `or` fallback).

Pass 2 verified the production code **CLEAN by running real JAX fits**: a
one-chunk run produces one checkpoint, **zero** in-loop updates and exactly one
outer `during_analysis=False` update; a two-chunk run produces `[True, False]`
and two checkpoints.

Pass 2's remaining findings were about **test strength**: source-level string
assertions can pass while a semantically-equivalent regression is reintroduced.
Fixed by extracting the two rules into named seams (`_is_final_boundary`,
`_stop_reason_on_resume`) and pinning them by exhaustive parametrised behaviour,
leaving the source assertion as a thin wiring guard.

Final: **1557 passed, 1 skipped**.

## Residual, stated rather than papered over

The cross-search wiring guard cannot prove a search *uses* the value the helper
returns — a contrived regression that calls it and discards the result would pass.
Closing that needs the `_fit` bodies (jax/optax/emcee), out of scope for the
NumPy-only library suite; covered where those bodies actually run, in the
workspace test repos.

## Lessons

- **Reading the call shape is not verification.** Probe the callee. The original
  five-sibling claim was wrong in both directions: three of the five were fine,
  and one of the "fine" ones (zeus) had a different, real bug.
- **A flag that names a phase does not necessarily gate the work of that phase.**
  `during_analysis` reads like it gates the final pass; it gates almost none of it.
- Both adversarial review passes changed the code, and in both cases the first
  fix was wrong in a way the test suite alone would not have caught.

## Original prompt

# Three MultiStart / cadence follow-ups from the PR#1421 review

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: medium
Autonomy: safe
Priority: high
Status: draft

Combines three drafts filed on 2026-07-27 (PyAutoMind `8a3a4d1`) into one task,
at the human's explicit request — one issue, one branch, one PR. They share a
subsystem (`autofit/non_linear/search/`), a review provenance (the adversarial
Codex `gpt-5.6-sol` pass over
[PR#1421](https://github.com/PyAutoLabs/PyAutoFit/pull/1421), merged `e217292`)
and a test file, so the usual one-prompt-one-PR split would cost three round
trips for three small, independently-verified fixes. The superseded drafts are
`emcee_blackjax_iterations_per_full_update_float_crash.md`,
`multistart_duplicate_final_perform_update.md` and
`multistart_stale_stop_reason_on_resume.md`.

Each part below is independently shippable — if one turns out to be wrong or
larger than it looks, drop it and ship the rest rather than blocking the PR.

---

## Part 1 — Emcee and BlackJAX NUTS crash on a real cadence (highest value)

The defect class fixed for MultiStart in PR#1421, still live in two more
searches. `AbstractSearch.__init__` coerces `iterations_per_full_update` to
**float** (`abstract_search.py:219`); both searches feed that float straight into
something needing an `int`. Latent for everyone because the packaged default is
`1e99`, so the `min`/comparison always picks the int operand — only a cadence
*below* the remaining budget reaches the crash.

Both **verified empirically**, not inferred from the call shape:

- `mcmc/emcee/search.py:203-206` — the float reaches
  `emcee.EnsembleSampler.sample(iterations=...)`, whose body does
  `range(iterations)` with no cast.
  (`inspect.getsource` contains `range(iterations)` and no `int(iterations)`.)
- `mcmc/blackjax/nuts/search.py:291` —
  `chunk_n = min(self.iterations_per_full_update, iterations_remaining)` is a
  float, passed at line 294 to `jax.random.split`, which raises
  `TypeError: 'float' object cannot be interpreted as an integer` on `50.0`.

Reproducer for the emcee leg: `af.Emcee(nsteps=100, iterations_per_full_update=50)`.

### Explicitly NOT affected — verify before touching, do not "fix" these

An earlier pass claimed five affected searches by reading the call shape. Three
are fine:

- `mcmc/zeus/search.py:239-242` — **safe**: zeus casts internally
  (`self.nsteps = int(iterations)`).
- `mle/bfgs/search.py:171` — tolerated: becomes SciPy's `maxiter`, comparisons only.
- `nest/dynesty/search/abstract.py:365`, `nest/nautilus/search.py:477` —
  tolerated: returned as comparison limits, never a loop count.

### Preferred fix: the producer, not the consumer

PR#1421's rationale for casting at the consumer — "the shared `float()` coercion
exists so the inf-like `1e99` default is representable" — **is wrong**: Python
ints represent `1e99` fine. The coercion at `abstract_search.py:219-220` (and the
HPC branch at `:240-241`) protects nothing and is the source of the whole class.

Assess storing `iterations_per_full_update` / `iterations_per_quick_update` as
`int`. Audit every consumer first: `updater.py:183` does arithmetic with it,
`fitness.py:400` compares `quick_update_count >=` it,
`test_autofit/non_linear/search/test_updater.py:17` passes `1.0`, and
`test_autofit/non_linear/test_dict.py:26` asserts the serialised `1e99`. If a
consumer genuinely needs a float, say which and why, and fall back to casting at
the two broken consumers.

Reuse PR#1421's validation idiom rather than clamping: a cadence below 1 or a
fractional one raises a `ValueError` naming the value, never silently rounded.

---

## Part 2 — MultiStart runs the expensive final `perform_update` twice

`AbstractMultiStartGradient._fit` performs its own final update with
`during_analysis=False` (`multi_start_gradient/search.py:430-439`):

```python
is_final = converged or total_steps >= self.n_steps
self.perform_update(..., during_analysis=not is_final, ...)
```

`AbstractSearch.start_resume_fit` then **unconditionally** performs the same
final update right after `_fit` returns (`abstract_search.py:704-710`,
`during_analysis=False`). Final sample output, latent computation, visualization
and profiling therefore all run twice at the end of every MultiStart run — on a
pixelized or GPU fit, a large and entirely wasted cost.

**This is MultiStart being an outlier, not the framework's pattern.** Every other
search passes `during_analysis=True` unconditionally inside `_fit`, leaving the
single `False` call to `start_resume_fit`: `mcmc/emcee/search.py:238`,
`mle/bfgs/search.py:219`, `nest/nautilus/search.py:438`.

Fix: pass `during_analysis=True` unconditionally in the MultiStart step-loop
update and delete the `is_final` computation — unless `_fit` genuinely needs a
final-flavoured update before returning, in which case say why and fix the
duplication at the other end.

Check the early-stopping path: when the search converges, the in-loop update
carries `converged`/`stop_reason` into `samples_info`. Confirm that still reaches
the final samples via the `search_internal` dict `_fit` returns (it should —
`start_resume_fit`'s update is built from that same dict).

Regression test: count `perform_update` calls with `during_analysis=False` across
one search. NumPy-only — stub/monkeypatch rather than running a JAX fit.

---

## Part 3 — Stale `stop_reason` when a finished search is resumed with a larger `n_steps`

`_fit` restores `stop_reason` from the loaded `search_internal` on the resume
path, and only reassigns it inside the loop when one of two conditions fires
(`multi_start_gradient/search.py:413-416`):

```python
if converged:
    stop_reason = "converged"
elif total_steps >= self.n_steps:
    stop_reason = "max_steps"
```

Resume a search that finished with `stop_reason="max_steps"` using a larger
`n_steps` (the documented way to extend a budget). The `while` guard lets the
loop continue (`stop_reason != "converged"`), but until the *new* ceiling is
reached neither branch fires — so the restored `"max_steps"` survives into every
intermediate checkpoint. A search that is actively running reports
`samples_info["stop_reason"] == "max_steps"`, so anything reading results mid-run
(aggregator, results inspector, monitoring) sees a finished-looking search that
is not finished. The final checkpoint self-corrects, so this is a mid-run
reporting defect, not a wrong final answer — hence lowest priority of the three.

Fix: clear `stop_reason` when entering the loop on a resume that will run further
steps; any real stop reason is re-derived inside the loop. Guard the interaction
with the `converged` short-circuit — a genuinely converged search must still
refuse to resume into more steps, so the reset must not clear `"converged"`.

Test: NumPy-only over the stop-reason state machine — build the `search_internal`
dict directly and assert `stop_reason` / `converged` via
`samples_via_internal_from`, rather than running a JAX fit.

---

## Constraints

- Library unit tests stay **NumPy-only** — `_fit` needs jax + optax + a
  JAX-traceable `Analysis` and cannot be driven from the suite. Test the
  extracted seams, and add a wiring guard where a test would otherwise still
  pass if the call site regressed (the trap PR#1421 hit).
- Full suite green before ship: `python -m pytest test_autofit/`.
- Independent adversarial review with Codex `gpt-5.6-sol` at the end, per the
  human's instruction, before the ship gate's review leg is settled.
