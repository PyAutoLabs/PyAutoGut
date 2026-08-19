# positions-penalty-repin

- shipped: 2026-08-19
- PR: https://github.com/PyAutoLabs/autolens_workspace_test/pull/257 (squash-merged as `197ce6e`)
- repos: autolens_workspace_test (pins only — no library change)
- session: cloud (Claude Code remote), driven from the /wake_up → /bug flow

## Summary

The nightly release was blocked at Stage 3 (release-fidelity integration) on
2026-08-18 and 2026-08-19 by three `autolens_test` script parity failures.
Root cause: PyAutoLens PR #700 (`fb1aefe`, merged 2026-08-17 22:06 UTC, after
that morning's 2026.8.17.1 release) fixed
`AnalysisLens.log_likelihood_penalty_from` — the accumulator was overwritten
per entry then added to itself, so the analysis subtracted **2×** the last
`PositionsLH` penalty. It now subtracts the documented 1e8/arcsec sum. Every
`autolens_workspace_test` script whose pinned `fitness._vmap` literal was
generated with an **active** positions penalty at prior medians therefore saw
its likelihood halve (observed ratios 0.49987–0.49999980). The library fix is
correct; the pins were stale. Repinned (no script logic touched):

- `imaging/jax_likelihood/lp.py`: `-1.34797827e09` → `-6.74165366e08`
- `interferometer/jax_likelihood/lp.py` (×2, incl. TransformerNUFFT
  cross-check): `-1.16915394e09` → `-5.84578547e08`
- `interferometer/jax_likelihood/mge.py` (×2): `-7.94439429e08` → `-3.97221282e08`
- `imaging/substructure/subhalo.py` A/B: `-1.412105e09` → `-7.062287e08`;
  C/D: `-1.349200e09` → `-6.747760e08`

Regenerated and validated green end-to-end against the exact library mains of
the failing rehearsal (autolens `6087581`, autofit `21288bb`, autoarray
`74cf5a0`, autogalaxy `49115ad`, autonerves `b6b6ab6`) under the release env
profile in a cloud container (pip install from main checkouts; the nightly
dev wheels are not on public PyPI). Smoke CI (3.12 + 3.13) green on the final
head; merged same day. Confirmation the blocker is cleared = the next nightly
(03:00 UTC) passing Stage 3.

## Key traps / findings

- **A "green" nightly can be a blocked nightly.** The Nightly Release run
  renders a gate-blocked night as success (OUTCOME CONTRACT); the signal is
  the "Blocked at a gate — no release was made" step, not the run conclusion.
  Same trap at Stage 3: the Heart run had 0 *failed jobs* on page 1 — the two
  failing `run_scripts` jobs were on page 2 of the 53-job list, and
  `get_job_logs failed_only` missed them.
- **Coverage seams hide siblings.** The nightly caught 3 scripts; smoke
  caught a 4th (`interferometer/mge.py`) because the release Stage 3
  interferometer group doesn't run it but the smoke set does — and this PR
  was the *first* smoke run against post-#700 mains (previous: 08-10). After
  any deliberate numeric contract change, sweep ALL pinned literals
  (`grep -rn -- '-[0-9]\.[0-9]*e0[789]'`), not just the ones CI flagged.
- **Which scripts carry penalty-scale pins**: only those where the median
  model trips the 0.4" positions threshold (PowerLaw lens median on the
  jax_test datasets) AND pin a vmap literal. `multipole.py` (same median, no
  vmap pin) and `smbh.py` (Isothermal median, penalty inactive, pin
  `+1194.85`) were correctly untouched. Pin-shift arithmetic: new = old + P;
  penalty-dominated pins halve.
- **`ENV: jax full_datasets` headers make smoke and release evaluate the same
  configuration** for these scripts — one pin serves both profiles (local
  full-dataset run reproduced CI's smoke value exactly).
- The Bug Agent's deterministic classifier misread this prompt as
  "infrastructure (PyAutoMind), too-large" — keyword heuristic; the evidence
  said small workspace_test repin. Decision overridden on evidence.
- Cloud repro path that worked: clone library mains at the rehearsal's exact
  SHAs + `pip install ./pyautonerves ./pyautofit ./pyautoarray ./pyautogalaxy
  ./pyautolens jax==0.10.2 jaxlib==0.10.2 nufftax pynufft==2025.1.1
  jaxnnls==1.0.1` into a **Python 3.12** venv (autonerves requires ≥3.12;
  container default 3.11 fails). Datasets auto-simulate deterministically.

## Original prompt

Filed as `draft/bug/health_fixes/positions_penalty_stale_pins.md` (2026-08-19,
this session); see git history of that file for the full text — symptom
(2 nights of Stage 3 blocks, runs 32094560862 / 32211283776), root-cause
analysis, and the fix plan that was executed unchanged apart from the
smoke-discovered fourth script.
