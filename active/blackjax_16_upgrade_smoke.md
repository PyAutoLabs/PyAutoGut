# Phase 0(b): validate blackjax ≥1.6.2 + mainline NSS smoke + BlackJAXNUTS 1.6 API check

Type: maintenance
Target: autolens_profiling
Repos:
- @autolens_profiling
Difficulty: small
Autonomy: supervised
Priority: high

Phase 0(b) of the inference programme
(`autolens_profiling/results/notes/inference/PROGRAMME.md`) — the
environment-validation half of critical-path item CP-2, runnable on CPU in a
cloud session (human-directed 2026-08-18: "no need for laptop as not actually
doing gpu runs for profiling just getting install type stuff working"). The
GPU MGE smoke half of CP-2 stays laptop work.

Task:
- Install blackjax ≥1.6.2 with CPU JAX in a clean venv; record the resolved
  versions and any dependency friction.
- Smoke `blackjax.nss` on a 2D toy with an analytic evidence check (Gaussian
  likelihood × uniform prior → known logZ), using the mainline API
  (native-space `logprior_fn`, `num_delete`, dlogz termination, ensemble
  logZ error via `utils.finalise`) — the API shape Phase 2's
  profiling-local runner will wire.
- Install released `autofit` alongside blackjax 1.6 and check
  `af.BlackJAXNUTS` against the 1.6 API (import + tiny CPU fit on a toy
  likelihood). Check whether PyAutoFit's requirements cap blackjax below
  1.6 — a cap is a source finding for the §7 change list.
- Record findings in
  `results/notes/inference/phase_00_unblocking/RESULTS.md` (created by this
  task) and update the PROGRAMME phase-state table: 0(b) validated on cloud
  CPU, local venv + RAL stack upgrades remaining.

No profiling conclusions from any timing observed here (wrong tier, CPU toy
scale); this is install/API validation only.
