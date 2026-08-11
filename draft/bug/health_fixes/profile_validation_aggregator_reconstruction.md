# Finish the profile-validation fix for the aggregator reconstruction path

Type: bug
Target: health_fixes
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised

## Context

The new profile constructor guards added by PyAutoGalaxy
[#566](https://github.com/PyAutoLabs/PyAutoGalaxy/pull/566) reject parameter values that
the **results/aggregator** paths legitimately replay from stored samples, blocking the
nightly release at Stage 3. A follow-up fix
([#568](https://github.com/PyAutoLabs/PyAutoGalaxy/pull/568)) closed most of it; **one
path remains open**.

Owners: @PyAutoGalaxy (fix locus), @autolens_workspace, @autogalaxy_workspace.

## What happened, in order

| When | PyAutoGalaxy SHA | Effect |
|---|---|---|
| 2026-08-07 | `63d69b87` | Release 2026.8.7.1 shipped; Stage 3 integrate **51/51 green** |
| 2026-08-09 22:33Z | `a366f771` (#566) | Guards land → 4 scripts fail on 08-10 |
| 2026-08-10 22:53Z | `be61b8d0` (#568) | "resample invalid profile parameters" → down to 1 script on 08-11 |

#566 added, per its own message:

- **B11** — `sersic_index <= 0` / non-finite, guarded at both Sersic bases.
- **B12** — `ell_comps` outside the unit circle, guarded once at `EllProfile`,
  "the single base every elliptical light and mass profile inherits".

Both guards are correct in principle; the unit suite was green ("1080 passed, zero
regressions"). What they did not cover is **reconstruction of historical sampled
values**, where boundary and degenerate points genuinely occur.

## Evidence

**2026-08-10** — integrate run
[31354307923](https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/31354307923), 4 scripts:

- `autogalaxy_workspace/scripts/guides/results/start_here.py` —
  `ValueError: ell_comps must satisfy ell_comps[0]**2 + ell_comps[1]**2 < 1; got (0.9291695328614863, 0.9295569...)`
- `autogalaxy_workspace/scripts/guides/results/aggregator/samples_via_aggregator.py` —
  same, `got (0.7622534931728601, ...)`
- `autogalaxy_workspace/scripts/guides/results/aggregator/samples.py` —
  `ValueError: sersic_index must be a finite positive number; got 0.0`
- `autolens_workspace/scripts/group/features/pixelization/cpu_fast_modeling.py` —
  same ell_comps guard, `got (-0.9485691198305576, ...)`

**2026-08-11** — integrate run
[31456732688](https://github.com/PyAutoLabs/PyAutoHeart/actions/runs/31456732688), 1 script:

- `autolens_workspace/scripts/guides/results/aggregator/samples.py` —
  `autogalaxy.exc.ModelParameterException: ell_comps must satisfy ell_comps[0]**2 + ell_comps[1]**2 < 1; got (-0.6204377795161573, 0.8320610222286696), whose magnitude is 1.0379154989512194`

Note the exception **class** changed between the two nights (`ValueError` →
`autogalaxy.exc.ModelParameterException`) while the message stayed identical. That is
#568 re-typing the guard so the sampler treats it as a rejection and resamples.

## Why one script still fails

#568's remedy is *resampling* — valid while a search is running and free to draw
another point. The surviving failure is in an **aggregator** script, which reconstructs
profiles from samples already written to disk. There is no sampler in that path and
nothing to resample: the stored value has magnitude 1.0379 and the guard rejects it,
so the script dies.

This also explains why the failing set looked non-deterministic across nights while the
count stayed ~20: which stored/sampled points sit outside the unit circle varies run to
run.

## Required work

1. Decide the contract for reconstruction, and write it down: when `EllProfile` is
   rebuilt from a stored sample, is an out-of-circle `ell_comps` an error, or is it
   data to be surfaced? A guard that is right at user construction time is not
   automatically right at deserialization time.
2. Fix in **PyAutoGalaxy**. Options, in the order they should be considered:
   (a) apply the guard only on user-facing construction and let the aggregator
   reconstruct-and-report; (b) have the aggregator filter or flag invalid stored
   samples with a clear message naming the sample; (c) keep the raise but make the
   aggregator surface it as a skipped sample rather than a crash.
   Do **not** widen or delete the guard to make the script pass — #566 fixed real
   defects (B12 previously produced silent all-NaN deflections).
3. Do not edit the workspace script or park it in `no_run.yaml`.
4. Add coverage for the reconstruction path — a stored sample outside the unit circle
   round-tripped through the aggregator. The gap that let this through is that #566's
   1080 passing tests contained no such case.
5. Confirm the three scripts that #568 already fixed stay fixed; only
   `guides/results/aggregator/samples.py` should change state.

<!-- filed by the Bug Agent (health-issue mode) on 2026-08-11 from nightly runs 31354026679 + 31456340441 -->
