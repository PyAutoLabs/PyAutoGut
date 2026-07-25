# Assistants: regime-aware routing for multi_galaxy / group / cluster (follow-up)

Type: docs
Target: autolens_assistant
Repos:
- autolens_assistant
Difficulty: medium
Autonomy: supervised
Priority: low
Status: draft (deferred — land after the workspace/doc reorganization ships)
Parent: draft/docs/autolens/split_lensing_regimes.md

Once the three-regime reorganization (parent plan) has landed in
autolens_workspace, autogalaxy_workspace and the RTD docs, extend the
assistants so a user describing their system is routed to the right regime
workflow.

## Scope

- @autolens_assistant: add/extend skills so "I have a lens with two lens
  galaxies / a group / a cluster" routes to the multi_galaxy, group or
  cluster workflow respectively; teach the regime decision rules (co-dominant
  deflectors vs host halo vs many-source point workflow; all groups/clusters
  are multi-galaxy systems but not vice versa); refresh `wiki/core/` regime
  pages via `al_update_wiki`; add the parent plan's flagship literature
  systems to `wiki/literature/` following its schema.
- Galaxy-side assistant: the autogalaxy assistant does not exist yet as a
  repo; when it is seeded (via the Clone/Mitosis machinery), its seed should
  inherit the multi_galaxy + cluster (light) workflows. Record the
  requirement here; do not create the repo as part of this task.

## Ordering

Blocked on: multi_galaxy_package, group_halo_explicit_choice,
cluster_regime_narrative, autogalaxy packages. Do not start before those
merge — the assistant must document the shipped surface, not the plan.
