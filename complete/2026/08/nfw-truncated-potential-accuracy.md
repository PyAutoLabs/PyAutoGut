`NFWTruncatedSph.potential_2d_from` failed the `grad(psi)=alpha` finite-difference
self-consistency check at med 7.1e-2 (vs ~8e-4 for every other NFW/gNFW/cNFW
variant) — the MGE decomposition's sigma range (`radii_max = truncation_radius * 5`)
was the prime suspect.

**Shipped:** [PyAutoGalaxy#564](https://github.com/PyAutoLabs/PyAutoGalaxy/pull/564),
merged 2026-08-09 (fixes PyAutoGalaxy#563). This ledger entry was reconciled
retroactively on 2026-08-19 — the fix shipped outside the prompt's dev flow, so the
draft prompt and `planned.md` entry had gone stale.

## What shipped (and how it differed from the plan)

The prompt's plan was to **widen/refine the MGE sigma range**. The shipped fix went
further: the MGE approximation was **replaced entirely** by the exact analytic
lensing potential — equation (18) of Baltz, Marshall & Oguri (2009) for the n=1
smoothly truncated NFW — which the prompt's step 3 had flagged as a cross-check.
The analytic form became the implementation:

- `potential_func_sph_from(grid_radius, tau, xp)` — dimensionless analytic BMO
  potential, with a sixth-order small-radius series below `x = 1e-1` to avoid
  catastrophic cancellation in NumPy/JAX float32, zero-centred per the paper's
  convention.
- `NFWTruncatedSph.potential_2d_from` applies the `2 kappa_s r_s^2` normalisation.

## Validation

From the PR: 48 profile tests + 1054 full `test_autogalaxy/` pass; full-mode
200×200 workspace checks across three tNFW truncation regimes 9 PASS / 0 FAIL;
independent comparison against lenstronomy TNFW; JAX JIT/autodiff/float32, centre,
`x=1` and large-truncation checks. The unit tests the prompt asked for exist in
`test_autogalaxy/profiles/mass/dark/test_nfw_truncated.py`:
`test__potential_2d_from__gradient_matches_analytic_deflections` (rel 1e-6),
`__laplacian_matches_analytic_convergence` (rel 1e-5), an independent-implementation
match, and an NFW-limit comparison at large truncation radius.

Independent re-verification on `main` (49115ad, 2026-08-19), finite-differencing
`grad(psi)` against `coord_func_m`-based deflections over r in [1e-3, 20] arcsec:

| tau | median frac err | max |
|-----|-----------------|-----|
| 2.0 (defaults) | 1.4e-09 | 4.3e-07 |
| 10.0 | 2.2e-09 | 4.8e-07 |
| 0.5 | 1.2e-09 | 4.6e-07 |

The med 7.1e-2 failure is gone — errors are now at the FD-scheme floor, ~5 orders
below the other profiles' MGE-limited ~8e-4.

## Traps / lessons

- **Analytic beat MGE re-tuning.** The prompt's "widen the sigma range" plan would
  have kept an approximation where a closed form exists. When a profile has a
  published analytic potential (BMO 2009 here), port it — the MGE path is for
  profiles without one.
- **Ledger drift:** the fix merged 2026-08-09 but the prompt sat in `draft/` and
  `planned.md` for ten more days, still surfacing on the dashboard as open
  high-priority work. A fix shipped outside the prompt's own dev flow must
  reconcile the Mind in the same breath.
- Related but distinct: the Isothermal Ell/Sph potential disagreement
  (`planned.md` § `isothermal-ell-sph-oversampling-at-the-cusp`) was once guessed
  to share this root cause — retracted; MGE is not involved there.
- `draft/feature/autogalaxy/piemass_potential.md` (PIEMass has *no* potential) is
  the sibling task and remains open; the BMO-style analytic-port route used here
  is the template for it.

## Original prompt

# `NFWTruncatedSph.potential_2d_from`: MGE potential fails `grad(psi)=alpha` self-consistency

Type: bug
Target: PyAutoGalaxy
Difficulty: too-large
Autonomy: supervised
Priority: high
Status: formalised

Pre-existing accuracy bug surfaced while fixing the missing dark-matter
potentials (PyAutoGalaxy `feature/dark-matter-potentials`, the
`NFW`/`gNFW`/`gNFWSph` + `NFWSph` work). `NFWTruncatedSph` already *has* a
`potential_2d_from` (it is not missing), but the value it returns is not
self-consistent with its own deflection field.

## Symptom

`autolens_workspace_test/scripts/mass/dark.py` runs the source-independent
self-consistency checks `div(alpha)=2 kappa`, `grad(psi)=alpha`,
`lap(psi)=2 kappa` by finite differencing. With all the
`feature/dark-matter-potentials` fixes in place the sweep is:

```
| Profile          | div(a)=2k | grad(p)=a            | lap(p)=2k |
| NFW              | PASS      | PASS med=8.1e-04     | PASS      |
| NFWSph           | PASS      | PASS med=7.6e-04     | PASS      |
| gNFW             | PASS      | PASS med=8.5e-04     | PASS      |
| gNFWSph          | PASS      | PASS med=8.1e-04     | PASS      |
| cNFW             | PASS      | PASS med=7.9e-04     | PASS      |
| cNFWSph          | PASS      | PASS med=6.9e-04     | PASS      |
| NFWTruncatedSph  | PASS      | FAIL med=7.1e-02 max=1.4e-01 | PASS (med=3.3e-02) |
```

Every NFW/gNFW/cNFW variant passes `grad(psi)=alpha` at med ~8e-4 except
`NFWTruncatedSph`, which is ~100x worse (med 7.1e-2). `div(alpha)=2 kappa`
passes, so the deflection field is fine; only the potential is off.

## Where the code lives

`autogalaxy/profiles/mass/dark/nfw_truncated.py`, `potential_2d_from`
(currently ~line 137). It uses the MGE decomposition exactly like `cNFW`:

```python
radii_min = self.scale_radius / 1000.0
radii_max = self.truncation_radius * 5.0
sigmas = xp.exp(xp.linspace(xp.log(radii_min), xp.log(radii_max), 30))
mge_decomp = MGEDecomposer(mass_profile=self)
return mge_decomp.potential_2d_via_mge_from(
    grid=grid, xp=xp, sigma_log_list=sigmas,
    ellipticity_convention="major", three_D=True,
)
```

## Likely cause / where to look

The MGE sigma range is the prime suspect. `cNFW` uses
`scale_radius/1000 .. scale_radius*200` (20-30 Gaussians); the truncated
profile caps `radii_max` at `truncation_radius * 5`, which is much
narrower and may not capture the deflection-relevant range, biasing the
radial potential integral. The convergence/deflection MGE for the same
profile presumably uses a different (wider) range — compare them.

## Plan

1. Reproduce on clean `main` first (this is pre-existing — confirm it is
   not a regression from the `feature/dark-matter-potentials` merge).
2. Widen / refine the `sigma_log_list` for the potential to match the
   range used by `NFWTruncatedSph`'s convergence/deflection decomposition,
   re-run `dark.py` (full mode, `rtol=1e-2`) until `grad(psi)=alpha` and
   `lap(psi)=2 kappa` both PASS at the same ~1e-3 med as the other NFW
   variants.
3. Cross-check the corrected potential against the spherical truncated-NFW
   analytic potential if a closed form exists (Baltz, Marshall & Oguri
   2009 give the BMO/truncated-NFW lensing potential).
4. Add a `test__potential_2d_from` assertion to
   `test_autogalaxy/profiles/mass/dark/test_nfw_truncated.py`.

## Validation

`PYAUTO_MASS_MODE=full python scripts/mass/dark.py` in
`autolens_workspace_test` — the `NFWTruncatedSph` row must flip
`grad(p)=a` from FAIL to PASS, joining the other dark profiles at ~1e-3.

<!-- formalised retroactively by the Intake (Conception) Agent on 2026-07-08 -->
