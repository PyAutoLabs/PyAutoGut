# PyAutoGut — Agent Guidance

This file is for AI coding agents (Claude Code, Codex, Cursor, etc.) and humans
discovering this repository. PyAutoGut is the **Gut** organ of the PyAuto
organism — it owns the lifecycle of *condemned self-material*.

<!-- repos_sync:map:begin -->
**You are one organ of the PyAuto organism** — an agentic ecosystem for
human-led, natural-language software development. The organs below are
peer repositories; this repo is one of them, not a part of another.
Canonical boundaries live in `PyAutoBrain/ORGANISM.md`; the full body map
(every repo, not just organs) is `PyAutoMind/repos.yaml`.

| Organ | Repo | Role |
|-------|------|------|
| **Brain** | PyAutoBrain | Reasoning/orchestration layer; how work is decomposed and routed; the specialist agents. |
| **Mind** | PyAutoMind | Intent, goals, priorities, workflow state; every task starts as a markdown prompt here. |
| **Cortex** | PyAutoCortex | The Cortex — where the organism keeps track of what is true: the science body map (`projects.yaml`) and one ledger per science project (what was run, what came back, what was learned, where to pick up); the science mirror of the Mind (runs and a dated log, not prompts and PRs). |
| **Memory** | PyAutoMemory | Long-term scientific/software/project knowledge (see science pointer below). |
| **Eyes** | PyAutoEyes | The Eyes — where the organism sees what its figures look like: the cross-project visualization dashboard over the `<lib>_visualization` project repos (autolens_visualization, autogalaxy_visualization, autofit_visualization and autocti_visualization) — the registry of those repos, the tracked-manifest read contract (`gallery/viz_manifest.yaml`) and the Pages board that links to their PNGs as the single point of contact for the visual behaviour of the whole ecosystem. Renders nothing and copies no figures (the project repos render and hold them); never judges them (the Brain's Eyes conductor does) and never edits library plot code (critiques route through intake). |
| **Ears** | PyAutoEars | The Ears — the community listening organ: owns read-only public conversation collection, the versioned community snapshot contract, coverage receipts and the dashboard. GitHub conversations remain authoritative; Brain’s Community conductor owns judgement, reply drafts and development routing, and Mind owns task state. Never posts replies, labels or issues, exports raw transcripts or private sources, or treats unknown coverage as no work. |
| **Heart** | PyAutoHeart | Health/readiness — the authoritative "is it safe to release?" verdict. |
| **Hands** | PyAutoHands | Packaging, tagging, notebook generation, PyPI release execution. |
| **Pulse** | PyAutoPulse | The Pulse — where the organism feels how fast it runs: the cross-project profiling dashboard over the `<lib>_profiling` project repos (today autolens_profiling) — campaign intent and pending domain tasks, the instance registry, the versioned `profiling-summary` read contract (v1 live at `autolens_profiling/dashboard/summary.json`), the ingest receipts (resolved commit per project per render) and the Pages board. Validates the exchange contract only; never moves pins, combines unmatched timings, applies the compile threshold to runtime, computes an ecosystem-wide speed score or issues a Heart verdict, and never judges (the Brain's profiling conductor does); the project repos keep their producers, results, drift policy and their own Pages page. |
| **Insight** | PyAutoInsight | Owns inference campaign intent and pending domain tasks, the cross-project inference instance registry, versioned `inference-summary` read contract, ingest receipts and evidence dashboard. Projects own execution, producers and raw samples; Cortex owns scientific run records, observations and human conclusions; Mind owns bounded implementation lifecycle and repository claims. Never infers scientific acceptance from execution, ranks incompatible runs or submits compute on refresh. |
| **Nerves** | PyAutoNerves | The Nerves — the configuration/serialization layer connecting workspace conventions to libraries (layered config, version handshake, test_mode), delivered as the `autonerves` package. |
| **Gut** | PyAutoGut | Owns the lifecycle of condemned self-material (stale branches, stashes, dead code/tests): holds it as durable, recoverable git refs through a transit window and voids it on a sweep. The storage mirror of Memory (retention vs release). |

Call chain (always this order): **Brain → Heart (gate) → Build (execute)**. Brain agents are **conductors** (front-door; a human drives them; they decide *and* act) or **faculties** (read-only opinions the conductors consult; they judge and stop). New capability grows as a faculty, not a new organ, unless it owns state or effects no existing organ can.

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
- **The reach covers sibling repos (PyAutoGut#11), through the org PAT.** An
  entry whose `archive-ref` says `… on <Repo> origin` is voided on that repo:
  `--void-plan` carries `{name, repo, sha}` per entry, and void.yml deletes
  a sibling ref with `secrets.PAT_PYAUTOLABS` (the Gut's own token cannot
  reach another repo). The PAT is sent as an `http.extraheader` via
  `GIT_CONFIG_*` env from an empty scratch repo — never in a URL, argv or log
  — and masked with `::add-mask::`. No PAT → "skipped: no PAT"; a 403 (the
  PAT403 precedent: a newborn repo missing from the PAT's repository list) →
  a per-ref failure row naming the repo. Either way the ref stays and the
  issue stays open; it closes as completed only when every requested ref was
  voided or absent.
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
