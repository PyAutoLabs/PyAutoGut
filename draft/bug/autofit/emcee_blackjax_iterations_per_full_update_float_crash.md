# Emcee and BlackJAX NUTS crash on a real iterations_per_full_update cadence

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: safe
Priority: high
Status: draft

## The bug

The same defect class fixed for the MultiStart gradient search in
[PyAutoFit#1420 / PR#1421](https://github.com/PyAutoLabs/PyAutoFit/pull/1421),
still live in two more searches. `AbstractSearch.__init__` coerces
`iterations_per_full_update` to **float** (`abstract_search.py:219`); both
searches then feed that float straight into an iteration count that requires an
`int`. It is latent for everyone because the packaged config default is `1e99`,
so the `min`/comparison always selects the int operand — only a user-supplied
cadence *below* the remaining budget reaches the crash.

Both were **verified empirically**, not inferred from the call shape:

- `autofit/non_linear/search/mcmc/emcee/search.py:203-206` — the float reaches
  `emcee.EnsembleSampler.sample(iterations=...)`, whose body does
  `range(iterations)` with no cast of its own. Confirmed:
  `inspect.getsource(emcee.EnsembleSampler.sample)` contains `range(iterations)`
  and no `int(iterations)`.
- `autofit/non_linear/search/mcmc/blackjax/nuts/search.py:291` —
  `chunk_n = min(self.iterations_per_full_update, iterations_remaining)` is a
  float, and line 294 passes it to `jax.random.split`. Confirmed:
  `jax.random.split(jax.random.PRNGKey(0), 50.0)` raises
  `TypeError: 'float' object cannot be interpreted as an integer`.

Reproducer for the emcee leg: `af.Emcee(nsteps=100, iterations_per_full_update=50)`.

## Explicitly NOT affected (checked, do not "fix" these)

An earlier pass claimed five affected searches by reading the call shape. Three
of those are fine — verify before touching them:

- `mcmc/zeus/search.py:239-242` — **safe**: zeus casts internally
  (`self.nsteps = int(iterations)` in `EnsembleSampler`).
- `mle/bfgs/search.py:171` — tolerated: the value becomes SciPy's `maxiter`,
  used in comparisons only.
- `nest/dynesty/search/abstract.py:365` and `nest/nautilus/search.py:477` —
  tolerated: returned as comparison limits, never as a loop count.

## Fix

Prefer **fixing the producer** this time. The rationale used in PR#1421 for
casting at the consumer — "the shared `float()` coercion exists so the inf-like
`1e99` default is representable" — is wrong: Python ints represent `1e99`
exactly fine. The coercion at `abstract_search.py:219-220` (and the HPC branch at
`:240-241`) protects nothing and is the source of the whole defect class.

Assess whether `iterations_per_full_update` / `iterations_per_quick_update` can
simply be stored as `int`. Check every consumer first —
`updater.py:183` does arithmetic with it, `fitness.py` compares
`quick_update_count >=` it, and `test_autofit/non_linear/search/test_updater.py:17`
passes `1.0` while `test_dict.py:26` asserts the serialised value `1e99`. If a
consumer genuinely needs the float, say which and why, and fall back to casting
at the two broken consumers.

Add a unit test per fixed search that a cadence below the budget produces an
`int` iteration count (NumPy-only — library unit tests stay JAX-free; for the
BlackJAX leg assert the chunk-size computation, not a live NUTS run).

Reuse the validation idiom from PR#1421 rather than clamping: a cadence below 1
or a fractional one should raise a `ValueError` naming the value, never be
silently rounded into something plausible.
