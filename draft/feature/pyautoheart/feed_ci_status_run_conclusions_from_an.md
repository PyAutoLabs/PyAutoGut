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
