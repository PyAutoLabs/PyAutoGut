# MGE examples: floor the smallest Gaussian at a tenth of the pixel scale (`sigma_min`)

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- autogalaxy_workspace
- HowToLens
- HowToGalaxy
- autogalaxy_assistant
- autolens_assistant
Difficulty: medium
Autonomy: supervised
Priority: normal

## Original request (verbatim)

> Can you review this PR https://github.com/PyAutoLabs/PyAutoGalaxy/pull/549, I think we should
> update workspace exampels to make the input always log10(pixel_scale/10.0) but keep the default
> of -4

Clarified in session: the argument stays **linear** (`sigma_min`, as merged), because linear
arcsec reads better at the call site than a log10 value. "Keep the default of -4" means keep the
library default reproducing the old `1e-4` behaviour exactly — which #549 does, and which is
now locked by a regression test. The examples are what change.

Second clarification (verbatim):

> For sources, use the -4 default (if that was always used) for the lower bound, the source
> should not be tied to the dataset pixel scale due to lensing

Answering the parenthetical: yes, `-4` was always what source MGEs got. Every `mge_model_from`
call inherited the hardcoded `np.linspace(-4, ...)`, lens and source alike — no call site has
ever passed anything else, because until #549 there was no argument to pass. So leaving source
call sites untouched preserves exactly their current behaviour. (The 31 hand-rolled teaching
ladders are the exception: those were written at `-2`, so a source ladder among them is at `-2`
today and moving it to `-4` would be a change — flagged below.)

## Background

PyAutoGalaxy#549 merged 2026-08-04. It added `sigma_min` to `ag.model_util.mge_model_from`
(default `1e-4`) and, in the follow-up commit, to `mge_point_model_from` (default `0.01`).

The original bug: `mge_model_from` hardcoded `np.linspace(-4, np.log10(mask_radius), N)` while
its comment claimed the ladder spanned `0.01"`. So the basis always spent Gaussians ~2 dex below
the resolution of any real dataset.

**The library defaults are deliberately unchanged**, so that the fixed `sigma` values — and
therefore the PyAutoFit identifier of every archived run — stay bit-identical. Verified during
review: `np.log10(1e-4)` is exactly `-4.0` and `np.log10(0.01)` exactly `-2.0`, and a
model-by-model diff against the pre-PR code across 1440 configurations showed zero sigma
differences and zero identifier differences.

The consequence is that **nothing improves for users until the examples pass the argument**.
That is this task.

## Scope

In (user-facing surfaces):

- `autolens_workspace`, `autogalaxy_workspace`, `HowToLens`, `HowToGalaxy`
- ~116 `.py` files call `mge_model_from` / `mge_point_model_from`
- a further 31 files hand-roll the ladder inline for teaching purposes rather than calling the
  helper, currently `np.linspace(-2, ...)`. The upper bound cleanly separates plane:
  - `np.log10(mask_radius)` (43 occurrences) — image-plane lens/galaxy light → lower bound
    becomes `np.log10(dataset.pixel_scales[0] / 10.0)`
  - `np.log10(2.0 * pixel_scales)` (2) — the hand-rolled point-source MGE, image-plane → same
  - `np.log10(0.5)` (10) — **source plane**; these sit next to `source_bulge` and use a compact
    0.5" upper bound. Leave the lower bound alone per the source rule — but see the open
    question below, because they are at `-2` today, not `-4`
  - `np.log10(1.0)` (4) and `np.log10(-3, ...)` variants — resolve per file
- regenerate `notebooks/` and `markdown/` from `scripts/` afterwards
- assistant prose documenting the old floor: `autogalaxy_assistant/skills/ag_basis_profiles.md`
  states the ladder spans `0.01"`; sweep siblings in
  `autogalaxy_assistant/wiki/core/concepts/linear_light_profiles_and_mge.md` and the
  `autolens_assistant` equivalents

Out (this pass):

- `autolens_workspace_test`, `autogalaxy_workspace_test`, `autolens_workspace_developer`,
  `autolens_profiling`, `euclid_strong_lens_modeling_pipeline` — a changed sigma ladder changes
  fit results there, so those need re-baselining as a separate, deliberate decision.

## Preferred idiom

**Image-plane (deflector / galaxy light) MGEs only:**

```python
sigma_min=dataset.pixel_scales[0] / 10.0
```

Not a literal. `dataset` is in scope at every call site — including inside the SLaM pipeline
functions, which take it as an argument — and a literal pixel scale silently drifts from the
dataset it is supposed to describe. Note `pixel_scales` is a `(y, x)` tuple, hence the `[0]`.

Only ~17 of the caller files define a real `pixel_scale = <value>` variable; the overwhelming
majority pass `pixel_scales=0.1` as a keyword argument to `from_fits`, so a variable-based idiom
would not generalise.

## Source-plane MGEs keep the `-4` default (human decision)

**Source galaxies are NOT tied to the pixel scale.** The source is lensed, so magnification means
the source plane is sampled far more finely than the image-plane pixel scale — flooring a source
basis at a tenth of the image pixel scale would truncate real small-scale source structure that
the lensing actually resolves. Source MGEs therefore keep the existing `1e-4` default: **do not
pass `sigma_min` at a source call site at all.**

This makes the sweep a classification job, not a regex. The split in `autolens_workspace`
(234 call lines):

- 59 explicitly named source calls (`source_bulge`, `source_0_bulge`, `source_1_bulge`,
  `source_bulge_1`) — leave alone
- 29 explicitly named `lens_bulge` — take `pixel_scales[0] / 10.0`
- 143 bare `bulge = ...` — **ambiguous, must be classified per call site** by tracing which
  galaxy the variable is passed to (`lens=af.Model(al.Galaxy, ..., bulge=bulge)` vs
  `source=af.Model(...)`). Sampling the files that contain a bare `bulge`: 41 are source-only,
  2 lens-only, 16 contain BOTH, 12 match neither pattern.

The same file can reuse the name for both. `scripts/multi_galaxy/modeling.py` assigns
`bulge = al.model_util.mge_model_from(...)` at line 451 for a lens galaxy and again at line 478
for `source = af.Model(al.Galaxy, redshift=1.0, bulge=bulge)`. Any blind sweep gets this wrong.

`autogalaxy_workspace` and `HowToGalaxy` have no source plane at all — every MGE there is
image-plane light, so all of them take the pixel-scale floor.

`mge_point_model_from` stays pixel-scale-tied by construction: its upper bound is already
`2 * pixel_scales`, i.e. it exists to model something at the resolution limit.

## OPEN QUESTION — hand-rolled source ladders sit at `-2`, not `-4`

The source rule says "keep the `-4` default, because that is what was always used". That is true
of every **helper** call site — none has ever passed anything but the hardcoded `-4`. It is NOT
true of the ~10-14 **hand-rolled** source ladders, which were written at `-2`.

So for those the instruction's own conditional does not resolve, and there are two defensible
answers:

1. **Leave them at `-2`** — preserves current behaviour exactly, changes nothing for anyone
   re-running a tutorial.
2. **Move them to `-4`** — makes a hand-written source basis behave identically to one built by
   `mge_model_from`. These files exist to teach what the helper does under the hood, so having
   them silently disagree with it is the inconsistency the sweep is meant to remove.

Recommendation: **(2)**, since these are pedagogical mirrors of the helper and the whole point of
the task is to stop the two surfaces disagreeing. Cheap to reverse either way. Needs a human
answer before phase 1 touches these specific files; everything else in phase 1 is unblocked.

## Notes / risks

- This **does** change fit results in the examples — that is the point of the task, but it means
  any script whose expected output is pinned needs checking.
- `mask_radius` is a local float in most scripts (often `3.0`); `sigma_min` must stay below it or
  `mge_model_from` raises. At a tenth of a typical `0.1"` pixel scale (`0.01"`) that is never
  close, but the group/cluster scripts with small mask radii are worth a glance.
- Verify the smoke-test surface still passes; several of these scripts are in the CI smoke set.
