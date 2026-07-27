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
