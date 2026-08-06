## autogalaxy-cluster-package
- completed: 2026-07-25
- summary: Created `scripts/cluster/` in autogalaxy_workspace (cluster-population light modelling); shipped alongside the multi_galaxy package via autogalaxy_workspace#168 + autogalaxy_workspace_test#97 (merged 2026-07-25) — sibling record [[autogalaxy-multi-galaxy-package]].

## Lifecycle note

Record backfilled 2026-08-06 (draft Status-sweep): the task shipped but its prompt never advanced out of draft/; retired here dated by ship day.

## Original prompt (autogalaxy_cluster_package)

# autogalaxy_workspace: new cluster package (many-galaxy light modelling)

Type: docs
Target: autogalaxy_workspace
Repos:
- autogalaxy_workspace
- autogalaxy_workspace_test
Difficulty: large
Autonomy: supervised
Priority: normal
Status: shipped 2026-07-25 (autogalaxy_workspace#168 + autogalaxy_workspace_test#97 merged) — awaiting lifecycle completion record
Parent: draft/docs/autolens/split_lensing_regimes.md

Create the `scripts/cluster/` package in @autogalaxy_workspace: modelling the
LIGHT of a cluster's galaxy population — BCG(s) modelled individually plus tens
to hundreds of member galaxies loaded from catalogues. PyAutoGalaxy deals in
neither mass models nor lensed sources, so this package is the photometric
counterpart of the autolens cluster package: the same population-scale
composition machinery, applied to light.

## Contents

- `start_here.py` — a cluster field image; BCG with individual MGE light
  model; member population loaded from a CSV catalogue via the galaxy
  CSV-loading API (`galaxy_table_from_csv`, `galaxies_from_csv_tables`,
  `galaxy_models_from_csv`); simultaneous or iterative fit of the population's
  light. IMPORTANT: unlike the autolens cluster start_here, this workflow's
  entire point IS the foreground galaxies' light — make that contrast explicit
  (parent plan records it as the first significant galaxy/lens divergence).
- `simulator.py` — simulate a cluster field (BCG + N members from a catalogue).
- `modeling.py`, `csv_api.py` — the CSV surface for light profiles, mirroring
  `autolens_workspace/scripts/cluster/csv_api.py` (which covers mass + points;
  here it is light + population catalogues).
- `features/` — e.g. scaling the population fit (linear light profiles across
  many galaxies), masking/segmentation of members, intracluster light as an
  advanced note if the API supports it.
- `README.md` — regime framing + pointer to the autolens cluster package for
  the lensing side of the same objects.

## Cross-cutting

- Register smoke entries; regenerate notebooks + navigator catalogue.
- autogalaxy_workspace_test: mirror integration scripts.
- If any gap surfaces in the PyAutoGalaxy CSV/light API while writing the
  examples, file it as a separate library prompt rather than working around
  it in workspace prose.

## Acceptance

- Smoke suite green; notebooks + navigator regenerated.
