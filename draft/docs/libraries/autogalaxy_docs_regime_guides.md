# PyAutoGalaxy RTD docs: multi_galaxy + cluster in New User Guide and overviews

Type: docs
Target: PyAutoGalaxy
Repos:
- PyAutoGalaxy
Difficulty: small
Autonomy: supervised
Priority: normal
Status: shipped 2026-07-25 (PyAutoGalaxy#526 merged — New User Guide system-scale ladder; overview_1/3 touch-ups remain open if needed)
Parent: draft/docs/autolens/split_lensing_regimes.md

Surface the new autogalaxy_workspace `multi_galaxy` and `cluster` packages in
the PyAutoGalaxy Sphinx/RTD documentation (`PyAutoGalaxy/docs/`), mirroring the
three-regime restructure landing in PyAutoLens docs (parent plan).

## Changes

- `docs/overview/overview_2_new_user_guide.md`: add the routing rungs — single
  galaxy → multi_galaxy (2+ blended galaxies' light) → cluster (BCG + a member
  population from a catalogue) — with links to the new start_here notebooks.
- `docs/overview/overview_1_start_here.md` / `overview_3_features.md`: mention
  the multiple-galaxy composition API and the galaxy CSV-loading API
  (`galaxy_table_from_csv`, `galaxies_from_csv_tables`,
  `galaxy_models_from_csv`) where features are enumerated.
- State the deliberate galaxy/lens divergence where the cluster workflow is
  introduced: autogalaxy cluster examples model the foreground galaxies'
  light (that is the whole task); autolens cluster examples do not (point
  source constraints only, lens light later) — one sentence each side, so
  users moving between libraries are not surprised.

## Ordering

Land after the autogalaxy_workspace multi_galaxy and cluster packages exist,
so links resolve.

## Acceptance

- Sphinx build clean; links resolve.
