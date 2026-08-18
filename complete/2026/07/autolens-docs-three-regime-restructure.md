## autolens-docs-three-regime-restructure
- completed: 2026-07-26
- summary: PyAutoLens RTD docs restructured around the three above-galaxy-scale regimes (multi_galaxy / group / cluster): New User Guide four-rung ladder + flagship citations, overview_1 regime enumerations, overview_3 section rename, api mass/point/galaxy regime notes + new CSV galaxy-catalogue section, model_cookbook regime recipes. PyAutoLens#652/#653/#654 merged 2026-07-25/26.

## Verification (2026-08-18)

- All planned edits confirmed present on PyAutoLens `main` (overview_1/2/3,
  api/mass.rst, api/point.rst, api/galaxy.rst, general/model_cookbook.md).
- Docs CI (`docs.yml` → Heart's reusable docs-build, warning-count gate against
  `docs/sphinx_warning_baseline.txt`) green on every `main` push since the
  merge, including current HEAD `5d55825` — the prompt's pending "RTD build
  confirmation on merge" gate.
- All nine autolens_workspace notebook links in the sections this task added
  resolve on `main`. One PRE-EXISTING cookbook link (Model Linking section,
  `notebooks/imaging/advanced/chaining/start_here.ipynb`) 404s — not this
  task's edit; re-filed as draft/docs/autolens/cookbook_stale_chaining_link.md
  (correct target: `notebooks/guides/modeling/chaining.ipynb`).

## Lifecycle note

Record backfilled 2026-08-18: the task shipped 2026-07-26 but its prompt never
advanced out of draft/ (draft/docs/autolens/docs_three_regime_restructure.md);
retired here dated by ship day once the RTD-build gate was confirmed.

## Original prompt (docs_three_regime_restructure)

# PyAutoLens RTD docs: three-regime restructure (multi_galaxy / group / cluster)

Type: docs
Target: PyAutoLens
Repos:
- PyAutoLens
Difficulty: medium
Autonomy: supervised
Priority: high
Status: shipped 2026-07-26 (PyAutoLens#652/#653/#654 merged, branch claude/pyautolens-doc-reorganization-w6a1l5); RTD/docs build confirmed green on main 2026-08-18
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
