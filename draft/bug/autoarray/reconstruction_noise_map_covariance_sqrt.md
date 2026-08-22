# `reconstruction_noise_map_with_covariance` sqrt-NaNs every off-diagonal by construction

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: medium
Status: draft

## Why this exists

Found during the 2026-08-21 reproduction gate for
`draft/bug/health_fixes/numerical_inversion_failures.md` (record:
`complete/2026/08/numerical-inversion-failures.md`). That prompt alleged
non-positive-definite inversion matrices; it was **refuted** (2/2 scripts pass).
This warning was the one real defect the gate turned up, and the prompt itself
flagged it as "worth its own PyAutoArray prompt".

**Read this first if you are chasing an inversion conditioning bug:** these NaNs
look exactly like evidence of a non-positive-definite matrix and are not. They
are unconditional — they appear for *any* input matrix, however well-conditioned.
This finding has now been mistaken for a conditioning symptom once; don't let it
happen twice.

## The defect

`autoarray/inversion/inversion/abstract.py:839-859`, verified on `main` @ `a6b07cd`
(2026-08-22):

```python
@property
def reconstruction_noise_map_with_covariance(self) -> np.ndarray:
    """
    Returns the noise-map of the reconstruction as a two dimension matrix which accounts for the covariance
    of the noise between pixels.

    The diagonal of this matrix is the noise-map of the reconstruction, ...
    """
    return np.sqrt(np.linalg.inv(self.curvature_reg_matrix))
```

`np.sqrt` is applied **elementwise to the entire inverse matrix**. That inverse is
the reconstruction covariance matrix `C = inv(curvature_reg_matrix)`, whose
off-diagonal entries are covariances and are **generally negative**. So every
negative off-diagonal becomes `NaN`, and each call emits
`RuntimeWarning: invalid value encountered in sqrt`.

This is unconditional, not data-dependent: any covariance matrix with an
anti-correlated pixel pair NaNs. Observed as 4x `RuntimeWarning` from a clean,
passing run of
`autogalaxy_workspace/scripts/interferometer/features/pixelization/galaxy_reconstruction.py`.

## Why it is worth fixing

The property is public API and its docstring promises a matrix that "accounts for
the covariance of the noise between pixels". It returns NaN in exactly the entries
that carry that covariance — so the documented purpose of the property is the part
that is broken. Any consumer reading off-diagonals gets NaN.

Severity is bounded, and the bound should be stated honestly: **the science path is
correct.** The 1D `reconstruction_noise_map` takes `np.diagonal(...)` of this
property, and elementwise-sqrt commutes with taking the diagonal, so
`diag(sqrt(C)) == sqrt(diag(C))` — the right answer. Only the covariance-aware
consumer and the warning spam are hit.

## The trap — read before changing the return value

`reconstruction_noise_map` (line 881) is **derived from this property's diagonal**:

```python
return np.diagonal(self.reconstruction_noise_map_with_covariance)
```

If the fix changes the diagonal's meaning — e.g. returning the raw covariance
matrix `C` — then `reconstruction_noise_map` silently changes from **standard
deviation to variance**. That is a science regression in the one path that is
currently correct, and no existing test would catch it in a way that names the
cause. Any fix must either keep this property's diagonal as standard deviations,
or decouple `reconstruction_noise_map` from it and compute `sqrt(diag(C))`
directly.

## The decision this needs (do not guess it inline)

What the off-diagonals *should* be is an API/science call, not an obvious repair.
The plausible options:

1. **Return `C` unchanged** (a true covariance matrix; diagonal = variances).
   Cleanest semantics, but breaks the "diagonal is the noise-map" docstring claim
   and springs the trap above — `reconstruction_noise_map` must be rewritten in
   the same change.
2. **Sqrt the diagonal only**, leave off-diagonals as covariances. Preserves both
   docstring claims and every current caller, but the matrix has mixed units
   (std devs on the diagonal, variances off it), which is a strange object to hand
   a user.
3. **Signed sqrt**, `sign(C) * sqrt(|C|)`. Keeps a consistent "root" scale
   throughout and preserves the diagonal, but is a non-standard quantity that
   needs a documented justification.

Option 2 is the smallest, least disruptive change and is the natural reading of
the existing docstring. Option 1 is the most defensible statistically. Put the
choice to a human — this is a public-API contract, and the property's name should
probably change with it if the units do.

## Verification

- Off-diagonals are finite for a well-conditioned `curvature_reg_matrix` with an
  anti-correlated pixel pair. **There is currently no such test** — the only
  assertion on this property is
  `test_autoarray/inversion/inversion/test_abstract.py:684`, which checks `[0, 0]`,
  a *diagonal* element. The off-diagonal NaNs are entirely untested; that gap is
  why this shipped.
- No `RuntimeWarning: invalid value encountered in sqrt` is emitted. Consider
  running the regression test under `-W error::RuntimeWarning` so a regression
  fails loudly rather than warning quietly.
- `reconstruction_noise_map` still returns `sqrt(diag(C))` — assert this
  explicitly, against a hand-computed value, in the same test. The existing
  assertion at `test_abstract.py:686` covers the values but not the invariant.
- `test_autoarray/inversion/plot/test_inversion_plotters.py:82,110` monkeypatch
  this property to a singular matrix to force a `LinAlgError` and check plots/CSV
  degrade gracefully. Those must still pass — confirm the fix does not alter which
  exception escapes.
- Check downstream consumers before shipping: this sweep covered **PyAutoArray
  only**, where the sole in-repo consumer is `reconstruction_noise_map`. Grep
  @PyAutoGalaxy and @PyAutoLens for `reconstruction_noise_map_with_covariance`
  before assuming the change is contained.

Repro environment: `PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`,
`NUMBA_CACHE_DIR=/tmp/numba_cache`, `MPLCONFIGDIR=/tmp/matplotlib`,
`PYAUTO_DISABLE_JAX=1`.

## Also worth folding in

`reconstruction_noise_map`'s docstring says it "is computed as the square root of
the diagonal of the `reconstruction_noise_map_with_covariance` matrix". The code
takes the diagonal of an already-square-rooted matrix — no second sqrt. The two
are numerically equal today only because sqrt is elementwise, which is precisely
the bug. Whichever option is chosen, that sentence needs rewriting to match.

## Provenance

- Found during: `complete/2026/08/numerical-inversion-failures.md` (2026-08-22)
- **Not** a symptom of the refuted non-positive-definite hypothesis in that
  prompt, nor of the earlier `complete/2026/07/pix-inversion-not-positive-definite.md`
  cluster (also refuted). Independent of both.
