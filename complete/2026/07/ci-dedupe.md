Fleet CI dedupe: every PR's checks now run exactly once.

- issue: PyAutoLabs/PyAutoHeart#130 (left open for human close)
- prs: 17, one per repo, all merged (HowTo x3 #41/#52/#64, workspaces #129/#192/#405,
  workspace_test #13/#80/#100/#235, libraries Nerves#144/Fit#1432/Array#426/
  Galaxy#540/Lens#669/CTI#103, Heart#131)
- change (26 workflow files): bare `on: [push, pull_request]` → `push: branches: [main]`
  + `pull_request`, plus a concurrency group cancelling superseded runs on PR refs
  ONLY — never main, since `cancelled` ∈ Heart FAILURE_CONCLUSIONS (a cancelled main
  run would read as red CI). Post-merge main runs preserved (Heart ws_ci input).
- live proof: PR check rows dropped 8-12 → 5-6 on the batch's own PRs.
- trade-off: a branch pushed with no open PR gets no CI until its PR opens.
- incident: autogalaxy_workspace_test's 3.13 smoke leg hung 1h46m inside "Run smoke
  tests" (known workspace_test hang class) — cancelled + rerun → green in ~13 min.

## Original prompt

# Fleet CI dedupe: stop running every PR's checks twice

Type: maintenance
Target: ci
Repos: 17 (HowTo x3, workspaces x3, workspace_test x4, libraries x6, PyAutoHeart)
Difficulty: small
Autonomy: safe
Priority: high
Status: issued — https://github.com/PyAutoLabs/PyAutoHeart/issues/130

24 workflows are bare `on: [push, pull_request]` → every PR commit runs CI twice.
Fix: `push: branches: [main]` + `pull_request` + concurrency cancel-in-progress on
non-main refs only (cancelled ∈ Heart FAILURE_CONCLUSIONS — never cancel main).
Filed from the 2026-07-30 CI/release audit follow-on assessment.
