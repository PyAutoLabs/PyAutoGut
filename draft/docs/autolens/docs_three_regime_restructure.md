# PyAutoLens RTD docs: three-regime restructure (multi_galaxy / group / cluster)

Type: docs
Target: PyAutoLens
Repos:
- PyAutoLens
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft
Parent: draft/docs/autolens/split_lensing_regimes.md

Restructure the PyAutoLens Sphinx/RTD documentation (`PyAutoLens/docs/`) around
the three above-galaxy-scale regimes defined in the parent plan: `multi_galaxy`,
`group`, `cluster` — each presented as its own section with its own tutorials,
example links, API pointers and modelling philosophy.

## Landed (2026-07-25, this task branch)

- `docs/overview/overview_2_new_user_guide.md`: the multi_galaxy rung and the
  four-step ladder routing with the analysis-split prose landed (PyAutoLens
  `c086863` + review fixes). The remaining items below are still open.

## Changes

- ~~`docs/overview/overview_2_new_user_guide.md`~~ LANDED (see above). For
  reference, the rung decision rules used:
  - multi_galaxy: ≥2 co-dominant deflectors, no host halo, standard extended
    source.
  - group: optional host halo (explicit modelling choice), truncated members
    on scaling relations, one dominant extended source.
  - cluster: same mass framework as group; many sources at many redshifts →
    point-source/multi-image-position workflow by default.
  Include the taxonomy sentence: all groups and clusters are multi-galaxy
  systems, but not vice versa.
- `docs/overview/overview_1_start_here.md` + `overview_3_features.md`: add the
  regime split where scales are enumerated; link the three start_here Colab
  notebooks.
- `docs/api/`: ensure the mass/galaxy/point API pages surface the
  regime-relevant surfaces where users will look for them — dPIE profiles,
  `al.sr` scaling relations, `galaxy_table_from_csv` /
  `galaxies_from_csv_tables` / `galaxy_models_from_csv` CSV APIs, and the
  point-source/`PointSolver` machinery — grouped or cross-referenced by
  regime (a short "which regime uses this" note per surface is enough; do not
  fork the API reference into three copies).
- `docs/general/model_cookbook.md`: add multi_galaxy, group (both
  with/without-halo compositions) and cluster model recipes.
- Scientific grounding: each regime section cites 2–3 flagship
  systems/surveys from the parent plan's literature research (e.g. the
  multi_galaxy flagship, SL2S/CASSOWARY groups, HFF/A2744 clusters) so the
  docs point at real, recognisable science.

## Ordering

Land after (or alongside) the `multi_galaxy` workspace package so notebook
links resolve; the group/cluster narrative edits can reference the workspace
tasks' outcomes but must not block on them.

## Acceptance

- Sphinx build clean against `sphinx_warning_baseline.txt`.
- Every notebook link resolves to an existing notebook on the release branch
  convention used by the docs.
