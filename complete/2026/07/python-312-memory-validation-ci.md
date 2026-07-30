## python-312-memory-validation-ci
- issue: https://github.com/PyAutoLabs/PyAutoMemory/issues/30 (open; ready for human close)
- completed: 2026-07-30
- workspace-pr: https://github.com/PyAutoLabs/PyAutoMemory/pull/31 (merged 5fe0536a)
- summary: PyAutoMemory validation now runs on Python 3.12 and its repository-structure validator recognizes the shared root `AI_POLICY.md`.
- validation: `make validate` passed; `make test` passed with 10 tests; PR validation green.
- notes: The allowlist regression was the pre-existing blocker discovered while shipping the Python selector, so both one-line corrections landed together.

## Original prompt

# Python 3.12 floor — Memory validation CI

Type: bug
Target: PyAutoMemory
Difficulty: small
Autonomy: human-required
Priority: high

Parent: `python-312-floor`

## Scope

Raise `.github/workflows/validate.yml` from Python 3.11 to Python 3.12 so the
Memory organ's active validation surface matches the supported ecosystem
floor. Preserve the unrelated dirty `reading-queue.md` in the main checkout by
working from a clean `origin/main` task worktree.

Run only workflow syntax and residual-selector checks; do not rerun the full
ecosystem release or workspace suite.

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

> I approve

No Claude delegation is authorized for this follow-up.
