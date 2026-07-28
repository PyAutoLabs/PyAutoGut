# 5 jax_likelihood smoke scripts fail: constants are right, the dataset shrank

Type: bug
Target: workspaces
Repos:
- @autolens_workspace_test
Difficulty: small
Autonomy: supervised
Priority: high
Status: draft

## Original request (verbatim)

> ok do deeper research on the 5 stale, we either need to justify changing them or
> know why they changed and go from there

## Verdict

**Do NOT change the hardcoded likelihood constants. They are correct.** The likelihood
never moved; the *dataset* did.

## The five failing scripts

All in `autolens_workspace_test`, all in the smoke set, all failing on `main`:

- `scripts/imaging/jax_likelihood/lp.py`
- `scripts/imaging/jax_likelihood/rectangular.py`
- `scripts/imaging/jax_likelihood/mge.py`
- `scripts/interferometer/jax_likelihood/rectangular.py`
- `scripts/multi/jax_likelihood/mge.py`

## Evidence (2026-07-28, all libraries at origin/main)

| Script | under `PYAUTO_SMALL_DATASETS=1` | full size, dataset deleted first |
|---|---|---|
| imaging/lp | FAIL | **PASS** |
| imaging/rectangular | FAIL | **PASS** |
| imaging/mge | FAIL | **PASS** |
| interferometer/rectangular | FAIL | **PASS** |
| multi/mge | FAIL | **PASS** |

`lp.py` at full size returns `-1.34797842e+09` against its constant `-1.34797827e+09` —
agreement to **1.1e-7**, far inside `rtol=1e-4`.

The JAX/NumPy parity assertion that follows the constant check (and never runs, because the
script dies on the constant first) passes exactly:

```
NumPy fit.log_likelihood: -352316.6109446431
JIT   fit.log_likelihood: -352316.61094464315
PASS: jit(fit_from) round-trip matches NumPy scalar.
```

So the JAX path is correct. Only the constant check fails, and only on small data.

## Root cause

`d75abd6` (2026-07-24, autolens_workspace_test#213) — *"simulator auto-bootstrap:
regenerable datasets leave the tip"* — `git rm`'d the committed FITS:

- `dataset/imaging/jax_test`: 6 tracked files before, **0** now
- `dataset/multi/lens_sersic`: 8 tracked files before, **0** now

Datasets are now regenerated on demand. But `config/build/profile_smoke.yaml` sets
`PYAUTO_SMALL_DATASETS: "1"` (line 16), which caps regeneration to **16×16**. The committed
originals were **150×150** (multi) and ~**180×180** (jax_test). The constants were calibrated
in April against the committed full-size data (`89a9865`, 2026-04-05) and are now being
checked against ~1/40th of the pixels.

#213's commit message states *"Byte-reproduction verified per simulator against the hardcoded
LL literals"*. That verification was genuine but ran **at full size only** — it never
exercised the `PYAUTO_SMALL_DATASETS=1` path that the smoke profile actually uses.

`config/build/profile_release.yaml` already sets `PYAUTO_SMALL_DATASETS: "0"` (line 30), so
the release path is unaffected. **Smoke only.**

## The fix

Add a `PYAUTO_SMALL_DATASETS: "0"` override for `jax_likelihood/` to
`autolens_workspace_test/config/build/profile_smoke.yaml`.

This is an established pattern, not a new one: `autolens_workspace/config/build/profile_release.yaml`
already carries the identical override for `*/start_here`, `guides/` and
`*/features/potential_correction/`, with the rationale stated in-file:

> Non-simulator scripts that load committed FITS data need full-size datasets to avoid shape
> mismatch with pre-existing 100x100 data.

These five are exactly that class and were missed when the datasets left the tip.

## Why this matters beyond the five scripts

Library unit tests are NumPy-only by policy ([[feedback_no_jax_in_unit_tests]]), so these
`jax_likelihood` scripts are the **only** validation of the JAX/`xp` path. While they are red,
that entire surface is unguarded — and they sit in the per-PR smoke gate.

## Traps found while investigating (do not repeat)

- **Toggling `PYAUTO_SMALL_DATASETS` requires deleting the dataset dir first.**
  `should_simulate` only `rmtree`s when the flag is `"1"`. With it `"0"` and a stale 16×16
  dataset present, it returns `False`, skips re-simulation, and silently loads the small data.
  A first pass without deleting produced a false "multi/mge is 35x off" reading.
- **Delete only the regenerable dataset, not its parent.** `rm -rf dataset/interferometer`
  destroys `dataset/interferometer/uv_wavelengths/sma.fits`, which is committed, real
  uv-coverage data and not regenerable. Remove `dataset/interferometer/simple` instead.

## Follow-up worth considering (not this task)

The nightly-release blocker (`workspace-validation` failing 3 runs) shows the same *family* of
symptom in `autolens_workspace` / `autogalaxy_workspace` — `FileNotFoundError` on a dataset
path under a profile that sets `PYAUTO_SMALL_DATASETS=1`. Different symptom (missing file vs
value mismatch), possibly the same root class. Check whether those workspaces had an
equivalent dataset-untracking change.
