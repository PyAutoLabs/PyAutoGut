Wired the generator behind `Spawn Drift`. The check detected drift but nothing
regenerated: the templates are declared a generated view, yet the only thing
that ever regenerated them was a human typing `/spawn --apply`. So the scheduled
leg went red, stayed red, and was cleared by hand.

Every green run in the workflow's history was a manual dispatch fired 16-19
seconds after such a sync (2026-07-13 `11:08:46Z` → `11:09:02Z`; 2026-07-27
`19:30:29Z` → `19:30:48Z`), which is exactly why it could not fail. This closes
the arc opened by #118.

## What ships

On schedule/dispatch the workflow regenerates and opens (or refreshes) a sync PR
on each drifted template repo.

**A PR, not a bot push.** These repos are force-synced generated views, so an
automated push would be a force-push to a published `main`. #118 — a leak that
sat public for eight days — is the argument for a human seeing what gets
published. This keeps the sanctioned force-push a human act while removing the
"nothing regenerates" gap.

## The safety interlock

`--check` collapsed every failure into exit 1. Now:

| code | meaning | reaches the PR step? |
|---|---|---|
| 0 | clean | — |
| 1 | content drift — mechanical | **yes** |
| 2 | UNMATCHED or canary hit — human decision | no |
| 3 | unhandled exception | no |

A canary hit means the regenerated tree carries live instance content, so
auto-proposing it would be #118 with a robot doing it.

## Two defects found by EXECUTING the workflow, not reading it

Both `run:` blocks were extracted and run under `bash -e` against a CI-shaped
fixture with `git push`/`gh` stubbed. That surfaced:

1. **A latent bug from #120.** `stamp_complete_index()` broke on a *relative*
   `--write DIR` — the child resolves the script path after chdir'ing to `cwd`,
   so `--write regenerated` (what a CI step naturally passes) died with "can't
   open file". Every invocation to date happened to use an absolute path.
2. **A crash was indistinguishable from drift.** Python exits 1 on an unhandled
   exception, so the self-heal would have read defect 1 as "templates are stale"
   and proposed a PR from a partial tree.

## Independent review (Codex) — six findings, all real, all fixed

**The most important: this change broke rule 9, which it had established one PR
earlier.** Adding the PAT-dependent step meant the template would ship
`secrets.PAT_PYAUTOLABS`, violating the no-configured-secret condition.
Confirmed against a post-merge generation.

The root cause was in the **tests**: the `.github` fixtures were hand-written
miniatures, so `test_no_shipped_workflow_needs_a_configured_secret` was checking
a toy workflow with no PAT while the real one had grown one. Fixtures now READ
THE REAL WORKFLOW FILES; control-tested — shipping `spawn_drift.yml` again fails
four tests including the secret check.

Rule 9b accordingly revised `KEEP`-with-schedule-stripped → **DROP** (human
decision): the self-heal makes the workflow depend on a PAT *and* on published
`*-template` repos, so every path in it is unrunnable in a fresh org. The
generator and its guards still travel via `scripts/` and `tests/`. The
schedule-strip transform is retired as dead code with its tests.

Also fixed:

- `gh pr view` matches **merged and closed** PRs, so once a sync PR was merged
  the reused branch would report "refreshed" forever and never open another.
  Now `gh pr list --state open --head`; both paths dry-run tested.
- Every exit-code test compared a subprocess result with constants from the same
  module — swapping `EXIT_DRIFT`/`EXIT_UNSAFE` would have left them green while
  the workflow still auto-proposed literal exit 1. Two tests now pin the
  CONSUMER against the producer by reading the real workflow. Control-tested.
- Fail-closed paths raise `SystemExit("message")` → exit 1, indistinguishable
  from drift. Those are human decisions like UNMATCHED, so they map to
  `EXIT_UNSAFE`. The crash guard alone only covered exceptions.
- Added a `concurrency` group (queue, not cancel — a cancelled run could leave a
  pushed branch with no PR).
- `diff` exit 2 means *trouble*, not differences; only exit 1 is drift now.

## Verification

- 79 tests pass locally and on GitHub runners (count confirmed in the CI log).
- Dry-run under `bash -e`: clean → no PR; drift → PR opened with the
  already-current repo skipped; open PR → refreshed, no duplicate; merged PR →
  new one opened; canary → job fails, `code=2`, nothing proposed.
- Published `PyAutoMind-template` `d4c8104`; Memory already current.
- `--check` against freshly cloned published repos: **exit 0**.
- The published template now carries exactly one workflow
  (`lifecycle_drift.yml`) and no configured secrets.

## Genuinely pending — merging did not settle either

1. ~~Whether `PAT_PYAUTOLABS` grants write to the template repos.~~ **SETTLED
   the same day, by testing rather than waiting.** Two corrections to what this
   record first claimed:

   * It was described as unknowable without a real run. It was not — the secret
     inventory is readable via the API, and the check showed `PAT_PYAUTOLABS`
     was **absent from PyAutoMind entirely** (it is a repo-level secret on
     PyAutoBrain and PyAutoHands; repo secrets do not cross repos). Monday's run
     would have hit the guard and failed. "Only a real run tells us" was a
     failure to look, not a genuine limit.
   * Once a fine-grained PAT was added (2026-08-04 20:58Z), the whole path was
     exercised end to end rather than left for the schedule: a trivial drift
     marker was pushed to `PyAutoMind-template`, `workflow_dispatch` fired, and
     **24 seconds later the self-heal opened PR #1** proposing exactly the right
     diff (remove the marker, refresh `SPAWNED_FROM`) — with `PyAutoMemory-template`
     correctly skipped as already current. Merged as `7f8576f`; `--check` back to
     exit 0, branch auto-deleted.

   Residual risk: the fine-grained token expires. When it does, the Monday run
   fails at the clone or `gh pr create` with the message naming the repo —
   visible, not silent, but worth a calendar note.
2. **The scheduled leg has still never passed on its own.** Monday 06:17 UTC is
   its first honest test — and the first chance to see whether the self-heal
   opens a PR rather than just going red.

## The arc this closes

Nine issues/PRs from one question — "why does this only pass when a human pushes
the button":

| | |
|---|---|
| #118/#119 | the `EMPTY` leak — live registry entries public for 8 days |
| #120 | the self-heal drift loop that *publishing the fix* created |
| #121/#122 | `.github` shipping 13 failing workflows into fresh orgs |
| #123/#124 | the last live-byte parse — could have leaked 231 task records |
| #125/#126 | the missing generator (this) |

Every significant defect was caught by a check that disagreed with local
verification: an independent review found the first fix republished the leak
through KEEP-copied fixtures; a dispatched workflow failed where a local
`--check` passed; a tripwire test rejected a `.github` design before it shipped;
and executing the workflow shell exposed a latent crash from an earlier PR in
the same arc. A green local suite proved very little here.

## Original prompt

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
