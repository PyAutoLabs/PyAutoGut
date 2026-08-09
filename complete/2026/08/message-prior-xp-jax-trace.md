## message-prior-xp-jax-trace
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1459
- completed: 2026-08-09
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1461 (squash-MERGED as fbe9f45deac2f8f4646d61bdf5f4cb75ac950e30)
- summary: made the remaining message and compound-prior array-namespace paths
  JAX-traceable. Beta/Gamma constructors now select JAX broadcasting for traced
  parameters; their log partitions dispatch special functions through SciPy or
  `jax.scipy`; arithmetic and modified priors propagate `xp` recursively; and
  `Log` / `Log10` use the selected backend.
- API impact: `Prior.instance_for_arguments` gained the optional `xp=np` keyword,
  aligning direct priors with `AbstractPriorModel.instance_for_arguments` so
  nested compound expressions can preserve their backend. This is additive and
  defaults to the existing NumPy behaviour; no workspace migration is required.
- root-cause extension: the issue originally named four direct NumPy/SciPy
  leaks, but the exact JIT regression first failed earlier in
  `AbstractMessage.__init__`: Beta/Gamma always used `np.broadcast` even for
  traced parameters. The established `NormalMessage` backend-selection pattern
  closed that constructor boundary before the special-function fixes could run.
- evidence: the exact new tests produced 12 expected failures and 20 passes on
  untouched post-#1460 `main`; all 32 cases passed on the branch with both JAX
  0.7.0 (supported minimum) and 0.10.2. Focused prior/message suites passed 317
  tests; the full local PyAutoFit suite passed 1701 tests with 4 skipped. GitHub
  Docs and Tests both passed on exact head
  `28fe9862d37a40b7c25333d137a106a58db80c82` before the guarded merge.
- scope: six files, including direct scalar/batched NumPy-parity tests for
  Gamma/Beta partitions and direct, child-compound, and nested-modifier tests
  for prior arithmetic. No workspace source changes or remaining follow-up are
  required for this issue.

## Original prompt

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
