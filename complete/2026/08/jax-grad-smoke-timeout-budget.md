Three `autolens_workspace_test` jax_grad scripts TIMEOUT at the 300s smoke cap
(PyAutoHeart workspace-smoke run 30858578587). The question asked was whether
this was a real slowdown (JIT compile regression, lost caching) or a cap that
was always marginal — fix the cause, or reclassify with an explicit reason, but
do not raise the cap silently.

## Verdict: a marginal cap, not a slowdown — measured, not argued

Measured on PyAutoHeart workspace-smoke run 30938311069, the first run in which
these scripts could finish. All seven live jax_grad scripts PASS:

| script | 06:31Z | 22:25Z | after |
|---|---|---|---|
| lp.py | 40.0s | 39.6s | 41.6s |
| mge.py | 42.1s | 41.8s | 41.2s |
| delaunay.py | 84.6s | 92.4s | 89.6s |
| knn.py | 175.8s | 200.0s | 186.5s |
| pixelization.py | 244.8s | TIMEOUT | 259.8s PASS |
| regularization.py | FAIL (import) | TIMEOUT | 301.7s PASS |
| gradient.py | TIMEOUT | TIMEOUT | 568.2s PASS |

The regression hypothesis is dead. It was deliberately kept open because the
2026-08-03 slowdown scaled monotonically with runtime (-1% at 40s to +23% at
245s), which fits a graph-size-dependent XLA regression as well as contention,
and the flat cheap scripts did NOT discriminate between them. It resolves as
contention: pixelization.py returned 259.8s against its 244.8s baseline (+6%,
ordinary variance), and knn.py (200.0 -> 186.5) and delaunay.py (92.4 -> 89.6)
both came back DOWN. A graph-size regression does not undo itself.

Per script: pixelization.py was always marginal (82% of cap, no headroom to
absorb a slow runner). regularization.py exceeded the cap by 1.7 SECONDS — it
never was far too slow, and the tfp-nightly/bessel_kve import gap masked that
until the install was fixed. gradient.py is 1.9x the cap, having grown by design
in 50f1c33 (+281 lines, 1e-5 solver, 6-step FD sweeps over four extra models).

## Shipped

- PyAutoHands#227 -> 52408a84. `build_util.timeout_for(env)` resolves the cap
  parent-side for execute_script + execute_notebook; the TimeoutExpired handlers
  keep a truncated output tail and record the cap in force; the SLOW banner says
  "default" cap. 25 tests, control-tested (11 fail against the unfixed
  behaviour).
- PyAutoHeart#138 -> 1bdf8188. Comment-only: corrects the release cap's "smoke
  mode is unchanged (still 300s)" premise.
- autolens_workspace_test#249 -> a430ea61. The `jax_grad/` budget, plus the
  second-runner fix.
- autolens_workspace_test#250 -> 527c1669. Tightens 1800s -> 900s on measured
  durations (~1.6x headroom over the 568.2s worst case).

Heart effect: the workspace-validation YELLOW reason went from "3 failed, 3
timeout" naming these scripts to "2 failed" naming only autolens (not _test)
interferometer likelihood_function — pre-existing and out of scope.

## Two defects found that were not in the brief

1. **The timeout artefact was blind.** `build_util` discarded
   `TimeoutExpired.stdout/stderr`, recording only "Timed out after Ns". A killed
   script cannot report its own progress, so no CI artefact could say WHICH
   block died — the reason this was undiagnosable from CI at all. Fixing that
   first is what made the measurement legible.
2. **A second runner had the same bug.** `autolens_workspace_test/.github/
   scripts/run_smoke.py` builds the per-script env via `build_env_for_script`
   but capped `proc.communicate(timeout=...)` with its own module-global, so the
   PR gate would have silently ignored the very budget #249 adds — the two
   runners disagreeing about the same profile. Latent (smoke_tests.txt has no
   jax_grad entries) but fixed rather than left as a trap.

## Corrections made during the work

- **">400s on 2026-07-13" withdrawn.** Cited as corroboration that
  pixelization.py was always marginal; commit 74673c8 (07-23) rewrote both
  gradient scripts, so it described an ancestor. Caught by Codex cross-review.
- **"Not a regression" was initially too strong** and was softened to "not
  established" until the measurement settled it.
- **A projection was wrong.** gradient.py was projected at ~940s in CI from a
  local 665.9s scaled by knn.py's CI/local ratio (~1.41x). The real figure is
  568.2s — CI is FASTER than local for that script, so the ratio did not
  transfer. Conclusion held; the extrapolated number did not. #250 records
  "measure, do not extrapolate".
- **A `timeout:` profile key would have failed validation**
  (ALLOWED_OVERRIDE_KEYS is {pattern, set, unset}); the existing `set:` key was
  used instead, so no profile schema change and every existing profile stays
  valid. Also caught by Codex.

## Method notes worth keeping

- The `lp.py` CONTROL is what prevented reporting two phantom correctness
  regressions: it fails locally while PASSING in CI, so the local
  eager-vs-jit and AD-vs-FD failures in pixelization/regularization were
  environment artefacts, not source defects. Never budget from local jax_grad
  numbers.
- Precedence is profile > ambient global > 300 default, because `run_all.py:256`
  exports BUILD_SCRIPT_TIMEOUT unconditionally — the parent cannot tell a
  deliberate operator cap from the CLI default, so "explicit global wins" would
  make per-script budgets work in CI and be silently ignored locally.
- Brain sized this too-large (13) with a 4-phase split; not taken, the score is
  prose-driven off an evidence-dense prompt.

## Follow-ups filed (not absorbed)

- `draft/bug/pyautoheart/script_timing_baselines_orphaned_and_window_filled.md`
  — path-derived slugs orphaned every jax_grad baseline at the #216 restructure
  (no history accumulating since 2026-07-24), and every stored history is one
  value repeated 7x, so the "median of 7" ratio is a single-observation compare.
- `draft/bug/autolens_workspace_test/jax_grad_local_assertions_fail_but_pass_in_ci.md`
  — the local-vs-CI assertion divergence above (suspect numpy 2.2.6 vs 2.4.6).

## Original prompt

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
