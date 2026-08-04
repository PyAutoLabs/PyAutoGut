# Three JAX-gradient scripts TIMEOUT at the 300s smoke cap

Type: bug
Target: PyAutoHeart
Repos:
- PyAutoHeart
- PyAutoHands
- autolens_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

## Original request (verbatim)

> 4. Three JAX-gradient script timeouts
>
> In the PyAutoLabs workspace, three scripts TIMEOUT at the 300s smoke cap:
>
>   autolens_workspace_test scripts/imaging/jax_grad/pixelization.py
>   autolens_workspace_test scripts/imaging/jax_grad/regularization.py
>   autolens_workspace_test scripts/point_source/jax_grad/gradient.py
>
> Evidence: PyAutoHeart workspace-smoke run 30858578587
> (2026-08-03T22:25Z), jobs "smoke / run_scripts (3.12, autolens_test,
> imaging)" and "(3.12, autolens_test, point_source)". All three are
> TIMEOUT, not error — they never finished.
>
> Work out whether this is real slowdown (JIT compile-time regression,
> lost caching) or just a cap that was always marginal for these three:
> check whether they ever passed in smoke and how close they were. Compare
> against Heart's script_timing baselines if there's history. Fix the
> cause, or — with an explicit reason — reclassify them; don't just raise
> the cap silently. Route through start_dev.

## Diagnosis (evidence gathered 2026-08-04, pre-plan)

**Verdict: NOT a slowdown regression. The 300s smoke cap was never adequate for
this class of script.**

### Negative control — the siblings got FASTER

All seven `jax_grad` scripts declare `ENV: jax full_datasets`, so they share one
JAX stack and one env profile. If JIT compile time or caching had regressed, the
cheap ones would have regressed too. They did not:

| script | Heart baseline | run 30790463134 (06:31Z) | run 30858578587 (22:25Z) |
|---|---|---|---|
| `imaging/jax_grad/lp.py` | 45.99s | PASS 40.0s | PASS 39.6s |
| `imaging/jax_grad/mge.py` | 48.65s | PASS 42.1s | PASS 41.8s |
| `imaging/jax_grad/delaunay.py` | — | PASS 84.6s | PASS 92.4s |
| `imaging/jax_grad/knn.py` | — | PASS 175.8s | PASS 200.0s |
| `imaging/jax_grad/pixelization.py` | — | **PASS 244.8s** | **TIMEOUT (300s)** |
| `imaging/jax_grad/regularization.py` | — | FAIL 103.5s (import) | **TIMEOUT (300s)** |
| `point_source/jax_grad/gradient.py` | 39.24s (stale, see below) | **TIMEOUT (300s)** | **TIMEOUT (300s)** |

`lp.py` and `mge.py` both run ~13% FASTER than their Heart baselines. There is no
shared-infrastructure slowdown to find.

### Per-script findings — three different stories, none of them a regression

1. **`pixelization.py` — always marginal, never had headroom.** Its one smoke pass
   was 244.8s = **82% of the cap**, 16 hours before the failure. Ordinary runner
   variance tips that over. Independently corroborated: the existing prompt
   `draft/feature/profiling/profiling_agent_jax_compile_time_scope.md` records this
   same script (then `jax_grad/imaging_pixelization.py`) at **>400s** on 2026-07-13.
   A script known to take >400s was never going to fit a 300s cap.

2. **`regularization.py` — has never once completed in smoke.** Its only prior
   result, FAIL (103.5s), was the `tfp-nightly`/`bessel_kve` import gap documented
   in `workspace-validation.yml:249-254`, not a timing result — it died at import
   before doing the work. Once that install gap was closed, its true cost surfaced
   for the first time and exceeds 300s. **There is no passing baseline to regress
   from.**

3. **`gradient.py` — TIMEOUT in both runs; never passed in smoke.** Heart's 39.24s
   baseline is for the *pre-restructure* `jax_grad/point_source.py`, measured
   2026-07-30 — **before** commit 50f1c33 (2026-07-31) added solver-gradient blocks
   C–F: a `pixel_scale_precision=1e-5` solver (100× finer than production) plus
   6-step FD sweeps across four additional models. The script grew ~8×+ **by
   design**; the baseline describes a different script.

### Root cause of the mismatch

These scripts declare `ENV: jax full_datasets`, which opts them OUT of the smoke
reductions (`PYAUTO_TEST_MODE=2`, `PYAUTO_SMALL_DATASETS=1`,
`PYAUTO_DISABLE_JAX=1`). They therefore do the **same full-resolution
finite-difference work in smoke as in release**.

The release leg already recognised exactly this and set `BUILD_SCRIPT_TIMEOUT: 1800`
with a written rationale (`workspace-validation.yml:319-326`: *"mode=release runs
REAL searches and finite-difference JAX gradient scripts, which legitimately exceed
the 300s smoke cap"*) — but deliberately left smoke at 300s on the premise that
smoke work is reduced. **For this script class that premise is false.** The smoke
exemption was omitted on reasoning that does not hold for `full_datasets` scripts.

### Fix constraint (grounded, not assumed)

`PyAutoHands/autohands/build_util.py:12` reads
`TIMEOUT_SECS = int(os.environ.get("BUILD_SCRIPT_TIMEOUT", "300"))` **once at import
in the parent runner**, and applies it as `subprocess.run(..., timeout=TIMEOUT_SECS)`.
Per-script env from `profile_smoke.yaml` is injected into the **child** env only, so
a per-script `BUILD_SCRIPT_TIMEOUT` override **cannot work today** — a per-script or
per-class timeout requires plumbing in PyAutoHands.

### Two secondary defects found while investigating

- **Heart's script_timing baselines are orphaned.** The slug is path-derived, so the
  #216 restructure (`scripts/jax_grad/imaging_lp` → `scripts/imaging/jax_grad/lp`)
  stranded every old entry. No new-layout slug exists for any of these scripts, so
  Heart is accumulating no history for them.
- **Every timing history is one value repeated 7×** (a rolling-window fill, not 7
  observations), so the "median of 7" regression ratio is really a
  single-observation comparison.

### Scope note

`knn.py` at 200.0s (67% of cap, up from 175.8s) is the next to fall and should be
covered by whatever decision is taken.

Out of scope for this task (other failures in the same run): `autolens_test,
interferometer`, `autofit_test, jax_assertions`, `howtogalaxy,
chapter_4_pixelizations`.

<!-- Evidence gathered 2026-08-04 from PyAutoHeart runs 30858578587 and 30790463134
     (job logs), ~/.pyauto-heart/timings/, and workspace-validation.yml. -->
