# PyAutoGut — Agent Guidance

This file is for AI coding agents (Claude Code, Codex, Cursor, etc.) and humans
discovering this repository. PyAutoGut is the **Gut** organ of the PyAuto
organism — it owns the lifecycle of *condemned self-material*.

<!-- repos_sync:map:begin -->
**You are one peer organ of the PyAuto organism** (human-led, natural-language software development), not a part of another. Boundaries: `PyAutoBrain/ORGANISM.md`; every repo: `PyAutoMind/repos.yaml`.

| Organ | Repo | Role |
|-------|------|------|
| **Brain** | PyAutoBrain | Reasoning and orchestration: decomposes and routes work through its conductors and faculties. |
| **Broca** | PyAutoBroca | Assistant evaluation history, upkeep evidence and its dashboard. |
| **Mind** | PyAutoMind | Intent, priorities and workflow state; every task starts as a prompt here. |
| **Cortex** | PyAutoCortex | What is true in the science: the project body map and one ledger per project. |
| **Memory** | PyAutoMemory | Long-term scientific, software and project knowledge. |
| **Eyes** | PyAutoEyes | Cross-project figure dashboard over the `<lib>_visualization` repos. |
| **Ears** | PyAutoEars | Read-only community listening: conversation snapshots and coverage. |
| **Heart** | PyAutoHeart | Health/readiness — the authoritative release verdict. |
| **Hands** | PyAutoHands | Packaging, tagging, notebooks and PyPI release execution. |
| **Pulse** | PyAutoPulse | Cross-project profiling dashboard over the `<lib>_profiling` repos. |
| **Insight** | PyAutoInsight | Inference campaign intent, instance registry and evidence dashboard. |
| **DNA** | PyAutoDNA | Software-stack specifications, environment inventories and upgrade campaigns. |
| **Nerves** | PyAutoNerves | Configuration/serialization layer (`autonerves`): layered config, version handshake, test_mode. |
| **Gut** | PyAutoGut | Condemned branches, stashes and dead code, held as recoverable refs until swept. |

Call chain: **Brain → Heart (gate) → Build (execute)**. Conductors decide *and* act; faculties judge read-only and stop. New capability grows as a faculty, not an organ, unless it owns state or effects no organ can.

Generated from `PyAutoMind/repos.yaml` + `PyAutoBrain/ORGANISM.md`; edit there, then run `python3 PyAutoMind/scripts/repos_sync.py --write`.
<!-- repos_sync:map:end -->

## What this repo is

PyAutoGut is a **storage organ**, a peer to PyAutoMemory. Memory holds what the
organism *keeps* (durable knowledge); PyAutoGut holds what it *sheds* (durable
discard, recoverable until voided). **Retention vs release.**

Its material is the *self and spent*: stale branches, `git stash` entries, dead
code and retired tests — code that is not *wrong*, just *done*. A hygiene /
`repo_cleanup` sweep is 95%-but-not-100% sure each item is trash, so it needs a
home that is neither "keep" nor "delete now": a **staging state** with a clock.

The organ's defining property is **elimination** — PyAutoGut performs the final
deletion itself. (An organ that only filtered and handed waste downstream would
be the spleen; the one that *voids* is the gut.)

## Lifecycle: condemn → transit → void

1. **Condemn** — the Brain hygiene conductor's `tidy` pass files an entry into
   the `condemned.md` manifest in PyAutoMind (async, no synchronous per-item
   gate). Fragile forms are archived to a durable ref here *first*.
2. **Transit** — the entry carries a `sweep-after` date. Until then it is
   **recoverable** (reabsorption): restore the branch/stash from its archive
   ref. The holding window *is* the gut's transit time, with a clock on it.
3. **Void** — a batch `sweep` runs the existing `repo_cleanup` safety gates
   against entries past `sweep-after` and eliminates them.

## Storage model

- **Payload = durable git refs, never markdown.** Fragile forms (local unmerged
  branches, stashes) are materialised as real commits and pushed under the
  archive namespace `refs/heads/archive/condemned/<name>` into this repo (the
  attic remote) *before* the local copy is deleted. Recovery is a checkout. A
  stash becomes a branch/commit via `git stash branch` or a tagged stash commit.
  (The archive is a **branch prefix**, not a custom `refs/archive/*` namespace:
  GitHub only accepts pushes to `refs/heads/*` and `refs/tags/*`, so a custom
  namespace is unpushable. The refs stay tidy under the `archive/condemned/`
  prefix — filter them out of normal views with
  `git branch --list 'archive/condemned/*'` — rather than being fully hidden
  from `git branch -a`.)
- **Catalog = `condemned.md` in PyAutoMind** (symmetric to `parked.md`). The
  `.md` is the index; the refs here are the payload. Schema and lifecycle are
  documented there.
- **Merged branches skip the pen** — reachable from `main` forever; the
  conductor recommends them straight to deletion without staging.
- **Committed code / test deletions** — the old bytes live in remote history;
  only the pre-delete SHA is recorded.

The `bin/pyauto-gut` entrypoint provides the mechanics: `archive`, `recover`,
`list`, `void`.

## Boundaries

- **vs Immune (`bug`)** — Immune fights the *foreign and pathological* (bugs,
  regressions, failing tests: code that is *wrong*). PyAutoGut processes the
  *self and spent* (code that is not wrong, just done). No overlap.
- **vs the hygiene conductor** — mirror the **Heart ↔ vitals** template: Heart is
  the organ that health-checks, the vitals faculty only *reads* it. Likewise
  PyAutoGut is the organ that *holds and voids*; the hygiene conductor *drives*
  it (decides what to condemn, triggers a sweep) and owns none of the storage.
- **vs Memory** — the two storage organs are mirrors: Memory keeps, Gut sheds.
- **vs Heart / profiling** — PyAutoGut issues no health verdict and measures no
  compute speed; it is upkeep storage, not observation.

New capability grows as a Brain faculty, not a new organ, unless it owns state or
effects no existing organ can. PyAutoGut earned a repo by owning a persistent,
recoverable store of git objects held through a transit window — a persistent
reusable-artifact lifecycle. See
`PyAutoMind/complete/2026/07/pyautogut-organ.md`.

## The board and the void workflow (PyAutoGut#9)

The Gut publishes a board (`scripts/board.py` → `gut_board.yml` → Pages +
`state.json`), and voiding is a button: a prefilled `void: <name>` (or
`void: all-due`) issue that `.github/workflows/void.yml` acts on. Rules:

- **The issue is the human yes.** Submitting a `void:` issue is the explicit
  consent `pyauto-gut void --yes` asks for; an agent never opens one on its
  own initiative.
- **Truth is two sources.** The board and the workflow both reconcile
  `git ls-remote` against the Mind's `condemned.md` (parsed by the Brain's
  `_hygiene_condemned.py`); void names come from each entry's `archive-ref`,
  never its `##` heading.
- **Never bulk-void undated entries.** Held (`sweep-after: never`) refs — in
  the Gut or on a sibling repo — are refused by the workflow and left out of
  `all-due`; orphans (no ledger entry) are single-void only, never in
  `all-due`.
- **The reach covers sibling repos (PyAutoGut#11), through the org App.** An
  entry whose `archive-ref` says `… on <Repo> origin` is voided on that repo:
  `--void-plan` carries `{name, repo, sha}` per entry, and void.yml deletes
  a sibling ref with a one-hour `pyautolabs-bot` App token (owner-wide,
  contents write; the Gut's own token cannot reach another repo), handed to
  git by `gh auth setup-git` from an empty scratch repo — never in a URL. A
  mint failure fails the run; a 403 from a sibling → a per-ref failure row
  naming the repo, the ref stays and the issue stays open; it closes as
  completed only when every requested ref was voided or absent. The
  dispatch-only `dry_run` probe `push --dry-run --delete`s every due sibling
  ref to prove the credential and changes nothing.
- **Ledger retirement is a session act.** Neither token edits the Mind; a
  voided ref's entry is retired from `condemned.md` by a session (the board's
  "retire entry" payload).
- **Never red.** The feed is grey when nothing could be listed, yellow when
  anything is due / orphaned / dangling, green otherwise.

<!-- repos_sync:history:begin -->
## Never rewrite history

Never rewrite pushed history on any repo with a remote — no `git init` over a
tracked repo, no force-push to `main`, no fresh-start "Initial commit", no
`filter-repo` / `filter-branch` / `rebase -i` on pushed branches. To get a
clean tree: `git fetch origin && git reset --hard origin/main && git clean -fd`.
<!-- repos_sync:history:end -->

<!-- repos_sync:deliverable:begin -->
## Sessions end at their deliverable

A session ends when it reports its deliverable — never arm anything that
outlives the turn to wait for CI, a review or a merge: no `send_later`, no
`subscribe_pr_activity`, no `CronCreate`, no `ScheduleWakeup`, no `/loop`, no
`RemoteTrigger` create/update/run. Judge once, report, stop; the human re-runs
`/prm` (or the batch review) when it is green. Measured: five batch members
armed hourly check-ins on 2026-08-31, and a mobile `/prm` re-armed a 60-minute
`send_later` hourly all night on 2026-09-03 with no task active, draining usage.
<!-- repos_sync:deliverable:end -->

<!-- repos_sync:filing:begin -->
## Where to file

Questions, help with code or an analysis, ideas, bug reports and results from a
user or collaborator — or an agent acting for one — go to
<https://github.com/orgs/PyAutoLabs/discussions> in the matching category
(Help & Questions, Ideas & Proposals, Bugs & Errors, Show and tell;
Announcements is maintainers-only), never to this repo's Issues. An agent never
runs `gh issue create` for such a report: it drafts the title, category and
body and hands them to the human (sessions cannot create Discussions). Only the
development flow — Mind prompt → `/start_dev` → `/create_issue` → one issue per
task → PR — opens issues here. Why: `PyAutoMind/policy/community_surface.md`.
<!-- repos_sync:filing:end -->

<!-- repos_sync:standards:begin -->
## Shared standards

Before changing a shared interface, consult the applicable
[organism standard](https://github.com/PyAutoLabs/PyAutoBrain/blob/main/docs/standards.md)
on demand, identify affected consumers, and validate their adoption. Change
generated guidance at its canonical source and regenerate.

For board changes, follow the applicable sizing, navigation and orchestration
standards and reuse Brain’s shared components. Keep domain data, prompt meaning
and approval boundaries with the board’s owner.
<!-- repos_sync:standards:end -->
