# howtofit-stub-fork-cleanup

**Completed:** 2026-08-07
**Type:** maintenance · **Target:** workspaces (@HowToFit) · **No code PR** —
GitHub admin actions + this Mind record (branch
`claude/howtofit-migration-prep-k2d7sa`).

## Summary

Closed out the corrected HowToFit build-target prompt: the org repo
(PyAutoLabs/HowToFit) was always fine; the 2026-07 health-sweep failure was a
checkout artifact of a cloud session whose `HowToFit` sibling was a clone of
the **Jammy2211/HowToFit** README-only stub. The stub is now archived
(read-only, 2026-08-07) with both stray `claude/*` branches deleted, and the
"session source mapping" loose end resolved by audit: no persistent
configuration ever carried the bad mapping.

## What was done

- **Verified the org repo + test (cloud session, 2026-08-06):**
  `PyAutoLabs/HowToFit` sibling checkout carries the full `config/build/` set
  (`no_run.yaml`, `profile_smoke.yaml`, `markdown_examples.yaml`);
  `PyAutoHands/tests/test_workspace_config_precedence.py` passes 8/8 including
  `test_every_build_target_owns_no_run`.
- **Audited session/trigger config:** no stored Routine, trigger, or cloud
  environment maps `HowToFit` to Jammy2211 — the 2026-07-25 mapping was a
  one-off source selection in that health-sweep session. Nothing to repoint.
- **Fork cleanup (human, browser, 2026-08-07):** deleted the stray branches
  `claude/g-heart-green-fable-opus-uuiaqf` (the known 2026-07-25 seed) and
  `claude/rename-pyautobuild-pyautohands-w4b27e` (2026-07-18, found during
  verification), then archived Jammy2211/HowToFit. Only `main` remains;
  GitHub now rejects all pushes to it.

## Key findings / traps

- **Cloud sessions cannot administer cross-owner repos.** The GitHub MCP
  surface has no archive-repo or delete-branch tools, and `add_repo` rejects
  cross-owner adds ("cross-tier adds are not supported in v1") — a
  PyAutoLabs-scoped session cannot reach a Jammy2211 repo even with push
  rights on the account. Repo-admin actions on personal-account repos are
  browser-only.
- **The stub still appears in `list_repos`** (now with `archived: true`).
  Archived = read-only, so a mis-mapped session can no longer push to it, but
  the picker can still offer it. Optional belt-and-braces (not done): remove
  Jammy2211/HowToFit from the Claude GitHub App's repository access at
  github.com/settings/installations on the Jammy2211 account.
- Root-cause pattern for the original false alarm: a health sweep judging a
  sibling-path check must confirm *which remote* each sibling maps to before
  reporting a repo defective.

## Original prompt

# CORRECTED: HowToFit build target is fine — the stub is the Jammy2211 fork

Type: maintenance
Target: workspaces
Repos:
- @HowToFit
Difficulty: easy
Autonomy: supervised
Priority: low
Status: draft

## Correction (2026-07-25, supersedes the original finding)

The original version of this prompt claimed PyAutoLabs/HowToFit was an empty
shell missing `config/build/no_run.yaml`, failing PyAutoHands'
`test_every_build_target_owns_no_run` on full checkouts. **That was wrong.**

PyAutoLabs/HowToFit is fully populated (scripts/, notebooks/, config/build/
with no_run.yaml + profile_smoke.yaml + markdown_examples.yaml,
smoke_tests.txt). The failing test was a checkout artifact of the cloud
session that ran the health sweep: its `HowToFit` sibling directory was a
clone of **Jammy2211/HowToFit** — a stub containing only a README — so the
sibling-path check found no config there.

## Remaining (small) task

Two loose ends, both about the stub fork, not the org repo:

1. Decide the fate of **Jammy2211/HowToFit** (README-only stub). If it has no
   purpose, archive or delete it so tooling and session source-lists cannot
   confuse it with PyAutoLabs/HowToFit. (A stray
   `claude/g-heart-green-fable-opus-uuiaqf` branch with one harmless seed
   commit was pushed to it on 2026-07-25 before the mix-up was caught; branch
   deletion was permission-blocked from the session — remove it when
   archiving/cleaning.)
2. Check the cloud-session source configuration that produced the checkout:
   the session mapped `HowToFit` to the Jammy2211 fork while every other
   repo mapped to PyAutoLabs. Point it at PyAutoLabs/HowToFit.

## Acceptance

- Jammy2211/HowToFit archived/deleted or clearly marked; no session source
  list resolves `HowToFit` to the stub. ✅ (archived 2026-08-07; no persistent
  source config carries the mapping)
- PyAutoHands `test_every_build_target_owns_no_run` passes on a full sibling
  checkout that uses the corrected mapping (already true with the org repo).
  ✅ (8/8 pass, 2026-08-06)
