- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/179
- completed: 2026-08-25
- library-pr: PyAutoHeart#180 (merged a570d0a -> main) — shared with #178, the two halves of one no-gh path
- what shipped: `HEART_CLOUD_CI_DIR` (`$HEART_STATE_DIR/cloud_ci/<Name>.json`) holding `{ts, runs}`, read by `ci_status.cloud_runs()` and consulted by `main` **only when the live fetch already failed**. New `source` field on the sidecar (`"gh"` | `"cloud"`) recording provenance. `ts` optional — file mtime is used when absent.
- why the ordering matters: `gh` is authoritative and is never second-guessed, so on the dev box `error` is empty and the new path never runs. That is what keeps dev-box behaviour byte-for-byte unchanged.
- the insight that made it small: MCP's `list_workflow_runs` returns exactly the `{"workflow_runs": [...]}` snake_case shape `normalize_runs` already expects — verified against the live API — so nothing is reshaped on the way in. Mirrors `test_run.py`'s proven `cloud_validation.json` hand-off rather than inventing a second idiom.
- speed decision that matters most: the tick does **no** network work for this. It only reads the drop point, as it already reads `cloud_validation.json`; population is a separate one-shot leg. ~20 repos of network calls inside the tick loop would blow the <30s budget outright.
- fails closed everywhere: unreadable, malformed, empty, undated-and-un-stat-able, or past `HEART_CLOUD_CI_MAX_AGE` (default 3600s) all degrade to the same `unavailable` a failed fetch produces, never a stale green. A rejected payload appends its reason to the original fetch error rather than vanishing, so "no gh AND the payload was stale" is one readable string.
- validation: 635 tests pass (13 new across `cloud_runs`' freshness/fail-closed paths and `main`'s ordering). End-to-end in a gh-less container against a drop point built from a real MCP response: consumed with `source="cloud"` and the error cleared.
- the finding worth keeping: that same run still declined to report success, because PyAutoFit's `main` advanced between fetching the runs and the tick, so the pre-existing `on_head` guard marked them off-HEAD. The guard working as intended — and the reason the age bound alone is not sufficient. **A payload can be fresh by clock and stale by commit.** The on-HEAD success path is covered by a unit test rather than by rewriting the sha to force a green.
- standing constraint, not solved here: the Actions API needs each repo attached to the session, and attachment can be refused — it was, for one library, during the session that motivated this. Such a repo degrades to `unavailable`, which is correct rather than an error, but it means this half delivers less on mobile than #178 does.

## Original prompt

# Feed ci_status run conclusions from an MCP drop point

Type: feature
Target: PyAutoHeart
Repos:
- PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

# Feed ci_status run conclusions from an MCP drop point

Type: feature
Target: PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: normal

## Problem

`heart/checks/ci_status.sh` fetches each repo's recent `main` workflow runs with
`gh api`. On a mobile/cloud session there is no `gh`, so every polled repo
records `status="unavailable"` and CI is unknown per-library.

Observed 2026-08-25 in a cloud session: readiness reported five
`CI status unavailable` rows, all from this one missing binary.

## Why this is small

`gh` is only **transport**, not judgment. The reasoning already lives in
`heart/checks/ci_status.py`, which reads a REST-shaped
`{"workflow_runs": [...]}` payload from stdin (`ci_status.py:113,127`).
`mcp__github__actions_list(list_workflow_runs)` returns exactly that shape,
snake_case keys included — verified against PyAutoLabs/PyAutoHeart. The MCP tools
already emit byte-compatible input for the existing parser, so nothing needs
reimplementing.

The pattern is proven here already: `test_run.py:64-72` defines an MCP-supplied
drop point for precisely this case, and that is what cleared the test-run gap on
mobile. Mirror it rather than inventing a second idiom.

## Change

- Add a per-repo drop point (e.g. `$HEART_STATE_DIR/cloud_ci/<Name>.json`
  carrying `{runs, ts}`).
- `check_one_repo_ci` prefers the drop point when present and within an age
  bound, falls back to `gh`, then to today's `unavailable`.
- Brain populates it via MCP using the same "bash cannot call MCP, so emit a plan
  the agent executes" hand-off `rehearse.sh` already uses.

## Keeping it fast

1. **The tick never does network work for this.** Population is a separate
   one-shot leg; the `<30s` tick only *reads* the drop point, exactly as it reads
   `cloud_validation.json`. 20 repos of network calls inside the tick loop would
   blow the budget outright.
2. **Default scope is the five release-gate libraries**, not the whole poll set —
   5 MCP calls, not 20. A full sweep stays available but opt-in.
3. **No MCP call for the sha.** That half is `git ls-remote` (separate task),
   which halves the round trips and needs no repo attachment.
4. **Age-bound the drop point** so stale data never masquerades as fresh.

Note the operational constraint: the Actions API requires each repo attached to
the session, and attachment can be refused. Degrading to `unavailable` for a repo
that cannot be reached is the correct outcome, not an error.

## Acceptance

- In a cloud session with no `gh`, `pyauto-heart tick && pyauto-heart readiness`
  reports CI status for the five release-gate libraries.
- The tick stays inside its `<30s` budget with the drop point populated.
- With neither drop point nor `gh`, behaviour is unchanged from today.
- A drop point past its age bound reads as `unavailable`, never as fresh.

<!-- formalised by the Intake (Conception) Agent on 2026-08-25 from file:/tmp/claude-0/-home-user/1e0c2b0b-8607-5d9d-8871-ab7a769bb699/scratchpad/p2_dropoint.md -->
