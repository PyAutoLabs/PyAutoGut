# Phase 1: fix the pynufft AttributeError breaking all jax_profiling dataset setup

Type: maintenance
Target: autolens_workspace_developer
Repos:
- @autolens_workspace_developer
Difficulty: low
Autonomy: supervised
Priority: normal
Status: issued
Filed: 2026-08-23
Issued: 2026-08-23

Phase 1 of 3. Parent: `pynufft_removal_downstream_residue.md` (full evidence,
provenance and out-of-scope list live there). Phases are independent — no
ordering constraint, no library-first gate, because **no PyAuto\* library source
changes are involved**.

## The break (reproduced 2026-08-23)

`jax_profiling/dataset_setup/interferometer.py`

```
:140        "nufft_pynufft": al.TransformerNUFFTPyNUFFT,
```

```
AttributeError: module 'autolens' has no attribute 'TransformerNUFFTPyNUFFT'
```

`TransformerNUFFTPyNUFFT` was deleted by @PyAutoArray#475 (2026-08-22). The
dict at `:137` is built **eagerly** inside `simulate()` (`:106`), before the key
lookup — so **every** instrument raises, not only the `alma_high_res` config at
`:76` that selects `"nufft_pynufft"`. Confirmed by calling `simulate('sma')`, a
**DFT** dataset, which still fails. All JAX-profiling dataset setup in this repo
is currently broken.

This is the **only** executable reference to the deleted class in any repo.

## Task

Drop the `"nufft_pynufft"` arm of the dict and repoint the `alma_high_res`
config's `transformer_class` to `"nufft"` (`al.TransformerNUFFT`, nufftax-backed).

This is a decision, not a mechanical rename. Both objections in the `:65-69`
comment were checked (2026-08-23):

- *"DFT would need a dense (n_vis x n_real_space) matrix = ~20GB and OOM on a
  15GB laptop"* — **still true**, and it rules DFT out here. 5000 vis x 512x512
  = 1.31e9, far above the ~1e7 `n_vis * n_pix` crossover measured in
  `remove_pynufft_legacy_transformer.md`, where the NUFFT is the only feasible
  path.
- *"nufftax requires Python >= 3.12 (PyAutoGPU venv is 3.10)"* — **obsolete**.
  PyAutoArray, PyAutoLens and PyAutoNerves all declare
  `requires-python = ">=3.12"`, and nufftax 0.6.1 needs only `>=3.11`. A 3.10
  venv cannot run current autolens at all.

Rewrite that comment to record the new rationale rather than deleting it — the
OOM constraint is still the reason this config is not DFT.

## Why it went unnoticed

This repo has **no smoke coverage**, the same root cause recorded in
`draft/maintenance/autolens_workspace_developer/stale_api_rot_audit.md`
(Status: formalised). That prompt's alias-aware scan ran 2026-08-04 and found 56
stale symbols; `TransformerNUFFTPyNUFFT` only became stale on 2026-08-22, so it
is **absent** from that inventory — same repo, same class of rot, different
instance. If a minimal smoke tier is added under that prompt,
`dataset_setup/interferometer.py` is a strong candidate for it.

## Acceptance

- `simulate()` runs for **every** instrument key, not just the changed one — the
  eager dict is exactly why a single-instrument check would miss a regression here.
- The `alma_high_res` path produces a dataset rather than OOMing.
- No executable reference to `TransformerNUFFTPyNUFFT` remains in the repo
  (re-run an alias-aware attribute sweep; do not trust the inventory above as proof).
- The `alma_high_res` rationale comment reflects the decision actually taken.
