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
