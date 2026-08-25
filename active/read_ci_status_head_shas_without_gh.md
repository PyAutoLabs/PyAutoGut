# Read ci_status HEAD shas without gh, via git ls-remote

Type: feature
Target: PyAutoHeart
Repos:
- PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

# Read ci_status HEAD shas without gh, via git ls-remote

Type: feature
Target: PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: normal

## Problem

`heart/checks/ci_status.sh` reads each repo's `main` HEAD sha with
`gh api repos/<owner>/<name>/commits/main --jq .sha`. On a mobile/cloud session
`gh` is not installed, so the sha comes back empty. Readiness then cannot
confirm an ingested release-validation report against the live HEADs and reports
`release validation source unconfirmed (current HEADs unknown)`.

Observed 2026-08-25 in a cloud session: all three named evidence gaps were
cleared, yet readiness stayed STALE on this reason alone.

## Change

Read the sha with `git ls-remote <url> refs/heads/main` instead of `gh`, either
as the primary source or as the fallback when `gh` is absent.

This needs no authentication and no session repo attachment — it works on public
repos over the plain git lane. Verified in a cloud session for all five
release-gate libraries, including one whose `add_repo` attachment was refused
outright.

Keep it cheap: `ls-remote` with an explicit ref pattern is a single ref read, no
clone, and it slots into the existing `check_one_repo_ci` parallel fan-out, so
the `<30s` tick budget is unaffected. Preserve the current graceful degradation —
an empty sha on failure, never a fabricated one.

Scope is the sha only. The CI *conclusions* half still needs the Actions API and
is a separate task.

## Acceptance

- With `gh` absent, `pyauto-heart tick` records a real `head_sha` for each polled
  repo and readiness no longer emits `release validation source unconfirmed
  (current HEADs unknown)`.
- The tick stays inside its `<30s` budget.
- A failed `ls-remote` still yields an empty sha, not a wrong one.

<!-- formalised by the Intake (Conception) Agent on 2026-08-25 from file:/tmp/claude-0/-home-user/1e0c2b0b-8607-5d9d-8871-ab7a769bb699/scratchpad/p1_lsremote.md -->
