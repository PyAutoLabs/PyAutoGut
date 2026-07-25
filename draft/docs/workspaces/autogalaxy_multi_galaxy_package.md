# autogalaxy_workspace: new multi_galaxy package

Type: docs
Target: autogalaxy_workspace
Repos:
- autogalaxy_workspace
- autogalaxy_workspace_test
Difficulty: large
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/autolens/split_lensing_regimes.md

Create the `scripts/multi_galaxy/` package in @autogalaxy_workspace, mirroring
the regime split being introduced in @autolens_workspace (parent plan). This is
the light-only counterpart: simultaneous modelling of the LIGHT of two or more
galaxies in one image (blended/overlapping systems, pairs, compact groups) —
PyAutoGalaxy deals in neither mass models nor source galaxies, so the regime
here is purely "how do I compose and fit N galaxies' light at once".

The name `multi_galaxy` is shared deliberately with autolens (the autolens name
was chosen to mirror this package). No collision with `multi/`
(multi-wavelength), which keeps its name.

## Contents

- `start_here.py` — two overlapping galaxies (e.g. a close pair with blended
  light), composing two `ag.Galaxy` models with MGE/linear light profiles,
  centres from JSON (reuse the centre-GUI convention from the autolens group
  package), `AnalysisImaging` fit.
- `simulator.py`, `modeling.py`, `features/` (linear light profiles, MGE,
  sky subtraction, ellipse variants where sensible), `README.md`.
- Uses the multiple-galaxy model-composition API and the galaxy CSV-loading
  API already in PyAutoGalaxy (`galaxy_table_from_csv`,
  `galaxies_from_csv_tables`, `galaxy_models_from_csv`) — a features example
  demonstrates loading many galaxies from CSV.

## Cross-cutting

- Top-level README + any new-user routing prose: introduce the two-package
  extension (multi_galaxy, cluster) of the workspace taxonomy.
- Register smoke entries; regenerate notebooks + navigator catalogue.
- autogalaxy_workspace_test: mirror integration scripts (model_fit +
  jax_likelihood) under the same package name.

## Key divergence to document (from the parent plan)

In autogalaxy, multi-galaxy and cluster examples ARE about the foreground
galaxies' light — the default workflow models it. In autolens, the cluster
default workflow does NOT model foreground lens light (point-source
constraints only; lens-light features later). This is the first significant
deliberate divergence between the galaxy and lens doc trees — state it in the
README so users moving between the two libraries aren't surprised.

## Acceptance

- Smoke suite green; notebooks + navigator regenerated.
