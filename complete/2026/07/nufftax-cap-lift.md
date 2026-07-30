Lifted the nufftax cap and rank-guarded its vmap batching, fixing the nightly
release blocker (Stage 3 failed 4 of 5 nights to 2026-07-30).

- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/424 (auto-closed by the PR)
- prs: PyAutoArray#425 (`6b6463fad`), PyAutoHeart#118 (`971328955`) — both merged
  unchanged (merge trees byte-identical to the reviewed heads)
- trigger: the 2026-07-29 19:42 workspace commits made MultiStartProdigy the
  `interferometer/start_here.py` default — the first CI exercise of a gradient
  through `TransformerNUFFT`; `transformer.py` itself was unchanged since the
  green rehearsal.
- TWO stacked bugs, both external (nufftax):
  1. 0.4.0 `_nufft2d2_bwd` assumed 2-D `f` → any batched-mapping-matrix gradient
     crashed ("expected 2"). Fixed by lifting `nufftax>=0.4.0,<0.5.0` →
     `>=0.6.1,<0.7.0` (pyproject main + dev extras; the old cap only existed for
     the Python 3.11 floor). Forward transform verified bit-identical
     0.4.0↔0.6.1 at eps=1e-12 (2-D + batched, x64) — pinned baselines safe.
  2. 0.6.x's batching fast path re-binds primitives with NO rank guard, so
     nested batching (MultiStartProdigy's `jax.vmap(jax.value_and_grad(...))`
     over the already-batched matrix) still crashed ("expected 3"). Fixed by
     `_patch_nufftax_batchers()` in `autoarray/operators/transformer.py`: a
     table-driven rank-guarded batcher for all nine primitives (within native
     rank bind as before; beyond it collapse stacked batch axes into the impl's
     one native axis and unflatten). Applied only for nufftax 0.6.x; DELETE when
     fixed upstream (GragasLab/nufftax — no fix on HEAD; upstream filing left
     for human authorization).
- evidence: `vmap(value_and_grad)` matches a per-item loop exactly (jit(vmap)
  ~1e-12); the failing script completes end-to-end (exit 0) on the branch
  autoarray; full suite 929 passed; PyAutoHeart#118 lifts the three
  workspace-validation install pins + stale 0.4.x comment.
- trap: a bare `PYTHONPATH=<dir>` in a verification command replaces the
  profile's source-checkout chain → false `No module named 'autonerves'`;
  prepend `:$PYTHONPATH` and assert the intended `__file__` won.
- remaining known Stage 3 failure: `autolens/scripts/group/start_here.py`
  1800 s timeout (separate Mind prompt).

## Original prompt

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
