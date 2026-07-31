## start-here-other-feature-sections
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/442 (closed)
- completed: 2026-07-31
- workspace-prs: https://github.com/PyAutoLabs/autolens_workspace/pull/445, https://github.com/PyAutoLabs/autogalaxy_workspace/pull/196 (both merged 2026-07-31)
- library-prs: https://github.com/PyAutoLabs/PyAutoLens/pull/681, https://github.com/PyAutoLabs/PyAutoGalaxy/pull/543 (docs-only, both merged 2026-07-31)
- summary: The `__Other:__` stub closing `autolens_workspace/start_here.py` (four bare bullets) and its duplicate `## Other` in `PyAutoLens/docs/overview/overview_3_features.md` were replaced with five full feature sections in the established format (heading → science prose → paper link → `Checkout` pointer): Mass Models (total vs decomposed stellar+dark, multipoles m=1/3/4; arXiv 2410.12987 + 2407.12983), Automated Pipelines / SLaM (`guides/modeling/slam_start_here.py`), Dark Matter Subhalos (detect + sensitivity mapping; arXiv 2209.10566), Graphical Models (H0 time-delay example + hierarchical; `guides/modeling/advanced/{graphical,hierarchical}.py`) and Weak Lensing (`weak/start_here.py`, A2744 quickstart). The autogalaxy siblings (`autogalaxy_workspace/start_here.py`, `PyAutoGalaxy/docs/overview/overview_3_features.md`) got a Graphical Models section only, pointing at `autofit_workspace/*/features/graphical_models.py`; the "Automated pipelines / database tools" bullet was dropped per the request. All `Checkout` pointers verified to exist on both scripts and notebooks sides before writing. Notebooks regenerated via PyAutoHands `generate.py` (only `start_here.ipynb` diffs in each workspace).
- gotchas: "the aris paper" is ambiguous — the Amvrosiadis-led paper is the m=1 lopsidedness one (2407.12983, already cited by the Ellipse Fitting section), while the topically-matching "Galaxy Mass Modelling" JWST paper is Lange & Amvrosiadis (2410.12987); the Mass Models section cites both. Brain Feature Agent recommended a research/ re-home (prose-keyword artifact, repos "(none resolved)") — overridden as docs. Shipped under human-authorized Heart-RED override (RED = nightly release-validation integrate failure, unrelated; same-day precedent PyAutoLens#679). PyAutoLens claimed concurrently by #672/#678 worktrees — docs-only file, zero overlap, human-approved parallel run.
- follow-ups: none filed; if a dedicated Amvrosiadis mass-models paper appears later, swap/extend the Mass Models citations.

## Original prompt

## start-here-other-stub-feature-sections

Type: docs
Target: workspaces
Difficulty: medium
Autonomy: safe
Priority: normal
Status: formalised

The `__Other:__` section at the end of `autolens_workspace/start_here.py` is an
unfinished stub listing features as bare bullets instead of the full illustrated
sections used for every other feature (MGE, Groups, Multi-Wavelength, etc.):

- mass models (aris paper)
- Automated pipelines / SLaM.
- Dark matter subhalos.
- Graphical models.

The same stub is duplicated in `PyAutoLens/docs/overview/overview_3_features.md`
(`## Other`). The autogalaxy siblings carry the equivalent stub
(`autogalaxy_workspace/start_here.py` and
`PyAutoGalaxy/docs/overview/overview_3_features.md`, listing
"Automated pipelines / database tools" and "Graphical models").

Flesh these stubs out into full feature sections matching the established
per-feature format (heading, short description, image where available, science
applications, paper link where relevant, `Checkout ...` pointer to the
workspace package/notebook):

- **autolens** (`start_here.py` + PyAutoLens features doc): mass models (the
  Aris paper), automated pipelines / SLaM, dark matter subhalos, graphical
  models, AND weak lensing.
- **autogalaxy** (`start_here.py` + PyAutoGalaxy features doc): graphical
  models only.

Regenerate the workspace notebooks after the script edits.

Original request verbatim:

> start_here.py in autolens workspace neds in:
>
> __Other:__
>
> - mass models (aris paper)
> - Automated pipelines / SLaM.
> - Dark matter subhalos.
> - Graphical models.
> Presumably this is missing from the features part of docs too.
>
> Can you flesh this out for autolens, e.g. include the docs and wahtnot for
> mass models, slam, dark subhalos, graphical AND weak lensing, just graphical
> for galaxy.
