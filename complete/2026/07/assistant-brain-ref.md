Assistant boundary CI: paired PRs can declare their Brain dependency.

- issue: PyAutoBrain#186 (auto-closed) · prs: autolens_assistant#102 (`74e25a227`),
  autocti_assistant#18 (`44d0e0b43`), PyAutoBrain#187 docs (`d63600f7a`) — merged unchanged
- decision (of declared-ref / pinned-sha / advisory): DECLARED-DEPENDENCY — matches how
  paired PRs are developed, no standing pins. `Brain-ref: <branch-or-sha>` on its own
  line in the PR body → clone-boundary checks out PyAutoLabs/PyAutoBrain at that ref;
  absent/push → main (gate stays hard). Ref charset excludes shell metacharacters and
  only ever reaches actions/checkout (pinned to the Brain repo); hygiene, not a
  security boundary. Extraction tested over CRLF/missing/sha/injection cases. Future
  cells inherit via the reference clone-boundary.yml + the clone conductor AGENTS note.

## Original prompt

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
