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
