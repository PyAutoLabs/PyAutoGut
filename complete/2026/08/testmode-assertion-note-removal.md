## testmode-assertion-note-removal
- issue: https://github.com/PyAutoLabs/autocti_workspace/issues/24 (closed)
- completed: 2026-08-24
- workspace-pr: https://github.com/PyAutoLabs/autocti_workspace/pull/25 (merged 2933cddd)
- workspace-pr: https://github.com/PyAutoLabs/autocti_workspace_test/pull/17 (merged bfdb876b)
- workspace-pr: https://github.com/PyAutoLabs/autocti_assistant/pull/21 (merged 6a0f645c)
- summary: Follow-up to test-mode-bypass-assertion-ties (PyAutoFit#1520, merged
  438f56fac). Three CTI repos documented the now-fixed TEST_MODE bypass crash as a
  live artifact readers must work around. Deleted per the testmode-env-drift
  precedent ("delete the trap, don't document it") rather than updated. All three
  branches proven ancestors of their main (0 unmerged commits each).
- key-finding: the prompt said "if a sibling note exists" — BOTH siblings existed,
  and the second was not a note. In autocti_workspace_test/AGENTS.md the claim was
  a parenthetical RATIONALE for a convention ("integration scripts are ...
  single-trap (because ordered traps tie under the bypass)"). Deleting the whole
  bullet would have quietly repealed a test-design rule. Removed only the
  rationale; left the convention standing and flagged it for a maintainer.
- open-question: autocti_workspace_test's single-trap convention now has no stated
  reason. If it existed only to dodge the bypass crash it can be dropped, and
  multi-trap ordered models exercised — arguably better coverage, since ordered
  traps are the realistic CTI case. If it also exists for runtime/simplicity the
  bullet needs that reason written in. Deliberately not guessed.
- key-finding: the third site was in a SKILL (autocti_assistant
  skills/ac_fit_cti_model.md), i.e. what the assistant tells users — a stale
  "known artifact" there is active advice to work around a bug that no longer
  exists. Worse than a stale AGENTS.md note. Its .claude/skills/ copy is a
  SYMLINK (git mode 120000), so one edit covered both discovery surfaces; do not
  assume the mirrored skills dirs are copies.
- deliberately-untouched: the add_assertion example at ac_fit_cti_model.md:54.
  The ordering-assertion API is unchanged and still the right idiom for breaking
  exchange degeneracy — only the bypass's handling of it was broken.
- trap: autocti_assistant's `wiki-currency` check is RED ON MAIN, independently of
  any PR. Confirmed by dispatching it on main at 960fdd1c (run 32762029277):
  failed identically. Proof it is not the PR's: the drift-report artifacts are
  964 bytes (PR) vs 961 (main), and the report header's `assistant_ref` line
  differs by exactly 3 chars (refs/pull/21/merge vs refs/heads/main) — so every
  drift FINDING is byte-identical. Artifact byte-size diffing is a cheap way to
  prove two CI failures are the same failure when the log hides the detail.
- trap: that workflow redirects each sub-check into drift-report.md
  (`>> "$REPORT" 2>&1`), so the job log NEVER names which of its five checks
  failed. Read the artifact; do not try to infer it from the log tail.
- decision: PR#21 was merged deliberately over that known-bad base (human-
  authorised at /prm) rather than regenerating an API baseline inside a docs PR.
  The drift is filed separately as draft/bug/autocti/wiki_currency_baseline_drift.md.
- gate-note: autocti_workspace has NO CI configured at all (zero workflow runs,
  zero checks). #25 was merged on explicit human authorisation per /prm's
  no-checks guard. autocti_workspace_test's smoke ran `changes` green and skipped
  `smoke` by path filter — correct for a docs-only diff, not a pending check.
- follow-up: draft/test/autocti/phase5_smoke_reenable_ordered_trap_scripts.md —
  re-enable the smoke coverage the PyAutoFit fix unblocks (CTI epic Phase 5).
- environment: web-github; no worktree. Clones at /home/user/autocti_{workspace,
  workspace_test,assistant}.

## Original prompt

# Delete the TEST_MODE ordered-assertion workaround note from @autocti_workspace AGENTS.md

Type: docs
Target: autocti_workspace
Repos:
- @autocti_workspace
- @autocti_workspace_test
- @autocti_assistant
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-24
Issued: 2026-08-24

Re-homed from `draft/triage/` by the filing session: intake classified this
`triage` / `Target: PyAutoFit` / `too-large` on low confidence, which is wrong on
all three counts — the PyAutoFit fix has already shipped, so nothing here touches
library source. This is a prose deletion across up to three workspace repos.

Delete the TEST_MODE ordered-assertion workaround note from @autocti_workspace AGENTS.md. PyAutoFit#1520 (merged 438f56fac, 2026-08-24) fixed the bypass so a model with identical priors plus an ordering assertion no longer ties at the prior medians — the bypass now picks a deterministic assertion-valid point via _test_mode_valid_parameter_vector, at TEST_MODE 2 and 3. The workspace AGENTS.md documents the crash as a live artifact and tells readers to work around it; that text is now wrong. Delete the note rather than update it — the testmode-env-drift precedent is delete the trap, do not document it. Verify the note's exact wording and location in autocti_workspace first; if a sibling note exists in autocti_workspace_test or autocti_assistant, remove those too.

<!-- formalised by the Intake (Conception) Agent on 2026-08-24 from user-intake -->
