# Numerical-hazard profiling

This instrument records numerical properties that change how a likelihood
surface behaves under sampling: flat saturations, non-finite derivatives,
backend divergence, and scale-dependent conditioning mechanisms. It complements
the runtime profiles; a fast evaluation is not sampler-friendly if its surface
contains a NaN gradient or a broad plateau.

Reusable detectors live here, independent of what they inspect. Dataset-specific
fixtures and cells belong under `scripts/<dataset>/hazards/`. A finding carries
its tier as metadata and declares one subject scope:

- `component` — a profile or lensing calculation, with no dataset;
- `matrix` — synthetic linear-algebra inputs, with no dataset;
- `likelihood` — a real dataset and complete likelihood (phase 2).

Risk is typed. The schema uses `prior_mass`, `epsilon_neighbourhood`,
`reachability`, or `error_curve`; it never forces measure-zero and continuous
hazards through Monte Carlo prior volume.

## Running

From the repository root:

```bash
python scripts/misc/hazards/scan.py
python scripts/misc/hazards/scan.py --subject component --backend jax
python scripts/misc/hazards/scan.py --check
```

The normal scan writes per-check JSON/PNG pairs and the generated seed summary
under `results/hazards/`. `--check` re-runs the reproducers without writing and
returns non-zero when a new semantic finding ID appears. A moved source anchor
does not create a new finding; persistence comes from the reproducer, while the
token fingerprint helps relocate the implementation.

## Phase-one vertical slice

<!-- BEGIN auto-table:hazards -->
| Finding | Subject | Hazard | Risk basis | Backends |
|---|---|---|---|---|
| `component.ell_comps.magnitude-saturation` | `component` | `saturation` | prior_mass, reachability | numpy, jax |
| `component.isothermal.near-spherical-saturation` | `component` | `saturation` | epsilon_neighbourhood, reachability | numpy, jax |
| `component.power-law.series-vs-hyp2f1-divergence` | `component` | `backend_divergence` | error_curve, reachability | numpy, jax |
| `component.spherical-geometry.radial-sqrt-gradient-at-zero` | `component` | `nonfinite_gradient` | epsilon_neighbourhood, reachability | jax |
| `matrix.curvature.absolute-diagonal-floor` | `matrix` | `conditioning_floor` | error_curve, reachability | numpy, jax |
<!-- END auto-table:hazards -->

The phase-one slice intentionally proves four shapes rather than scanning the
full `component × backend` matrix:

1. `ell_comps` and Isothermal saturation;
2. the measure-zero radial `sqrt` gradient at `r=0`;
3. PowerLaw `hyp2f1` versus the fixed 20-term JAX series;
4. the absolute curvature-diagonal floor on synthetic matrix scales.

The likelihood-scoped consumer and breadth sweep are phase 2. The placeholder
at [`scripts/imaging/hazards/`](../../imaging/hazards/README.md) fixes that
boundary without adding a dataset cell prematurely.
