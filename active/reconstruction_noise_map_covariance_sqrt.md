# `reconstruction_noise_map_with_covariance` — form the covariance properly, fix the sqrt

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: medium
Status: in-progress

## Why this exists

Found during the 2026-08-21 reproduction gate for
`draft/bug/health_fixes/numerical_inversion_failures.md` (record:
`complete/2026/08/numerical-inversion-failures.md`). That prompt alleged
non-positive-definite inversion matrices and was **refuted**; this was the real
defect the gate turned up.

**Scope note (2026-08-22).** Deeper research found the noise map is wrong in
*four* distinct ways. This prompt owns the two that need no science decision —
the numerics and the semantics. The estimator-level defects (the noise map
describes a different estimator than the default solver, and ignores edge-zeroed
pixels) are **`draft/bug/autoarray/reconstruction_noise_map_solver_mismatch.md`**,
which is the larger and more consequential of the two. Do that one second; this
one first, because it is small, safe and unblocks the other.

## Defect A — elementwise sqrt NaNs every off-diagonal

`autoarray/inversion/inversion/abstract.py:839-859`, verified on `main` @ `a6b07cd`:

```python
@property
def reconstruction_noise_map_with_covariance(self) -> np.ndarray:
    """... a two dimension matrix which accounts for the covariance of the noise between pixels."""
    return np.sqrt(np.linalg.inv(self.curvature_reg_matrix))
```

`np.sqrt` is applied **elementwise to the entire inverse**. That inverse is the
covariance matrix `C`, whose off-diagonals are covariances and are generally
negative — so they become `NaN`, and each call emits
`RuntimeWarning: invalid value encountered in sqrt`. Unconditional: any matrix
with an anti-correlated pixel pair NaNs, however well-conditioned.

**This does NOT affect the 1D noise map.** `np.sqrt` is elementwise, so it
commutes with taking the diagonal — `np.diagonal(np.sqrt(C))[i] == sqrt(C[i,i])`.
The off-diagonal NaNs never reach `reconstruction_noise_map`. Do not cite this
defect as the cause of unreliable 1D noise maps; that is the sibling prompt.

## Defect B — `np.linalg.inv` is the wrong routine, and the repo already says so

The same file, 50 lines up, documents exactly this hazard for the log-det path
(`abstract.py:805-806`):

> the analytically exact `pixels * log(coeff) - log det C` from a single Cholesky
> of their covariance `C`, **avoiding the round-off of factorizing the explicitly
> formed inverse** (which reaches ~1e-6 absolute in the evidence at
> **cond(C) ~ 1e9 on clustered traced mesh vertices**)

That reasoning was applied to the log-det and never to the noise map, which still
forms the explicit inverse — of the same matrix, at the same conditioning, on the
same clustered-mesh geometry.

Three consequences, all pointing the same way:

1. `np.linalg.inv` is LU-based. It exploits neither symmetry nor
   positive-definiteness, both of which this matrix has (when it is well-posed).
2. It **raises only on exactly-singular input.** Near-singular passes through with
   amplified error, so a diagonal entry can come back negative — impossible for a
   true PD inverse — and `sqrt` turns it into NaN, or leaves it barely positive and
   yields a wildly wrong RMS. Silently.
3. The reconstruction path never inverts: `reconstruction_positive_negative_from`
   uses `xp.linalg.solve` and `fnnls_cholesky` uses
   `slg.solve(..., assume_a="pos")`. The noise map is the only place in the
   inversion that forms an explicit inverse.

**This is already biting users.** `inversion_plots.py:395` wraps the noise map in
`except np.linalg.LinAlgError` and writes the CSV column as NaN with a warning —
a guard that exists because this fails in practice.

## The fix

Option 1 from the original draft, chosen 2026-08-22: the property should return
the actual covariance matrix, computed via Cholesky. `scipy` is already a hard
dependency (`pyproject.toml`).

```python
from scipy.linalg import cho_factor, cho_solve

@property
def reconstruction_covariance_matrix(self) -> np.ndarray:
    """The covariance matrix C = [F + λH]^-1 of the reconstruction."""
    matrix = np.asarray(self.curvature_reg_matrix)
    covariance = cho_solve(cho_factor(matrix), np.eye(matrix.shape[0]))
    return 0.5 * (covariance + covariance.T)   # remove rounding asymmetry

@property
def reconstruction_noise_map(self) -> np.ndarray:
    """1D RMS noise: sqrt of the diagonal of the covariance matrix."""
    return np.sqrt(np.diag(self.reconstruction_covariance_matrix))
```

Why this shape:

- **`cho_factor` raises `LinAlgError` on a non-PD matrix**, so the noise map now
  fails loudly on exactly the matrices the reconstruction already rejects. Today
  the two disagree: `solve` raises and resamples, `inv` returns garbage.
- **`reconstruction_noise_map` is decoupled** and computes `sqrt(diag(C))`
  directly. Today it is correct only *incidentally*, because sqrt happens to be
  elementwise — change the matrix and it silently becomes a variance. Decoupling
  removes that trap permanently.
- **Off-diagonals become real covariances**, so the docstring's promise holds.

**Naming.** `..._with_covariance` returning a covariance matrix should be
`reconstruction_covariance_matrix`. Keep the old name as a `DeprecationWarning`
alias returning the new matrix. Its values *do* change — diagonal from std-dev to
variance, off-diagonals from NaN to covariances — but every off-diagonal consumer
was reading NaN, so nothing correct can break. Note the change in the release
notes regardless.

Optional, only if profiling asks for it: if just the diagonal is needed,
`diag(C)` is available from the Cholesky factor as the squared row-norms of
`L^-1`, avoiding the full `n x n` product. Not worth the complexity up front —
this is computed once per fit, not per-likelihood.

## Verification

- **Off-diagonals finite** for a well-conditioned matrix with an anti-correlated
  pixel pair. **No such test exists today** — the only assertion on this property
  (`test_autoarray/inversion/inversion/test_abstract.py:684`) checks `[0, 0]`, a
  *diagonal* element. That gap is why this shipped.
- **No `RuntimeWarning`.** Run the regression test under `-W error::RuntimeWarning`
  so a regression fails rather than warns.
- **`reconstruction_noise_map` still returns `sqrt(diag(C))`** — assert against a
  hand-computed value, and assert the invariant explicitly, not just the numbers.
- **The `inv`-vs-`cho_solve` A/B was run on 2026-08-22 and refuted two of the
  claims above.** Recorded so nobody re-derives the wrong reasoning:

  | Claim | Verdict |
  |---|---|
  | `inv` gives negative diagonals on well-formed SPD | **REFUTED** — 0 across cond 1e3–1e15, n=400, 20 trials each |
  | `inv` is materially less accurate on the diagonal | **REFUTED** — matches `cho_solve`; at cond 1e15 `inv` was marginally *better* |
  | Near-coincident mesh vertices degrade the inverse | **REFUTED** — with regularization the matrix stays PD (cond ~6.8e7 even at exactly duplicated columns) |
  | `inv` returns asymmetric output | **CONFIRMED** — 5.2e-7 at cond 1e12 vs 2.6e-16 |
  | `inv` silently succeeds on indefinite matrices | **CONFIRMED** |

  The surviving argument is **detection, not accuracy**. `cho_factor` raises
  `LinAlgError` on a negative eigenvalue; `inv` raises only on an *exactly*
  singular matrix and otherwise returns a plausible-looking covariance. At
  eigenvalue `-1e-8` all 300 diagonals came back negative (whole noise map NaN);
  at `-1.0`, **zero** did — no NaN, no warning, no error, wrong numbers.

  **Not established:** that a real `curvature_reg_matrix` *is* indefinite in a
  converged fit. `Settings.no_regularization_add_to_curvature_diag_value` and the
  `curvature_matrix_with_added_to_diag_from` docstring ("it is common for the
  `curvature_matrix` computed to not be positive-definite") say it happens, but no
  fit was instrumented to confirm it. Worth doing under the sibling prompt.
- `test_autoarray/inversion/plot/test_inversion_plotters.py:82,110` monkeypatch
  this property to force a `LinAlgError` and check plots/CSV degrade gracefully.
  Confirm the same exception still escapes — `cho_factor` also raises
  `LinAlgError`, so this should hold, but assert it.
- **Downstream:** this sweep covered PyAutoArray only, where the sole in-repo
  consumer is `reconstruction_noise_map`. Grep @PyAutoGalaxy and @PyAutoLens for
  `reconstruction_noise_map_with_covariance` before assuming containment.

## Also fold in

`reconstruction_noise_map`'s docstring claims it "is computed as the square root
of the diagonal of the `reconstruction_noise_map_with_covariance` matrix". The
code takes the diagonal of an already-square-rooted matrix — no second sqrt. The
two agree today only because sqrt is elementwise, which is precisely the bug.
Rewrite the sentence to match whatever ships.

## Note on the JAX path

This property uses bare `np`, not `self._xp`, so it is already numpy-only even
under a JAX fit — a JAX `curvature_reg_matrix` is coerced via `__array__`, forcing
a device→host sync. The scipy fix does not regress that (there was no JAX support
to lose) but it does make it explicit. Add `np.asarray` at the boundary, as above,
and note the limitation in the docstring rather than leaving it implicit.

## Provenance

- Found during: `complete/2026/08/numerical-inversion-failures.md` (2026-08-22)
- Sibling: `draft/bug/autoarray/reconstruction_noise_map_solver_mismatch.md`
- **Not** a symptom of the refuted non-positive-definite hypothesis in that record,
  nor of `complete/2026/07/pix-inversion-not-positive-definite.md` (also refuted).
