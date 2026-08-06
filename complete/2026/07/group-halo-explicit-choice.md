## group-halo-explicit-choice
- completed: 2026-07-26
- summary: Group-regime explicit halo choice: signature tutorial (2026-07-25) plus three-tier start_here and modeling/simulator halo-narrative threading (2026-07-26). Full scope landed per the in-prompt Landed log; the doc-reorganization branch has since merged (PyAutoLens PR#652-654 chain).

## Lifecycle note

Record backfilled 2026-08-06 (draft Status-sweep): the task shipped but its prompt never advanced out of draft/; retired here dated by ship day.

## Original prompt (group_halo_explicit_choice)

# Group package: host halo as an explicit modelling choice + default scaling/extra tiers

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- autolens_workspace_test
Difficulty: large
Autonomy: supervised
Priority: high
Status: complete — signature tutorial 2026-07-25; three-tier start_here + modeling/simulator halo-narrative threading 2026-07-26 (branch claude/pyautolens-doc-reorganization-w6a1l5). Full scope landed.
Parent: draft/docs/autolens/split_lensing_regimes.md

## Landed (2026-07-25, this task branch)

- `group/features/group_halo/` (simulator + modeling + README): fits the
  same dataset members-only vs members+halo with an identical truncated-dPIE
  member tier (Bergamini+19 tied exponents, vanishing cores), the
  radius/evidence/external-information decision framework, and an
  `include_group_halo` simulator switch to invert the verdict. Registered in
  smoke (validated green from a clean slate); notebooks regenerated;
  features README + regime-ladder README edits landed with the multi_galaxy
  package commit.

## Landed (2026-07-26, this task branch)

- `group/start_here.py` default model is now three-tier: main (2 galaxies —
  the central galaxy plus the bright companion 0.36" away, promoted from
  the extras catalogue after image inspection confirmed a distinct peak;
  each MGE + Isothermal), extra (1, from `extra_galaxies_centres.json` —
  MGE with a ±0.1" uniform light-centre prior + mass-centre-fixed bounded
  `IsothermalSph`), scaling (5, mass-only untruncated `IsothermalSph` on a
  shared `einstein_radius_ref` prior via
  `einstein_radius_ref * luminosity_ratio**0.5`; the truncated-dPIE variant
  stays pointed at `features/group_halo`). Scaling-galaxy
  centres/luminosities for the real Euclid dataset were derived from the
  image itself (gaussian-smoothed peak detection outside the main pair,
  1"-aperture photometry, normalized to the brightest) and committed as
  `dataset/group/.../scaling_galaxies.csv` with provenance documented in
  the script prose. 24-free-parameter model validated end-to-end under
  test mode.

## Landed (2026-07-26, narrative threading)

- `group/simulator.py`: new `__No Group Halo__` section — the simulation
  deliberately has no shared halo; a real group's halo is an explicit
  choice; `features/group_halo` is the with-halo counterpart (halo +
  truncated dPIE members enter together).
- `group/modeling.py`: new `__Group Halo__` section — the absent-halo
  choice framed explicitly, the fit-both decision framework pointer,
  the truncated-dPIE pairing, and CSWA 19 (Ding et al. 2025) cited as a
  published PyAutoLens group model combining both; `group_halo` added to
  the closing features list.

## Future option (not blocking)

- CSWA 19 as a real-data flagship dataset for the group_halo feature
  (public HST + published PyAutoLens model, arXiv:2504.11445) — would
  need frames downloaded and prepared from a local-network session, like
  the J1011+0143 swap-in.

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
