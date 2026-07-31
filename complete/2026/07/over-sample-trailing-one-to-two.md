## over-sample-trailing-one-to-two
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/443
- completed: 2026-07-31
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/447, https://github.com/PyAutoLabs/autogalaxy_workspace/pull/197, https://github.com/PyAutoLabs/HowToGalaxy/pull/53, https://github.com/PyAutoLabs/autolens_workspace_test/pull/242, https://github.com/PyAutoLabs/autogalaxy_workspace_test/pull/102
- summary: Replaced every trailing sub_size 1 in adaptive over-sampling schemes across five repos (169 files, 186 sites: [4,2,1]→[4,2,2], [8,4,1]→[8,4,2]) so lensed-source arcs are never evaluated without over-sampling — MGE Gaussians alias at 1x1, degrading gradient-based searches. Updated 7 stale cored-profile prose blocks to the MGE-era 2x2-outer-floor justification; notebooks regenerated; simulators ([32,8,2]) untouched. Smoke green (autolens 36, autogalaxy 15, autolens_test 19) after refreshing three MGE jax_likelihood pinned constants that were computed under [4,2,1] (mge −86283.10392994, delaunay_mge −561.39264708, rectangular_mge −11.65793201) — only the MGE pins moved beyond rtol, empirically confirming the motivation. Gotchas: shipped under acknowledged Heart RED (unrelated interferometer nightly failures); a concurrent session's smoke run produced contaminated cache tallies that had to be discarded and re-run sequentially; five pinned-constant scripts sat outside the smoke subset and needed a manual audit; the autogalaxy_workspace_test 3.12 CI leg hung on a runner flake (cancel + rerun fixed it, 3.13 had passed the same diff). Follow-up: dpie PR#446 (autolens_workspace, still open) may need a one-token rebase over this sweep.

## Original prompt

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
