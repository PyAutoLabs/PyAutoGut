# EP hierarchical parent-scale collapse — cure the basin, or document the caveat

Type: bug
Target: PyAutoFit
Repos:
- PyAutoFit
Difficulty: large
Autonomy: supervised
Priority: high
Status: formalised
Issue: (none yet — parent report is https://github.com/PyAutoLabs/PyAutoFit/issues/1405)

## What this is

**Leg 2** of PyAutoFit#1405 follow-up 2, split out because one prompt is one task
is one PR. **Leg 1 shipped** as PyAutoFit#1465 (issue #1464, record
`complete/2026/08/ep-hierarchical-scale-collapse-guard.md`): a collapsed parent
scale is now flagged loudly instead of being reported as a confident answer. The
basin itself is untouched — that is this prompt.

Do **not** re-open #1464 or reuse its merged branch for this work.

## The defect

A hierarchical EP fit of a parent **scale** hyperparameter (the `sigma` of a
`HierarchicalFactor` parent Gaussian) is stochastically unstable: repeated fits of
an *identical, known-answer* problem land in qualitatively different basins. The
joint `Dynesty` fit of the same graph is stable and correct every time — **the
graph and the data are fine; EP is the sole source of the instability.**

**Confirmed mechanism (do not re-derive): over-shrinkage feedback.** Per-group
drawn-variable posterior *means* cluster far tighter than truth; the parent factor
then sees near-identical draws, infers a tiny scatter, and tightens the shrinkage
further — positive feedback to a fixed point at scatter ≈ 0 with an ≈ 0 reported
error. Delta-method / boundary artefact was **refuted**; under-convergence explains
movement into and out of basins, not the fixed point. Full forensics:
`complete/2026/07/ep_scale_collapse_assets/EP_TOY_FINDINGS.md`.

## Candidate levers, in the order the evidence favours

1. **A more robust / damped `HierarchicalFactor` scale moment-match** — the moment
   match is where near-identical draws get converted into a tiny scatter.
2. **A deterministic per-factor optimiser** in place of the per-factor nested
   sampler, to cut the sampler noise that appears to drive basin selection (the
   instability is stochastic across identical inputs — that noise enters somewhere).

**Naive damping is NOT a free lever and is known to make this worse**: on
`slope_hierarchy`, `delta=0.5` gave full collapse, 67 `BAD_PROJECTION`, and
log-evidence blowing up to 5e7.

## Acceptance — deliberately two-sided

Curing the basin is the **stretch goal**. If the basin proves inherent to EP for
scale hyperparameters, the deliverable **converts to a documented methods caveat**
(EP is fast and correct for the parent **mean**; use a joint sampler for the
**scatter**) plus the leg-1 guard that already shipped. A well-evidenced caveat is
a pass, not a failure.

**Any verdict needs a LOOP of runs, not one.** Collapse is intermittent; a fix that
"works" on a single run proves nothing (`feedback_flaky_test_sample_size`).

## Repro — rebuilt and working (2026-08-11)

The original toy (`complete/2026/07/ep_scale_collapse_assets/ep_toy_diagnostic.py`)
loads the HowToFit chapter-3 dataset, which is **gitignored and ships with no
data**, so it cannot be run as-is from a fresh checkout. Its generative model is
fully specified in its own docstring, so the data is cheaply regenerated instead:
N Gaussians, `centre_i ~ N(50, 10)`, `normalization=0.5`, `sigma=5.0`, on a 100-pixel
grid with Gaussian noise; parent hyper-priors
`mean=TruncatedGaussianPrior(50, 10, 0, 100)`, `sigma=TruncatedGaussianPrior(10, 5, 0, 100)`.

**The rebuild reproduces COLLAPSE**, and cheaply — ~55 s per run on 4 CPU cores,
no JAX, no lensing. First seed tried collapsed outright:
`scatter=0.3384` against truth 10, with `err=7.37e-08`.

That run also **confirms the leg-1 guard fires on a real collapse** rather than only
on hand-built fixtures.

## Closed leads — do NOT re-chase

- **`_HierarchicalFactor.message_dict` tempering is INERT.** The override
  (`hierarchical.py:195`) drops the base class's `1/(count - 1)` tempering and
  carries the comment "*Does not account for inverse cavity behaviour as this
  caused bugs for hierarchical factors*", which made it look like the
  over-counting culprit. **Traced empirically and refuted**: while
  `FactorGraphModel` builds the global mean field the override is called **0
  times**, and the tempered base implementation is called once
  (`AbstractDeclarativeFactor.optimise` → `self.mean_field_approximation()` on the
  *collection*, not on the factor). The override is only reachable via a single
  factor's own `mean_field_approximation()`, which the EP loop does not use.

<!-- filed 2026-08-11, split from the leg-1 task at its merge. Classification via
     the Intake Agent (bug / PyAutoFit / large / supervised); priority raised to
     high to match the parent prompt. -->
