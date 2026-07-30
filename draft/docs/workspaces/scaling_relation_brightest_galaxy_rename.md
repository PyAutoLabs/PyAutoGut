# scaling_relation: rename BGC/BCG to "brightest galaxy" outside the group/cluster regimes

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft
Follows: draft/docs/workspaces/scaling_relation_bgc_anchored_feature_packages.md (shipped
2026-07-30, autolens_workspace PR#396 + PR#398)

## Original request (verbatim)

> In scaling_relation for multi_galaxy, imaging, interferometer, point_souce dont refer to it as
> the BCG (Brightest cluster galaxy opr _bcg) as these are not clusters, just call it the
> brightest galaxy and keep a note in the docs that for group and clusters its the BCG)

## Scope (verified by grep, 2026-07-30)

The BGC/BCG terminology is confined to two places in the four named regimes:

- `multi_galaxy/features/scaling_relation/` — all six files carry it (README.md, modeling.py,
  fit.py, simulator.py, slam.py, likelihood_function.py), in both prose ("the BGC") and
  identifiers (`bgc_index`, `bgc_key`, `luminosity_bgc`, `einstein_radius_bgc`, `L_bgc`).
- `point_source/features/scaling_relation/likelihood_function.py:4` — a single stray
  "BGC-anchored scaling tier" in the module docstring.

`imaging/features/scaling_relation/` and `interferometer/features/scaling_relation/` are already
clean — they use `anchor` / "the main lens" throughout, and their two cross-references to the
multi_galaxy package already say "the brightest of several co-dominant deflectors". No change
needed there; confirm and report rather than inventing edits.

`group/features/scaling_relation/` is **out of scope** — a group genuinely has a BCG/BGG, and
`modeling.py:256` correctly says "set it to the BCG/BGG magnitude". Leave it.

## Required changes

1. Prose: "the BGC" → "the brightest galaxy" (or "the brightest of the pair" where that reads
   better in context). Section header `__What Changes For A BGC-Anchored Tier__` and
   `__Luminosities + The BGC__` rename accordingly.
2. Identifiers: `bgc_index` → `brightest_index`, `bgc_key` → `brightest_key`,
   `luminosity_bgc` → `luminosity_brightest`, `einstein_radius_bgc` → `einstein_radius_brightest`,
   `L_bgc` → `L_brightest` (including in the `slam.py` pipeline-function keyword arguments and
   their call sites).
3. Add a short docs note — multi_galaxy README.md plus the modeling.py docstring — that in the
   group and cluster regimes this same anchor galaxy is the BCG (brightest cluster galaxy) /
   BGG, and point at `group/features/scaling_relation`.
4. Regenerate the notebook mirrors (`notebooks/multi_galaxy/features/scaling_relation/*.ipynb`,
   `notebooks/point_source/features/scaling_relation/likelihood_function.ipynb`,
   `notebooks/multi_galaxy/features/scaling_relation/README.md`) from the scripts rather than
   hand-editing them.

## Acceptance

- `grep -rin "bgc\|bcg" scripts/{imaging,interferometer,multi_galaxy,point_source}/features/scaling_relation/`
  returns nothing except deliberate "in a group or cluster this is the BCG" notes.
- Same grep over the corresponding `notebooks/` trees.
- `group/features/scaling_relation` diff is empty.
- The four scaling_relation scripts that run still run (fit.py / likelihood_function.py are the
  cheap ones; modeling.py / slam.py under test mode).
