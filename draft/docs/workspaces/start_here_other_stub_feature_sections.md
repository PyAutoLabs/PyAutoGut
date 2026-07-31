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
