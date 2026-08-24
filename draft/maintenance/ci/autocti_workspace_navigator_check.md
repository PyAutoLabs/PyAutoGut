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
