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
