jax 0.11 changed `jnp.broadcast_arrays` from returning a `list` to a `tuple`
(NumPy 2 alignment), so `MessageInterface.shape`'s `isinstance(..., list)` JAX
branch stopped matching and every jnp-backed message construction died with
`AttributeError: 'tuple' object has no attribute 'shape'` — the regression that
held the autonerves `jax`/`jaxlib` cap at `<0.11.0` (reverted widen, PyAutoNerves#150).

Shipped as two PRs, merged in library-first order on 2026-08-22:

- **PyAutoFit#1513** — `shape` returns the real broadcast shape read off the
  container's first element (list and tuple forms both); `size`/`ndim` derive
  from it instead of attribute-accessing the container. New
  `test_message_shape_and_logpdf_match_numpy` asserts NumPy/JAX parity of
  shape/size/ndim and batched logpdf over Normal/Beta/Gamma; mutation-checked
  (fails 6 ways against the old sentinel on jax 0.10 alone).
- **PyAutoNerves#152** — cap widened to `<0.12.0`; the "Cap stays <0.11"
  comment replaced with the effective-floor note (jax 0.11 ⇒ numpy>=2.1,
  scipy>=1.15).

## Key findings / traps

- **The minimal fix was the wrong fix.** The obvious `isinstance(..., (list,
  tuple))` widen preserved the `()` shape sentinel — a live silent bug on jax
  0.10: batched JAX `logpdf` returned an (n, n) matrix of wrong values via the
  `shape[1:] == self.shape` branch, and `size`/`ndim` raised for any JAX-backed
  message. There was no behaviour to preserve: on 0.11 the old paths raised, on
  0.10 they were wrong — so the semantic fix carried no compat risk.
- **The breakage surface was wider than the failing tests.** All four failures
  were beta/gamma log-partition jit tests, but any jnp-backed message
  construction (Normal included, outside jit too) raised on 0.11 —
  `test_jax_trace.py` is the *only* coverage constructing jnp-backed messages;
  the workspace `jax_assertions` scripts never see them.
- **Downstream CI cannot pre-verify a cap widen.** PyAutoGalaxy/PyAutoLens CI
  (PyAutoHeart `lib-tests.yml`) resolves jax from the autonerves cap, so their
  green CI before the widen only exercises 0.10 — "their CI must be green
  first" is vacuous. Gate used instead: forced `jax==0.11.1` installs against
  the fix branch (`test_autogalaxy` 1103 passed, `test_autolens` 532 passed,
  identical on 0.10.2/0.11.1). The reusable workflow's matching-branch checkout
  is the CI-native alternative: same-named branches in Fit and Nerves made
  PyAutoFit#1513's own CI run under 0.11 pre-merge.
- **`dir()`-diff audits miss behaviour changes inside unchanged signatures.**
  The 0.11 changelog also carries `jnp.empty`/`empty_like` now returning
  uninitialized memory, the `take_along_axis` `wrap_negative_indices` default
  flip, and the `jnp.ogrid` container change — all verified no-op for this
  stack, none findable by the public-API diff. Future cap-widen audits should
  include a changelog pass.
- **Evidence-table correction:** `multi_start_gradient_auto_convergence.py`
  (reported failing in all cells) passes in a fresh container on both jax
  versions — environment-sensitive, not broken on `main`. Only
  `priors_xp_dispatch.py` fails deterministically (float32 tolerance,
  rtol 1.5e-7 vs 1e-7), identical in every cell — pre-existing, split out.

## Verification

Full matrix in PyAutoFit#1510: `test_autofit` 2030 passed on jax 0.10.2 and
0.11.1 (unfixed main: 2024 / 4-failed); `jax_assertions` 9/10 in all four
version-by-fix cells; `test_autonerves` 157, `test_autogalaxy` 1103,
`test_autolens` 532 passed on both versions. Adjacent finding left for its own
prompt: message `xp` dispatch keys on the *first* parameter's type only, so
`NormalMessage(1.0, jnp.array(...))` silently converts to the NumPy backend.

## Original prompt

# jax 0.11 breaks beta/gamma message log_partition under jit ('tuple' object has no attribute 'shape')

Type: bug
Target: PyAutoFit
Repos:
- PyAutoFit
- PyAutoNerves
Difficulty: small
Autonomy: supervised
Priority: medium
Status: draft

Found during the JAX-default-dependency arc (PyAutoLens#702): widening the jax
cap in autonerves from `<0.11.0` to `<0.12.0` let CI resolve jax/jaxlib 0.11.1,
which fails five autofit tests on both Python legs
(run 32285606183; local jax 0.10.2 passes):

- `test_autofit/graphical/functionality/test_messages.py::test_beta`
- `test_autofit/messages/test_jax_trace.py::test_message_log_partition_is_jittable_and_matches_numpy[{scalar,batched}-{gamma,beta}]`

all with `AttributeError: 'tuple' object has no attribute 'shape'`.

The cap widen was reverted in PyAutoNerves#150 (commit 848a254) with a comment
pointing here — the promotion shipped with the cap still `<0.11.0`.

Task: find what jax 0.11 changed in the beta/gamma `log_partition` trace path
(likely a `jax.scipy.special` return-shape/tuple change or a shape-polymorphism
change under jit), fix autofit's message code to be compatible with both 0.10
and 0.11, then widen the autonerves cap to `<0.12.0` in the same arc
(@PyAutoNerves pyproject — remove the "Cap stays <0.11" comment). The cap
widen matters because jax is now a base dependency and the `<0.11` cap
conflicts with e.g. Colab's preinstalled jax.

Note (2026-08-19, later same day): the no-jax CI leg exposed that
beta/gamma/normal message `xp` dispatch misrouted NumPy scalars
(np.int64/np.float64 are not int/float under NumPy 2) into the JAX branch —
fixed on the same branch (PyAutoFit 19c679583, np.generic added). `test_beta`
was one of the five jax-0.11 failures, so re-test under 0.11 AFTER that fix
lands: the remaining failures are probably only the deliberate jax-trace
tests (`test_jax_trace.py`), which narrows the compat surface.
