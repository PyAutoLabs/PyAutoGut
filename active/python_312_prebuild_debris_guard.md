# Python 3.12 floor — prevent pre-build debris commits

Type: bug
Target: PyAutoHands
Difficulty: small
Autonomy: human-required
Priority: high

Parent: `python-312-floor`
Release evidence: `PyAutoHands` run `30487799523`, version `2026.7.29.2`

## Scope

Correct the release-preparation staging failure exposed by the Python 3.12
release. Commit `95f7502` swept the zero-byte root file `=3.12` and 2,058
generated files under `run_logs/` into `PyAutoHands` because `pre_build.sh`
uses a repository-wide `git add -A` for a step that produces no PyAutoHands
source artifacts.

- Remove `=3.12` and `run_logs/` from the current tree without rewriting
  history; the files remain recoverable from commit `95f7502`.
- Ignore the generated `run_logs/` tree.
- Replace the PyAutoHands self-staging sweep with a fail-fast clean-tree
  invariant before any release preparation side effects.
- Update the pre-build documentation and focused regression tests.
- Do not rerun the ecosystem release or full workspace validation.

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

> I approve

No Claude delegation is authorized for this follow-up.
