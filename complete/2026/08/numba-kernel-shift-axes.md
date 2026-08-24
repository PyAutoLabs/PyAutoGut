- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/486 (issued 2026-08-24, auto-closed by the merge)
- pr: https://github.com/PyAutoLabs/PyAutoArray/pull/487 (MERGED as `68a69ae`, branch
  `claude/numba-kernel-shift-axes-j5wo2p`)
- shipped: 2026-08-24 — both numba PSF gathers in
  `autoarray/inversion/inversion/imaging_numba/inversion_imaging_numba_util.py`
  (`psf_weighted_data_from` line 48, `psf_precision_value_from` line 313) now derive the
  y half-width from `kernel_native.shape[0]` and the x half-width from `shape[1]`.
- classification: bug (PyAutoArray, library-only). Split out from the OOB-gather fix
  (#456 / `numba-first-call-garbage-psf-weighted-data`) under the one-prompt-one-task rule.
- environment: web-github cloud session. No local PyAutoLabs tree; the container ships
  Python 3.11 and no scientific stack while autoarray requires >=3.12, so validation ran in
  a purpose-built 3.12 venv. Worth knowing before assuming a cloud session can run this suite.

## Root cause — a translation, not a rotation

The kernel *indexing* was never wrong: `k0_y` iterates axis 0 and is added to `y`, `k0_x`
iterates axis 1 and is added to `x`, and the tap is `kernel_native[k0_y, k0_x]`. Only the
**centring constant** came from the wrong axis. So the displacement between buggy and fixed is

```
Δy = ky//2 − kx//2        Δx = kx//2 − ky//2  =  −Δy
```

— a pure rigid shift of the sampling window along the anti-diagonal, magnitude |ky−kx|/2.

Two consequences worth remembering, because both are counter-intuitive:

- **Square kernels are exactly inert at any size and either parity.** The expression carries
  no parity term, so *squareness* is what matters, not oddness. Verified across 3x3, 5x5,
  7x7, 2x2, 4x4, 6x6: `max|buggy − fixed| = 0.000e+00` for every one.
- **It is not a rotation or transpose.** `buggy(y,x) == fixed(y+Δy, x+Δx)` holds to
  `0.000e+00` on interior pixels; transpose / rot90 / rot180 hypotheses all leave residuals
  of order 10¹. Anyone reading "wrong kernel axes" will reach for a rotation first — don't.

## The second defect the prompt did not name

In `psf_precision_value_from` the same variables also drive the pair-overlap early-exit
(`ip_y_offset < 2 * kernel_shift_y or ...`). For a 3x5 kernel the transposition admitted y
offsets to ±4 (should be ±2) while rejecting x offsets beyond ±2 (should be ±4), so
genuinely overlapping image-pixel pairs were silently **dropped** on one axis and
non-overlapping ones admitted on the other. The swap corrects it; no separate change needed.

## The test that mirrored the bug

`test__psf_precision_operator_sparse_from__edge_pixels` built a `_reference_value` helper its
own comment called an "independent reference" — but it replicated the same transposition
(`kernel_shift_y = -(kw // 2)`), agreeing with the buggy code only because its kernel was
square. Left alone, the new non-square case would have asserted the bug. This is the trap
worth carrying forward: **a hand-rolled reference written from the same mental model as the
code under test is not independent**, and a symmetric fixture hides it.

## Validation

- Reproduced pre-fix: 3x5 kernel on a fully-unmasked 5x5 image, `max|numba − numpy| = 1420.0`,
  the numba result being the numpy result shifted. Square control `0.0`. Post-fix both `0.0`.
- Tests parametrised over 3x3 / 3x5 / 5x3 / 5x7 on both functions, plus two direct orientation
  probes (single-tap kernel over a coordinate-encoding map, so the return value *names* the
  pixel gathered rather than the test re-deriving the kernel walk).
- **Verified as a detector, not merely as passing tests**: against unpatched source 8 fail —
  every non-square parametrisation plus both probes — while the 6 square cases pass, which is
  precisely why the defect survived. Full suite with the fix: 1154 passed, 55 skipped.
- CI green on all three legs (unittest 3.12, unittest 3.13, unittest-nojax).

## Follow-up check: the correlation convention is correct (no action needed)

The equivalence tests pin numba to numpy but cannot judge whether the *shared* convention is
right, so the "no kernel flip" (correlation) convention was checked separately against a dense
ground-truth `H` built from the definition of a PSF convolution, with a non-square asymmetric
3x5 PSF:

| path | claims | vs dense truth |
|---|---|---|
| numpy `psf_weighted_data_from` | `H^T N^-1 d` | `1.78e-15` |
| numba `psf_weighted_data_from` | `H^T N^-1 d` | `1.78e-15` |
| numba `psf_precision_operator_from` | `H^T N^-1 H` | `3.55e-15` |
| JAX `ImagingSparseOperator.apply_operator` | `H^T N^-1 H` | `7.11e-15` |

Correlation is correct because the adjoint of a convolution *is* a correlation:
`(H^T g)[j] = Σ_κ psf[κ]·g[j+κ−c]`. The flipped alternative misses truth by `7.086e+00`, so
the distinction is observable and the code is on the right side of it. The JAX
`Khat_r` / `Khat_flip_r` pair that prompted the question is the correctly-assembled adjoint
pair — unflipped forward blur (`H`), flipped back-projection (`H^T`). Control: swapping JAX's
crop offsets `(cy,cx) → (cx,cy)` shifts the result by `9.97e-01`, so that path is genuinely
orientation-sensitive and simply gets it right. No follow-up task filed.

## Orientation audit (repo-wide)

A scan for every half-width derivation in the library found these two functions were the only
transposed sites. Already correct and untouched: `convolve_with_kernel_native` (the in-file
reference idiom), `psf_precision_operator_sparse_from`'s orientation-agnostic
`kernel_overlap_size`, the numpy twin at `inversion_imaging_util.py:44-45`, the JAX precision
operator, and `array_2d_util.py:311-319` resize centring.

- downstream impact: none. Internal numba util; behaviour is bit-identical for square kernels,
  which is every PSF in the workspaces today. No workspace changes required.
- affected-repos:
  - PyAutoArray

## Original prompt

# Numba PSF gathers derive the y/x kernel shifts from the wrong kernel axes

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: low
Autonomy: supervised
Priority: medium
Status: formalised
Filed: 2026-08-21 (backfilled from git)
Issued: 2026-08-24

Found 2026-08-21 while fixing
`draft/bug/autoarray/numba_first_call_garbage_psf_weighted_data.md` (the
out-of-bounds gather in `psf_weighted_data_from`). Split out under the
one-prompt-one-task rule: separate defect, separate blast radius.

## Symptom

Both numba PSF gathers in
`autoarray/inversion/inversion/imaging_numba/inversion_imaging_numba_util.py`
compute their kernel half-widths from the **transposed** kernel axes:

```python
kernel_shift_y = -(kernel_native.shape[1] // 2)   # shape[1] is x
kernel_shift_x = -(kernel_native.shape[0] // 2)   # shape[0] is y
```

at `psf_weighted_data_from` (line ~48) and `psf_precision_value_from`
(line ~294). The y shift must come from `shape[0]` and the x shift from
`shape[1]`.

The zero-padded numpy twin
(`imaging/inversion_imaging_util.py:psf_weighted_data_from`) gets it right and
is the reference:

```python
Ky, Kx = kernel_native.shape
ph, pw = Ky // 2, Kx // 2
```

## Reachability

Harmless for square kernels (`shape[0] == shape[1]`), which is the common
case and why no test catches it. It is **not** unreachable: kernels are
validated as *odd* in each axis, not square — `exc.KernelException("Convolver
Convolver must be odd")` in `operators/convolver.py:268` and
`structures/grids/uniform_2d.py:1153` check parity only. A non-square odd PSF
(e.g. 3x5) therefore mis-centres the gather, sampling the weight map / noise
map off-centre along both axes.

With the bounds guard now in place the mis-centred reads are clipped rather
than reading uninitialized memory, so this is a silent wrong-answer bug, not
a crash or a garbage-value bug.

## Fix

Swap the two right-hand sides in both functions. Fix them **together** — they
must agree on kernel orientation, and correcting only one would make the
`psf_weighted_data` and `psf_precision_operator` paths disagree.

## Acceptance

Extend the numba-vs-numpy equivalence test added by the OOB fix
(`test_autoarray/inversion/inversion/imaging/test_inversion_imaging_util.py::
test__psf_weighted_data_from__unmasked_pixels_on_array_edge`) to a non-square
odd kernel (e.g. 3x5). It passes today only because that test uses a square
kernel; with a non-square kernel the two implementations diverge.
