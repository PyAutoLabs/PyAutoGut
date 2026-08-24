- completed: 2026-08-24
- issue: https://github.com/PyAutoLabs/autocti_workspace/issues/29
- prs:
  - https://github.com/PyAutoLabs/autocti_workspace/pull/30 (merged)
- summary: |
    CTI CI standardisation Phase 6, task 1 of 3 (HIGH). autocti_workspace was
    listed in PyAutoHeart's `workspaces` group, whose required workflows are
    ["Smoke Tests", "Navigator Check"], but carried only the former — and a
    required workflow with no runs never satisfies `all_green`, so the repo
    rolled up as permanently `in_progress`: able to go red, never able to go
    green. Added the missing workflow AND the catalogue it gates on.

## The prompt's premise was wrong, and it was load-bearing

The prompt said the repo "has root-level catalogue files the assistant's
citation checks already lean on (`llms.txt`, `llms-full.txt`,
`workspace_index.json`)". **It has none of the three** — `git ls-files` finds
nothing. The line it was reading, in `autocti_assistant/.github/workflows/
wiki-currency.yml`, is a comment explaining git's *cone-mode* behaviour
("root-level files … are always included automatically"), not an assertion that
those files exist.

This is the second consecutive CTI task whose prompt asserted a file that was
never there (Phase 5: "add them back to the workspace `smoke_tests.txt`" — there
was no `smoke_tests.txt`). Worth noticing as a pattern in how these prompts get
written, not just as two separate corrections.

Why it mattered rather than being a detail: the staleness job ends in

```
git diff --exit-code llms-full.txt workspace_index.json
```

and on **untracked** paths `git diff` exits **0**. Verified directly. So adding
the workflow alone would have produced a permanently green job that checked
nothing — the same class of vacuous gate the task set out to close.

## What Navigator Check actually is

Not a Heart reusable. `PyAutoHeart/.github/workflows/` has no
`navigator_check.yml`; the name appears only in `config/repos.yaml` and
`heart/checks/ci_status.py`. Each workspace owns a ~30-line thin caller of
`PyAutoLabs/PyAutoHands/.github/workflows/navigator_check.yml@main` whose only
input is `project:`. Confirmed identical in shape across `autofit_workspace`
(`autofit`), `autogalaxy_workspace` (`autogalaxy`), `autolens_workspace`
(`autolens`) and `HowToLens` (`howtolens`).

The reusable workflow runs three jobs: a path/banner lint
(`check_navigator.py`), an unbatched multi-start search guard
(`check_search_memory.py`), and a staleness job that regenerates the catalogue
and diffs it. `autocti` was already registered in `autohands/navigator.py`'s
`WORKSPACE_TITLES`, so no PyAutoHands change was needed.

## The 12 docstring underlines

Twelve scripts — both `extract.py`s, four `data_preparation/examples/`, and the
whole six-part `overview/` series — opened with a `-----` title underline rather
than `=====`. `navigator._parse_header` only treats a line as a title underline
when `set(underline) == {"="}`, so for all twelve the dashes became the *summary*,
and the generated catalogue read `[Extract](scripts/dataset_1d/extract.py): -------`.

Fixed here rather than committing a knowingly-broken artifact: one line per file,
docstring-only. Called out explicitly in the PR body as a deliberate widening of
a CI PR into `scripts/`, with an offer to split it out.

**Trap, caught before pushing:** six of the twelve files are CRLF. The first pass
read them with `open(p).read()` (universal newlines) and wrote back LF, producing
a 1,558-line diff across six files instead of six one-line changes. Redone in
binary mode preserving each line's own terminator; `git diff --stat` then showed
exactly `12 files changed, 12 insertions(+), 12 deletions(-)`.

## Verified

All three reusable jobs run locally against the branch before pushing, then green
in CI:

| job | local | CI |
|---|---|---|
| `check_navigator.py --banners=fail` | OK | ✅ Navigator paths + banner lint |
| `check_search_memory.py` | OK | ✅ Unbatched multi-start search check |
| `regenerate_navigator.py autocti` + `git diff --exit-code` | OK, byte-identical across two runs | ✅ Catalogue staleness |

Plus `smoke (3.12)` and `smoke (3.13)` green — six checks, no reruns. All 12
edited scripts byte-compile; none is in `smoke_tests.txt`.

## The acceptance criterion, confirmed against the real function

The prompt was explicit that the criterion is the roll-up flipping, not "the
workflow passes". Both required workflows completed green on `main` HEAD
(`4b162ae`, the PR #30 merge), and feeding that through `heart/checks/
ci_status.py`'s real `rollup()` gives:

```
required for `workspaces`: ['Smoke Tests', 'Navigator Check']

BEFORE (Navigator Check had never run) -> {'conclusion': '',        'status': 'in_progress'}
AFTER  (both green on 4b162ae)         -> {'conclusion': 'success', 'status': 'completed'}
```

All three per-workflow conditions `rollup` applies — `conclusion == "success"`,
`status == "completed"`, `on_head` — are satisfied. The repo can be seen as
CI-clean by the readiness gate for the first time.

## Work item 4 — the general case, surveyed not guessed

The prompt asked whether other repos have the same silent-never-green defect.
Surveyed all 15 repos across the four groups carrying `required_workflows`:

| group | required | missing a file |
|---|---|---|
| `libraries` (6) | `Tests` | none |
| `workspaces` (4) | `Smoke Tests`, `Navigator Check` | **autocti_workspace** |
| `workspaces_test` (4) | `Smoke Tests` | none |
| `howto` (3) | `Smoke Tests`, `Navigator Check` | none |

Exactly one instance, now closed. The proposal for a Heart-side drift check was
posted on the issue rather than implemented, per the prompt's instruction not to
widen: the failure mode is silent by construction (a missing gate reads as
*pending*, indistinguishable from *a run is in flight*), and it reopens on every
edit to `repos.yaml` that adds a repo to a group or a workflow to a group's
requirements. Suggested shape: a deep-tier (not per-tick) check matching each
group's required names against the parsed `name:` field of each repo's workflow
files, reported as a *configuration* finding rather than red CI.

## Follow-ups deliberately not taken

- **A hand-curated `llms.txt`.** Every sibling carries one — a hand-maintained
  routing layer the generator never writes and `check_navigator.py` skips when
  missing. Doc-authoring, not CI.
- **13 scripts catalogue as `(no summary in script docstring)`** — they have a
  title but no prose paragraph. A documentation gap; nothing gates on it.
- **Notebook regeneration is blocked for this workspace entirely.**
  `autohands/generate.py` exits on any project absent from
  `build_util.COLAB_PROJECTS`, and `autocti` is not there (nor in PyAutoNerves'
  `setup_colab.py` `_PROJECTS`). So `generate.py autocti` cannot run at all —
  discovered while documenting the regeneration command, and recorded in
  `AGENTS.md` so the next person does not try. `regenerate_navigator.py` is
  unaffected; it never touches that registry. Worth its own task.

## Heart gate

`pyauto-brain vitals` → **STALE**, score 65. Every reason was the same
organism-scope evidence gap — `gh: command not found` in this cloud session, so
`ci_status` could not be queried for any repo. Nothing known-bad. STALE passes
the dev-ship gate by design (PyAutoHeart `AGENTS.md`; `AUTONOMY.md` leg 4)
because the gap is organism-scope rather than branch-scope; branch-scope
evidence was the local job table above.

## Original prompt

# autocti_workspace has no Navigator Check, so its CI can never roll up green

Type: maintenance
Target: autocti_workspace
Repos:
- @autocti_workspace
- @PyAutoHeart
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

`PyAutoHeart/config/repos.yaml` lists `autocti_workspace` in the `workspaces`
group, whose required workflows are:

```yaml
required_workflows:
  workspaces: ["Smoke Tests", "Navigator Check"]   # smoke_tests.yml + navigator_check.yml
```

`Smoke Tests` now exists (autocti_workspace#27/#28, 2026-08-24 — the repo's first
CI). **`Navigator Check` does not.** That is not cosmetic.

## Why this blocks readiness, not just tidiness

`heart/checks/ci_status.py` rolls a repo up over its *required* workflows. A
required workflow with **no runs at all** is not scored as a failure — it simply
never satisfies `all_green`. Verified directly against the real function:

```
required for `workspaces`: ['Smoke Tests', 'Navigator Check']

Smoke green, Navigator MISSING -> {'conclusion': '',        'status': 'in_progress'}
both green                     -> {'conclusion': 'success', 'status': 'completed'}
smoke red, Navigator MISSING   -> {'conclusion': 'failure', 'status': 'completed'}
```

So `autocti_workspace` rolls up as **permanently `in_progress`** — never green,
never red. It cannot reach `conclusion: success` no matter how healthy it is,
which means the readiness/release gate can never see this repo as CI-clean.
Adding Smoke Tests was necessary but not sufficient.

Note the asymmetry in that table: a *red* Smoke Tests still reports failure
correctly. So the repo can go red but can never go green — the worst shape for a
gate to be in.

## Work

1. **Find out what `Navigator Check` actually is.** It is not a Heart reusable
   workflow — `PyAutoHeart/.github/workflows/` has no `navigator_check.yml`; the
   name appears only in `config/repos.yaml` and `heart/checks/ci_status.py`.
   Each workspace owns its own `.github/workflows/navigator_check.yml`. Read a
   sibling that has one (`autolens_workspace`, `autogalaxy_workspace`,
   `autofit_workspace`, or a `HowTo*` repo) and mirror it. Do **not** invent a
   check from the name.
2. **Add it to `autocti_workspace`**, adapted to this repo's actual navigator
   surface. autocti_workspace has root-level catalogue files the assistant's
   citation checks already lean on (`llms.txt`, `llms-full.txt`,
   `workspace_index.json` are sparse-checked out by
   `autocti_assistant/.github/workflows/wiki-currency.yml`), so there is a real
   navigator surface here to validate.
3. **Confirm the roll-up flips to `success`** once both workflows are green on
   `main` HEAD — that is the actual acceptance criterion, not "the workflow
   passes".
4. **Consider the general case.** If other repos in a required group are missing
   a required workflow, they have the same silent-never-green defect. A Heart-side
   drift check ("every repo in a required group has a workflow file for each of
   its required workflows") would catch this class rather than this instance.
   Raise it as a proposal with findings; do not widen this task unilaterally.

## Why it was left out of the smoke task

autocti_workspace#28 was scoped to the ordered-trap smoke coverage (CTI epic
Phase 5). Adding a second, unrelated workflow would have widened that PR beyond
its task. Filed here instead, deliberately.

## Context

`PyAutoMind/complete/2026/08/phase5-smoke-ordered-trap-scripts.md` — how the
repo got its first CI, and the `arcticpy: true` caller convention it uses.
