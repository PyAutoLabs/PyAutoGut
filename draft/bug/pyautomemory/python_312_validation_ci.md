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
