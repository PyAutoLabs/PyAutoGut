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
| **Mind** | PyAutoMind | Intent, goals, priorities, workflow state; every task starts as a markdown prompt here. |
| **Brain** | PyAutoBrain | Reasoning/orchestration layer; how work is decomposed and routed; the specialist agents. |
| **Hands** | PyAutoBuild | Packaging, tagging, notebook generation, PyPI release execution. |
| **Heart** | PyAutoHeart | Health/readiness — the authoritative "is it safe to release?" verdict. |
| **Memory** | PyAutoMemory | Long-term scientific/software/project knowledge (see science pointer below). |
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
  archive namespace `refs/archive/condemned/<name>` — which stays out of
  `git branch -a` — into this repo (the attic remote) *before* the local copy is
  deleted. Recovery is a checkout. A stash becomes a branch/commit via
  `git stash branch` or a tagged stash commit.
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
`PyAutoMind/research/pyautobrain/pyautogut_organ_decision.md`.

<!-- repos_sync:history:begin -->
## Never rewrite history

NEVER perform these operations on any repo with a remote:

- `git init` in a directory already tracked by git
- `rm -rf .git && git init`
- Commit with subject "Initial commit", "Fresh start", "Start fresh", "Reset
  for AI workflow", or any equivalent message on a branch with a remote
- `git push --force` to `main` (or any branch tracked as `origin/HEAD`)
- `git filter-repo` / `git filter-branch` on shared branches
- `git rebase -i` rewriting commits already pushed to a shared branch

If the working tree needs a clean state, the **only** correct sequence is:

    git fetch origin
    git reset --hard origin/main
    git clean -fd

This applies equally to humans, local Claude Code, cloud Claude agents, Codex,
and any other agent. The "Initial commit — fresh start for AI workflow" pattern
that appeared independently on origin and local for three workspace repos is
exactly what this rule prevents — it costs ~40 commits of redundant local work
every time it happens.
<!-- repos_sync:history:end -->
