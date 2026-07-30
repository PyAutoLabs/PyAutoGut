# Distill the multi_plane.py Slack transcript into a proper units explanation

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: normal

## Original request (verbatim)

> Can you read the long discussion in scripts/guides/advanced/multi_plane.py
> and compare it to the literature and distill it in a better explanation using
> the PyAutoLens docstring format and with python examples? Do you understan
> what its trying to portray? Its really the difference in how one might
> approachc luster modeing vs galaxy scale in terms of unit defintions.

## Context

`scripts/guides/advanced/multi_plane.py` currently ends with a ~400-line raw
Slack transcript about which source redshift defines `sigma_crit` (and hence
`kappa_s`) in a multi-plane system with multiple source planes. The physics
the transcript settles on:

- Galaxy-scale (single source plane): lensing units `(kappa_s, theta_s)`
  uniquely determine the deflection field; many physical `(M200, c, z)`
  combinations map onto them — sampling lensing units is clean and works with
  unknown redshifts.
- Cluster-scale (multiple source planes): `sigma_crit` differs per source
  plane, so there is no single convergence field and the degeneracy breaks —
  physical parameterization `(M200, c)` becomes natural.
- PyAutoLens convention: every profile's deflections are reduced deflections
  to the FINAL (highest-redshift) plane; physical profiles take
  `redshift_source = z_max_plane`; projected mass is
  `Sigma = kappa * sigma_crit(z_profile, z_max)`.
- Unifying identity (verified against `PyAutoGalaxy:autogalaxy/cosmology/model.py:315`):
  the multi-plane scaling factor is a ratio of critical surface densities,
  `beta_ij = sigma_crit(z_i, z_final) / sigma_crit(z_i, z_j)`.

Drift found in the current script:

- Line 10: literal placeholder "this paper: ?" — the formalism is Schneider,
  Ehlers & Falco 1992 §9.1 (Eq. 9.6 scaled deflections, Eq. 9.7b recursion).
  Mid-transcript a wrong citation (McCully et al. 2014, arXiv:1403.5278) is
  corrected inline — awkward to leave in user docs.
- The pasted copy of `scaling_factor_between_redshifts_from` carries a stale
  docstring/variable name (`D_l1s` / `..._redshift_1_and_final`); the library
  now correctly documents `D_l0s` (first lens → final source).
- `plane_index_limit: int = Optional[None]` typo (should be
  `Optional[int] = None`).
- `__Contents__` entries are truncated/garbled.

## Scope

Rewrite the guide in the standard workspace docstring format:

1. Overview/formalism with the SEF 1992 citation fixed and the beta equation
   stated once, cleanly.
2. Keep the pedagogical copied functions, refreshed against today's library
   source (fixes the naming drift and typos); keep the traced-coordinate
   example.
3. New "Lensing Units vs Physical Units" section — the galaxy-scale vs
   cluster-scale division distilled as tutorial prose, replacing the raw
   Slack dump.
4. New "PyAutoLens Convention" section — `redshift_source = z_max` for every
   physical profile; `Sigma = kappa * sigma_crit(z_profile, z_max)`; beta as
   a sigma_crit ratio.
5. New runnable examples: `NFWMCRLudlow` halos at z=0.5 and z=1.0 in a
   3-plane tracer with `redshift_source=2.0` for both; numeric check that
   beta equals the sigma_crit ratio via
   `critical_surface_density_between_redshifts_from`; sanity check that
   adding a massless plane changes nothing.
6. Science corollaries: mass-sheet degeneracy breaking + beta cosmography
   (arXiv:2110.06232).
7. One-paragraph attribution note crediting the Slack discussion.

Tutorial prose is written in-session (not delegated), per the prose
convention.

## Acceptance

- Script runs end-to-end (guide profile: full datasets env; it uses no
  datasets, so a plain run suffices).
- Numeric checks in the new examples actually assert/print consistent values.
- Notebook regenerated via the standard generate path.
