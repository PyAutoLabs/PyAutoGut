# nufftax batched nufft2d2 vjp crashes interferometer gradients (nightly release blocker)

Type: bug
Target: autoarray (fix may land in the external `nufftax` package)
Repos:
- PyAutoArray
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft

## Symptom

`nufftax/transforms/autodiff.py:676` `_nufft2d2_bwd` does `n2, n1 = f.shape`, but
`autoarray/operators/transformer.py:818` `transform_mapping_matrix` feeds a batched
(stacked-column) matrix through `nufft2d2`. Any *gradient* through an interferometer
inversion therefore dies with `ValueError: too many values to unpack (expected 2)`.

Observed 2026-07-30 in Heart workspace-validation run
`PyAutoLabs/PyAutoHeart` cloud#30516167217 (mode=release): both
`autogalaxy/scripts/interferometer/start_here.py` and
`autolens/scripts/interferometer/start_here.py` crash in
`MultiStartProdigy._broad_starts → jax.value_and_grad` at wheels `2026.7.29.2.dev*`.
**This failed the nightly's Stage 3 on 4 of the 5 nights up to 2026-07-30** — it is the
actual current release blocker behind Heart's "workspace validation not passing" YELLOW.

## Scope

Fix the backward pass for batched inputs — either teach `_nufft2d2_bwd` to handle a
leading batch dimension, or make `transform_mapping_matrix` map the transform
per-column so the vjp only ever sees 2-D `f`. Add a gradient regression test
(numpy-only in library unit tests per convention; JAX validation via vmap harness).
Forward-only paths are unaffected — only `value_and_grad` through
`operated_mapping_matrix` breaks, which is why non-gradient searches pass.

## Evidence

- Failing run: https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/30516167217
- Full tracebacks in its `workspace-validation-report` artifact (`report.json`).
