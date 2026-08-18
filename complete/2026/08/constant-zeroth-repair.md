- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/448 (CLOSED completed)
- pr: https://github.com/PyAutoLabs/PyAutoArray/pull/449 — MERGED 2026-08-18 as `74cf5a0`, 2 files, +99/-1
- classification: library (PyAutoArray) — bug, Phase 8C of the inference programme (autolens_profiling#134)
- branch: `feature/constant-zeroth-repair` (remote cloud session; the issue's suggested branch, not the session's `claude/…` default)
- worktree: none — remote-handoff task by design (CPU-only, numpy-only tests); no local claim was ever made

## What was wrong

`al.reg.ConstantZeroth` was dead code presenting as a public feature — two
independent defects in `autoarray/inversion/regularization/constant_zeroth.py`,
both reproduced on clean main (`7d1906e`) before any fix (tracebacks on #448):

1. **`eye(P)` shape bug** — the zeroth term was `xp.eye(P)` with
   `P = neighbors.shape[1]` (neighbour-column count, e.g. 4), not `S` (mesh
   pixel count), so `const + zeroth` raised a broadcast `ValueError` whenever
   `S != P`.
2. **Missing `neighbors_sizes` at the class API** —
   `ConstantZeroth.regularization_matrix_from` omitted the required argument,
   raising `TypeError` before the shape bug was even reached.

## Fix

Zeroth term is now the full `S x S` scaled identity
(`xp.eye(S) * coefficient_zeroth**2`, matching `zeroth.py`'s `eye(pixels)`
semantics); the class API threads `neighbors_sizes=linear_obj.neighbors.sizes`
mirroring `Constant`. Siblings `adapt_split_zeroth.py` / `brightness_zeroth.py`
checked clean — their zeroth terms are `xp.diag` over per-pixel weights, no
copy-paste pattern. Four numpy-only tests added
(`test_autoarray/inversion/regularizations/test_constant_zeroth.py`): shape
`(S, S)` with `S != P`, no null mode (`min eigvalsh >= lambda_z^2`), reduction
to Constant `+ lambda_z^2 * I`, class-API smoke. Constant/Adapt/AdaptSplit
numerics and `autoarray/__init__.py` untouched.

**Null-mode-lift verification** (9-pixel rectangular fixture,
`lambda_n = lambda_z = 1`): Constant min eigenvalue `1e-8` (jitter-floor null
mode, condition number `6e8`) → ConstantZeroth min eigenvalue `1.0 = lambda_z^2`
(condition number `7.0`); element-wise residual against `Constant + lambda_z^2 I`
exactly `0.0`. Recorded in the PR body for Phase 8C to cite. The fix makes the
scheme WORK; it does not recommend it over AdaptSplit.

## Traps and findings

- **No numerics or unique-identifier impact.** The class API raised
  unconditionally, so no fit anywhere ever produced a likelihood through it;
  `__init__` and instance attributes are unchanged, so PyAutoFit identifiers
  (built from model composition, not method bodies) are stable — no output
  paths orphaned.
- **One silent-wrongness edge existed in the old code:** with `P == 1` the
  `(S,S) + (1,1)` broadcast *succeeded* and added `lambda_z^2` to every element
  instead of the diagonal. Pathological mesh, unreachable via the class API,
  now correct — but any hand-rolled direct util call on such a mesh would
  (correctly) change value.
- **`zeroth.py` observed but not touched:** its class API drops `xp`
  (`zeroth_regularization_matrix_from(..., pixels=...)` without `xp=xp`) — a
  latent JAX-backend drop, out of scope here, worth a hygiene glance.
- **Remote-container environment traps:** `autonerves` requires Python >=3.12
  while the container default is 3.11 (use `uv venv --python 3.12`); the full
  suite needs the dev extras `numba` and `pynufft` or 4 tests fail on import;
  the 3 `test__nufft_pynufft__*` transformer tests fail regardless on modern
  scipy (`scipy.linalg.pinv2` removed, inside pynufft) — pre-existing on clean
  main, unrelated. Final run: 988 passed, 59 skipped, those 3 env failures.
  Repo CI (3.12/3.13) was fully green on the PR.

## Original prompt

# ConstantZeroth regularization is broken twice over — dead code presenting as a feature

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

Found during the reg-logdet investigation (autolens_workspace_developer#104
follow-up), and **independently confirmed by a second reviewer who actually ran
it**. `al.reg.ConstantZeroth` has never worked through its class API — it raises
before returning a matrix — yet it is a public, exported scheme
(`autoarray/inversion/regularization/__init__.py`).

Two distinct defects in `autoarray/inversion/regularization/constant_zeroth.py`:

1. **Shape bug.** `constant_zeroth_regularization_matrix_from` builds the
   neighbour term `const` as an `S x S` matrix (`S` = number of mesh pixels) but
   then builds the zeroth term as `xp.eye(P)` where `P = neighbors.shape[1]` is
   the **neighbour count** (e.g. 4), not `S`. `const + zeroth` therefore
   broadcasts `900x900 + 4x4` and raises. `constant_zeroth.py:68-72`:
   ```python
   reg_coeff = coefficient_zeroth**2.0
   zeroth = xp.eye(P) * reg_coeff        # P is the neighbour count, should be S
   return const + zeroth
   ```
   The zeroth-order term is meant to be a full `S x S` scaled identity
   (`+lam_z^2` on every pixel's diagonal), which is precisely the term that would
   lift the graph-Laplacian null mode and make this scheme well-conditioned.

2. **Missing-argument bug.** `ConstantZeroth.regularization_matrix_from` (the
   class API path) does not pass `neighbors_sizes` to
   `constant_zeroth_regularization_matrix_from`, so a correctly-shaped call raises
   `TypeError` before reaching the shape bug. Verify the exact call site and
   signature.

**Why this matters beyond "a broken scheme":** in the reg-logdet investigation,
`ConstantZeroth` was hypothesised to be the *already-correct* answer — a scheme
that adds a genuine model-scaled zeroth-order term (`+lam_z^2 * I`) lifting the
null mode, immune to the `1e-8`-below-the-noise-floor conditioning collapse that
afflicts `Constant`/`Adapt`. That hypothesis is **dead on arrival** because the
scheme itself is dead. Fixing it would resurrect a genuinely useful,
well-conditioned regularization option — and is a prerequisite for "just point
users at the zeroth-order variant" ever being a real answer.

Task: reproduce both failures on clean main FIRST (a two-line call through the
class API, then through the function with correct args). Then fix the `eye(P)` →
`eye(S)`/`S x S` shape and thread `neighbors_sizes`. Check the sibling
`adapt_split_zeroth.py` and `brightness_zeroth.py` for the same `eye(P)` / missing
-arg pattern — they may share the copy-paste. Add a unit test that builds the
matrix and asserts shape `(S, S)` and positive-definiteness (the whole point of a
zeroth-order term is that the result has NO null mode). Numpy-only test per repo
policy.

Do NOT bundle this with the reg-logdet log-det change or the Adapt double-square
probe — it is an independent, self-contained defect.
