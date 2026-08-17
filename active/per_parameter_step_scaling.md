# Per-parameter step scaling for the gradient searches — treat the cause of prior exits

Type: feature
Target: autofit
Repos:
- PyAutoFit
- autolens_profiling
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

## What this is

The **cause-side** follow-up to the prior-support clipper. Phase 2 of that work
(autolens_profiling#131, record `results/notes/clipper_campaign/RESULTS.md`)
established that clipping does its job perfectly and does not improve the answer,
and diagnosed *why* lanes reach the prior walls in the first place.

**The diagnosis.** On the `imaging/mge` hst model, prior box widths span **8.0
down to 0.2 — a 40x range** — while `MultiStartGradient` steps in **physical
parameter space with a single global step scale**:

| parameter | prior | box width | start range (unit [0.15, 0.85]) | nearest wall |
|---|---|---:|---|---:|
| `mass.einstein_radius` | U(0, 8) | 8.00 | [+1.20, +6.80] | 1.20 |
| `shear.gamma_1/2` | U(-0.3, 0.3) | 0.60 | [-0.21, +0.21] | 0.09 |
| `bulge.centre_0/1` | U(-0.1, 0.1) | 0.20 | [-0.07, +0.07] | **0.03** |

Prodigy's step scale `d` grows from `1.00e-06` at step 1 to
`2.26e-02 / 5.49e-02 / 8.29e-01` by step 3000. A step that is sensible for
`einstein_radius` is a wall-crossing for `bulge.centre`.

Lanes are **not initialised at the edges** — `_broad_starts` draws in the unit
cube at `[0.15, 0.85]`, the middle 70% of every prior. They *walk* to the walls.
The prediction that escapes concentrate in the narrow-box parameters is confirmed
by autolens_profiling#128's autopsy: 10 of 11 exits were the shear, landing at
±0.30-0.35 just outside its ±0.3 box.

## Do per-parameter scaling, NOT unit-cube reparameterisation

Phase 1 rejected unit-cube stepping on three grounds
(`complete/2026/08/prior-support-clipper.md`, "Deliberately out of scope"), and
those objections still stand:

1. A **logit reparameterisation sends the optimum to infinity** when it genuinely
   sits on a boundary — and this cell demonstrably has such optima (6/16 lanes end
   pinned).
2. The **inverse-CDF transform for non-uniform priors has `∂θ/∂u -> ∞` at the cube
   faces**, trading one numerical hazard for another.
3. It **invalidates every stored benchmark**.

Diagonal preconditioning — a per-parameter step scale derived from each prior's
width — buys the same normalisation and dodges all three: no logit, so boundary
optima stay finite; no inverse-CDF, so no face singularity; and the objective
stays the physical-space posterior, so the Jacobian trap below cannot arise.

**Carry this warning forward regardless.** Reparameterising the search path does
not move the optimum *provided the objective is still the physical-space posterior
evaluated at `θ(u)`*. Optimise the density **of `u`** instead and the Jacobian
makes the MAP non-invariant — and it fails **silently**. Any implementation must
have a test that pins this.

## Proposed design

### 1. A static per-parameter scale vector `s`, derived from the priors

Computed **once at fit start**, reusing the clipper's bounds machinery
(`AbstractClipper.bounds_from_model` returns `(lower, upper)` in physical order,
`±inf` when unbounded). Share the extraction helper; do **not** couple the two
features (see "Both features stay").

| prior | scale | note |
|---|---|---|
| `UniformPrior(lo, hi)` | `hi - lo` | — |
| `GaussianPrior(mu, sigma)` | `sigma` | unbounded, no width exists |
| `TruncatedGaussianPrior(mu, sigma, lo, hi)` | **`sigma`** | NOT the truncation width: `ell_comps` is sigma=0.3 inside a [-1,1] box, so the width overstates it 6x |
| `LogUniformPrior` | needs a decision | log-spaced, so the natural step is *multiplicative*; do not silently use the physical width |

Then **normalise so the geometric mean of `s` is 1**. This keeps the *global* step
magnitude unchanged and alters only the *ratios*, so the A/B measures rescaling
alone rather than being confounded with an effective learning-rate change.

### 2. Apply as a constant diagonal change of variables, not a post-hoc multiply

The tempting implementation is `params += s * updates` after the optimizer.
**Reject it**: Prodigy estimates `d` from the distance actually travelled
(`params0`, `grad_sum`), so rescaling its update externally leaves its own estimate
inconsistent with the trajectory it thinks it took.

Instead run the optimizer in scaled coordinates `phi = theta / s`, evaluating the
objective at `theta = s * phi`:

- **Prodigy needs no changes** — it sees `phi`, steps in `phi`, and its state stays
  self-consistent. Same for every other optax rule.
- The objective remains the **physical-space posterior at `theta(phi)`**, satisfying
  phase 1's silent-failure warning: the Jacobian is a *constant* diagonal, so it adds
  a constant to the log-density and **cannot move the MAP**. Write the test that pins
  this.
- The map is **linear**, so boundary optima stay finite — the exact failure that
  killed the logit reparameterisation.
- Clipping still composes: scale the bounds once (`phi_bounds = theta_bounds / s`)
  and clip in `phi`.

### 3. Default off, opt-in, bit-identical when off

The same discipline `seed`, `alive_history` and `reset_momentum_on_clip` shipped
under.

### 4. Why this repairs Prodigy's premise rather than merely helping it

Prodigy estimates a **single global** step scale `d`, which implicitly assumes every
coordinate has comparable scale. A 40x spread violates that assumption at the root.

### 5. The fixed-rate optimizers are MORE exposed, not less

Adam's update is `lr * m_hat / (sqrt(v_hat) + eps)`, and since `m_hat/sqrt(v_hat) ~ 1`
for a consistent gradient, **Adam steps by ~`lr` in PHYSICAL units in every
coordinate**. With `lr=0.01`:

- `bulge.centre` (box 0.2, wall 0.03 from the start band) -> **5% of the box per
  step**, crossing in ~3 steps;
- `einstein_radius` (box 8.0) -> 0.125% of the box per step.

Adam's per-coordinate normalisation therefore **guarantees** the pathology rather
than mitigating it, and Lion is worse still (sign-based, so literally `±lr`). Expect
the effect to be larger for `MultiStartAdam` / `Lion` / `ADABelief` than for the
Prodigy baseline measured here — see PyAutoFit#1481.

## Both features stay — they are not substitutes

Do **not** treat this as a replacement for the clipper. They solve different halves,
and the case that breaks a reparameterisation is exactly the case clipping is for:

- **Scaling treats the cause**: it reduces how often a lane reaches a wall.
- **Clipping guarantees the invariant**: scaling makes overshoot rarer, never
  impossible (a large gradient, bad curvature, or a grown `d` can still cross), and
  without clipping that failure is **silent** — the lane goes `-inf`, is discarded,
  and nothing is raised.
- **Where the likelihood genuinely prefers a value outside the prior, the clipped
  lane sitting on the bound is the correct MAP answer under the declared prior.**
  This cell has 6/16 such lanes. Only clipping can express that.

**Keep `ClipperPriorBox` ON in every arm of this work**, so the clip rate is
measurable as a diagnostic rather than being confounded with the scaling change.

## The comparison this task must end with

**This is the deliverable.** Re-run the exact arms phase 2 ran and put the numbers
side by side, so "steps are now linked to priors sensibly" is demonstrated rather
than asserted.

Matched configuration (do not vary it — the point is comparability):
`multi_start_prodigy`, `imaging/mge`, `hst`, **16 starts x 3000 steps**,
**seeds 0 and 1**, JAX **float64**, `check_for_convergence=False`, via
`scripts/misc/searches/clipper_campaign.py`.

Baseline to beat, from `results/notes/clipper_campaign/multi_start_prodigy_imaging_mge_hst.json`:

| arm | seed | max_log_likelihood | gap to bar | value-NaN | clips | alive fraction | pinned | wall (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `none` | 0 | 31787.929 | -1.146 | 31655 | 0 | 0.341 | — | 1126 |
| `none` | 1 | -139485.799 | 171272.581 | 27870 | 0 | 0.419 | — | 2203 |
| `prior_box` | 0 | 31787.929 | -1.146 | 2 | 15142 | 1.000 | 6/16 | 1255 |
| `prior_box` | 1 | -120880.568 | 152667.350 | 0 | 15744 | 1.000 | 4/16 | 1251 |
| `prior_box_reset` | 0 | 31787.929 | -1.146 | 2523 | 18611 | 0.947 | 7/16 | 1744 |
| `prior_box_reset` | 1 | -137783.609 | 169570.391 | 0 | 8798 | 1.000 | 4/16 | 1123 |

Truth bar: Nautilus `max_log_likelihood = 31786.782462488976`
(`results/searches/nautilus/imaging/mge/hst/hpc_a100_fp64.json`). Negative gap means
the MAP optimizer exceeded it, which is expected.

### What would count as success

- **Clip rate collapses.** Today clipping runs at **31.5% of lane-steps**
  (15142 / (16 x 3000)). Well-scaled steps should drive this toward zero. This is
  the primary readout: it is the direct measure of "steps are now commensurate with
  prior widths".
- **Seed 1 is the real test.** Seed 0 already reaches the bar under every arm, so it
  can only show a no-regression. Seed 1 sits **171,272 nats** away and neither
  clipping nor momentum reset rescued it. If per-parameter scaling moves seed 1
  materially toward the bar, that is the result this whole line of work has been
  looking for.
- **Seed 0 must not regress** past the bar-beating `31787.929`.
- **Pinned lanes fall.** 6/16 pinned should drop if the pinning is a step-scale
  artefact. If it does **not** fall, that is evidence those lanes are pinned because
  the likelihood genuinely prefers the boundary — a science finding about the shear
  prior, not a bug (see "Pinning is a result" in the phase-2 prompt).
- **Wall time does not rise materially.** A diagonal multiply should be free.

### What would falsify it

Write these down before running and report them honestly:

- Clip rate falls but the answer does not move on either seed -> scaling is as
  cosmetic as clipping was, and the prior-exit line of work is closed rather than
  advanced.
- Seed 0 regresses -> the preconditioner is fighting Prodigy's own `d` estimate.
- Clip rate does **not** fall -> the diagnosis in this prompt is wrong, and the wall
  contact is not a step-scale effect. Say so; do not re-scope to save the idea.
- Results become seed-*more*-dependent -> preconditioning has narrowed the basin of
  attraction.

## Traps carried forward (all already paid for)

- **Grade on the alive-versus-step CURVE, not the percentage.** The lane counters
  are survival integrals — a dead lane keeps counting every later step, so the same
  death curve reads ~60% at 150 steps and ~75% at 300. `alive_history` is now in
  `search_internal` and `alive_fraction` is the budget-independent scalar.
- **At least two seeds, always.** Identical settings swing the outcome **171,000
  nats** between seeds 0 and 1. Use the search's `seed` argument — seeding
  `random`/`numpy` reaches only the initializer, and before that argument existed
  `_broad_starts` hardcoded `default_rng(0)` so every run drew the same population.
- **The clipper does not enter the search identifier**, so arms differing only in a
  search knob collide on one output directory. Give every arm a unique `name`, clear
  its directory, and assert `total_steps == n_steps` — a short-circuited run reports
  the *previous* run's counters, not zeros.
- **`search.summary` is `Key = Value`**, not colon-separated. A colon parser returns
  an empty dict and every counter reads `None` — indistinguishable from a feature
  that never fired.
- **Budget decides the answer.** At 105 steps clipping was worth 114 nats; by 3000
  it was worth zero. Never state a result without its step budget.
- **`--out` must actually reach the search.** The campaign driver sets the output
  root through `conf`; before that fix a stale `.completed` short-circuited `fit()`
  and returned a cached result in 2.9 s with every counter `None`.
- **A GPU run is ~20-35 min per arm** on the laptop RTX 2060 at 16x3000 fp64
  (3.3 GB of 6 GB, `XLA_PYTHON_CLIENT_MEM_FRACTION=0.5`). Six arms is a long
  evening. Check A100 availability first — during the phase-2 session all 8 were
  allocated to another user's array.

## Deliverables

- The library change in `@PyAutoFit`, default off and bit-identical when off, with
  the MAP-invariance test described above.
- Results JSON under `results/searches/` / `results/notes/clipper_campaign/`
  following the existing conventions.
- A note extending `results/notes/clipper_campaign/RESULTS.md` with the side-by-side
  table against the six baseline rows, and an explicit verdict on whether steps are
  now linked to prior widths sensibly.
- A recommendation on the clipper default (phase 3 of the prior-support work), which
  this evidence should finally be able to settle: if the clip rate collapses, the
  cost of defaulting it on approaches zero and its value becomes diagnostic.

## Environment

- Python 3.12+, `~/venv/PyAutoGPU` (Python 3.12.10, jax 0.10.2, CUDA working).
- `JAX_PLATFORM_NAME=cuda JAX_PLATFORMS=cuda,cpu XLA_PYTHON_CLIENT_MEM_FRACTION=0.5
  JAX_ENABLE_X64=True SEARCHES_DISABLE_VIZ=1`.
- Set `jax_enable_x64` **explicitly** under `sbatch` — it is not inherited.
- `autofit.__file__` must resolve to the checkout; the clipper, `seed`,
  `alive_history` and `reset_momentum_on_clip` are all unreleased.

## Out of scope

- Flipping the clipper default (that is phase 3, and this task feeds it).
- Removing or weakening the clipper — see "Both features stay".
- Unit-cube / logit reparameterisation, for the three reasons above.
- NUTS — it diverges rather than dying, a different mechanism.
- The **seed-dependence investigation**, which is filed separately and is arguably
  more important than this task.
