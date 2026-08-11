A collapsed hierarchical parent **scale** hyperparameter is no longer reported
as a confident answer. Leg 1 of PyAutoFit#1405 follow-up 2.

- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1464 (leg 1 only; the
  umbrella #1405 stays **open** — leg 2, curing the collapse basin, is untouched)
- pr: PyAutoFit#1465 — MERGED as `26470dbf`, base `18aae0f3`, +275/-13 across 3
  files. All three checks green (docs-build, unittest 3.12, unittest 3.13).
- shipped: `EPDiagnostics.register_hierarchical_scales` + `scale_variables`; a
  relative, boundary-aware limb in `check_sigma_collapse` for parent scale
  variables; and a repair to the existing monotone limb.

## Why F10 was silent — the substance of this task

The prompt asked an open question: is F10's threshold wrong, or do parent scale
hyperparameters need their own check? **The latter**, and the reason is
structural rather than a mis-set number. `check_sigma_collapse` missed on *both*
limbs:

- **Floor limb** requires `stds[-1] < 1e-8`. The measured collapses sit at std
  `0.11` and `~1e-5` against a parent hyper-prior of mean 10 — a miss by orders
  of magnitude.
- **Monotone limb** requires `stds[-1] < 1e-3 × stds[0]` (= `5e-3` here, so `0.11`
  misses on magnitude alone) **and** `np.all(np.diff(tail) < 0)` over 5 steps.

**The monotone limb was effectively dead code in any multi-factor graph** — the
most reusable finding here. `EPDiagnostics.snapshot` appends a row for *every*
variable on *every* factor update, but a factor update only moves the marginals
of the variables adjacent to *that* factor. A variable's history is therefore
dominated by steps at which it did not move, which give `diff == 0` and defeat
the strict `< 0` test. Five *consecutive* strictly-decreasing updates is close to
unreachable in practice. It fired in `test_sigma_collapse_monotone` only because
that test hand-builds a `np.geomspace` sequence directly into `variable_rows` —
**a test that passed while the code it covered could not fire on real data.**

The deeper mismatch: F10 was written for **#1332**, where *every* std shrinks to
zero around the starting means, so it is **absolute** and **variable-agnostic**.
This collapse has a different shape — the parent scale's **mean** goes to ~0
while its std stays moderate in absolute terms and is over-confident only
*relative to that mean*. No absolute std test can see a confident claim of "zero
scatter".

## Traps worth carrying forward

- **A guard's unit test can hide that the guard cannot fire.** The monotone limb
  was covered, green, and inert. When a check is fed by a *recorder*, test it
  against the recorder's real output shape, not a hand-built ideal series.
- **Grade thresholds against measured data, not intuition.** The separation here
  is clean only because the toy's numbers were on record: collapses at mean
  `0.80` (8% of the `10` hyper-prior mean) and `0.0030`, recoveries at
  `9.1–12.8 ± 0.9–2.4`. Both collapses flag; neither end of the recover band
  does. Those values are the test fixtures.
- **Check that new tests fail on the base.** 5 of the 9 fail on unmodified main;
  the other 4 are negative no-false-positive guards and pass on main by
  construction. Without that check a guard test can pass in both directions and
  prove nothing.
- **The prompt was STALE on one of its three legs.** Leg 3 (revise the standing
  damping hint) was already shipped on main at `diagnostics.py:250` and
  `graphical/README.md:158`, carrying this prompt's own finding that damping
  *worsened* hierarchical scale collapse. Grading a prompt against upstream main
  before starting cut a third of the task.

## What was NOT done — read before assuming this is finished

- **Heart never graded this.** `pyauto-brain vitals` returned `'pyauto-heart' not
  found on PATH` in the cloud session, so the documented fallback gate was used:
  the full `pytest test_autofit/` = **1714 passed, 4 skipped, 0 failed**. A Heart
  readiness tick is still owed before release. (Two earlier local failures —
  `test_beta`, `test_nautilus` — were session-venv gaps that failed identically on
  unmodified main; fixed by installing the declared optional extras `jax`,
  `astropy`, `nautilus-sampler==1.0.5`, not by touching code.)
- **Workspace impact was reasoned, not grepped.** Assessed (iii) none because the
  API change is additive only — one new method, one new attribute, two new
  defaulted kwargs; nothing removed, renamed or made required — so no downstream
  script can break. The workspace repos were not in the session and org-wide code
  search was out of scope. A grep for `check_sigma_collapse` /
  `register_hierarchical_scales` across the workspaces is cheap and still worth
  doing.
- **No smoke tests** — `/smoke_test` needs the workspace repos and PyAutoHands.
- **Leg 2 (curing the collapse basin) is untouched** and needs a fresh prompt and
  issue; do not reuse #1464 or the merged branch. One structural lead recorded
  during planning, explicitly a lead and **not** a finding:
  `_HierarchicalFactor.message_dict` (`hierarchical.py:195`) overrides the base
  and drops its `1/(count - 1)` tempering, with the comment "*Does not account for
  inverse cavity behaviour as this caused bugs for hierarchical factors*". A
  `HierarchicalFactor` generates one `_HierarchicalFactor` per drawn variable, all
  sharing the parent's scale prior — the geometry tempering exists to protect
  against, and over-counting shared information is the confirmed mechanism. **But
  `FactorGraphModel` inherits the tempered base `message_dict`, so the override
  may be inert for the global mean field.** Trace it before believing it.

## Verification

- `pytest test_autofit/` — 1714 passed, 4 skipped, 0 failed.
- `test_diagnostics.py` — 16 passed (7 pre-existing + 9 new).
- End-to-end on a real 5-drawn-variable hierarchical graph: the parent `sigma`
  registers and the parent `mean` correctly does not; the shallow collapse main
  passed silently now emits a specific `scale-collapse:` warning naming #1405.
- CI on the PR: docs-build, unittest 3.12, unittest 3.13 all green.

The change **reports; it never alters the fit** — the prompt's stated trap, and
the acceptance bar it set ("a collapsed parent scale is never *silently* reported
as a confident answer") is met.

## Original prompt

# EP: cure the hierarchical parent-scale collapse basin (and make F10 fire on it)

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised — PLANNED 2026-08-11 (leg 0 already shipped on main; ship leg 1 first, leg 2 deferred)
Issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1464 (leg 1 only; parent report is https://github.com/PyAutoLabs/PyAutoFit/issues/1405)

## The defect

Defect 1 of the two filed on PyAutoFit#1405. A hierarchical EP fit of a parent
**scale** hyperparameter (the `sigma` of a `HierarchicalFactor` parent Gaussian)
is stochastically unstable: repeated fits of an *identical, known-answer*
problem land in qualitatively different basins.

Measured over 30 identical-problem runs of a clean CPU toy (no JAX, no lensing;
parent scatter truth **σ=10**, far from the σ→0 boundary):

| outcome | freq | parent scatter (truth 10) |
|---|---|---|
| RECOVER | 70% | 9–13, sane errors — matches the joint sampler (12.8 [9.9, 16.3]) |
| **COLLAPSE** | 7% | **0.003–0.80 with an over-confident ≈0 error** |
| CRASH | 23% | `InitializerException` (split out — see the sibling prompt) |

The joint fit — `Dynesty` on `factor_graph.global_prior_model` for the same
graph — is stable and correct every time. **The graph and the data are fine; EP
is the sole source of the instability.** On PyAutoFit `f83f2f493`, i.e. this is
*downstream* of the #1383 projection fix and is a distinct, deeper issue.

## Mechanism (already established — do not re-derive)

Three candidate causes were tested; two are settled and one is confirmed:

- **Delta-method / boundary artefact → REFUTED.** Truth σ=10 with the base-space
  scatter message unbounded (`TruncatedNormal(mean≈0, lower=-inf, upper=inf)`),
  so `TransformedMessage.variance` is faithfully reporting a genuinely
  over-confident posterior — not a Jacobian linearization breaking down near a
  bound.
- **Over-shrinkage feedback → CONFIRMED as the collapse basin.** Per-group
  drawn-variable posterior *means* cluster far tighter than truth (spread ~0.6
  vs true ±10); the parent factor then sees near-identical draws, infers a tiny
  scatter, and tightens the shrinkage further — positive feedback to a fixed
  point at scatter ≈ 0 with ≈0 reported error. `ep_history.csv` shows recurring
  `BAD_PROJECTION` on the `HierarchicalFactor` and wildly swinging log-evidence
  through the collapse.
- **Under-convergence → transient only.** It explains movement *into and out of*
  basins, not a slow crawl toward truth. Both toy COLLAPSEs were at the shortest
  setting (`max_steps=20`); zero collapse at 25–60. But note the science case
  (`slope_hierarchy`, N=5 lenses) has a *stickier near-boundary variant* that
  converged to a stable wrong fixed point at σ≈0.026 vs truth 0.1 — it plateaued
  for the last ~2 of 12 sweeps and did not recover. So "just run longer" is not
  the fix.

## The task

1. **Make the collapse detectable before making it curable.** The **F10
   sigma-collapse guard** (`check_sigma_collapse`, from the #1335 diagnostics
   wave) passes a scatter≈0 / error≈0 parent **silently** today. That is the
   most defensible first deliverable and it is independently shippable: a
   hierarchical parent whose scatter has collapsed with a ~0 error should be
   flagged loudly. Decide whether F10's threshold is wrong or whether parent
   scale hyperparameters need their own check.
2. **Then attack the basin.** Candidate levers, in the order the evidence
   favours:
   - a **more robust / damped `HierarchicalFactor` scale moment-match** — the
     moment match is where near-identical draws get converted into a tiny
     scatter;
   - a **deterministic per-factor optimiser** in place of the per-factor nested
     sampler, to cut the sampler noise that appears to drive basin selection
     (the instability is stochastic across identical inputs — that noise has to
     enter somewhere).
3. ~~**Revise the diagnostics' standing hint.**~~ **ALREADY SHIPPED — see § Plan
   leg 0.** `ep_diagnostics` no longer suggests bare "consider damping, delta < 1".
   (Original text: naive damping made this worse — on `slope_hierarchy`, delta=0.5
   gave full collapse, 67 `BAD_PROJECTION`, and log-evidence blowing up to 5e7.
   The hint mis-diagnosed this mode.)

Note `factor_graph.optimise()` still cannot pass an `updater`/`delta` through
(filed: `draft/feature/autofit/ep_optimise_expose_updater_delta.md`); damping
experiments need the private `_make_ep_optimiser` workaround, pattern in
`slope_hierarchy/scripts/ep.py`.

## Plan (2026-08-11, Bug Agent)

Graded against PyAutoFit `main` @ `18aae0f3` (2026-08-10). Classification refined
from the heuristic first pass: **severity=high** (silent wrong answer, but on an
opt-in advanced feature, not a critical path) · **scope=single-repo** ·
**type=wrong-result** (not `runtime-error` — the CRASH arm was split out and
shipped) · **confidence=high** (mechanism established, repro exists) · **fix
locus=library source** · **strategy=split-into-phases**. The heuristic reported
`Reproduction: unknown`; that is wrong — see § Repro, the toy is committed.

### Leg 0 — already shipped, do not re-do

Task item 3 is **done on main** and this prompt was stale on it:

- `autofit/graphical/expectation_propagation/diagnostics.py:250` — the
  `check_sigma_collapse` floor warning now reads "*optional damping is available
  via `updater=af.SimplerUpdater(delta=0.5)`, but **has worsened hierarchical
  scale collapse in repeated-run diagnostics**; validate it across repeated
  fits*."
- `autofit/graphical/README.md:158` — "Damping is problem-dependent rather
  [than a default]".

Both carry this prompt's finding. Leg 0 is closed; the task is legs 1 and 2 only.

### Leg 1 — make the collapse detectable (small; independently shippable; ship first)

**Root cause of the silence: `check_sigma_collapse` cannot fire on this mode, on
either limb, for structural reasons — not because a threshold is slightly off.**

Grounding numbers, from the toy's parent hyper-prior
`sigma=af.TruncatedGaussianPrior(mean=10.0, sigma=5.0, …)` (so `stds[0] ≈ 5`) and
the two observed COLLAPSEs (`TruncatedNormal(mean=0.80, sigma=0.11)`, and the deep
run at scatter `0.0030 ± 0.0000`):

| limb | condition | collapsed run | verdict |
|---|---|---|---|
| A — floor | `stds[-1] < std_floor` (`1e-8`) | std `0.11` | misses by ~7 orders of magnitude |
| B — monotone shrink | `stds[-1] < shrink_factor * stds[0]` = `1e-3 × 5` = `5e-3` **and** `np.all(np.diff(tail) < 0)` over 5 steps | std `0.11` > `5e-3` | misses on magnitude |

**Limb B is worse than "mis-thresholded" — it is effectively dead code in any
multi-factor graph.** `EPDiagnostics.snapshot` appends a row for **every** variable
on **every** factor update, but a factor update only moves the marginals of the
variables adjacent to *that* factor. So a variable's history is dominated by steps
where it did not move at all, giving `diff == 0`, which fails the strict
`np.diff(tail) < 0`. Five *consecutive* strictly-decreasing updates is near
unreachable for any variable in a real graph. It fires in
`test_sigma_collapse_monotone` only because that test hand-builds a strictly
geometric `np.geomspace` sequence directly into `variable_rows`, bypassing the
sampling that makes it unreachable in practice.

The deeper mismatch: F10 was written for the **#1332 pathology** — *every* std
shrinking to zero around the *starting* means — so it is **absolute** and
**variable-agnostic**. This collapse is a different shape: the parent scale's
**mean** goes to ~0 while its std stays moderate in absolute terms and is only
over-confident *relative to that mean*. An absolute std check cannot see a
confident claim of "zero scatter".

So the prompt's open question ("threshold wrong, or do parent scale hyperparameters
need their own check?") resolves to: **parent scale hyperparameters need their own
check.** Proposed deliverables:

1. **Plumb the scale identity.** `check_sigma_collapse` today takes only
   `EPDiagnostics`, and `variable_rows` records `variable.name` with no marker.
   The information exists at snapshot time — `_HierarchicalFactor` knows its
   `distribution_model` (whose parameterising priors are the parent
   hyperparameters) and its `drawn_prior` (which is not one). Record a marker
   column on the row, read with `.get(...)` so the existing tests that hand-build
   `variable_rows` keep passing.
2. **A relative, boundary-aware check** for variables so marked: flag when the
   latest mean has fallen to a small fraction of its hyper-prior mean **and** the
   relative error `std / |mean|` is small — a confident near-zero. Separation is
   clean on the measured data: COLLAPSE is mean `0.80` (8% of the prior mean `10`)
   and mean `0.0030`; RECOVER is `9.1–12.8 ± 0.9–2.4`. Both collapses fire, no
   recover run does.
3. **Repair limb B independently** (a real defect in its own right): de-duplicate
   consecutive unchanged rows before the monotonicity test, or replace strict `< 0`
   with a tolerance. Worth its own test asserting it can fire on a *graph* run,
   not only on a synthetic sequence.

Wiring for a loud failure already exists and needs nothing new: `EPOptimiser`
calls `check_sigma_collapse` at `optimiser.py:560` (into `ep_diagnostics.results`)
and `optimiser.py:575` (`_warn_sigma_collapse`, logged **regardless of whether
output paths are enabled**).

**Validation must be a loop, not a run** — collapse is ~7% per run
(`feedback_flaky_test_sample_size`). But leg 1 is also unit-testable *without* the
flaky basin: assert the new check fires on hand-built rows reproducing the two
measured collapsed states, and does not fire on the measured RECOVER states.

### Leg 2 — attack the basin (too-large; scope after leg 1 ships)

Genuinely research-grade, and the prompt's own acceptance already sanctions the
exit: if the basin is inherent, this converts to a documented methods caveat plus
the leg-1 guard. Do **not** bundle it with leg 1. When scoped, one structural lead
is worth checking first, before the two levers the prompt already lists:

`_HierarchicalFactor.message_dict` (`hierarchical.py:195`) overrides the base
implementation and drops its tempering. The base
(`declarative/abstract.py:82`) raises each shared prior's message to
`1 / (count - 1)` so that the cavity at the first update equals the user's prior;
the override returns `prior.message` untempered, with the comment "*Does not
account for inverse cavity behaviour as this caused bugs for hierarchical
factors*". A `HierarchicalFactor` generates **one `_HierarchicalFactor` per drawn
variable**, all sharing the parent's scale prior, which is exactly the geometry
that tempering exists to protect against — and over-counting shared information is
precisely the confirmed mechanism. **Verify before believing it**: trace whether
that override is actually reached for the *global* mean field, or only when a
single factor's `mean_field_approximation()` is called — `FactorGraphModel`
inherits the tempered base version, so the override may be inert here. It is a
lead to check, not a finding.

## Repro and evidence

- Toy repro: `complete/2026/07/ep_scale_collapse_assets/ep_toy_diagnostic.py`,
  full forensics in `EP_TOY_FINDINGS.md` alongside it. Numpy-only, CPU, minutes.
  Collapse is only ~7% per run, so any verdict needs a **loop of runs**, not one
  — a fix that "works" on a single run proves nothing here
  (`feedback_flaky_test_sample_size`).
- Science case: Jammy2211/slope_hierarchy#1 (converged parity table, N=5 lenses,
  the stickier near-boundary variant).

## Acceptance

The honest bar is **not** "collapse never happens" — it is that a collapsed
parent scale is *never silently reported as a confident answer*. F10 firing on
the 7% is a pass; curing the basin outright is the stretch goal. If the basin
proves inherent to EP for scale hyperparameters, the deliverable converts to a
documented methods caveat (EP is fast and correct for the parent **mean**; use
a joint sampler for the **scatter**) plus the guard.

<!-- filed 2026-07-22 as the wrap-up follow-up of the ep-hierarchical-scale-collapse
task (report-only; PyAutoFit#1405). Sibling: ep_initializer_exception_should_not_abort.md -->
