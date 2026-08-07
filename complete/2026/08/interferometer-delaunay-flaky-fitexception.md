Phase 2 (the correctness half) of the intermittent interferometer-Delaunay
`FitException`. Phase 1 had already made the flake non-fatal; this fixes the
numerical producer so the fit is correct rather than merely tolerated.

## PRs

- **PyAutoArray#436** MERGED 2026-08-07 (`efaf3041`) — Phase 2, the producer fix.
  CI green first run on both matrix legs (3.12 + 3.13), `mergeable_state: clean`,
  3 files +229/-2.
- Phase 1 (earlier, both merged): **PyAutoFit#1408** (TEST_MODE=2 bypass tolerates
  a single-eval `FitException` as a resample-to-reject sentinel) and
  **autolens_workspace#311** (un-park the script + add it to smoke).

## The finding that mattered: the filed root cause was wrong

The issue and prompt both named `fnnls.py:134` (`alpha = np.min(d[q] / (d[q] -
s_chol[q]))`) as "the smoking gun", on the evidence that 45/250 phase-1 draws
emitted divide-by-zero `RuntimeWarning`s there. **It is not the producer.** Line
134 was exercised 599 times across 600 constraint-binding draws with *zero*
degenerate denominators. Those warnings are a downstream symptom. The line is
unchanged by this fix. Anyone resuming from the issue text alone would have
chased it — #640 now carries a correction comment.

## Actual producer: `cholesky_funcs.py` -> `cholinsertlast`

    S[index, index] = s22 = math.sqrt(x[index] - S12.dot(S12))   # unchecked

Two (near-)coincident source-mesh vertices give (near-)identical mapping-matrix
columns, so the normal-equations matrix is singular to working precision and the
Schur complement is **zero to within rounding** — measured at +-1.776e-15 (8*eps).
Which side of zero it lands on is decided purely by floating-point summation
order, i.e. **by the BLAS thread count**. That is the whole explanation for the
CI-vs-local thread dependence, and why phase 1's 250 local draws came back clean.

Measured over 60 exactly-singular draws, the same matrix failed three ways:
tiny-negative -> `ValueError` (raised, visible); **exactly 0.0 (27/60)** -> zero
pivot; **tiny-positive (19/60)** -> pivot ~4e-8 amplified by `cho_solve`. The last
two returned **NaN without raising**.

## Why it surfaced a stage away from its cause

`inversion_util.py:365` guards the solver with `except (RuntimeError,
LinAlgError, ValueError)` — a NaN raises none of those. So the NaN escaped as a
valid-looking reconstruction -> poisoned `adapt_data` -> `hilbert.py:275-284`
places mesh vertices from `adapt_data` with no NaN guard -> `scipy.spatial.Delaunay`
rejected them in `source_pix_2`. Cause and symptom sat in different files, in
different repos' call paths, one pixelization stage apart.

## TRAP: the first fix changed likelihood evaluations

The first implementation gated on a **relative tolerance** (`eps * index *
abs(diagonal)`). It looked principled and was wrong: measured against the old
code it converted **7/300 degenerate cases that had returned finite, plausible
reconstructions (max 0.26-0.46) into exceptions**. That is a silent change to
every likelihood evaluation touching a near-singular matrix. It was caught only
because a bitwise old-vs-new harness was built to check, on a mid-flight human
instruction ("make sure this won't change likelihood evaluations") — not by
reasoning. **Discarded.**

The shipped test is `schur > 0` and nothing stricter: `schur < 0` already raised
(`LinAlgError` subclasses `ValueError`, so existing handlers still catch it),
`schur == 0` yields NaN with certainty so there is no finite result to preserve,
and any positive Schur complement passes through returning a **bitwise identical**
pivot. Lesson: for a numerical guard, "reject the provably-broken condition" beats
"reject the suspicious-looking region" — and the difference is only visible if you
diff old-vs-new outputs bitwise.

## Invariance evidence (verified, not asserted)

- 800 old-vs-new problems (realistic + degenerate): **708 bitwise identical, 92
  raise in both, 0 finite->raise, 0 numerically different**.
- jitter-sweep `clean` counts identical pre/post: 115 / 82 / 71 / 71 / 120.
- full `test_autoarray` locally: 855 -> 887 passed with the **same 16 pre-existing
  failures** (env artefact: py3.11 vs the >=3.12 requirement, plus missing optional
  deps — baselined by stashing the diff and re-running).
- CI (the real 3.12/3.13 matrix, full deps): green on both legs first run, which
  is what actually validated the 32 new tests on supported Python.

## Tests

`test_autoarray/util/test_cholesky_degenerate.py` — 32 deterministic NumPy-only
tests: the pivot invariant (raise, or a strictly positive finite pivot — never
zero/non-finite), rejection of a non-positive Schur complement, bitwise
pass-through of a positive one, no non-finite solution across the near-degenerate
jitter band, no false positives on well-conditioned constraint-binding problems,
and that the raised type falls inside the inversion guard's except-tuple.

## Limit — stated, not papered over

The repro is **unit-level and deterministic** (thread-independent), which is
stronger than the CI-only flake for regression purposes. It was **NOT** executed
end-to-end through `source_pix_2`: the session container had no autolens stack and
ran py3.11 against a >=3.12 requirement. The `source_pix_2` link is established by
code reading (`inversion_util` guard -> `adapt_data` -> `hilbert.py:275-284`), not
by a run. Whether the workspace script still ever flakes is now only provable by
CI over time; the phase-1 tolerance means a residual occurrence would be
non-fatal.

## Environment note (web-github session)

No worktree root; operated on the `/home/user/` clones with
`PYTHONPATH=/home/user/PyAutoNerves:/home/user/PyAutoArray` and numpy/scipy/pytest/
matplotlib/dill/astropy pip-installed into the container. `prompt_sync_push` tried
to push PyAutoMind `main` (rejected non-fast-forward — local main is behind
origin); left alone deliberately rather than forced, work pushed to the designated
branch instead.

## Original prompt

# Interferometer Delaunay intermittent FitException (qhull NaN vertices + non-PD inversion)

Type: bug
Target: autoarray
Repos:
- PyAutoArray
- PyAutoLens
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

Surfaced 2026-07-21 while un-parking the Delaunay cluster (autolens_workspace#307, follow-up to
#300/#301). The **imaging** Delaunay is fixed and now smoke-gated; the **interferometer** Delaunay
is genuinely green *most* of the time but **flaky**: CI ran the identical commit (dce04672) twice and
py3.12 smoke FAILED on the push event with

    ValueError: Points cannot contain NaN   (scipy.spatial.Delaunay / qhull)
    [FAIL (exit 1)] interferometer/features/pixelization/delaunay.py

while PASSING on the pull_request event. Locally it passes 4/4 full-script runs and 20/20 random
prior-instance `fit_from` draws, so the failure rate is low (~1-in-N) and RNG/data/float-sensitive.

The old `(2,2) vs (1032,1032)` broadcast (the original 2026-04-10 symptom) is **gone** — this is a
distinct, intermittent NaN. It is currently parked in
`autolens_workspace/config/build/no_run.yaml` with an accurate note; HowToLens has no interferometer
Delaunay script.

## Hypothesis / where to look

A traced + border-relocated source-plane mesh vertex is occasionally NaN, which
`scipy.spatial.Delaunay` (qhull) rejects. The mesh vertices come from the image-plane `Overlay`
grid ray-traced by the mass model, then passed through `BorderRelocator`. Under
`PYAUTO_SMALL_DATASETS=1` the real-space mask is capped to 15x15, so heavily demagnified /
edge points near the mass centre may trace to inf/NaN for a small fraction of configs.

Likely loci:
- `PyAutoArray/autoarray/inversion/mesh/interpolator/delaunay.py` — the `scipy.spatial.Delaunay`
  call (guard/clean NaN vertices, or fail loudly with a diagnostic).
- `PyAutoArray/autoarray/inversion/mesh/border_relocator.py` — relocation producing NaN.
- `PyAutoLens` tracing of demagnified points to NaN in the interferometer path.

## Two masked signatures — both surface as `FitException` (reconcile before fixing)

The `FitException` at `analysis.py:182` masks the true error (`analysis.py:175-182`, numpy path,
wraps ANY exception → `af.exc.FitException`; PR#607 parity guard so the sampler resamples). In
`TEST_MODE=2` there is no sampler, so a single bad-eval instance hard-fails the script. Two distinct
underlying errors have now been observed for this same script — determine whether they share one
root (a degenerate Delaunay mesh) or are independent:

1. **qhull NaN vertices (this prompt's CI evidence, autolens_workspace#307):** `ValueError: Points
   cannot contain NaN` from `scipy.spatial.Delaunay` — a traced/relocated source-plane mesh vertex
   is NaN, *before* the inversion. Intermittent (~50% CI py3.12, `dce04672`).
2. **non-PD / singular inversion (closed #309's diagnosis):** numpy cholesky raises where JAX
   NaN-resamples — a non-PD/singular matrix in the interferometer Delaunay inversion (candidate:
   `log_det_regularization_matrix_term` for `ConstantSplit` at fixed `coefficient=1.0`, or the
   linear solve). This is the interferometer tail of the pix-NaN lineage (imaging half resolved:
   autogalaxy_workspace#140, PyAutoArray#391/#392 opt-in `slogdet`).

**Prime-suspect debunk:** PyAutoArray#396 (SMALL_DATASETS grid even-cap 15→16) was already merged
(`656be94b`) and *in* the failing #307 CI run, so it does NOT fully fix this — the failure persists
with the even cap. (#308 closed the marker as "stale/green" on local runs; CI overturned that, and
the no_run entry stayed parked with an accurate intermittent-NaN note.)

## Fix tiers (from #309 — choose by what reproduction shows; do NOT silently swallow the FitException)

- **T1 workspace:** opt the script into `log_det_method="slogdet"` (already in `al.Settings`) —
  cleanest if the non-PD is the log-det term and slogdet yields finite; default path unchanged.
- **T2 PyAutoLens** (`interferometer/model/analysis.py`): make the `TEST_MODE` bypass tolerate a
  single-eval `FitException` as a resample signal (sentinel low FOM) instead of hard-failing.
- **T3 PyAutoArray:** if the `ConstantSplit` reg matrix is genuinely degenerate on the Delaunay
  mesh (zeroed edge points → exact-zero rows) or the mesh has NaN vertices, fix conditioning /
  the NaN at the producer.

## First step

Reproduce **both** signatures deterministically: run the interferometer Delaunay modeling fit many
times (or sweep many mass-model instances) under `PYAUTO_TEST_MODE=2 PYAUTO_SMALL_DATASETS=1
PYAUTO_DISABLE_JAX=1` until (1) a NaN vertex and (2) a non-PD cholesky both appear; trace which
grid/relocation step introduces the NaN and whether the non-PD is the reg log-det or the solve.
Prefer fixing the producer (no silent None/NaN guards). Once robust, un-park the no_run entry and
add the script to the smoke gate (alongside the imaging Delaunay already added in #307).

Refs (all closed): autolens_workspace#300 (re-park), #307 (imaging added + interferometer kept
parked w/ CI flake evidence), #308 (drop-marker, closed), #309 (non-PD re-diagnosis, closed as dup).
Related: pixelization-inversion-not-PD, pix-NaN lineage (reg log-det slogdet fix).

## Reproduction evidence (2026-07-21, start_dev)

- **True flake, not a library race:** #307's two CI runs on the SAME commit (`dce04672`) started
  ~1 min apart (16:22 vs 16:23) and NO PyAutoArray/PyAutoLens main merge occurred in that window —
  yet one py3.12 run failed (qhull NaN) and one passed. Same code, same libraries.
- **Local repro is hard / environment-sensitive:** 250 random prior-instance `fit_from` draws on
  current main = 250/250 clean (0 raised) — the failure did NOT reproduce locally, consistent with
  a CI-runner thread-count / BLAS FP-summation-order dependence.
- **Smoking gun producer:** 45/250 draws emitted `RuntimeWarning: invalid value / divide by zero`
  at `PyAutoArray/autoarray/util/fnnls.py:134` (`alpha = np.min(d[q] / (d[q] - s_chol[q]))`) —
  frequent NaN/inf in the NNLS solver, usually benign locally but a candidate source of the
  occasional fatal NaN/non-PD on CI. (Note: confirm which solver path the script's modeling uses —
  it sets `use_positive_only_solver=False`, while a default analysis uses the positive/fnnls path.)

## Phasing (Bug Agent: multi-repo, flaky, split-into-phases)

- **Phase 1 — un-flake test-mode (PyAutoLens + autolens_workspace, small, environment-independent):**
  make the `TEST_MODE` bypass tolerate a single-eval `FitException` the way a real sampler does
  (resample / sentinel low FOM) instead of hard-failing — `analysis.py:175-182`. This un-flakes ALL
  FitException-prone pixelization scripts in test-mode, not just this one, and does not mask real
  breakage in a real fit. Then un-park the interferometer Delaunay `no_run` entry + add to smoke.
  (Log the tolerated FitException so it stays visible.)
- **Phase 2 — fix the numerical producer (PyAutoArray, deeper, separate PR):** guard/repair the
  `fnnls.py:134` divide-by-zero and/or the traced-mesh NaN / non-PD conditioning at the producer
  (no silent guards — fix the math). Reproduce on CI-like thread counts first.
