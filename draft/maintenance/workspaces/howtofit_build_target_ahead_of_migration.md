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
  list resolves `HowToFit` to the stub.
- PyAutoHands `test_every_build_target_owns_no_run` passes on a full sibling
  checkout that uses the corrected mapping (already true with the org repo).

## Status check (2026-08-06, cloud session)

Everything verifiable from a cloud session has been verified; what remains is
repo-admin clicks on the Jammy2211 account that no session can perform (the
GitHub MCP surface has no archive/delete-branch tools, and cross-owner
`add_repo` is blocked, so the fork is unreachable for pushes from a
PyAutoLabs-scoped session).

**Verified done / not-a-problem:**

- Acceptance item 2 **passes**: this session's `HowToFit` sibling maps to
  `PyAutoLabs/HowToFit` (fully populated: `config/build/no_run.yaml`,
  `profile_smoke.yaml`, `markdown_examples.yaml`), and
  `PyAutoHands/tests/test_workspace_config_precedence.py` passes 8/8 including
  `test_every_build_target_owns_no_run`.
- **No persistent config carries the bad mapping.** Audited all stored
  Routines/triggers (only PyAutoBuild-sourced ones exist) and the single cloud
  environment; the 2026-07-25 `HowToFit → Jammy2211` mapping was a one-off
  source selection in that health-sweep session, not a saved configuration.
  Nothing to repoint — task item 2 closes with this finding.
- Fork state as of today: **not archived**, three branches — `main` plus two
  stray Claude branches: `claude/g-heart-green-fable-opus-uuiaqf` (the known
  one, 2026-07-25) and `claude/rename-pyautobuild-pyautohands-w4b27e`
  (2026-07-18, previously unnoticed).

**Remaining manual runbook (~2 min, Jammy2211 account in a browser):**

1. Delete both stray branches at
   https://github.com/Jammy2211/HowToFit/branches (trash icon):
   `claude/g-heart-green-fable-opus-uuiaqf` and
   `claude/rename-pyautobuild-pyautohands-w4b27e`.
2. Archive (or delete) the repo:
   https://github.com/Jammy2211/HowToFit/settings → Danger Zone →
   "Archive this repository". Archiving is reversible and blocks all pushes.
3. Optional belt-and-braces: remove Jammy2211/HowToFit from the Claude GitHub
   App's repository access on the Jammy2211 account, so session source pickers
   stop offering it (it currently appears in `list_repos` with push access).

Once step 2 is done, both acceptance boxes are ticked and this prompt can be
retired to `complete/`.
