# Spawn Drift detects drift but nothing regenerates — wire the self-heal

Type: maintenance
Target: PyAutoMind
Repos:
- PyAutoMind
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

`Spawn Drift` (`.github/workflows/spawn_drift.yml`) is a drift check with no
generator behind it. The templates are declared a generated view, but the only
thing that ever regenerates them is a human typing `/spawn --apply`. So the
scheduled leg goes red, stays red, and is cleared by hand.

## The scheduled leg is real; the dispatch leg is not a check

Both legs run **identical code** — the workflow has no trigger-dependent
behaviour at all: no `actions/checkout`, no `github.ref`, no
`github.event_name`, no `if:` (as of the run history below; issue #118 later
added a PR-only `if:` to the drift job). It clones all four repos fresh from
their default branches and diffs. Reproduced locally: same six drifts as the
scheduled run.

The difference is purely *when* each leg runs relative to a human `--apply`:

| date | template force-synced | dispatch run | gap | result |
|---|---|---|---|---|
| 2026-07-13 | `11:08:46Z` (`aef2ebb6`) | `11:09:02Z` | 16 s | PASS |
| 2026-07-27 | `19:30:29Z` (`3424dba1`) | `19:30:48Z` | 19 s | PASS |

A leg fired seconds after the human stamped the templates cannot fail. Every
green run in the workflow's history is one of these. Meanwhile every scheduled
run since 2026-07-20 failed:

| run | date | event | failure |
|---|---|---|---|
| 29240410170 | 2026-07-13 | schedule | drift |
| 29731899064 | 2026-07-20 | schedule | 22 + 15 drifts |
| 30256898178 | 2026-07-27 | schedule | UNMATCHED `issued/remove_pulse_compat.md` |
| 30804113655 | 2026-08-03 | schedule | 6 drifts |

## Scope

Mirror the `lifecycle_drift.yml` self-heal (issue #116), which solved the same
shape of problem for the same reason — Mind takes pushes from many concurrent
agent sessions, so an alarm-only check just emails a human once per push.

On schedule: regenerate and, if the tree differs, **open a PR** rather than
pushing. Do NOT copy lifecycle_drift's direct bot-push: these two repos are
force-synced generated views, so an automated push here is a force-push to a
published repo's `main`. A PR keeps the sanctioned-force-push exception a human
act while removing the "nothing regenerates" gap.

Keep the check failing when regeneration itself fails (UNMATCHED, canary hits) —
those are human decisions by design and must not be auto-resolved.

## Depends on

Issue #118 (`spawn-empty-body-privacy-fix`) must land first. Until it does,
regenerating publishes instance content, so an *automated* regenerate would
publish a leak on a schedule rather than only when a human ran `--apply`.

## Also worth deciding

The weekly cadence was chosen when the templates were assumed near-static. With
`empty_body()` fixed the churn drops sharply (registry edits no longer drift the
template), so weekly may now be right — re-check after #118 lands rather than
tuning the cron blind.
