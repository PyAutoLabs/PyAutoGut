# Cluster package: point-source-default narrative + extended-source follow-up feature

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- autolens_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft
Parent: draft/docs/autolens/split_lensing_regimes.md

Align the `scripts/cluster/` package of @autolens_workspace with the
three-regime design (see parent plan). The mass framework (host halo(s) +
truncated members + scaling relations) is intentionally SHARED with the group
regime — the cluster regime is distinguished by the observational setting and
therefore the SOURCE MODELLING STRATEGY: dozens–hundreds of members, many
multiply-imaged sources across a wide redshift range, so the default workflow
is multiple-image positions / point-source constraints with individual source
redshifts, jointly optimizing one cluster mass model (multi-plane). Extended
source reconstruction is a specialised follow-up analysis of individual
systems, NOT the default.

Much of this package already exists (real Abell 2744 start_here on the
Bergamini et al. 2023 gold sample, dPIE + scaling relations, CSV API,
LensTool interop, mass_parameterizations guide). This task is narrative
alignment + gap-filling, not a rebuild.

## Changes

- `README.md` + `start_here.py` prose: state the regime-ladder design
  explicitly — same mass framework as `group/`, different source strategy;
  all clusters are multi-galaxy systems but not vice versa; link down the
  ladder to `group/` and `multi_galaxy/`.
- New `features/extended_source/` follow-up example: take one system from the
  cluster fit (e.g. one A2744 arc) and do a targeted extended-source
  reconstruction (imaging + pixelized source) with the cluster mass model as
  the starting point — framed explicitly as the specialised follow-up, and as
  the bridge back to the group/galaxy-scale source machinery. Note the
  foreground lens light is NOT modelled in the default cluster workflow (a
  deliberate divergence from @autogalaxy_workspace's cluster package, which
  is *about* the galaxies' light); an autolens lens-light cluster feature is
  future work, out of scope here.
- `mass_parameterizations.py` conventions cross-check against the parent
  plan's checklist (Bergamini et al. 2019 relation with tied truncation
  exponent and fixed gamma=0.2; members' r_core fixed small, unscaled;
  r_cut_ref ~5"; sigma-vs-b0 conventions per the Elíasdóttir 2007 /
  Kassiola & Kovner 1993 derivation note) — most already landed via the
  dPIE task series; verify and finish.
- gNFW guidance: ensure the "beyond the LensTool default" prose (dPIE host →
  (G)NFW host) is present and linked from start_here, per the expert feedback
  recorded in the parent plan.
- Ground the narrative in the parent plan's cluster literature section
  (HFF/CLASH/JWST-era benchmarks, model-comparison projects) with citations.
  Specifics from the research: state that start_here uses the PRE-JWST
  spectroscopic gold subset of Bergamini et al. 2023 by design (JWST-era
  models of A2744 now use ~135–150 images); name AS1063 as the "simplest
  relaxed cluster" counterpoint to merging A2744; candidate future feature
  systems — MACS J0416 (largest spec sample, scaling-up), SMACS J0723
  (mid-size, JWST-iconic), MACS J1149/SN Refsdal (time-delay cosmography),
  SDSS J1004+4112 (cluster-lensed quasar bridge from point_source users).

## autolens_workspace_test

Add/extend a cluster extended-source follow-up integration script.

## Acceptance

- Smoke suite green; notebooks + navigator regenerated.
- A new user reading cluster/README understands why cluster examples fit
  positions not pixels, and where the extended-source path lives.
