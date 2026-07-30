# Galaxy-scale features: extra_galaxies + scaling_galaxies extensions with regime caveats

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: superseded 2026-07-30
Parent: draft/docs/autolens/split_lensing_regimes.md
Superseded-by: draft/docs/workspaces/scaling_relation_bgc_anchored_feature_packages.md

**Superseded note (2026-07-30).** The `extra_galaxies` half of this prompt shipped as
autolens_workspace#376 (point_source) and autogalaxy_workspace#184 (multi_galaxy). The
`scaling_galaxies` half is now carried by the BGC-anchored prompt above, which supersedes the
mechanism assumed here: that prompt ties each scaling galaxy's Einstein radius to the brightest
main galaxy's own free radius (zero new free parameters) rather than to a standalone free
`einstein_radius_ref`. The requirements below — untruncated isothermals at galaxy/multi_galaxy
scale with the tidal-stripping reasoning, the "load of galaxies far from the lens" framing, and
the ladder wrap-up — carry over unchanged and are restated in the phase prompts.

Ensure the single-galaxy-scale example trees (`imaging/`, `interferometer/`,
`point_source/`) each expose `extra_galaxies` and `scaling_galaxies` as
FEATURES, with prose calibrated to the regime ladder (parent plan): the
main_galaxies / extra_galaxies / scaling_galaxies three-tier API is available
in ALL regimes, but at galaxy scale the tiers mean different things than at
group/cluster scale.

## Current state

`imaging/features/` already has `extra_galaxies/` and `scaling_relation/`.
Audit these against the requirements below and replicate/cross-link for
`interferometer/` and `point_source/` (cross-linking to the imaging feature is
acceptable where the physics is identical — do not fork near-identical prose).

## Requirements

- extra_galaxies at galaxy scale: expected, common practice (nearby
  perturbers with fixed centres, SIS/SIE mass) — say so.
- scaling_galaxies at galaxy scale: supported but explicitly framed as "a
  load of galaxies far from the lens" — usually a weak correction, not a
  co-dominant component. The example must say when this is and is not worth
  the complexity.
- Scaling galaxies at galaxy scale and multi_galaxy scale use UNTRUNCATED
  mass profiles (isothermals): truncation encodes tidal stripping by a host
  halo, which these regimes lack by definition. Truncated dPIE members are
  introduced at group scale. This physical reasoning must appear in the
  feature prose (it is the thread that ties the three regimes together).
- Each feature's wrap-up points up the ladder: "if your extra galaxies are
  co-dominant → multi_galaxy/; if they sit in a common halo → group/".

## Acceptance

- Smoke suite green; notebooks + navigator regenerated.
- Feature prose consistent across imaging/interferometer/point_source (one
  canonical text, cross-linked).
