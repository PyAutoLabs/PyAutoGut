# Tenant-firewall drift: 9 mismatches vs repos.yaml (Aug 2026)

Type: maintenance
Target: pyautomind
Difficulty: easy
Autonomy: supervised
Priority: normal

Heart's manifest-drift check is YELLOW: `PyAutoMind/scripts/repos_sync.py
--check` reports **check tenant firewall (organ code): 9 mismatch(es)** —
instance facts (satellite repo names) hardcoded in Brain/Heart/Hands organ
code outside the declared config surfaces (`FIREWALL_ALLOWLIST`). Same class
as the 2026-07-18 `tenant-firewall-drift` task; remedy is the same per-file
allowlist-vs-refactor judgment.

## Original request (verbatim)

> sort this: - Heart's one real warning: manifest drift: tenant firewall — 9
> mismatches vs PyAutoMind/repos.yaml. This is the recommended next checkpoint
> to clear YELLOW.

## Findings (from `repos_sync.py --check`, 2026-08-17)

Production files (2):

- `PyAutoBrain/agents/conductors/intake/_intake.py` — `autofit_workspace`
  (line 890): new token in an already-allowlisted file. It appears in a
  docstring describing measured noise classes ("Repo names —
  `autofit_workspace` (26 files)…") — documentation prose, not routing logic.
- `PyAutoHeart/heart/smoke.py` — 11 tokens (`HowToLens`, `PyAutoArray`,
  `PyAutoFit`, `PyAutoGalaxy`, `PyAutoLabs`, `PyAutoLens`,
  `autofit_workspace`, `autogalaxy_workspace`, `autolens_workspace`,
  `autolens_workspace_test`, `euclid_strong_lens_modeling_pipeline`): the
  `WORKSPACES` dict — a declared config surface mapping workspace keys to repo
  names + library dependency chains, same shape as the already-allowlisted
  `PyAutoHeart/heart/validate.py`.

Test files (7 — fixture names, baseline entries per precedent):

- `PyAutoBrain/tests/test_intake_dashboard.py` — `PyAutoLabs`
- `PyAutoBrain/tests/test_intake_reconcile_ranking.py` — `PyAutoArray`,
  `PyAutoFit`, `PyAutoLabs`, `autofit_workspace`, `autolens_workspace`
- `PyAutoBrain/tests/test_profiling_conductor.py` — `autolens_profiling`
- `PyAutoBrain/tests/test_worktree_conflict_guard.py` — `HowToFit`,
  `PyAutoArray`, `PyAutoFit`, `PyAutoGalaxy`, `PyAutoLens`, `PyAutoReduce`,
  `autolens_workspace`
- `PyAutoHeart/tests/test_release_run.py` — `autolens_workspace`
- `PyAutoHeart/tests/test_smoke.py` — `PyAutoArray`, `PyAutoFit`,
  `PyAutoLabs`
- `PyAutoHands/tests/test_pre_build_staging.py` — `HowToFit`, `PyAutoLabs`,
  `autofit_workspace`, `autolens_assistant`, `autolens_workspace`

## Remedy

Per-file allowlist-vs-refactor judgment per the tenant-firewall design
(`FIREWALL_ALLOWLIST` header: "never grow it casually"). Expected outcome:
extend the baseline in `PyAutoMind/scripts/repos_sync.py` for legitimate
branded facts / test fixtures; refactor only where a fact should derive from
the body map. Verify with `repos_sync.py --check` → tenant firewall OK, and
Heart's `manifest_drift` check going green on the next tick.
