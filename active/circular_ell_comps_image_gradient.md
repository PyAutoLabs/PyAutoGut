# Make circular ell_comps Sersic image gradients finite

@PyAutoGalaxy

Issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/570

## Problem

A circular Sersic profile evaluated on an off-centre grid has a finite image and likelihood at `ell_comps=(0, 0)`, but the JAX gradient with respect to the two Cartesian ellipticity components is non-finite. The current image path converts the Cartesian pair to polar axis ratio and angle, whose individual derivatives are undefined at the origin.

## Required fix

Preserve Cartesian `ell_comps` through the Sersic image-radius calculation. Do not assign arbitrary derivatives to the polar conversion. A suitable eccentric-radius identity for shifted coordinates `(y, x)`, `f²=e_y²+e_x²`, is:

```
r_ecc² =
  ((1 + f² - 2 e_x) x² - 4 e_y x y + (1 + f² + 2 e_x) y²)
  / (1 - f²)
```

Preserve the existing `fac <= 0.999` behavior in a traced, differentiable form.

## Acceptance

- NumPy image values match the existing implementation for circular, anisotropic, rotated, and near-clamped ellipticities.
- A downstream JAX `jit` + `grad` check is finite at `ell_comps=(0, 0)` on an off-centre grid.
- The origin gradient agrees with central finite differences and nearby Cartesian evaluations.
- The downstream full imaging likelihood keeps its finite value and obtains a finite origin gradient.
- PyAutoGalaxy unit tests stay NumPy-only; JAX checks run downstream per repository policy.
- No public API, prior, or configuration change; PyAutoGalaxy does not import AutoLens.
