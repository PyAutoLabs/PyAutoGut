## python-312-autocti-wiki-currency-ci
- issue: https://github.com/PyAutoLabs/autocti_assistant/issues/14
- completed: 2026-07-30
- workspace-pr: https://github.com/PyAutoLabs/autocti_assistant/pull/15
- summary: Raised the assistant wiki-currency runner to Python 3.12 and made
  the arcticpy source-build bootstrap explicit by installing setuptools and
  wheel. Both wiki-currency and clone-boundary checks passed.

## Original prompt

# Python 3.12 floor — AutoCTI assistant wiki CI

Type: bug
Target: autocti_assistant
Difficulty: small
Autonomy: human-required
Priority: high

Parent: `python-312-floor`

## Scope

Raise `.github/workflows/wiki-currency.yml` from Python 3.11 to Python 3.12 so
the assistant remains compatible with the ecosystem floor before its release
train invokes the same check.

Run only workflow syntax and residual-selector checks; do not rerun the full
ecosystem release or workspace suite.

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

> I approve

No Claude delegation is authorized for this follow-up.
