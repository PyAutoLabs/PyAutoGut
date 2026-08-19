# Repin autolens_workspace_test vmap literals stale since the PositionsLH penalty fix

Difficulty: small
Autonomy: high
Priority: high

## Symptom (Heart finding)

The nightly release has been blocked at Stage 3 (release-fidelity integration,
@PyAutoHeart `Release Integrate`) for two consecutive nights (2026-08-18 run
32094560862, 2026-08-19 run 32211283776) by the same three script parity
failures in @autolens_workspace_test, run against the nightly dev wheels
(autolens 2026.8.19.1.dev72301):

- `scripts/imaging/jax_likelihood/lp.py` — FAIL 7.7s, pinned `-1.34797827e09`
- `scripts/imaging/substructure/subhalo.py` — FAIL 9.1s at Scenario A, pinned `-1.412105e09`
- `scripts/interferometer/jax_likelihood/lp.py` — FAIL 6.6s, pinned `-1.16915394e09`

All sibling jax_likelihood / jax_grad scripts pass. The 2026-08-17 nightly
released cleanly, so the change landed on a library main between 08-17 03:00
and 08-18 03:00 UTC.

## Root cause (established)

@PyAutoLens PR #700 (`fb1aefe`, merged 2026-08-17 22:06 UTC — after that
morning's 2026.8.17.1 release) fixed `AnalysisLens.log_likelihood_penalty_from`:
the accumulator was overwritten per entry then added to itself, so the analysis
subtracted **2x the last** `PositionsLH` penalty and discarded earlier entries.
It now subtracts the documented sum (1e8/arcsec fence, not the accidental
2e8/arcsec). Inside-threshold results are unchanged.

The three failing scripts are exactly the ones whose pinned `fitness._vmap`
literals were generated with an **active** positions penalty at prior medians
(PowerLaw lens median trips the 0.4" threshold on the jax_test datasets), so
their literals encode the old 2x slope. Corroboration:

- `multipole.py` (same PowerLaw median, same PositionsLH) passes — it pins no
  vmap literal, only JIT-vs-NumPy self-consistency.
- `smbh.py` pins `+1194.85` — Isothermal median, penalty inactive.
- `delaunay.py` / interferometer `rectangular.py` have PositionsLH commented out.
- PR #700 repinned PyAutoLens's own unit tests (`-4.4097e10` → `-2.2049e10`,
  the 2x-last signature) but not these workspace-test parity literals.
- Pins in @autolens_workspace_test untouched since ≤ 2026-08-10; the
  mass-sensitivity audit (#253/#254) marks these scripts' literals as the
  genuinely sensitive ones.

## Fix

In @autolens_workspace_test only (the library fix is correct — do not touch
@PyAutoLens, and do not weaken any script): regenerate every stale vmap
literal against current library mains / nightly dev wheels:

- `scripts/imaging/jax_likelihood/lp.py` (1 literal)
- `scripts/interferometer/jax_likelihood/lp.py` (2 literals)
- `scripts/imaging/substructure/subhalo.py` (Scenario A/B literal and, if
  shifted, the C/D literal — all four scenarios share the penalty-active lens)

Validate by running the three scripts end-to-end against the same dev-wheel
set Stage 3 uses (autolens 2026.8.19.1.dev72301). Expected relationship for a
sanity check: new = old + P with P = 1e8 * (median max_separation − 0.4) per
dataset. The mass-sensitivity floor asserts from #254, where present, must
still hold after repinning.

## Impact

Unblocks the nightly release (Stage 3 gate) — currently no release can ship.
