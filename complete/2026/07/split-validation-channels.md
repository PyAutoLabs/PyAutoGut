Split Heart's workspace validation into one workflow file per meaning, so a
failed nightly release rehearsal can never overwrite the continuous smoke
verdict again.

- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/121 (auto-closed)
- prs: PyAutoHeart#122 (`969b4c89a`) then PyAutoBrain#183 (`780862b94`) —
  merged back-to-back (ordered: between them the nightly would have dispatched
  a workflow with no dispatch trigger); both merged unchanged (tree diff 0).
- shape: `workspace-validation.yml` → workflow_call-only shared body (jobs
  unchanged, filename kept so test_verify_install_script.py and the Build
  capability docs stay true); `workspace-smoke.yml` = Monday-03:00 schedule +
  bare dispatch → mode=smoke (the run history `test_run.py` reads —
  `VALIDATION_WORKFLOW` repointed); `release-integrate.yml` = dispatch/call
  with testpypi_version+commit_shas → mode=release, deliberately NO mode input
  (the channel IS the mode). Runs attribute to the CALLER workflow, which is
  what makes `gh run list --workflow <entry>` unambiguous.
- Brain side: validate.sh `INTEGRATE_WORKFLOW=release-integrate.yml`, emitted
  Stage 3 inputs drop `mode` (the new entry rejects unknown inputs);
  overnight_status glances workspace-smoke.yml.
- guard: tests/test_workflow_wiring.py parses the three files (body call-only,
  smoke owns the schedule, release entry mode-free, VALIDATION_WORKFLOW names
  an existing entry). Heart suite 320 passed.
- steady state: smoke verdict refreshes on Monday's schedule or a manual
  `workspace-smoke.yml` dispatch; the nightly exercises release-integrate.yml.
- residue (docs-only): PyAutoHands nightly_release_design.md / internals.md
  mentions + one release.yml comment still say workspace-validation.yml.

## Original prompt

# Split the workspace-validation signal: continuous smoke vs release rehearsal

Type: refactor
Target: pyautoheart (with a small PyAutoBrain follow-up)
Repos:
- PyAutoHeart
- PyAutoBrain
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft

## Problem

`PyAutoHeart/.github/workflows/workspace-validation.yml` serves two meanings —
weekly/dispatch `mode=smoke` (continuous readiness signal) and nightly-dispatched
`mode=release` (Stage 3 release-fidelity integration). Heart's
`test_run.py::_cloud_verdict()` reads the **latest run of the workflow file
regardless of mode**, so every failed nightly rehearsal overwrites the continuous
smoke verdict (and vice versa). `gh run list` cannot filter on dispatch inputs, so
mode cannot be recovered cheaply from the run record.

## Scope

1. PyAutoHeart PR: split into two thin entry workflows — `workspace-smoke.yml`
   (schedule + dispatch) and `release-integrate.yml` (workflow_call + dispatch) —
   both calling one shared reusable body (the current job set, parameterised by
   mode; the file already routes everything off a resolved `mode` output, so this
   is mostly mechanical). Point `test_run.py`'s `VALIDATION_WORKFLOW` at
   `workspace-smoke.yml` only. Keep the old filename briefly as a deprecation shim
   or land the Brain PR in the same window (see merge order).
2. PyAutoBrain PR (after 1): `agents/conductors/release/validate.sh` /
   `nightly.sh` dispatch plans reference the new `release-integrate.yml`.
3. Merge order matters (cross-repo): Heart first, Brain immediately after; the
   nightly between the two merges would dispatch a missing workflow — schedule the
   two merges together or keep a temporary alias workflow.

## Outcome

One workflow run per meaning; `test_run` (continuous) and `validation_report`
(rehearsal) each attributable to exactly one authoritative run.
