# PyAutoLens RTD docs: three-regime restructure (multi_galaxy / group / cluster)

Type: docs
Target: PyAutoLens
Repos:
- PyAutoLens
Difficulty: medium
Autonomy: supervised
Priority: high
Status: in progress — all planned edits landed 2026-07-26 (branch claude/pyautolens-doc-reorganization-w6a1l5); pending RTD build confirmation on merge
Parent: draft/docs/autolens/split_lensing_regimes.md

Restructure the PyAutoLens Sphinx/RTD documentation (`PyAutoLens/docs/`) around
the three above-galaxy-scale regimes defined in the parent plan: `multi_galaxy`,
`group`, `cluster` — each presented as its own section with its own tutorials,
example links, API pointers and modelling philosophy.

## Landed (2026-07-25, this task branch)

- `docs/overview/overview_2_new_user_guide.md`: the multi_galaxy rung and the
  four-step ladder routing with the analysis-split prose landed (PyAutoLens
  `c086863` + review fixes). `overview_3_features.md`: group section renamed
  "Multi-Galaxy Lenses, Groups and Clusters" (PyAutoLens#653).

## Landed (2026-07-26, this task branch)

- `docs/overview/overview_1_start_here.md`: the three regime enumerations
  now spell out the four-rung ladder (galaxy-scale, multi-galaxy,
  group-scale, cluster-scale).
- `docs/api/mass.rst`: regime note on the Total section — untruncated
  Isothermal/PowerLaw for galaxy/multi_galaxy, tidally truncated dPIE
  members for group/cluster (sigma_lt vs b0 parameterizations named).
- `docs/api/point.rst`: intro states point sources are the standard source
  strategy at cluster scale (per-source redshifts, multi-plane) with the
  workspace `cluster` package pointer.
- `docs/api/galaxy.rst`: new "Galaxy Catalogues (CSV)" section documenting
  `galaxy_table_from_csv` / `galaxies_from_csv_tables` /
  `galaxy_af_models_from_csv_tables` (previously absent from the API docs)
  with the scaling-tier regime framing.
- `docs/general/model_cookbook.md`: new "Multi Galaxy, Group and Cluster
  Models" section — per-deflector loop recipe, shared-prior scaling-relation
  tie recipe, cluster point-source framing, links to the four regime
  notebooks.

This completes the planned scope: the API reference stays single-copy with
per-surface regime notes (as specified), rather than a three-way fork.

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
- ~~`docs/overview/overview_1_start_here.md` + `overview_3_features.md`~~
  LANDED (see above).
- ~~`docs/api/`~~ LANDED (see above; per-surface regime notes, no fork).
- ~~`docs/general/model_cookbook.md`~~ LANDED (see above).
- ~~Scientific grounding~~ LANDED 2026-07-26: the New User Guide ladder now
  cites J1011+0143/B1608+656 (multi_galaxy), CSWA 19/SL2S (group) and
  HFF/A2744 (cluster).

## Ordering

Land after (or alongside) the `multi_galaxy` workspace package so notebook
links resolve; the group/cluster narrative edits can reference the workspace
tasks' outcomes but must not block on them.

## Acceptance

- Sphinx build clean against `sphinx_warning_baseline.txt`.
- Every notebook link resolves to an existing notebook on the release branch
  convention used by the docs.
