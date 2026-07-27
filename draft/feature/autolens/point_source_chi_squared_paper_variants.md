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
