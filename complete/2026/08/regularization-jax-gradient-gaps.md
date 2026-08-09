# regularization-jax-gradient-gaps

**PRs:** PyAutoLabs/PyAutoArray#437 (`5867db0e`) · PyAutoLabs/PyAutoArray#438 (`007904b3`) · PyAutoLabs/PyAutoMind#169 (`8499ecd7`) · **Shipped:** 2026-08-09

Closes all three legs of the 2026-07-26 regularization × mesh gradient sweep.
Legs 1 and 3 shipped earlier (2026-07-26 / 2026-07-28); leg 2 shipped here as
2a + 2b.

## The prompt was stale in three ways — check source before planning

Leg 2 was written before PyAutoArray#391 landed. Re-derived against main
`efaf3041`:

| Prompt said | Reality |
|---|---|
| `log det H` implicit — to do | **Already shipped.** `log_det_regularization_matrix_term_from` on all four kernel schemes, behind `log_det_method == "slogdet"` (#391). |
| jitter as a kwarg — to do | **Already shipped.** `jitter: Optional[float] = None` + `jitter_value` on all four. Only the *scaling* was outstanding. |
| "Keep `H` implicit" (headline goal) | **Not achievable.** See below. |

Starting dev on the prompt as written would have burned a session
rediscovering all three. The `too-large` / four-phase sizing the Feature Agent
returned was also wrong — an artefact of prompt *length* (legs 1 and 3 carry
their completion records inline), not of the work.

## The one thing that cannot be done — do not re-open

`curvature_reg_matrix` (`inversion/abstract.py:366`) is a dense
`xp.add(curvature_matrix, regularization_matrix)` feeding the dense solve for
the reconstruction. **`H` must be formed there.** Only the *evidence* terms can
avoid the explicit inverse. Any future attempt at a blanket implicit `H` needs
an iterative-solver design first, which is a different task.

## Leg 2a — `s^T H s` from one Cholesky solve

`regularization_term` contracted the formed `H`. For the kernel schemes
`H = coefficient * C^-1`, so the term is `coefficient * s^T C^-1 s` — one
Cholesky solve against `s` rather than forming `C^-1` and contracting it.

Built to the exact shape of the shipped log-det shortcut: a
`regularization_term_from` hook on `AbstractRegularization` returning `None` by
default, overridden by the four kernel schemes, consulted behind a **new**
`Settings.regularization_term_method` (`"matmul"` default, `"cho_solve"`
opt-in).

Deliberately a *separate* setting from `log_det_method`, not a reuse: the two
evidence terms can then be moved onto their exact factorizations
independently, which is what makes an evidence shift attributable to one term
rather than both. Gating `s^T H s` on a setting named for log-determinants
would also have been a lie in the name.

Measured at `cond(C) = 3.2e9`, graded against an exactly-known reference
(choosing `s = C v` makes `C^-1 s = v`, so the true form is `s^T v` and needs no
inverse anywhere):

| | relative error |
|---|---|
| explicit inverse | 5.99e-08 |
| Cholesky solve | 2.93e-16 |

This confirms the prompt's own ~1e-6..4e-5 noise-floor measurement was the
explicit inverse.

## Leg 2b — relative jitter (the prompt understated this one)

Filed as a "cheaper interim". It is a real bug with a silent failure mode.

The jitter was a fixed absolute `1e-8 * I`, meaningful only when `diag(C) ~ 1`.
Measured: true for the three unweighted kernels (`K(0) == 1`), **false** for
`MaternAdaptKernel`, whose `C_ii = w_i^2` spans the adaptive-weight dynamic
range. Distortion of the faintest pixel, 40-pixel fixture:

| inner/outer | faintest `C_ii` | distortion |
|---|---|---|
| 1.0 / 1.0 | 1.0e+00 | 1.0e-08 |
| 0.5 / 4.0 | 3.9e-03 | 2.6e-06 |
| 1.0 / 20.0 | 6.3e-06 | 1.6e-03 |
| 0.1 / 100.0 | 1.0e-08 | **1.0e+00** |

`inner_coefficient`/`outer_coefficient` are **free model parameters**, so a
sampler can walk into the bottom row mid-fit — no exception, no NaN, just the
faintest pixels' kernel structure replaced by jitter.

Fix: `jitter_relative=True` applies `C_ii *= (1 + jitter)`. With
`C = D^½ R D^½`, that is exactly `D^½ (R + jitter·I) D^½` — the jitter lands on
the **correlation** matrix, so every pixel gets the same relative protection
whatever its scale.

**Rejected design, recorded so it is not retried:** `jitter = N·eps·max(diag)`
("as small as possible above the round-off floor") fixes the distortion but
lets `cond(C)` reach **3.2e15**, at the edge of float64 — reintroducing exactly
the noise leg 2 exists to remove. The correlation-relative rule leaves
conditioning unchanged (3.16e9 both conventions, measured).

## Traps found (all pinned by tests)

- **`MaternAdaptKernel` inherits `coefficient=0.0`.** It passes `coefficient=0.0`
  to `MaternKernel.__init__` (its weights live inside `C_w`), so inheriting the
  parent's `regularization_term_from` would have **silently zeroed the term** —
  wrong but finite, the worst failure mode. It needs its own override.
- **`GaussianKernel`'s formed matrix ≠ the analytic `coefficient * C^-1`.** It
  carries a symmetrisation plus trace-scaled jitter which the shortcut excludes
  — consistent with how its log-det shortcut already behaves, since both exist
  only to guard a factorization these paths avoid. Test tolerance is at the
  jitter scale, not machine precision.
- **Fallback must be all-or-nothing.** Schemes with no factorization
  (`Constant`, `Adapt`, split families) return `None`, and one `None` falls the
  whole computation back to the formed matrix, so mixed inversions stay correct.

## Evidence-shift guidance (for anyone comparing against archived runs)

**Defaults move nothing.** All three switches (`log_det_method`,
`regularization_term_method`, `jitter_relative`) default to historical
behaviour; a test asserts the default jitter path is byte-identical. Archived
comparability holds — the constraint the #391 adversarial probe verdict imposed.

Opting in:

- `regularization_term_method="cho_solve"` — ~1e-15 on well-conditioned meshes;
  up to ~6e-8 relative on clustered ones. **The new value is the correct one**;
  the shift is error being removed.
- `jitter_relative=True` — negligible for the three unweighted schemes; can be
  **large** for `MaternAdaptKernel`, growing with the inner/outer range. At the
  extreme the old evidence was materially wrong.

Do not mix within a comparison: run both arms with the flags off, or re-run the
baseline with them on. The two settings are separate precisely so one term can
be moved at a time.

## Testing

29 new tests in PyAutoArray:

- `test_kernel_regularization_term.py` (9)
- `test_kernel_jitter_relative.py` (7)
- `test_kernel_jax_gradients.py` (13) — the JAX leg of the gate

JAX certification (the library-level stand-in for
`autolens_workspace_test/scripts/imaging/jax_grad/regularization.py`):

| check | result |
|---|---|
| FD certification of `d(s^T C^-1 s)/d(scale)` | 4.6e-09 |
| eager vs jit | 3.6e-15 |
| implicit vs explicit inverse (JAX) | 1.1e-13 |
| numpy vs jax parity | 8.4e-12 |

**Not covered:** Matérn's JAX path needs the modified Bessel from
`tfp-nightly`, an optional-of-an-optional. Gaussian and Exponential exercise the
same shared `apply_jitter` / `quadratic_form_via_cholesky` code. The workspace
script still covers Matérn end-to-end and is unaffected by these defaults.

## Side quest — main was red before this work started

PyAutoArray#437's CI failed on a test this branch does not touch. The identical
failure was already on main at `efaf3041` (run 31219374045, 2026-08-07):

```
FAILED test_autoarray/util/test_cholesky_degenerate.py::test__fnnls_cholesky__never_returns_a_non_finite_solution[0.0] - assert 0 > 0
```

The vacuity guard `assert raised > 0` requires `fnnls_cholesky` to *raise* for
at least one of 40 seeds. Raising is an **allowed** outcome, not a required one
— that file says so itself, in
`test__cholinsertlast__singular_insertion_never_yields_an_unusable_pivot`. On a
singular insertion the Schur complement is zero up to rounding, so which side it
lands on is decided by BLAS summation order; the module comment cites this as
why the original bug reproduced on CI but not locally. Measured: `[0.0]` passes
locally by a **single seed out of 40**, and zero on the CI runners — which is
exactly the one parametrisation that failed.

Fixed in **PyAutoArray#438** (merged first, so #437 landed on a green base):
`solved > 0` replaces `raised > 0` (at least one seed must reach the finiteness
assertion — that is what non-vacuous means, and it does not depend on
rounding), and "the band really is degenerate" is pinned on the fixture via
`cond(ZTZ) > 1e12` (measured 1.07e16–3.71e18, deterministic anywhere). Verified
in both directions by simulation: with no seed raising all four parametrisations
pass; with every seed raising it still fails. main went failure → success on
that merge.

## Remaining

Nothing owed on this prompt. Two follow-ups noted, neither blocking:

- Matérn JAX coverage at library level, if `tfp-nightly` ever becomes a
  reasonable test dependency.
- `gaussian_kernel.py` still trace-scales its *formed* `H` (`1e-8 * abs(diag_mean)`)
  while no other scheme does. That stabilisation guards the explicit inverse and
  was deliberately left alone here.

## Original prompt

# Regularization JAX gradient gaps — xp-ports + kernel-scheme linear algebra

Type: feature
Target: autoarray
Repos:
- PyAutoArray
- autolens_workspace_test
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

## Context (2026-07-26 regularization × mesh gradient sweep)

A full sweep of every `al.reg` scheme against the gradient-capable meshes
(`RectangularAdaptDensity` os_pix=4; `KNearestNeighbor`/`KNNBarycentric`
Hilbert + edge zeroing) mapped the JAX-gradient compatibility surface. The
matrix and measurements live in
`autolens_workspace_developer/jax_profiling/gradient/README.md`
("Regularization × mesh gradient matrix"); positive certifications are
pinned by `autolens_workspace_test/scripts/imaging/jax_grad/regularization.py`
and the mesh-family negatives by `jax_grad/knn.py`. Three actionable gaps
fell out — none blocks current production paths, so this is one prompt to
be split or trimmed at start-dev if any leg grows:

## 1. xp-ports — DONE

*Both legs shipped 2026-07-26 on `claude/rectangular-mesh-gradients-mh1j0z`:
`ExponentialKernel` (xp threaded through the covariance build, NaN-safe
`sqrt(d²+1e-20)` distances) and `BrightnessZeroth` (the `pixel_signals_from`
call site now threads `xp`). JAX gradients verified on both. Legs 2 and 3
below remain the open work of this prompt.*

## 2. Kernel-scheme linear algebra: avoid the explicit `C^-1` (the real one)

`MaternKernel`/`MaternAdaptKernel`/`GaussianKernel` build
`H = coefficient * inv_via_cholesky(C)` — an explicit dense inverse. On
well-spaced vertices (rectangular mesh: cond(C) ≈ 3e5 at nu=2.5) this is
fine and `MaternKernel(nu=2.5)` is strict-FD-certified (2.2e-4). On TRACED
(clustered) mesh vertices (KNN meshes: min pairwise separation ~7e-3 vs
median ~9e-2 → cond(C) ≈ 1.4e9 at nu=2.5) the explicit inverse puts a
~1e-6..4e-5 absolute numerical noise floor on the likelihood itself
(measured as eager-vs-jit LL differences), which caps FD verifiability at
~1e-3..1e-2 relative and adds the same noise to sampler-visible likelihoods.

Reformulation candidates (in the spirit of the opt-in slogdet, PyAutoArray#391):

- Keep `H` implicit through the Cholesky of `C`: `s^T H s` via
  `cho_solve(L, s)`, `log det H = -2 Σ log diag L` — no explicit inverse,
  one factorization, strictly more accurate and faster. Requires the
  inversion interface to accept an implicit/functional `H` (today it
  consumes a dense matrix — check `curvature_reg_matrix` assembly).
- Cheaper interim: scale the fixed `1e-8` diagonal jitter with the kernel's
  dynamic range / N, and expose it as a kwarg.

### Status of leg 2, re-derived against main `efaf3041` (2026-08-09)

The two candidates above were written before #391 landed and are now partly
stale. Checked against source rather than assumed:

- **`log det H` implicit — ALREADY SHIPPED.** `log_det_regularization_matrix_term_from`
  exists on all four kernel schemes (`MaternKernel`, `MaternAdaptKernel`,
  `GaussianKernel`, `ExponentialKernel`), gated behind
  `Settings.log_det_method == "slogdet"` (PyAutoArray#391). Nothing owed.
- **jitter as a kwarg — ALREADY SHIPPED.** All four carry
  `jitter: Optional[float] = None` + a `jitter_value` property. The *scaling*
  was the remaining half — tracked as leg 2b and now shipped too (see its block
  below). Note `gaussian_kernel.py` already trace-scales
  (`1e-8 * abs(diag_mean)`), but on the formed `H` rather than on `C`; that
  stabilisation is a separate guard on the explicit inverse and was left alone.
- **"Keep `H` implicit" in general — NOT ACHIEVABLE, do not re-open.**
  `curvature_reg_matrix` (`inversion/abstract.py:366`) is a dense
  `xp.add(curvature_matrix, regularization_matrix)` feeding the dense solve for
  the reconstruction. `H` must still be formed there. Only the *evidence* terms
  can avoid the explicit inverse. Any future attempt needs an iterative-solver
  design first, which is a different task.

**Leg 2a — `s^T H s` implicit — SHIPPED 2026-08-09** on branch
`claude/automind-task-planning-gm4flt` (PyAutoArray). The one genuinely open
piece: `regularization_term` (`inversion/abstract.py:698`) contracted the formed
`H`. For the kernel schemes the term is `coefficient * s^T C^-1 s`, from one
Cholesky solve against `s` instead of forming `C^-1` and contracting it.

Built to the exact shape of the shipped log-det shortcut: a
`regularization_term_from` hook on `AbstractRegularization` returning `None` by
default, overridden by the four kernel schemes, consulted by
`AbstractInversion.regularization_term` behind a new opt-in
`Settings.regularization_term_method` (`"matmul"` default, `"cho_solve"`
opt-in). Deliberately a *separate* setting from `log_det_method` so the two
evidence terms can move onto their exact factorizations independently — that is
what makes an evidence shift attributable to one term rather than both. Default
evidence values unchanged, so archived comparability holds (the constraint the
#391 adversarial probe verdict imposed).

Measured gain on a clustered fixture at `cond(C) = 3.2e9`, graded against an
exactly-known reference (`s = C v` makes `C^-1 s = v`, so the true form is
`s^T v`): relative error **5.99e-08 explicit vs 2.93e-16 implicit** — the
implicit path is at machine precision, confirming this prompt's
~1e-6..4e-5 noise-floor measurement was the explicit inverse.

Two traps found and pinned by tests: `MaternAdaptKernel` passes
`coefficient=0.0` to `MaternKernel.__init__` (its weights live inside `C_w`), so
inheriting the parent term would silently zero it — it needs its own override;
and `GaussianKernel`'s formed matrix carries a symmetrisation + trace-scaled
jitter the shortcut excludes, matching how its log-det shortcut already behaves.
Schemes with no factorization return `None`, and one `None` falls the whole
computation back to the formed matrix, so mixed inversions stay correct.

9 new tests in `test_autoarray/inversion/regularizations/test_kernel_regularization_term.py`.
Full inversion suite green (244 passed, 9 skipped).

**Leg 2b — jitter scaling — SHIPPED 2026-08-09** on the same branch.

Investigated before designing, and the prompt's framing ("scale with the
kernel's dynamic range / N") turned out to point at a real and more serious
problem than "cheaper interim" suggests. The jitter is a fixed absolute
`1e-8 * I`, which is only meaningful when `diag(C) ~ 1`. That holds for the
three unweighted kernels (`K(0) == 1`, measured) but NOT for
`MaternAdaptKernel`, whose `C_ii = w_i²` spans the adaptive-weight dynamic
range. Measured distortion of the faintest pixel on a 40-pixel fixture:

| inner/outer | faintest `C_ii` | distortion |
|---|---|---|
| 1.0 / 1.0 | 1.0e+00 | 1.0e-08 |
| 0.5 / 4.0 | 3.9e-03 | 2.6e-06 |
| 1.0 / 20.0 | 6.3e-06 | 1.6e-03 |
| 0.1 / 100.0 | 1.0e-08 | **1.0e+00** |

`inner_coefficient`/`outer_coefficient` are **free model parameters**, so a
sampler can walk into the bottom row mid-fit, at which point the jitter is 100%
of the faintest pixels' variance and their kernel structure is gone. Silent —
no exception, no NaN, just wrong smoothing.

Fix: `jitter_relative=True` applies `jitter * diag(diag(C))` (`C_ii *= 1 + jitter`).
With `C = D^½ R D^½` for correlation matrix `R`, that is exactly
`D^½ (R + jitter·I) D^½` — the jitter lands on the *correlation* matrix, so every
pixel gets the same relative protection whatever its scale.

One rejected design worth recording so it is not retried: `jitter = N·eps·max(diag)`
("as small as possible above the round-off floor") fixes the distortion but lets
`cond(C)` reach **3.2e15** on smooth clustered vertices — the edge of float64,
reintroducing exactly the noise leg 2 exists to remove. The correlation-relative
rule instead leaves conditioning *unchanged* (3.16e9 both ways, measured).

Default `False` everywhere, byte-identical to previous behaviour. Threaded
through all three covariance call sites per scheme, not just the constructor
(pinned by a test). 7 new tests in `test_kernel_jitter_relative.py`.

**This prompt now has no open work.** Both remaining legs are shipped; the file
is ready to advance to `complete/` once the branch merges. Note the JAX leg of
the gate (`jax_grad/regularization.py` re-passing) is still owed — it lives in
`autolens_workspace_test` and needs `tfp-nightly`, neither available in the
session that did this work.

Gate any change on the `regularization.py` jax_grad script re-passing and
on FoM parity on the numpy path.

## 3. Split-family shape guard on rectangular meshes (papercut) — DONE

*Shipped 2026-07-28 as phase 1 of the @rhayes777 audit epic —
PyAutoArray#417 (`9411904d`), merged. The first of the two options below is what
landed: `Pixelization.__init__` (`autoarray/inversion/pixelization.py:154`)
raises `PixelizationException` on any split regularization × rectangular mesh,
driven by `AbstractMesh.supports_split_regularization` ×
`AbstractRegularization.is_split_regularization`, with all 9 combinations
covered by `test_autoarray/inversion/pixelization/test_split_regularization_support.py`.
True pixel-centre crosses for the rectangular geometry were deliberately NOT
implemented — the capability is absent by design. The
`rectangular_adapt_constant_split_guard.md` merge question this section raises is
therefore moot; that prompt was recorded as complete on 2026-08-09
([[rectangular-adapt-constant-split-guard]]). Verified by the draft/ sweep against
main `efaf3041`. **All legs are now shipped — see the status block under leg 2.***

`ConstantSplit`/`AdaptSplit`/`AdaptSplitZeroth` on a rectangular mesh fail
with a raw broadcasting `TypeError` ((784,784) vs (3808,3808)): the split
machinery assumes 4-cross-per-pixel splits, while the rectangular
interpolator reuses its per-query 4-corner mappings for
`_mappings_sizes_weights_split`. Either raise a clear
"split regularization requires a Delaunay-family mesh" exception at
composition time, or implement true pixel-centre crosses for the
rectangular geometry (relates to
`draft/feature/autoarray/rectangular_adapt_constant_split_guard.md` if that
covers the same surface — merge at intake if so).

## Out of scope

- `ConstantZeroth` dead code — already filed
  (`draft/bug/autoarray/constant_zeroth_broken_dead_code.md`).
- `CurvatureMask`/`FourthOrderMask` — dpsi (potential-correction) schemes,
  correctly incompatible with source meshes; nothing to fix.
- Making neighbour-based schemes (`Constant`/`Adapt`) JAX-traceable on the
  Delaunay mesh family (kNN-derived neighbours) — bigger design question,
  only worth filing if a production pipeline needs it.
