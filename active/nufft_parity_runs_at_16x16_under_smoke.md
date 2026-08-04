# NUFFT parity test asserts a 256x256 tolerance while smoke runs it at 16x16

Type: bug
Target: autolens_workspace_test
Repos:
- @autolens_workspace_test
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

## Original request

> 3. nufft.py precision assertion
>
> In the PyAutoLabs workspace, this script fails in workspace-smoke:
>
>   autolens_workspace_test scripts/interferometer/nufft.py
>   AssertionError: pynufft should match TransformerDFT within its gridding precision
>   (FAIL after 9.9s)
>
> Evidence: PyAutoHeart workspace-smoke run 30858578587, job
> "smoke / run_scripts (3.12, autolens_test, interferometer)",
> 2026-08-03T22:34:59Z. Installed pynufft 2025.2.1, nufftax 0.6.1,
> jax 0.10.2, numpy 2.4.6 against released autolens 2026.7.29.2.
>
> This is a numerical-parity assertion, so establish first whether the
> tolerance is too tight or a transform genuinely regressed — reproduce
> locally and compare both paths on the same visibilities before changing
> either the tolerance or the code. Do not loosen the assertion just to go
> green. Route through start_dev.

## Finding

Neither. The tolerance is correct for the problem the script *says* it runs, and
no transform regressed — the script silently runs a different, much smaller
problem under the smoke profile.

`scripts/interferometer/nufft.py` carries no `__Env__` declaration, so it
inherits the smoke defaults from `config/build/profile_smoke.yaml`, including
`PYAUTO_SMALL_DATASETS=1`. That env var:

- makes `al.util.dataset.should_simulate` **delete** the committed dataset and
  re-simulate it at reduced size, and
- caps `Mask2D.circular(shape_native=(256, 256), pixel_scales=0.1, ...)` to
  `(16, 16)` at `0.6"` (`autoarray/util/dataset_util.py`,
  `SMALL_DATASETS_SHAPE_NATIVE`).

So test (b), documented and calibrated as "Lensed Sersic image, 256x256, real
SMA uv coverage", actually executes on a 16x16 grid at 6x the pixel scale.
pynufft's Kaiser-Bessel gridding (default `Jd=(6, 6)`, oversample ratio 2) is a
poor approximation there — the interpolation stencil spans ~37% of the grid —
so its error against the exact `TransformerDFT` explodes.

Reproduced locally on `autolens_workspace_test` `main` (e6eb41c), released-stack
parity not required to see it:

| run | (b) `max|Δ| pynufft − DFT` / `|vis_DFT|_max` | verdict |
|-----|---------------------------------------------|---------|
| bare (documented usage, true 256x256) | **6.0959e-02** | PASS (tol 1e-1) |
| full smoke profile (actually 16x16) | **8.9643e-01** | FAIL — ~15x over tol |
| smoke profile minus `PYAUTO_SMALL_DATASETS` | **6.0959e-02** | PASS |

nufftax is unaffected in both regimes (`3.02e-14` relative at 256x256,
`1.73e-14` at 16x16) — it is essentially exact at `eps=1e-12` regardless of N,
which is exactly why only the pynufft leg trips.

The failure only surfaced now because commit `6a6156c` (2026-07-28, "restore
real pynufft leg of the NUFFT parity test") fixed a vacuous comparison: before
it, the "pynufft" transformer was built as `al.TransformerNUFFT`, which now
resolves to the nufftax-backed default, so the assertion was comparing nufftax
against itself and reporting `0.0000e+00`. The 2026-08-03 smoke run is the
first one to evaluate the assertion for real under the smoke profile.

`PYAUTO_DISABLE_JAX=1` (also a smoke default) is not implicated — the script
calls `nufftax` directly and produces bit-identical numbers with and without it.

## Task

Declare the script's true environment requirement instead of touching the
tolerance or the transforms. Add an `__Env__` docstring section with
`ENV: full_datasets` (the token that releases `PYAUTO_SMALL_DATASETS`) so the
script runs the 256x256 case its assertions were calibrated for, and correct the
docstring so the resolution premise is stated rather than assumed.

No tolerance is to be loosened and no library code changed.

Cost is not a concern: the full-resolution run takes **12.0s** under the smoke
profile with the token applied, versus **9.9s** for the failing 16x16 run.

Under `profile_release.yaml` this is a provable no-op — that profile already
pins `PYAUTO_SMALL_DATASETS: "0"`.

## Acceptance

- `scripts/interferometer/nufft.py` passes under the full smoke profile.
- The pynufft-vs-DFT relative residual reported under smoke is the 256x256
  value (~6.1e-2), not the 16x16 value (~9.0e-1).
- Every assertion tolerance in the script is unchanged.
- No PyAutoArray / PyAutoLens source change.
- The script asserts the resolution it actually ran at, so a future silent
  downsizing fails loudly instead of drifting past the tolerance.

## Notes

- A sweep of `autolens_workspace_test/scripts/` for other numerical-tolerance
  assertions without `full_datasets` found no second instance of this specific
  failure mode: the rest are same-input A/B parity checks (JAX vs numpy, round
  trips) whose tolerances do not depend on grid size. They are out of scope.
- Related trap, same env var:
  `should_simulate` leaves the re-simulated 16x16 dataset on disk at
  `dataset/interferometer/simple/`, poisoning later full-resolution runs in the
  same checkout.
