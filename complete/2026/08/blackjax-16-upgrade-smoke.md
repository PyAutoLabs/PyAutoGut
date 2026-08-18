Validated the blackjax ≥1.6.2 environment for the inference programme —
Phase 0(b), the CPU half of critical-path item CP-2 — entirely from a
mobile/cloud session (human-directed scope: install/API validation, no GPU).

- **PR:** autolens_profiling#143 (merged `7a7eeaf`, closes #142).
- **All three checks PASS:** (1) blackjax 1.6.2 + jax 0.10.2 (CPU) +
  released autofit 2026.7.29.1 install cleanly together (`pip check`
  clean); (2) mainline `blackjax.nss` 2D toy smoke — logZ −4.609 ± 0.069 vs
  analytic −4.605, posterior recovered, full mainline API exercised
  (native-space logprior_fn, num_delete, dlogz termination via
  `state.integrator.logZ_live − logZ`, `ns.utils.finalise` +
  `log_weights` ensemble); (3) `af.BlackJAXNUTS` runs on 1.6.2
  **unmodified** — 0 divergences, acceptance 0.92 — no PyAutoFit
  compatibility fix needed.
- **Dependency findings:** PyAutoFit pins `blackjax>=1.2.0` (floor, no cap,
  `optional` extra) — the Gate-A floor bump is a one-liner; blackjax is not
  a hard autofit dependency, so every environment upgrade must install it
  explicitly.
- **Provenance upgrade for H2.1:** the installed 1.6.2 docstring states the
  `num_inner_steps ≥ max(5, 2·d)` rule and the upward logZ-bias direction
  verbatim — the programme's sharpest Phase-2 hypothesis is now cited from
  installed source, not release notes.
- **Deliverables:** `scripts/misc/searches/nss_smoke.py` (rerunnable,
  exits non-zero on FAIL — run in each environment after its upgrade) and
  `results/notes/inference/phase_00_unblocking/RESULTS.md`; PROGRAMME phase
  table 0(b) → validated (cloud CPU).
- **Remaining (laptop/RAL):** apply the upgrade to the local venvs and the
  RAL stack and re-run the smoke there; the GPU MGE smoke half of CP-2.
  Phase 0(c) (RAL harvest) is now the only untouched Phase 0 item.

## Original prompt

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
