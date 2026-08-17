# Clipper validation campaign — results and phase-3 recommendation

Phase 2 of the prior-support work (#128, #131). Phase 1 shipped `ClipperPriorBox`
(PyAutoFit#1477); this measures whether it earns the default in phase 3.

**Recommendation: do NOT flip the default on the evidence asked for. The fix does
exactly what it claims and it does not improve the answer.** A narrower case for
flipping it on hygiene grounds is set out at the end. The momentum-reset variant
should be dropped.

Run: `multi_start_prodigy`, `imaging/mge`, `hst`, 16 starts x 3000 steps,
**laptop RTX 2060, JAX float64**, two seeds per arm, `check_for_convergence=False`.
Raw rows in `multi_start_prodigy_imaging_mge_hst.json`.

A100s were checked first and were unavailable: all 8 allocated across
`euclid-ral-gpu-1/2` by another user's array, longest job 2d11h against a 27-day
limit.

## The result

Reference bar: Nautilus `max_log_likelihood = 31786.782462488976`
(`results/searches/nautilus/imaging/mge/hst/hpc_a100_fp64.json`, A100 fp64).
Nautilus samples in unit-cube coordinates, so it is structurally immune to this
failure mode. A negative `gap` means the MAP optimizer exceeded it, which is
expected — it maximises the posterior rather than sampling it.

| arm | seed | max_log_likelihood | gap to bar | value-NaN | clips | alive fraction | pinned | wall (s) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `none` | 0 | 31787.929 | **-1.146** | 31655 | 0 | 0.341 | — | 1126 |
| `none` | 1 | -139485.799 | **171272.581** | 27870 | 0 | 0.419 | — | 2203 |
| `prior_box` | 0 | 31787.929 | **-1.146** | 2 | 15142 | 1.000 | 6/16 | 1255 |
| `prior_box` | 1 | -120880.568 | **152667.350** | 0 | 15744 | 1.000 | 4/16 | 1251 |
| `prior_box_reset` | 0 | 31787.929 | **-1.146** | 2523 | 18611 | 0.947 | 7/16 | 1744 |
| `prior_box_reset` | 1 | -137783.609 | **169570.391** | 0 | 8798 | 1.000 | 4/16 | 1123 |

Every `ClipperPriorBox` arm clipped tens of thousands of lane-steps, so no arm is
the "reported zero clips" broken case, and each arm ran under a unique search
name with its output directory cleared and `total_steps == n_steps` asserted.

## The load-bearing question

> Does clipped `MultiStartProdigy` get closer to the Nautilus bar than unclipped?

**No.**

- **Where the search converges (seed 0), the answer is identical.** All three arms
  land on `31787.929` — the same value to 15 significant figures. The winning lane
  never left the prior box, so clipping never touched it, and every lane clipping
  rescued stayed worse than the incumbent best.
- **Where the search fails (seed 1), clipping does not rescue it.** -139485.8 ->
  -120880.6 is a genuine 18,605-nat move toward the bar, but the run is still
  **152,667 nats away**. Recovering 11% of a catastrophic gap is not a rescue; both
  arms failed.

Pre-registered falsification #1 — "lane deaths fall but best-fit logL does not move
toward the reference, so clipping keeps lanes alive without making them useful" —
**fires on seed 0 exactly, and substantively on seed 1.**

## What the fix does do

It works, and it is not free of value:

- **Prior-exit deaths are eliminated**: 31655 -> 2 and 27870 -> 0 value-NaN
  lane-steps; alive fraction 0.34 / 0.42 -> **1.00**.
- **It costs nothing, and sometimes less than nothing**: +11% wall on seed 0
  (1126 -> 1255 s) but **-43% on seed 1** (2203 -> 1251 s). The unclipped bad seed
  spent nearly twice the wall time, because dead lanes keep stepping and keep
  paying a full likelihood-and-gradient evaluation whose output is discarded.
  Pre-registered falsification #3 (wall time rises materially) does **not** fire.
- **It makes the counters mean something.** With prior deaths gone the constrained
  count becomes visible (`constrained 6/16` in the seed-1 log) — the `ell_comps`
  trapping #128 predicted would surface once the larger failure was removed.

## The alive-versus-step curve

Graded on the curve, not the scalar, since the counters are survival integrals.
Living lanes at steps 1 / 10 / 50 / 100 / 300 / 1000 / 3000:

| arm | seed | curve |
|---|---:|---|
| `none` | 0 | 16, 16, **6**, 4, 6, 6, 5 |
| `none` | 1 | 16, 16, **5**, 6, 8, 7, 6 |
| `prior_box` | 0 | 16, 16, 16, 16, 16, 16, 16 |
| `prior_box` | 1 | 16, 16, 16, 16, 16, 16, 16 |
| `prior_box_reset` | 0 | 16, 16, 16, 16, 16, 15, 14 |

**The die-off is an early transient, not a steady bleed.** The population collapses
between steps 10 and 50 — while Prodigy is still taking its largest steps — and
then never recovers. This corrects the natural reading of the 60%-style scalar as
an ongoing hazard: it is one short window, integrated over the whole run.

It also shows lanes *returning*. `none` seed 0 reads 4 alive at step 100 and 6 at
step 300, so "dead" is a per-step non-finite state, not an absorbing one — a lane
that steps outside the box can step back in. The #128 framing of a lane that
"stays dead for every remaining step" is right about the accounting and wrong
about the mechanism.

## Arm 3 (momentum reset) — drop it

`prior_box_reset` is worse than plain clipping on both seeds.

On seed 0 it gives the same answer while degrading everything else: deaths
2 -> 2523, clips 15142 -> 18611, pinned 6 -> **7**, wall +39%.

On seed 1 it makes the answer itself **worse**: -120880.6 -> **-137783.6**, giving
back ~16,900 of the 18,600 nats plain clipping had recovered and landing almost
exactly on the unclipped -139485.8. So the one arm where clipping had bought
anything measurable is the arm the momentum reset undoes.

It was motivated by the prototype's 5/16 and the CPU run's 11/16 pinned lanes, on
the theory that a clipped lane keeps the velocity that pushed it out and is
re-projected onto the same bound forever. The measurement does not support the
remedy: zeroing momentum shortens each step, so lanes loiter near a bound and get
re-clipped rather than escaping, and some lose enough state to die outright.

Pre-registered falsification #2 — "most surviving lanes end pinned" — **does not
fire**: 6/16 and 4/16 (37%, 25%) on `prior_box`, well below the CPU run's 11/16.
The wall is not absorbing the population, so the premise for this arm was weaker
than the earlier float32 CPU numbers suggested.

## Do the clips calm down once the search finds the basin? (not measured)

15,142 clips is 31.5% of the 48,000 lane-steps, which invites the question of
whether clipping is an early transient that settles, or a steady state. **The
artefacts cannot answer it**: `n_clipped_lane_steps` is recorded only as a
lifetime total, and the per-step log reports `alive` and `constrained` but not
clips. `alive_history` was added for exactly this class of question and the clip
equivalent should have been added with it — that is a gap in this campaign, not a
property of the fix.

The indirect evidence says the clips **persist** rather than settling:

| arm | seed | clips | clips/step | pinned at end |
|---|---:|---:|---:|---:|
| `prior_box` | 0 | 15142 | 5.05 | 6/16 |
| `prior_box` | 1 | 15744 | 5.25 | 4/16 |
| `prior_box_reset` | 0 | 18611 | 6.20 | 7/16 |
| `prior_box_reset` | 1 | 8798 | 2.93 | 4/16 |

- ~5 of 16 lanes are clipped on an average step and ~4-7 lanes end pinned to a
  bound. Those matching is the tell: most of the count is a few lanes sitting *on*
  a boundary being re-projected every step, not a burst of early crossings.
- Seed 0 and seed 1 clip at nearly the same rate (31.5% vs 32.8%) despite one
  converging past the bar and the other failing by 152,667 nats. An early-transient
  effect would not survive that difference.
- Prodigy's step scale grows through the run (`d` ends at 2.26e-02 / 5.49e-02 /
  8.29e-01 against 1.00e-06 at step 1), so late steps are larger and make *more*
  boundary contact, not less. Clipping continued long after `gained 0.0000`.

`prior_box_reset` seed 1 is the one row that does not fit (2.93 clips/step on 4
pinned lanes), so the picture is not uniform and this stays an inference.

**Next step:** add `clipped_history` beside `alive_history` and re-run one arm at
a short budget. Cheap, and it converts this section from argument to measurement.

## The bigger finding: seed dependence dwarfs the clipper

Identical settings, two seeds, and the outcome swings **171,000 nats**: seed 0
beats the Nautilus bar, seed 1 never finds the basin. That is a property of the
search, not of the clipper, and it is larger than every effect this campaign set
out to measure.

It was invisible before this campaign. `_broad_starts` hardcoded
`np.random.default_rng(0)`, so every run drew seed 0's population — the lucky one.
Seeding `random`/`numpy` reached only the initializer. A single-seed study on this
cell would have reported the unclipped search as healthy with total confidence.

**This deserves its own task**, and it matters more than phase 3.

## Recommendation for phase 3

**Not on the evidence the campaign asked for.** The claim "clipping recovers the
lost lanes without changing the answer" is now measured: it recovers the lanes
completely, and the second half is true in a way that undercuts the first — the
answer does not change because the recovered lanes never mattered.

A narrower case for flipping the default does stand, and should be argued honestly
as hygiene rather than accuracy:

- it removes a silent failure mode where two thirds of a search population is
  discarded without any error surfacing;
- it costs nothing measurable and saves substantial time on the bad seed;
- it unmasks the constrained-lane accounting that is currently hidden behind it.

If phase 3 proceeds on those grounds, the re-baseline is cheap: on this cell the
converged answer is bit-identical, so no existing benchmark number moves.

**Not yet generalised.** One cell, one sampler, two seeds. The pixelized cells —
the ones `resurrect=True` exists for, and the strongest test of whether clipping
and resurrection interact badly — have not been run; they need more VRAM than the
laptop card has. `point_source` and the unbounded-prior negative control are also
outstanding. Phase 3 should not be written on `imaging/mge` alone.

## Reproducing

```bash
JAX_PLATFORM_NAME=cuda JAX_PLATFORMS=cuda,cpu XLA_PYTHON_CLIENT_MEM_FRACTION=0.5 \
JAX_ENABLE_X64=True SEARCHES_DISABLE_VIZ=1 \
python scripts/misc/searches/clipper_campaign.py \
    --arms none,prior_box,prior_box_reset --seeds 0,1 \
    --n-starts 16 --n-steps 3000 --sampler multi_start_prodigy
```

Requires PyAutoFit at or after the `seed` / `alive_history` /
`reset_momentum_on_clip` commit; a released wheel has none of it, and
`autofit.__file__` must resolve to the checkout.

Two traps worth keeping, both paid for here:

- **`--out` used to be a no-op** unless the directory sat under the repo's
  `output/`, so the per-arm clearing deleted an unrelated directory, a stale
  `.completed` short-circuited `fit()`, and the arm returned a **cached result in
  2.9 s with every counter `None`**. The `total_steps == n_steps` assertion is what
  caught it. The output root now goes through `conf`.
- **`search.summary` is `Key = Value`, not colon-separated.** A colon parser
  returns an empty dict and every counter reads `None` — indistinguishable from a
  clipper that never fired.

## Budget is not a detail

The cloud CPU session ran this comparison at 16x150 and found the arms identical,
concluding clipping was cosmetic. Both of its arms were ~47,316 nats from the bar
— neither had found the basin, so the comparison could not have detected a
difference either way.

At 105 steps on GPU/fp64 the clipped arm was **114 nats** closer to the bar than
the unclipped one; by 3000 steps that advantage is gone and the two agree exactly.
So clipping does buy convergence *rate* at short budgets, and nothing at long
ones. Any statement about this fix has to name the step budget it was measured at.
