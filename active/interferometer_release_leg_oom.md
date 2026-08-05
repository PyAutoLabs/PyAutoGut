# interferometer/start_here.py OOM in nightly release-validation integrate leg

Difficulty: medium
Autonomy: supervised
Priority: high

Filed 2026-07-31 from the phase-4 ship gate of point-source-chi-squared-variants
(#657): Heart RED traced to the nightly Release Integrate run.

**Root cause CONFIRMED 2026-08-05 (see "Diagnosis"). The earlier
NUFFT/transformer hypothesis is WRONG and is retained only as the historical
record at the bottom of this file. Do not start in PyAutoArray.**

## Symptom

Nightly `Release Integrate` run
https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/30607596240
(v2026.7.31.1.dev69201, profile=release) fails in job
`integrate / run_scripts (3.12, autolens, interferometer)` — the release-mode
leg only:

```
scripts/interferometer/start_here.py ...   FAIL (58.8s)
jax.errors.JaxRuntimeError: RESOURCE_EXHAUSTED: Out of memory allocating 85898814480 bytes.
```

The night before (run 30516167217, 2026-07-30) the identically-named
`scripts/interferometer/start_here.py` failed in **both** the autolens and
autogalaxy shards, with the JAX traceback filter eating the real exception.

## Diagnosis (2026-08-05 — confirmed, not hypothesis)

The failure is the **`jax.vmap` batch of the multi-start gradient optimizer**,
not the NUFFT.

`af.MultiStartProdigy`'s `batch_size` defaults to `None`, which evaluates all
`n_starts` in a single `jax.vmap` and materializes the whole batched jvp at
once. Both `start_here.py` files switched to
`af.MultiStartProdigy(n_starts=48)` on 2026-07-29 — autogalaxy_workspace
`255aee4` (19:42), autolens_workspace `fa31bc7` (21:15) — with no `batch_size`.
The very next nightly (07-30) is the first failure. That is the regression
window, and it is a **workspace authoring change, not a library change**.

`autolens_workspace@d7385ff` (2026-07-31 23:23) already fixed the autolens side
with `batch_size=4`, and its commit message records a *verified* reproduction:

> Verified under the release profile env (JAX CPU, x64, TEST_MODE=1,
> SMALL_DATASETS): unchanged script reproduces the OOM at the same
> materialization site; patched script runs end-to-end (exit 0, ~5 min,
> <4 GB peak).

That is why the failure was "not observed on 08-01, 08-03 or 08-04" — it was
fixed, in one of the two workspaces, hours after this prompt was filed. The
prompt was never updated, which is why the 08-04 addendum re-opened it as an
unknown.

Corroborating evidence, all independently checked:

- **Only `start_here.py` uses this search.** An audit of every `search = af.*`
  constructor under `scripts/interferometer/` in both workspaces:
  `start_here.py` is the *only* script using `af.MultiStartProdigy`; all 45
  others use `af.Nautilus`, which has no 48-way vmapped jvp. In the failing run
  every sibling on the same dataset and the same `TransformerNUFFT` passed —
  `fit.py`, `modeling.py`, `likelihood_function.py`, and all seven
  `features/pixelization/*` scripts.
- **The number divides by `n_starts`.** 85,898,814,480 / 48 = 1,789,558,635
  bytes — ~1.79 GB of jvp per start.
- **PyAutoFit already documents this exact failure.**
  `autofit/non_linear/search/mle/multi_start_gradient/search.py:88-102`:
  "`None` (default) evaluates all `n_starts` in a single `jax.vmap` — fastest,
  but it allocates the whole batched jvp at once, which for a memory-heavy
  likelihood (e.g. a pixelized source at 16 starts, ~58 GB in float64) exhausts
  even an 80 GB GPU."
- **The "both workspaces" signal was real but pointed at the wrong shared
  layer.** It is a shared *authoring* event (both scripts inherited the same
  unguarded search default on 07-29), not shared NUFFT code. `chunk_size` and
  the nufftax 0.6.x batching shim are not implicated.

## Scope — three phases

### Phase 1 — close the live exposure (@autogalaxy_workspace)

`autogalaxy_workspace/scripts/interferometer/start_here.py` **is still
unguarded**: `n_starts=48`, no `batch_size`. It is listed in `smoke_tests.txt`.
The 07-31 fix was applied to autolens only. Mirror `batch_size=4` with the same
explanatory comment, and verify under the release profile.

### Phase 2 — stop the diagnosis blindness (@PyAutoHands)

`JAX_TRACEBACK_FILTERING` is set **nowhere** in the organism — not in
PyAutoHeart, not in PyAutoHands, not in any workspace
`config/build/profile_*.yaml` (verified by grep). On 07-30 the filter ate the
real exception and cost a night to identify. Same category as the exit-code
contract fixed in PyAutoBrain#196.

Set it at the single choke point every script run in every workspace and every
profile passes through:
`PyAutoHands/autohands/env_config.py::build_env_for_script`, applied as a base
default *before* `apply_profile` so a profile can still override it.

### Phase 3 — the general fix (@PyAutoFit)

Two workspace scripts are now hand-patched with magic numbers after the fact.
Any user writing `MultiStartProdigy` against a memory-heavy likelihood hits the
same wall with no warning — the search silently attempts an unbounded
allocation and dies inside XLA.

`af.Analysis.print_vram_use(model, batch_size)` already exists
(`autofit/non_linear/analysis/analysis.py:337`) but is the wrong instrument
here on two counts:

1. it profiles `fitness.call` — the **likelihood**, not the `value_and_grad`
   jvp, so it under-reports exactly the allocation that OOMs a gradient
   optimizer;
2. it is manual and no-ops under `skip_fit_output()`.

Make the guard automatic and correct: measure the jvp, and on a projected
over-budget batch either warn with an actionable `batch_size` suggestion or
auto-batch, rather than letting XLA raise `RESOURCE_EXHAUSTED`. Library-source
fix (no autoimmunity — the workspace scripts are documentation).

## Exit criteria

- Release-mode interferometer leg green in the nightly Release Integrate run
  for **both** the autolens and autogalaxy shards.
- A `MultiStartProdigy` run that would exceed memory reports an actionable
  message naming `batch_size`, instead of a raw XLA `RESOURCE_EXHAUSTED`.
- A future JAX failure in the release harness shows its real traceback.

## Historical record — the superseded hypothesis (2026-07-31 / 2026-08-04)

Retained so the reasoning trail is auditable. The 08-04 addendum inferred from
"both workspaces, identically-named file" that the cause must be at or below
the shared layer, and recommended starting at PyAutoArray's NUFFT/transformer.
The inference that it is **not** lens-specific was correct; the conclusion that
the shared layer was the *transformer* was not. The original triage notes also
flagged a `TestPyPI install failed after 30 attempts` retry in the same job's
`verify_install_release` step — unrelated flake, confirmed not part of this bug.
