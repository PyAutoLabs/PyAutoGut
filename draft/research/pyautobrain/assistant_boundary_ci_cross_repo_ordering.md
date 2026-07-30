# Assistant boundary CI: stop predictable-red on cross-repo Brain dependencies

Type: research
Target: pyautobrain
Repos:
- PyAutoBrain
- autolens_assistant
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

## Problem

`autolens_assistant/.github/workflows/clone-boundary.yml` (and the wiki-currency
workflow family) check out `PyAutoBrain@main` to run Brain's boundary/classifier
code. When an assistant PR depends on a not-yet-merged Brain change, the assistant
PR is predictably red until the Brain side merges and the workflow is rerun — an
expected-red state that trains people to ignore CI. The wiki-currency
`--check-citations` leg is likewise a hard cross-repo merge-order gate (see memory
`reference_docs_ci_gotchas_workspace_assistant`).

## Scope (decision note first, then a small implementation)

Weigh, and pick one:

1. **Declared-dependency escape hatch**: the assistant PR body/branch declares an
   upstream Brain ref (`Brain-ref: <branch|sha>`); the workflow checks out that
   ref when declared, `main` otherwise. Keeps the gate hard while making the
   paired-PR flow green-able before merge.
2. **Pinned checker**: the assistant repo pins the Brain checker to a recorded sha
   bumped deliberately (renovate-style). Predictable, but adds pin-bump churn and
   lets the boundary drift between bumps.
3. **Advisory mode**: keep the check on `main` but mark it `continue-on-error`
   when a dependency is declared. Simplest, weakest.

Recommendation to evaluate first: option 1 — it matches how the paired PRs are
actually developed and needs no standing pins. Implementation lands in the shared
workflow (assistants) + a note in the Clone Agent docs so future cells inherit it.
