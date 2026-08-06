## rename-pyautobuild-to-pyautohands (repo rename — Build organ becomes Hands)

- completed: 2026-07-19/20 (repo rename landed in the libraries; local dirs,
  remotes, PYTHONPATH and skill symlinks repointed)
- summary: renamed the repository **PyAutoBuild → PyAutoHands** (the organism's
  execution organ), alongside the sibling PyAutoConf → PyAutoNerves rename. The
  overnight cascade it triggered (Heart release/verify-install harness still
  pip-installing `autoconf`, org front-door drift, workspace bootstraps) was
  fixed 2026-07-20 via /wake_up — see project memory
  `project_autoconf_autonerves_rename_cascade` for the harness/HPC/science-
  project legs. The **package/CLI seam** (`autobuild` → `autohands`, 18 PRs
  across 18 repos) closed separately on 2026-07-23 — see
  [[rename-autobuild-to-autohands]].

## Lifecycle note

Record backfilled 2026-08-06: the rename shipped without a completion record
and its prompt never left `draft/refactor/pyautobuild/`; retired here dated by
the repo-rename landing. (The stale `PyAutoConf` repo reference in the
prompt's repo list predates the Nerves rename.)

## Original prompt

# Rename the repository PyAutoBuild to PyAutoHands

Type: refactor
Target: PyAutoBuild
Repos:
- PyAutoBuild
- PyAutoBrain
- PyAutoHeart
- PyAutoMind
- PyAutoMemory
- PyAutoConf
Difficulty: too-large
Autonomy: supervised
Priority: normal
Status: formalised

Rename the repository @PyAutoBuild to **PyAutoHands** while preserving all
functionality.

## Context

The PyAuto ecosystem is evolving into a coherent software organism:

- **PyAutoMind** — intent, prompts and workflow state.
- **PyAutoBrain** — reasoning through specialist agents.
- **PyAutoMemory** — long-term scientific and architectural memory.
- **PyAutoHeart** — health, validation and readiness.
- **PyAutoHands** — execution.
- **PyAutoGut** — quarantine and deletion.
- **PyAutoNerves** (PyAutoConf) — configuration and signalling.

The purpose of this rename is to make the architecture feel like a living
organism instead of a collection of engineering tools. PyAutoHands represents
execution: the Brain decides, the Hands do.

## Goal

Rename the repository while preserving all functionality. This includes:

- package names (where appropriate),
- documentation,
- README,
- GitHub branding,
- badges,
- references from other organism repositories,
- install instructions,
- examples,
- CI,
- release workflows,
- Claude skills,
- command aliases.

## Repository philosophy

PyAutoHands is responsible for **execution only**: running development
workflows, creating branches, building, testing, creating releases, opening
PRs, publishing packages. It does not perform planning or architectural
reasoning (PyAutoBrain), health validation (PyAutoHeart), intent (PyAutoMind),
or knowledge (PyAutoMemory).

## Documentation

Rewrite documentation so that it consistently refers to:

> PyAutoHands executes work on behalf of PyAutoBrain.

Update examples accordingly.

## Migration

Where possible:

- preserve backwards compatibility,
- provide redirects,
- avoid breaking downstream repositories,
- document migration from PyAutoBuild.

## Validation

Ensure:

- no stale references remain,
- no CI breaks,
- README examples still work,
- links resolve correctly.

## Deliverable

A PR titled **"Rename PyAutoBuild to PyAutoHands"**, including a concise
migration guide.

## Intake notes

- Sized **too-large** by the sizing faculty (score 13): expect start_dev to
  phase this into multiple PRs (e.g. in-repo rename/branding → cross-repo
  reference sweep incl. generated surfaces from `repos.yaml`/`ORGANISM.md` →
  GitHub-side rename + redirects + migration guide).
- Cross-cutting: the organ tables in every repo's AGENTS.md are generated from
  `PyAutoMind/repos.yaml` + `PyAutoBrain/ORGANISM.md` via
  `scripts/repos_sync.py --write` — the rename must flow through that source,
  not hand-edits. CI in the workspaces/HowTo repos checks out PyAutoBuild by
  name and `smoke_tests.yml`/`navigator_check.yml` reference it; the Heart and
  Brain resolve the `autobuild` binary by name.
- Architectural / API risk keywords present — review scope at start_dev before
  any build.

<!-- formalised by the Intake (Conception) Agent on 2026-07-18 from user-intake;
     work-type corrected docs→refactor and target pyautobrain→pyautobuild in review -->
