# Make remaining message and compound-prior xp paths JAX-traceable

Type: bug
Target: PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Existing issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1459

## Problem

The prior/message backend audit performed while shipping PyAutoFit#1460
reproduced four additional `jax.jit` failures on current `main`. Each affected
method accepts an `xp` argument but calls NumPy or SciPy directly, coercing a
traced value through `__array__` and raising
`jax.errors.TracerArrayConversionError`:

- `GammaMessage.log_partition(xp=jnp)` uses `scipy.special.gammaln` and
  `np.log`.
- `BetaMessage.log_partition(xp=jnp)` uses `scipy.special.betaln`.
- compound-prior `Log._instance_for_arguments(..., xp=jnp)` calls `np.log`.
- compound-prior `Log10._instance_for_arguments(..., xp=jnp)` calls
  `np.log10`.

## Requested change

- Preserve the SciPy implementation on the NumPy path and use JAX-compatible
  special functions for Gamma/Beta log partitions when `xp` is JAX.
- Use `xp.log` and `xp.log10` in the compound-prior modifiers.
- Check whether compound priors must forward `xp` recursively to child prior
  models, and cover nested compound expressions through the real
  `instance_for_arguments(..., xp=jnp)` API.
- Add scalar and batched `jax.jit` regression tests with NumPy/SciPy numerical
  parity and unchanged statistical semantics.
- Run focused prior/message tests and the full PyAutoFit suite.

This is a separate follow-up to PyAutoFit#1458/#1460 so the completed fixed-array
repair remains focused.

## Implementation progress (2026-08-09)

- Draft PR: https://github.com/PyAutoLabs/PyAutoFit/pull/1461
- Root-cause extension: traced Beta/Gamma construction failed first in
  `AbstractMessage.__init__` because both classes always selected NumPy
  broadcasting. They now use the same backend-selection pattern as
  `NormalMessage` before dispatching their log-partition special functions.
- Recursive prior fix: direct priors accept the optional `xp` keyword and
  arithmetic / modified priors propagate it to nested children; `Log` and
  `Log10` use the selected backend.
- Verification: the new exact tests give 12 expected failures on untouched
  post-#1460 `main` and all 32 cases pass on both JAX 0.7.0 and 0.10.2. Focused
  prior/message suites: 317 passed. Full PyAutoFit suite: 1701 passed, 4
  skipped.
