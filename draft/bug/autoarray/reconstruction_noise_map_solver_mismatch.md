# The reconstruction noise map describes a different estimator than the default solver

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: medium
Autonomy: human-required
Priority: high
Status: draft

## Why this exists

Found 2026-08-22 while researching
`draft/bug/autoarray/reconstruction_noise_map_covariance_sqrt.md` (the numerics
and semantics half). The question that started it: *why has the noise map on
source reconstructions not always been reliable?*

The answer is not the elementwise-sqrt bug — that only touches off-diagonals and
provably cannot reach the 1D noise map. It is this: **the noise map is computed
from a formula that describes an estimator PyAutoArray no longer uses by
default.** `Autonomy: human-required` because the primary fix is a statistical
decision about what the reported uncertainty *means*, not a code repair.

## Defect 1 — the covariance formula assumes an unconstrained solve; the default is NNLS

`abstract.py:859` computes `C = inv(curvature_reg_matrix)` = `[F + λH]^-1`. That
is the posterior covariance of the **classical semi-linear inversion** — the
unconstrained linear-Gaussian solution of Warren & Dye (2003) eq. 12, which is
what `reconstruction_positive_negative_from` computes.

But `config/general.yaml` ships:

```yaml
use_positive_only_solver: true      # DEFAULT
```

So the default reconstruction is `fnnls_cholesky` — a **non-negative least
squares** solve, minimising `||Zs - x||²` subject to `s >= 0`. That is a
*constrained* estimator with an active set: `fnnls` maintains a passive set `P`
and solves `slg.solve(ZTZ[P][:,P], ..., assume_a="pos")` on the free pixels only,
pinning the rest at exactly zero.

Imposing `s >= 0` is equivalent to truncating the Gaussian prior to the
non-negative orthant. The posterior is then a **truncated** multivariate Gaussian,
whose covariance is *not* `[F + λH]^-1`:

- For pixels well inside the positive region, the constraint is inactive and
  `[F + λH]^-1` is a good approximation.
- For pixels near the boundary, truncation **reduces** the variance, so the
  reported noise is systematically **overstated**.
- For pixels pinned at exactly zero, the marginal posterior is not Gaussian at
  all — it piles up at the boundary. The reported number is meaningless.

**Why this bites source reconstructions hardest.** A lensed source is compact; most
of the mesh is empty sky. So NNLS pins a *large fraction* of pixels at zero, the
active set is large, and the unconstrained formula is worst exactly where it is
most used. That matches the reported symptom precisely.

The docstring makes an uncertainty claim, not a diagnostic one — "the RMS standard
deviation of the noise in every pixel ... should be used for any scientific
analysis (e.g. source reconstructions of strong lenses)" — so this matters.

**The honest counter-argument, which a human should weigh:** if the noise map is
meant only as a *diagnostic* of how well each pixel is constrained by data plus
regularization, `[F + λH]^-1` is defensible for any solver, and the fix is to
rewrite the docstring rather than the maths. Decide which of the two it is before
writing code. That decision is the point of this prompt.

## Defect 2 — the noise map ignores edge-zeroed pixels the reconstruction excluded

`config/general.yaml` also ships `use_edge_zeroed_pixels: true`. Under it, the
reconstruction (`abstract.py:511-539`) subsets the system:

```python
curvature_reg_matrix = self.curvature_reg_matrix[self.zeroed_ids_to_keep][:, self.zeroed_ids_to_keep]
```

solves the reduced problem, then scatters back with **exact zeros** at the zeroed
pixels. `reconstruction_noise_map_with_covariance` inverts `self.curvature_reg_matrix`
— the **full** matrix, respecting neither this reduction nor the separate
`mapper_indices` reduction that `curvature_reg_matrix_reduced` applies for the
log-det.

Those excluded rows are, by the Delaunay mesh's own docstring, the
"poorly constrained boundary vertices" whose zeroing exists to "stabilize the
linear inversion" and "prevent poorly constrained boundary vertices from absorbing
flux". **The noise map re-admits into an explicit inverse precisely the degenerate
rows the reconstruction deliberately dropped to stay stable.**

The user-visible result: a pixel whose reconstruction reads exactly `0` (meaning
"not solved for") gets a noise value computed as though it had been solved.
Reconstruction and noise map disagree about what those pixels mean.

Scope: only bites when `zeroed_pixels > 0`. `Delaunay.__init__` defaults it to `0`,
so this is opt-in per mesh — check `rectangular_rtu_adapt_density` and any
workspace configs before sizing the blast radius.

## Defect 3 — `use_edge_zeroed_pixels` is silently ignored unless the positive-only solver is on

This is the "does the edge-pixel handling make sense next to positive-only?"
question, and the answer is no. The control flow (`abstract.py:509-554`):

```python
if self.settings.use_positive_only_solver:          # default True
    if self.settings.use_edge_zeroed_pixels and self.has(cls=Mapper):
        ...subset, fnnls, scatter back...
    else:
        return reconstruction_positive_only_from(FULL matrix)
return reconstruction_positive_negative_from(FULL matrix)   # edge-zeroing never consulted
```

`use_edge_zeroed_pixels` is nested **inside** the positive-only branch. Setting
`use_positive_only_solver: false` — a reasonable thing to do, for speed or to
permit negative values — **silently disables edge-zeroing too**, with no warning.
The poorly-constrained boundary vertices come straight back into the solve and
results change for a reason the config does not express.

These are orthogonal concerns. Which parameters are *solvable* (edge-zeroing) is a
statement about the mesh; which solver walks them is a separate choice. Edge-zeroing
should apply to both branches, or the coupling should be made explicit and
documented.

## Suggested direction (not a decision — see Defect 1)

If the noise map is to describe the estimator actually used, the covariance should
be formed on the **same index set the reconstruction solved**, and scattered back:

1. Determine the kept set exactly as `reconstruction` does — `zeroed_ids_to_keep`
   under edge-zeroing, and, for the NNLS answer to Defect 1, further restricted to
   the free set (pixels with `reconstruction > 0`).
2. Cholesky-invert that submatrix (per the sibling prompt's `cho_factor` /
   `cho_solve` fix).
3. Scatter back into full shape. **Decide what the excluded pixels report** — `0`
   matches the reconstruction's own convention and keeps plots working; `NaN` is
   more honest ("never estimated") but breaks colourbars and the CSV. Recommend
   `0` with an explicit docstring statement, since the reconstruction already
   reports `0` there and consumers handle it.

Restricting to the NNLS free set gives the covariance *conditional on the active
set* — standard practice for constrained least squares, and a defensible,
documentable choice. It is still an approximation: it ignores the uncertainty in
the active set itself. Say so in the docstring rather than implying exactness.

## Downstream evidence for why this matters (added 2026-08-22)

`autolens_workspace` uses the 1D noise map directly in user-facing science scripts —
`scripts/{imaging,interferometer,group,multi_galaxy}/features/pixelization/source_science.py`
compute:

```python
reconstruction_noise_map = inversion.reconstruction_noise_map
signal_to_noise_map = reconstruction / reconstruction_noise_map
```

So the quantity this prompt argues is computed for the wrong estimator is divided into the
reconstruction to produce a **signal-to-noise map on a source reconstruction** — the number
that ends up in papers. If the NNLS/unconstrained mismatch is real, it propagates straight
into published S/N. That raises the stakes on the Defect 1 decision and is the concrete
reason to instrument a real fit rather than reason about it further.

## Verification

- **Reproduce the symptom first.** Take a real Delaunay source fit, compute the
  noise map under the current code and under the free-set-restricted covariance,
  and compare. Quantify how many mesh pixels are pinned at zero by NNLS — the
  claim that this fraction is large for compact sources is **reasoned, not
  measured**, and the whole prompt rests on it. If the fraction turns out small,
  Defect 1 is a much smaller problem than stated here and should be re-graded.
- Confirm reconstruction and noise map agree on which pixels were solved: every
  pixel the reconstruction reports as an exact structural zero should be
  identifiable in the noise map by the documented convention.
- With `zeroed_pixels > 0`, assert the covariance is formed on the reduced matrix
  — regression-test the shape and the scatter-back, not just values.
- For Defect 3, assert `use_edge_zeroed_pixels: true` + `use_positive_only_solver:
  false` either applies edge-zeroing or raises/warns. It must not silently ignore
  the setting.
- Check whether `curvature_reg_matrix_reduced`'s `mapper_indices` reduction should
  apply to the noise map too. The log-det uses it; the noise map does not. Decide
  deliberately — this is a third, separate index set and the inconsistency between
  all three is itself a finding.

## Prior art — read before starting

- `complete/2026/08/numerical-inversion-failures.md` — this cluster's refutation.
- `complete/2026/07/pix-inversion-not-positive-definite.md` — an earlier
  non-positive-definite hypothesis, also refuted; documents the `GaussianKernel`
  PD-guarantee `f1817af0`.
- `autoarray/util/cholesky_funcs.py:50-80` — near-coincident mesh vertices make the
  Schur pivot's sign depend on BLAS thread count. The degeneracy is real and
  documented; this prompt is about not feeding it into an explicit inverse.
- `abstract.py:805` — the repo already documents `~1e-6` evidence round-off from
  "factorizing the explicitly formed inverse" at `cond(C) ~ 1e9` on clustered
  traced mesh vertices.

## Provenance

- Found during: research for the sibling prompt, 2026-08-22.
- Do the sibling first — it is small, needs no science decision, and its Cholesky
  covariance helper is the building block this prompt reuses.
