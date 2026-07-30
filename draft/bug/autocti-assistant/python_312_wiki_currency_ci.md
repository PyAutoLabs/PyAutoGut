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
