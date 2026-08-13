# Add a numerical-hazard profiling package to autolens_profiling

Type: feature
Target: workspaces
Repos:
- autolens_profiling
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

Create a new first-class package in `@autolens_profiling` under `misc/`, with
subfolders, that profiles model components — and their interaction with the
linear solver — for the numerical properties that determine how a likelihood
surface behaves under sampling.

This is scaffolding work. Build the capability and the results convention; do
not generate the full result set in this task (it will be re-run in
autolens_profiling once the package exists). The one exception is the written
summary described under "Seed result" below.

## Two tiers (structure)

Hazards divide by whether they need a dataset, and that division follows the
repo's existing layout law (`AGENTS.md`: dataset-first, task-second; `misc/`
holds each task's shared framework):

- **Tier 1 — component hazards.** Light/mass profiles and lensing calculations,
  evaluated with no likelihood and no data. Dataset-agnostic, so the framework
  and these checks live in `scripts/misc/hazards/`.
- **Tier 2 — likelihood hazards.** Everything wrapped on top of that: the linear
  algebra (inversion, NNLS, regularization), residuals and chi-squared. These
  are dataset-specific and live in `scripts/<dataset>/hazards/` —
  `scripts/imaging/hazards/` first, later `interferometer/` and `point_source/`.

The linear algebra is therefore **not** its own axis; it is lumped in with the
data-specific tier, because it only exists inside a full likelihood function.
This is forced rather than stylistic: the conditioning floors are absolute
constants added to matrices whose entries scale as (flux/noise)², so their
effective strength cannot be evaluated without a dataset.

The hazard analysis must run in both modes — on the lensing calculation alone,
and on the same components encased in a full likelihood function.

## Why this is needed

Downstream profiling tasks measure likelihood evaluation and gradient
performance for samplers. Those measurements are uninterpretable without knowing
where the surface is non-smooth: a flat plateau, an active-set kink or a
non-finite derivative changes sampler behaviour far more than a few percent of
evaluation time does. The organism currently has no systematic record of where
those sites are, so each investigation rediscovers them by hand.

An ad-hoc audit of three components (MGE lens light, power-law mass, external
shear) turned up fourteen such sites, including one that silently changes a
scientific result. That audit is the specification for what this package should
detect automatically, and is summarised in the artifact
https://claude.ai/code/artifact/9c6cc3b0-4652-47c4-aa81-8abccb350cd3

## What to build

Extend coverage to **all light and mass profiles and their combinations**, on
**both the JAX and numpy backends**. The natural matrix is
`component x backend x hazard class`, and the package should make adding a new
profile or a new hazard class a small, local change rather than a new script.

Support these hazard classes as the initial taxonomy — each derived from a real
finding, none speculative. The tier tag says where the check lives:

- **Saturating reparametrisations.** *(tier 1)* A clamp that maps an unbounded
  region of parameter space onto one value, producing an exactly flat likelihood
  with zero gradient. The `ell_comps` magnitude clamp is the reference case.
- **Active-set kinks.** *(tier 2)* The non-negative linear solver pins basis
  components at exactly zero, so the likelihood is piecewise-smooth and a pinned
  component contributes no gradient. This is the core of the linear-solver
  interaction, and only exists inside a full likelihood.
- **Conditioning floors.** *(tier 2)* Absolute values added to a curvature-matrix
  diagonal to make an ill-conditioned solve tractable, whose effective strength
  depends on the data's flux and noise scale rather than being scale-free — which
  is precisely why they cannot be measured without a dataset.
- **Non-finite value sites.** *(tier 1)* Parameter values inside the prior at
  which the model returns NaN or inf — including exact prior boundaries, which
  samplers do reach.
- **Non-finite gradient sites.** *(tier 1)* Points where the value is finite and
  correct but the derivative is not, typically a square root evaluated at zero.
  These are invisible to any check that only inspects likelihood values.
- **Backend divergence.** *(both tiers)* Places where the numpy and JAX paths
  implement different approximations of the same quantity and disagree by more
  than round-off. Report as relative error against the more exact path, as a
  function of the parameter that drives the divergence. Tier 1 covers profile
  math (e.g. `PowerLaw`'s exact `hyp2f1` vs its 20-term series); tier 2 covers
  the solver (active-set FNNLS vs interior-point PDIP).
- **Structural degeneracies.** *(tier 2)* Directions in which a parameter stops
  affecting the likelihood as another approaches a prior edge — funnels that
  waste live points and defeat mass-matrix adaptation.

Each check should report the parameter region affected, the fraction of prior
volume it covers under that component's default priors, and which backends it
applies to. Prior-volume weighting is what separates a real risk from a curiosity
and should be built in from the start, not added later.

## Results convention

Write results into the repo's existing `results/` folder, following the style
already used there for overall results, so they persist as organism memory.
Two consumers matter and should shape the format:

- **Downstream tasks** that profile likelihood and gradient performance read
  these results programmatically, so emit a machine-readable record alongside
  any human-readable summary.
- **A human** reading the results months later needs the finding, its code
  anchor, and how it was measured — a bare number is not enough.

Keep the record keyed so a re-run can be compared against the previous one; the
point of storing them is to notice when a hazard appears, moves or is fixed.

## Seed result

Write one good summary of the `ell_comps` clamp work into the `results/` folder
as part of this task, in the convention the package establishes. It is the
worked example that shows the format carrying real content, and the finding is
already fully characterised:

- `convert.py:71-77` clamps the magnitude at `0.999`, pinning the axis ratio at
  `q = 5.0025e-4` for every `|ell_comps| >= 1`. Present since 2020-11-08. The
  region is a finite, very low, exactly flat likelihood — never NaN — so
  samplers were never rejecting it, only wasting effort in it.
- The constructor guard added in issues #440/#568 (`profiles/validate.py:145-167`)
  rejects the region on numpy via `FitException` to the resample sentinel, but
  returns early for tracers, and `Fitness.call`'s JAX branch has no exception
  handling — so under gradient-based sampling the plateau is unchanged.
- Prior volume beyond the unit circle: 0.22% under the default
  `TruncatedGaussian(0, 0.3)` per component, 5.1% at sigma 0.5, 21.4% under
  `Uniform(-1, 1)` per component.

## Subject scope vs. where code lives

Refined after an adversarial plan review (Codex, 2026-08-13). The two tiers stay,
but as **metadata on a finding** rather than as the thing deciding where a
detector's code lives:

- **All reusable detectors live in `scripts/misc/hazards/`**, whatever their
  subject — detector logic is never duplicated per dataset.
- **`scripts/<dataset>/hazards/` holds dataset-specific cells and fixtures only.**

A finding declares one of three subject scopes: `component` (a profile, no data),
`matrix` (synthetic matrices, no dataset), `likelihood` (a real dataset). The
middle one exists because `reconstruction_positive_only_from` takes `data_vector`
and `curvature_reg_matrix` directly — a dataset is needed to judge a floor's
**scientific relevance**, not to **detect the mechanism**. The linear algebra is
still tied to the whole likelihood function where it *means* something, which is
the `likelihood` subject in `scripts/imaging/hazards/`.

## Risk is typed, not one universal predicate

Each hazard class declares its own risk basis. Prior mass is one of four, not the
contract for all:

- `prior_mass` — finite-measure regions; report MC estimate + sample count + CI.
- `epsilon_neighbourhood` — measure-zero sites; report prior mass of an
  **explicit** ε-ball with ε stated.
- `reachability` — sites reached only via construction or grid alignment.
- `error_curve` — continuous discrepancies, as a function of the driving parameter.

A uniform predicate would be wrong for most of the taxonomy: a non-finite
*gradient* site has measure zero, so MC reports 0% whether or not it exists, and
the `0.99999` clamp spans only ~5e-6 of ellipticity magnitude, which random prior
sampling would never find.

## Reachability is recorded, not assumed

`EllProfile.__init__` calls `validate_ell_comps` at construction
(`geometry_profiles.py:237`), so the `ell_comps` clamp is **not reachable on the
public numpy path at all** — while JAX tracing skips the guard and reaches it.
Every finding therefore records `code_exists`, `reachable_via`, `blocked_by`
(with the guard's anchor) and `affects_science` as distinct states.

## Phasing

Sized `large`. Phase 1 is a **vertical slice** — one case per subject shape, so
the schema is proven against all of them before the scaffolding is built:

- **Phase 1 (this prompt).** (1) `component`/saturation — the `ell_comps` clamp;
  (2) `component`/non-finite-gradient — the radial `sqrt` at r=0, the measure-zero
  case; (3) `component`/backend-divergence — `PowerLaw` `hyp2f1` vs the 20-term
  series; (4) `matrix`/conditioning-floor — the `1.0e-3` curvature-diagonal add
  from synthetic matrices. Plus the minimum record/report schema those four need,
  the regenerated seed result, a `--check` regression mode, and
  `hazards_index.json` as the consumer-facing artifact.
- **Phase 2** (`draft/feature/workspaces/hazard_profiling_likelihood_tier.md`).
  The `likelihood` subject under `scripts/imaging/hazards/` — active-set kinks,
  the floors judged against real flux/noise, structural degeneracies, solver
  backend divergence — plus breadth across the profile registry, and a named
  first consumer of `hazards_index.json`.

Neither phase runs the full `component x backend` matrix; that is deferred by
design (see the top of this prompt).

## Boundary

All work lands in `@autolens_profiling`. This task creates the package, its
structure and its results convention, plus the one seed summary. It does not
touch or fix any of the findings in the source libraries — each of those is its
own task, filed separately. Source-library file paths cited above are evidence
for the seed summary, not work to be done here.

<!-- formalised by the Intake (Conception) Agent on 2026-08-13 from file:/tmp/claude-0/-home-user/ed97e64a-5c90-56a4-96ce-23855e9c9173/scratchpad/prompt_body.md -->
