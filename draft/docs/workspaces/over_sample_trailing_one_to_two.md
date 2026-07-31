# Adaptive over-sampling: replace trailing sub_size 1 with 2 in examples

Sweep the workspace and tutorial repos so no adaptive over-sampling scheme
drops to sub_size 1 in its outer zone. The examples pair
`sub_size_list=[4, 2, 1]` with `radial_list=[0.3, 0.6]` centred on the lens
centre and applied to `over_sample_size_lp`, so everything beyond 0.6" —
including the lensed source arcs at the typical ~1.0-1.6" Einstein radius —
is evaluated at sub_size 1. With MGE now the headline source model, that
under-resolves compact Gaussians in the arcs, putting aliasing structure on
the likelihood surface that gradient-based searches (MultiStartGradient,
Adam) are sensitive to, even though nested samplers average over it.

Scope (verified inventory, 2026-07-31):

- `[4, 2, 1]` → `[4, 2, 2]`: ~115 sites in autolens_workspace (modeling,
  SLaM, features, guides), autogalaxy_workspace, autolens_workspace_test,
  autogalaxy_workspace_test.
- `[8, 4, 1]` → `[8, 4, 2]`: ~45 sibling sites in autolens_workspace,
  autogalaxy_workspace, HowToGalaxy — same trailing-1 aliasing trap.
- Simulators already use `[32, 8, 2]` and the misc tiers (`[24, 8, 2]`,
  `[16, 8, 2]`, `[8, 4, 2]`) already end in 2 — verify no simulator or other
  scheme retains a trailing 1, but no changes expected there.
- Update the stale prose justification in
  `autolens_workspace/scripts/guides/advanced/over_sampling.py` (line ~28),
  which says sub_size 1 is fine for sources because cored profiles are used —
  replace with the MGE-era reasoning above. Sweep any sibling prose in
  autogalaxy_workspace / HowTo repos that repeats the cored-profile claim or
  describes the outer zone as sub_size 1.
- Notebooks regenerate from scripts via the standard generate step; markdown
  siblings follow the ship_workspace flow.

## Original request

Lots of examples use adaptive over sampling with [4,2,1], but I think we
should switch sub size list to [4, 2, 2], because I realised that the 1 would
prob ruin gradients in the modeling (e.g. the MGE source for sub size 1 is
not gonna work great). Do you agree?

[follow-up] sounds good, but I would do this on simulators too just to avoid
confusion
