# Group package: host halo as an explicit modelling choice + default scaling/extra tiers

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- autolens_workspace_test
Difficulty: large
Autonomy: supervised
Priority: high
Status: draft
Parent: draft/docs/autolens/split_lensing_regimes.md

Rework the `scripts/group/` package of @autolens_workspace to match the
three-regime design (see parent plan): a group-scale lens has a DOMINANT
group-scale dark matter halo (~10^13–10^14 M_sun) as a *candidate* model
component, member galaxies as tidally truncated subhalos (dPIE/truncated
isothermal) tied by luminosity scaling relations, and typically ONE dominant
extended lensed source — so the source-modelling philosophy is unchanged from
galaxy scale (Sersic, MGE, Delaunay/adaptive pixelizations).

## The central documentation requirement

Every group-scale tutorial and example must present the inclusion of the group
dark matter halo as an EXPLICIT modelling choice, never an assumption. Some
systems genuinely require a host halo; others are adequately described by the
member galaxies alone. Users must learn BOTH workflows and when a host halo is
scientifically motivated (evidence: image configurations/arc curvature not
reproducible by members alone, mass-to-light offsets, X-ray/dynamical priors —
ground this in the parent plan's literature section, e.g. the SL2S/CASSOWARY
group-modeling papers).

## Changes

- `start_here.py`: add the scaling-galaxies and extra-galaxies tiers to the
  DEFAULT model (currently it fits only the 2 main lens galaxies). The default
  start_here composition becomes: main_galaxies + extra_galaxies +
  scaling_galaxies — all three tiers, as at cluster scale. Keep the current
  real Euclid dataset unless the parent plan's literature section motivates a
  better public flagship (one dominant arc, 2–5 members, host-halo evidence).
- New `features/group_halo/` example (name it `group_halo`, not `host_halo`,
  to match regime vocabulary): compose the SAME system twice — (a)
  members-only, (b) members + group-scale halo (dPIE per Lenstool convention,
  with a gNFW variant shown) — fit both, and walk through Bayesian model
  comparison (evidence difference) plus the physical arguments for/against
  the halo. This is the regime's signature tutorial. Preferred system per the
  parent plan's research: **CASSOWARY 19 (SDSS J0900+2234)** — public HST,
  theta_E ~ 7", one dominant z=2.03 source, and a published PyAutoLens model
  (Ding et al. 2025, arXiv:2504.11445: dPIE group halo + 16 dPIE members +
  shear) the tutorial can reproduce; model the 3–5 brightest members
  explicitly and put the rest on the scaling relation.
- `modeling.py` / `simulator.py`: thread the halo-choice narrative through;
  simulator gains a with-halo variant so both feature workflows have data.
- Scaling-relation prose: align with the conventions checklist in the parent
  plan (Bergamini et al. 2019-style relation; members' r_core fixed small and
  NOT scaled with luminosity; truncation exponent tied to the dispersion
  exponent; r_cut_ref ~5" scale, not 20").
- `README.md`: regime ladder (down to `multi_galaxy/`, up to `cluster/`),
  "is my lens a group?" guidance, literature pointers from the parent plan.

## autolens_workspace_test

Extend `scripts/group/` (or add) integration scripts covering members-only vs
members+halo model composition, so both compositions stay green in CI.

## Acceptance

- Smoke suite green; notebooks + navigator regenerated.
- No group example presents the host halo as mandatory; the halo-choice
  tutorial fits both compositions end-to-end under PYAUTO_TEST_MODE.
