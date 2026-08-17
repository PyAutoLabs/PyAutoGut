# Tenant-firewall drift: clear the 9 right + gate recurrence (Aug 2026)

Type: maintenance
Target: pyautomind
Difficulty: medium
Autonomy: supervised
Priority: normal

Heart's manifest-drift check is YELLOW: `PyAutoMind/scripts/repos_sync.py
--check` reports **check tenant firewall (organ code): 9 mismatch(es)**.
Deep-research pass (2026-08-17, three parallel agents over the design docs,
CI surfaces, and each finding) overturned the naive allowlist-all-9 clear and
set the scope to a two-phase arc, per the recorded decision rule
(`complete/2026/08/autohands-firewall-allowlist.md`): **"derivable or
arbitrary → refactor; genuine branded fact → declare the surface."**

## Original request (verbatim)

> sort this: - Heart's one real warning: manifest drift: tenant firewall — 9
> mismatches vs PyAutoMind/repos.yaml. This is the recommended next checkpoint
> to clear YELLOW.

> do deep research that this is the right approach long term to sort it all
> and stop recurrance of any issues

## Research conclusions (evidence in the issue)

- The allowlist reached its intended terminal state 2026-07-10 (72 files /
  262 tokens: "docstring examples + test fixtures + workspace-root defaults
  only", `complete/2026/07/pyautoscientist-4b.md`); it has since accreted to
  109 files / 430 tokens through six reactive drift patches. Growing it
  casually is what the header forbids.
- All 9 findings postdate the July clear; every one merged through a green PR
  because **no CI anywhere runs the firewall check** (organ test workflows
  are deliberately pytest-only; Mind's own CI never executes `repos_sync.py`;
  Heart's `manifest_drift` is exit-0 local-only monitoring invisible to the
  cloud health run). Recurrence is structural until a PR-time gate exists.
- Explicitly rejected shortcut (do not re-propose): teaching the checker to
  ignore comments/docstrings (`complete/2026/08/autohands-firewall-allowlist.md`).

## Phase A — clear the 9 by the decision rule

- `PyAutoHeart/heart/smoke.py`: **extract** `WORKSPACES` + `IMPORT_NAMES` to a
  `smoke:` block in `PyAutoHeart/config/repos.yaml` with a strict loader
  (twin precedents: Heart `version_skew`, Hands `autohands/config/
  workspaces.yaml`, both from `pyautoscientist-3b-config`). Reword the
  residual `--root` help string ("organism root"). Extend `check_heart` in
  `repos_sync.py` to validate the new block's repo names against the manifest.
- **Genericise fixtures** (synthetic names, verified non-load-bearing; add the
  convention comment so real names don't creep back):
  `PyAutoBrain/tests/test_worktree_conflict_guard.py`,
  `test_intake_dashboard.py`, `test_profiling_conductor.py`,
  `PyAutoHeart/tests/test_smoke.py`, `test_release_run.py`.
- `PyAutoHands/tests/test_pre_build_staging.py`: **derive in-file** — replace
  arbitrary repo literals with picks from the already-parsed `SPECS`; rename
  the `PyAutoLabs` fixture dir.
- **Allowlist only the 2 justified**: `_intake.py` +`autofit_workspace`
  (measured-noise docstring where names/counts are the evidence);
  `tests/test_intake_reconcile_ranking.py` (assertions pin resolution against
  the live body map). Net +1 entry / +1 token. Run the exactness/negative-probe
  audit the Aug 5 record mandates on any allowlist growth.

## Phase B — PR-time enforcement (stop recurrence)

- `repos_sync.py main()`: add an `--only <check-label>` selector (all-or-
  nothing today; an organ gate must fail only on the leg it can cause).
- `PyAutoBrain/.github/workflows/tests.yml`: add the firewall step (already
  checks out Brain+Mind side by side — the exact layout `--root` needs).
- `PyAutoHeart/.github/workflows/heart-tests.yml` and
  `PyAutoHands/.github/workflows/tests.yml`: restructure to path-based
  checkout + `PyAutoLabs/PyAutoMind` sibling, add the same step.
- Mind-side leg: run the firewall (four-repo checkout) on PRs touching
  `scripts/repos_sync.py`, so allowlist edits are themselves verified.

## Phase C — filed separately, not in this task

Draft prompt for the design's own endgame (assessment §8-4): teach
`repos_sync --write` to stamp organ config surfaces from the body map +
per-organ policy, removing hand-mirroring entirely.

## Verification

`repos_sync.py --check` → tenant firewall OK, all other legs unchanged;
pytest green in Mind/Brain/Heart/Hands (incl. the touched test files); Heart
`manifest_drift` → "identity in sync"; each organ's amended workflow passes on
its own PR (the gate step proving itself).
