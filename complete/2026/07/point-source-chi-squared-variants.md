## point-source-chi-squared-variants
- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/657
- completed: 2026-07-31 (series close-out; phases have their own records)
- library-pr: PyAutoArray#414, PyAutoGalaxy#531, PyAutoLens#659 (phase 2); PyAutoLens#677 (phase 5)
- workspace-pr: wst#237/profiling#96/wsdev#121 (phase 3); autolens_workspace#425 (phase 4); wst#240/wsdev#123/profiling#98 (phase 5); autolens_profiling#99 (benchmark addendum)
- summary: 5-phase series implementing the Lombardi 2024 (arXiv:2406.15280 = gravity.jl) solved point-source likelihoods, closed same-day with a truth-anchored Prodigy-vs-Nautilus benchmark. Phase records: `point-source-solved-guides` (4), `point-solver-implicit-diff` (5); phases 1-3 literals in project memory `point-source-solved-likelihoods`. Benchmark verdict (profiling#99): Prodigy + PointSolved/PairAllSolved converges to truth THROUGH the solver (64x300, ~16 min); free-centre needs 256 starts; scalar-mu^2 source-plane catastrophically biased (truth -33788 vs wrong models -110, the mu=367 image's radial noise mis-mapped) while the tensor-solved variant ranks truth first by >1500 logL — isolation proved the TENSOR WEIGHTING is the fix, the solved centre the orthogonal dimensionality win.
- follow-ups: `draft/feature/autolens/point_source_defaults_campaign.md` (next chat: logsumexp fix, free-centre tensor option, pairing discriminator, posterior-width honesty, near-caustic stress; galaxy+CLUSTER tiers on RAL A100s; ends in full workspace docs update — supersedes the same-day centre-split decision); cluster swap in flight as autolens_workspace#436; cosmology pytree flattening + PairAll logsumexp in ideas.md (absorbed by campaign); interferometer nightly OOM draft bug (unrelated, found at phase-4 gate).

## Original prompt

# Point-source chi-squared variants (arXiv:2406.15280) — Phase 1: design

Parent: `point_source_chi_squared_paper_variants.md` (verbatim request there).
Phase 1 of 5. Judgment-heavy — stays with the lead (Opus) session per
`PyAutoBrain/skills/WORKFLOW.md`; no source edits in this phase.

## Goal

Produce the approved design for centre-free point-source likelihoods:
which variants from Lombardi 2024 (arXiv:2406.15280, Gravity.jl) we
implement, and the exact API. Output = design writeup on the GitHub issue
+ any corrections to the phase 2–5 prompts.

## Grounding (verified 2026-07-27)

- Model classes: `PyAutoGalaxy/autogalaxy/profiles/point_sources.py` has only
  `Point(centre)` and `PointFlux(centre, flux)` — centre is always a free
  (y,x). No centre-free class exists anywhere.
- Centre plumbing is a single funnel:
  `PyAutoLens/autolens/point/fit/abstract.py:144-153`
  `source_plane_coordinate → self.profile.centre`. Every fit uses it.
- Fit classes (`autolens/point/fit/positions/`): `FitPositionsImagePair`
  (Hungarian, numpy-only, not jittable), `FitPositionsImagePairAll`
  (all-to-all LogSumExp mixture, from this paper, JAX-blessed),
  `FitPositionsImagePairRepeat` (nearest-with-repeats + unmatched-model
  policies, JAX-shaped, `AnalysisPoint` default), `FitPositionsSource`
  (source-plane, scalar µ² noise weighting).
- `fit_positions_cls` is the only pluggable hook (`fit/dataset.py:34` default
  `FitPositionsImagePair`; `model/analysis.py:42` default
  `FitPositionsImagePairRepeat` — note the defaults DIFFER).
- FALSE DOCSTRINGS: a "barycenter of ray-traced positions" option is claimed
  but not implemented in `fit/positions/abstract.py:48`,
  `image/abstract.py:49`, `image/pair.py:30`, `image/pair_all.py:26`,
  `image/pair_repeat.py:18`, and the workspace guide
  `autolens_workspace/scripts/cluster/likelihood_function.py:312-318`
  (claims `FitPositionsSource(profile=None)` uses a centroid — it actually
  raises `PointExtractionException`). Phase 2 must make the docstrings true
  or delete them; phase 4 fixes the guide.
- JAX blockers on the source-plane path (relevant to any new source-plane
  variant): `Grid2DIrregular.grid_2d_via_deflection_grid_from`
  (`PyAutoArray/autoarray/structures/grids/irregular_2d.py:170`) takes no
  `xp`; `FitPositionsSource` missing from pytree registration
  (`model/analysis.py:181-218`). `distances_to_coordinate_from` (:204) is
  already `_xp`-threaded.

## Paper taxonomy to design against

- Image-plane (Eqs. 29–38): direct association / best-match / marginalize
  over all pairings (LogSumExp — our `PairAll`). Baseline forms keep the
  source position β as a free non-linear parameter.
- Source-plane linearized (Eqs. ~41–48): linearize the lens equation around
  each observed image; β enters linearly and is solved analytically as a
  precision-weighted (full local Jacobian / inverse-magnification-tensor
  weighted) mean of back-traced positions. This is BOTH the centre-free
  source-plane chi-squared AND the better-errors variant (tensor weighting
  vs our scalar µ²).
- Centre-free image-plane: profile the analytic β* (from weighted
  back-projection) into the image-plane chi-squareds — forward-solve model
  images from β* instead of a sampled `profile.centre`, for the pair-repeat
  and all-to-all schemes.

## Decisions to make (the actual design work)

1. Variant set: (a) source-plane analytic-centre with tensor weighting;
   (b) source-plane analytic-centre with current scalar µ² weighting (for
   continuity/comparison)? (c) centre-free `PairRepeat`; (d) centre-free
   `PairAll`; (e) is a centre-free Hungarian `Pair` worth it given it is
   numpy-only? Recommend which becomes the documented default for cluster
   fits (Lenstool parity uses `FitPositionsSource`).
2. API: removing the (y,x) priors REQUIRES a parameter-free `al.ps` model
   class (priors derive from `__init__`) — `fit_positions_cls` alone cannot
   do it. Decide: one new class (e.g. `al.ps.PointSolved`, name TBD) +
   orthogonal centre-resolution on the fit side, vs new fit subclasses per
   scheme (the guide's existing class-attribute pattern, cf.
   `unmatched_model_policy`), vs both. Decide the semantics of
   `source_plane_coordinate` when the centre is solved (keep the single
   funnel; no silent None-guards — absence of a centre must be explicit).
3. Name-pairing: dataset `name` → profile pairing must keep working for the
   new class (`fit/abstract.py:84-90`).
4. JAX plan: the analytic β* (weighted mean) is fixed-shape and xp-friendly;
   decide whether phase 2 also fixes the two `FitPositionsSource` jit
   blockers above (recommended — new source-plane variants sit on the same
   primitives). Any `PyAutoArray` change makes this a 3-repo task
   (autoarray + autogalaxy + autolens); the FeatureDecision's
   "repos: autolens" is understated — record the override.
5. Error-fidelity check design: how phase 2 unit tests demonstrate (numpy
   only, no JAX in unit tests) that solved-centre likelihoods match the
   free-centre likelihood profiled over centre, and that tensor weighting
   reproduces image-plane errors better than scalar µ² on a known asymmetric
   configuration.
6. Fluxes — IN SCOPE, alternative to the current implementation. Paper
   (Eq. 39 + §6.1): magnitude-space Gaussian with lensing modulus
   `LMᵢ = 2.5 log10|Aᵢ⁻¹|`; intrinsic magnitude M enters linearly →
   analytically marginalized/profiled (conjugate prior), removing M as a
   free parameter. PyAutoLens is magnification-first flux-space:
   `FitFluxes.model_data = |µᵢ| × profile.flux` (`fit/fluxes.py:110-124`)
   with `flux` a free param on `PointFlux`. Decide the port: flux-space
   analytic profiling (linear least squares,
   `F* = Σ µᵢ f̂ᵢ/σᵢ² / Σ µᵢ²/σᵢ²` — natural fit to our flux-space noise
   maps and outputs) vs paper-exact magnitude space; and what the model
   class looks like (flux-free `PointFlux` sibling composing with the
   solved-centre class). NOTE: there is no `fit_flux_cls` hook —
   `FitFluxes`/`FitTimeDelays` are hard-wired in `fit/dataset.py:114,130`;
   the design must add pluggable hooks (mirroring `fit_positions_cls`) or
   an equivalent mechanism.
7. Time delays — IN SCOPE, alternative to current. Paper (Eqs. 24-25):
   `tᵢ = T + Tᵢ` with reference time T entering linearly → analytic
   marginalization, same structure as M. Current `FitTimeDelays` takes
   residuals relative to the MINIMUM delay (`fit/times_delays.py:109-110`)
   — an ad-hoc T elimination. Design the precision-weighted analytic T
   alternative and compare error behaviour vs min-subtraction.
8. Missing-image penalty — scope against what exists. The paper's
   mechanism is purely combinatorial: marginalizing over pairings with
   normalization `1/|Σ|` (with repetition `|Σ| = P^I`; without repetition
   `|Σ| = P!/(P−I)!`) penalizes many-predicted/few-observed configurations;
   no explicit detection-probability term. `FitPositionsImagePairAll`
   ALREADY implements `-log(n_permutations)` (`pair_all.py:151-154`, cited
   to this paper). Verify it matches `P^I` exactly; decide whether to add
   the without-repetition variant; decide whether the paper-principled
   penalty should be offered as an `unmatched_model_policy` alternative to
   `PairRepeat`'s ad-hoc `no_image_residual = 1e4` floor and
   noise-normalized "penalize" policy (`pair_repeat.py:93-95, 215-219`).
9. JAX-gradient groundwork for phase 5 (design only, no implementation):
   confirm which variants get analytic/custom-JVP treatment vs plain
   autodiff — see the phase 5 prompt for the paper's gradient formulas.

## Consults

- `autolens_assistant/wiki/core/concepts/point_source.md` (read; background
  current as of 2026-07-09) and `skills/al_point_source.md`.
- PyAutoMemory `methods` wiki (likelihood/jax) per FeatureDecision.
- Paper full text: https://arxiv.org/html/2406.15280 §§2, 5 (and 6.1 for the
  deferred marginalization option).

## Exit criteria

Design posted to the issue; user approves variant set + API; phase 2–4
prompts updated to match. No code changes.

## Original prompt (series)

# Point-source chi-squared variants from arXiv:2406.15280 (no free source centre)

**Split into phases** (FeatureDecision 2026-07-27, difficulty too-large/10;
user extended scope 2026-07-27 with fluxes/time delays, missing-image
penalty, and a final JAX-gradients phase — 5 phases, overriding the
Brain's 4): this file is the umbrella; the executable prompts are
`point_source_chi_squared_paper_variants_phase_{1_design,2_core_api,3_workspace_examples,4_docs,5_jax_gradients}.md`.
Run `start_dev` on phase 1 first; phases 2–5 are placeholders until the
phase 1 design is approved.

Original request (verbatim):

> This paper does an amazing job of describing the different likelihood
> functions, for both a source plane chi squared and image plane chi squared,
> one may use in strong lens modeling: https://arxiv.org/abs/2406.15280. We
> have some of these implemented (e.g. FitPositionsImagePairAll) is the
> all-to-all case, and was taken straight out of this paper. Something to note
> is that currently all al.ps.Point models, whether it be a source plane chi
> squared or image chi squared, add a source centre free parameters (y,x) for
> every component, and we definitely need to incorporate models from this
> paper which avoid them being non linear free parameters. I want us to
> implement more of the options, in particular I want us to have: (i) the best
> (or multiple best) examples of a source plane chi squared, especially one
> which does not keep adding a source centre but also any which perhaps give
> better errors than our current implementation and; (ii) same for image plane
> chi squared, truth is I think we have the implementations for this good
> already except for the variant which does not add source centre free
> parameters, it would be good if this included all-to-all and the other pair
> one we use. You need to think about API a bit — should the no-free-centre
> extend al.ps.Point as a new class? or should it be an input setting like the
> API documented in guides/point_source_pairing.py and workspace sections on
> image plane chi squared / source plane chi squared which instead change the
> inputs to FitPoint and AnalysisPoint (see fit_positions_cls). Through this
> task we should be updating the guides on all these options. Plan out the
> task, probably in phases, but note that implementation will be delegated to
> other models. For each task also pair it to
> autolens_workspace_test/scripts/*/jax_likelihood examples and
> autolens_profiling/*/point_source/likelihood_runtime and
> cluster/likelihood_runtime examples.

Framing notes:

- Reference paper: arXiv:2406.15280 (survey of point-source likelihood
  functions for strong lens modeling; source-plane and image-plane
  chi-squared families). `FitPositionsImagePairAll` (all-to-all image-plane
  chi-squared) was already taken from this paper.
- Core requirement: variants where the source centre (y,x) is NOT a
  non-linear free parameter per point component (analytically marginalized /
  implicitly solved), for BOTH the source-plane and image-plane chi-squared
  families. For image-plane this should cover the all-to-all case and the
  pair-matching case currently in use.
- Also wanted: any source-plane chi-squared variant from the paper that gives
  better (more faithful) errors than the current implementation.
- API decision required before implementation: new `al.ps.Point` subclass vs
  a setting/input on `FitPoint` / `AnalysisPoint` (cf. `fit_positions_cls`
  and the API documented in `guides/point_source_pairing.py`).
- Guides must be updated across the point-source chi-squared options
  (autolens_workspace guides + image-plane / source-plane chi-squared
  sections).
- Every implementation phase must be paired with:
  - `autolens_workspace_test/scripts/*/jax_likelihood` examples,
  - `autolens_profiling/*/point_source/likelihood_runtime` examples,
  - `autolens_profiling/*/cluster/likelihood_runtime` examples.
- Planning/judgment in the lead session; implementation delegated to
  execution models per `PyAutoBrain/skills/WORKFLOW.md`.

## Original prompt (phase 2)

# Point-source chi-squared variants (arXiv:2406.15280) — Phase 2: core API

Parent: `point_source_chi_squared_paper_variants.md`. Phase 2 of 5.
Blocked on phase 1 design approval — the class names, variant set and
centre-resolution API below are placeholders until phase 1 lands.
Mechanical execution delegated (Sonnet) per `PyAutoBrain/skills/WORKFLOW.md`;
design deviations come back to the lead session.

## Scope (repos: autoarray? + autogalaxy + autolens — per phase 1 decision)

1. **Model class** (`PyAutoGalaxy/autogalaxy/profiles/point_sources.py`):
   add the parameter-free point-source class from the phase 1 design
   (working name `al.ps.PointSolved`). No free (y,x); composes via
   `af.Model` contributing zero non-linear parameters; dataset-name pairing
   (`autolens/point/fit/abstract.py:84-90`) keeps working. Export via
   `autogalaxy/__init__` `ps` alias → `al.ps`.
2. **Fit classes** (`PyAutoLens/autolens/point/fit/`): per the phase 1 API
   decision, implement analytic source-centre resolution — β* = precision-
   weighted mean of back-traced observed positions (weights per phase 1:
   full local inverse-magnification tensor; paper Eqs. ~41–48) — for:
   - source-plane chi-squared (tensor-weighted; supersedes/complements
     `FitPositionsSource`'s scalar µ² weighting),
   - image-plane pair-repeat and all-to-all: forward-solve model images
     from β* via the existing `PointSolver` path
     (`fit/positions/image/abstract.py:121-127`) instead of a sampled
     `profile.centre`.
   Keep the `source_plane_coordinate` single funnel
   (`fit/abstract.py:144-153`); no silent None-guards — a fit given a
   centre-free profile with a centre-requiring configuration must raise
   loudly.
3. **Docstring truth sweep**: the five false "barycenter" docstrings
   (`fit/positions/abstract.py:48`, `image/abstract.py:49`,
   `image/pair.py:30`, `image/pair_all.py:26`, `image/pair_repeat.py:18`)
   become true (pointing at the new machinery) or are corrected.
4. **JAX**: thread `xp` through all new code paths (fixed-shape only);
   register new fit classes in `AnalysisPoint._register_fit_point_pytrees`
   (`model/analysis.py:181-218`). If phase 1 approved it: fix
   `Grid2DIrregular.grid_2d_via_deflection_grid_from`
   (`PyAutoArray/autoarray/structures/grids/irregular_2d.py:170`) to accept
   and propagate `xp`, and add `FitPositionsSource` to the pytree
   registrations (its two known jit blockers).
5. **Fluxes/time delays — alternatives to current implementation** (per
   phase 1 §6-7 design): analytic-flux fit (magnification-first flux
   space: `F*` solved by linear least squares from `|µᵢ|` at the observed
   positions, unless phase 1 chose magnitude space) removing `flux` as a
   free parameter, + the flux-free model-class sibling; analytic
   reference-time treatment for time delays as an alternative to
   min-subtraction (`fit/times_delays.py:109-110`). Requires adding
   pluggable hooks (`fit_flux_cls` / `fit_time_delays_cls` mirroring
   `fit_positions_cls`) since both are hard-wired in
   `fit/dataset.py:114,130` — keep current classes as the defaults.
6. **Missing-image penalty** (per phase 1 §8): verify
   `FitPositionsImagePairAll`'s `-log(n_permutations)` equals the paper's
   `1/|Σ| = 1/P^I`; implement whatever phase 1 approved (without-repetition
   normalization and/or a paper-principled `unmatched_model_policy` option
   alongside `PairRepeat`'s existing ad-hoc penalties).
7. **Config/priors**: add any needed default-prior/config entries for the
   new classes (a parameter-free class may need none — verify, don't
   assume; check the autogalaxy prior config dirs and workspace config
   overrides).

## Tests (numpy-only — never JAX in unit tests)

- Analytic-centre correctness: β* equals the brute-force minimizer of the
  source-plane chi-squared over centre on a fixed mock tracer.
- Profile-likelihood parity: solved-centre fit log-likelihood ≈ free-centre
  fit maximized over centre (same scheme), on pair-repeat, all-to-all, and
  source-plane variants.
- Tensor vs scalar weighting: on an anisotropic-magnification mock, tensor
  weighting reproduces the image-plane chi-squared ordering that scalar µ²
  gets wrong (concrete case from phase 1 §5).
- Analytic-flux correctness: `F*` equals the brute-force minimizer over
  flux on a fixed mock; solved-flux likelihood ≈ free-flux likelihood
  profiled over flux. Same pattern for the analytic reference time vs a
  brute-force scan over T.
- Penalty: with-repetition normalization equals `-I log P` on a counted
  mock configuration; predicted-image surplus lowers the likelihood
  monotonically.
- Loud-failure tests for invalid combinations (e.g. current `FitFluxes`
  given the flux-free class must raise, not silently skip).
- Mirror the existing test taxonomy under
  `PyAutoLens/test_autolens/point/` (`__Env__` declarations, existing
  file layout).

JAX validation lives in scripts, not unit tests (vmap/value_and_grad-based,
per workspace conventions) — that is phase 3's paired examples.

## Paired examples (updated in phase 3, listed here for traceability)

- `autolens_workspace_test/scripts/point_source/jax_likelihood/{image_plane,source_plane,point}.py`
- `autolens_workspace_test/scripts/point_source/jax_grad/gradient.py`
- `autolens_profiling/scripts/point_source/likelihood_runtime/{image_plane,source_plane}.py`
- `autolens_profiling/scripts/cluster/likelihood_breakdown/{image_plane,source_plane}.py`

## Exit criteria

Library PRs open behind the ship gate (`ship_library`): tests green,
pytrees registered, docstrings truthful. Downstream workspace impact
analysis recorded for phases 3–4.

## Phase 1 design outcome (2026-07-27 — supersedes placeholders above)

Approved design: https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5095032024

Deltas binding on this phase:
- Model class is `al.ps.PointSolved` (parameter-free; NO flux sibling — the
  analytic-flux fit never reads `profile.flux`, so `PointSolved` covers
  positions+fluxes+delays datasets alone).
- Fit-side API is a `SolvedCentre` mixin overriding the single
  `source_plane_coordinate` funnel to return the tensor-weighted analytic
  β* (paper §5.1: `β* = (ΣAᵢᵀΘᵢAᵢ)⁻¹ ΣAᵢᵀΘᵢβ̂ᵢ`, A from
  `ag.LensCalc.hessian_from`); concrete classes `FitPositionsSourceSolved`
  (+ `weighting = "jacobian"|"magnification"` class attribute, incl. the
  marginalization det term), `FitPositionsImagePairAllSolved`,
  `FitPositionsImagePairRepeatSolved`, `FitFluxesSolved` (flux-space
  `F* = Σµᵢf̂ᵢ/σᵢ² / Σµᵢ²/σᵢ²`), `FitTimeDelaysSolved` (precision-weighted
  `T*`). Hungarian `Pair` gets NO solved variant (skip recorded).
- Missing-image penalty: verification + docs only — `PairAll` already
  implements the paper's `1/P^I`; `PairRepeat` policies stay as-is; the
  without-repetition `P!/(P−I)!` form is rejected (factorial, JAX-hostile).
- Mismatch behaviour: BOTH directions raise loudly (centre-requiring fit ×
  `PointSolved`, and Solved fit × `Point`/`PointFlux`).
- PyAutoArray IS in scope (xp fix + pytree registration for
  `FitPositionsSource`) — 3-repo series, override recorded.
- Attribution: centre-free IMAGE-plane variants are OUR extension (glafic
  precedent), not from the paper — docs/prose must not cite the paper for
  them.

## Original prompt (phase 3)

# Point-source chi-squared variants (arXiv:2406.15280) — Phase 3: test + profiling examples

Parent: `point_source_chi_squared_paper_variants.md`. Phase 3 of 5.
Blocked on phase 2 merge. Mechanical — delegated (Sonnet); these are
test/dev scripts, not tutorial prose.

## Goal

Pair every new likelihood variant with JAX-regression and
likelihood-runtime examples, per the original request.

## autolens_workspace_test (`scripts/point_source/`)

- `jax_likelihood/image_plane.py` (currently `FitPositionsImagePairAll`,
  jit end-to-end): add/extend to cover the centre-free all-to-all and
  pair-repeat variants — jit the full `analysis.fit_from`, assert
  numpy-vs-jax parity.
- `jax_likelihood/source_plane.py` (currently `FitPositionsSource`; prints
  a BLOCKER line for the known jit failure): add the tensor-weighted
  solved-centre variant; if phase 2 fixed the
  `grid_2d_via_deflection_grid_from` xp gap + pytree registration, remove
  the BLOCKER path and assert jit works for both old and new source-plane
  fits.
- `jax_likelihood/point.py`: cover the centre-free variants alongside
  `FitPositionsImagePairAll`; ALSO fix its wrong header docstring (it is a
  copy-paste of "Func Grad: Light Parametric Operated" — a point-source
  script; hygiene fix in passing).
- Flux/time-delay terms: where the phase 2 analytic-flux / analytic-T
  alternatives shipped, extend the jax_likelihood scripts (or add
  siblings) so at least one config exercises a dataset with fluxes and
  one with time delays through the new fit classes, numpy-vs-jax parity
  asserted.
- `jax_grad/gradient.py`: gradient finiteness + finite-difference checks
  for the SOLVED-CENTRE SOURCE-PLANE variants only (analytic β*/F*/T* are
  plain autodiff — no solver in the loop). Image-plane gradients through
  `PointSolver` are PHASE 5 — do not attempt them here; leave an explicit
  pointer comment instead of a BLOCKER hack.
- Follow existing script structure/style in these files; validate via the
  standard workspace_test run conventions before shipping.

## autolens_profiling

- `scripts/point_source/likelihood_runtime/image_plane.py` and
  `source_plane.py`: add the centre-free variants to the profiled configs
  (or sibling scripts per the existing naming pattern) — lower/compile/
  first-call/steady-state timings, `af.ModelInstance` pytree JIT input as
  in the existing harness. Record results JSON+PNG under
  `results/likelihood/point_source/` following the existing
  `*_summary_v<version>` naming.
- `scripts/cluster/likelihood_breakdown/image_plane.py` and
  `source_plane.py` (NOTE: the request said `cluster/likelihood_runtime`;
  the actual directory is `likelihood_breakdown/`): add per-step
  decomposition entries for the centre-free variants on the standard
  cluster model (2 dPIE + 10 scaling dPIE + NFW / 2 source planes). Key
  question: how much runtime the analytic β* adds/saves vs the
  ~14-parameter-smaller non-linear space (cluster fits drop 2 params per
  point source).
- Developer mirrors if touched by convention:
  `autolens_workspace_developer/jax_profiling/{jit,gradient}/point_source/`.

## Exit criteria

All paired scripts run green (jit parity asserted, no BLOCKER lines left
for fixed paths), profiling numbers recorded, `ship_workspace` PRs open
behind the library-first merge gate.

## Phase 1 design outcome (2026-07-27 — supersedes placeholders above)

Approved design: https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5095032024

Deltas binding on this phase:
- Model class is `al.ps.PointSolved` (parameter-free; NO flux sibling — the
  analytic-flux fit never reads `profile.flux`, so `PointSolved` covers
  positions+fluxes+delays datasets alone).
- Fit-side API is a `SolvedCentre` mixin overriding the single
  `source_plane_coordinate` funnel to return the tensor-weighted analytic
  β* (paper §5.1: `β* = (ΣAᵢᵀΘᵢAᵢ)⁻¹ ΣAᵢᵀΘᵢβ̂ᵢ`, A from
  `ag.LensCalc.hessian_from`); concrete classes `FitPositionsSourceSolved`
  (+ `weighting = "jacobian"|"magnification"` class attribute, incl. the
  marginalization det term), `FitPositionsImagePairAllSolved`,
  `FitPositionsImagePairRepeatSolved`, `FitFluxesSolved` (flux-space
  `F* = Σµᵢf̂ᵢ/σᵢ² / Σµᵢ²/σᵢ²`), `FitTimeDelaysSolved` (precision-weighted
  `T*`). Hungarian `Pair` gets NO solved variant (skip recorded).
- Missing-image penalty: verification + docs only — `PairAll` already
  implements the paper's `1/P^I`; `PairRepeat` policies stay as-is; the
  without-repetition `P!/(P−I)!` form is rejected (factorial, JAX-hostile).
- Mismatch behaviour: BOTH directions raise loudly (centre-requiring fit ×
  `PointSolved`, and Solved fit × `Point`/`PointFlux`).
- PyAutoArray IS in scope (xp fix + pytree registration for
  `FitPositionsSource`) — 3-repo series, override recorded.
- Attribution: centre-free IMAGE-plane variants are OUR extension (glafic
  precedent), not from the paper — docs/prose must not cite the paper for
  them.
