# Point-source chi-squared variants (arXiv:2406.15280) — Phase 4: guides + docs

Parent: `point_source_chi_squared_paper_variants.md`. Phase 4 of 5.
Blocked on phase 2 merge (phase 3 can run in parallel). Tutorial PROSE
stays with Opus per `PyAutoBrain/skills/WORKFLOW.md`; notebook
regeneration/mechanics delegated.

## Goal

Update the workspace guides so the full likelihood-option matrix —
pairing scheme × centre treatment (free vs analytically solved) — is
documented in one place, citing Lombardi 2024 (arXiv:2406.15280).

## Files

- `autolens_workspace/scripts/guides/point_source_pairing.py` (+ notebook):
  extend from the three pairing schemes + `unmatched_model_policy` to the
  full matrix; document the new `al.ps` class and when to prefer solved
  centre (dimensionality: −2 non-linear params per point source; cluster
  fits with many sources gain most), and the tensor-weighted source-plane
  chi-squared's better error fidelity vs scalar µ².
- `autolens_workspace/scripts/point_source/fit.py` `__Chi Squared__`
  section (:333): add the new variants alongside
  `FitPositionsImagePairRepeat`/`Pair`/`Source`.
- `autolens_workspace/scripts/cluster/likelihood_function.py`: FIX the
  false claim at :312-318 that `FitPositionsSource(profile=None)` uses a
  ray-traced centroid (it raises `PointExtractionException`); document the
  real centre-free option shipped in phase 2; revisit the "search
  source-plane, validate image-plane" workflow advice in light of the new
  variants.
- `autolens_workspace/scripts/point_source/features/fluxes.py` and
  `features/time_delays.py`: document the analytic-flux (magnification-
  first, no free `flux` parameter) and analytic reference-time
  alternatives next to the current implementations, including when NOT to
  use fluxes (microlensing caveats already in the prose stay).
- `autolens_workspace/scripts/point_source/modeling.py` and
  `scripts/cluster/modeling.py` / `start_here.py` prose: mention the
  centre-free option where model composition is discussed; only change the
  demonstrated default if phase 1 recommended it.
- Check the `fit_positions_cls` defaults story is told honestly
  (`FitPointDataset` default `FitPositionsImagePair` vs `AnalysisPoint`
  default `FitPositionsImagePairRepeat`).
- Regenerate notebooks for every touched script (workspace
  `generate_and_merge` conventions).

## Style/constraints

- Docs minimal not maximal: flag/value + one-line note where a table row
  suffices; the pairing guide carries the deep prose.
- Workspace doc work anchors on the core API as merged (read the phase 2
  diff, not the plan).
- Follow-up (separate, maintainer-mode, NOT this task): refresh
  `autolens_assistant/wiki/core/concepts/point_source.md` +
  `skills/al_point_source.md` via `al_update_wiki` once released.

## Exit criteria

Guides + notebooks updated and consistent with shipped API;
`ship_workspace` PRs open behind the library-first merge gate; assistant
wiki follow-up filed.

## Phase 1 design outcome (2026-07-27 — supersedes placeholders above)

Approved design: https://github.com/PyAutoLabs/PyAutoLens/issues/657#issuecomment-5095032024

Deltas binding on this phase:
- Model class is `al.ps.PointSolved` (parameter-free; NO flux sibling — the
  analytic-flux fit never reads `profile.flux`, so `PointSolved` covers
  positions+fluxes+delays datasets alone).
- Fit-side API is a `SolvedCentre` mixin overriding the single
  `source_plane_coordinate` funnel to return the tensor-weighted analytic
  β* (paper §5.1: `β* = (ΣAᵢᵀΘᵢAᵢ)⁻¹ ΣAᵢᵀΘᵢβ̂ᵢ`, A from
  `ag.LensCalc.hessian_from`); concrete classes `FitPositionsSourceSolved`
  (+ `weighting = "jacobian"|"magnification"` class attribute, incl. the
  marginalization det term), `FitPositionsImagePairAllSolved`,
  `FitPositionsImagePairRepeatSolved`, `FitFluxesSolved` (flux-space
  `F* = Σµᵢf̂ᵢ/σᵢ² / Σµᵢ²/σᵢ²`), `FitTimeDelaysSolved` (precision-weighted
  `T*`). Hungarian `Pair` gets NO solved variant (skip recorded).
- Missing-image penalty: verification + docs only — `PairAll` already
  implements the paper's `1/P^I`; `PairRepeat` policies stay as-is; the
  without-repetition `P!/(P−I)!` form is rejected (factorial, JAX-hostile).
- Mismatch behaviour: BOTH directions raise loudly (centre-requiring fit ×
  `PointSolved`, and Solved fit × `Point`/`PointFlux`).
- PyAutoArray IS in scope (xp fix + pytree registration for
  `FitPositionsSource`) — 3-repo series, override recorded.
- Attribution: centre-free IMAGE-plane variants are OUR extension (glafic
  precedent), not from the paper — docs/prose must not cite the paper for
  them.
