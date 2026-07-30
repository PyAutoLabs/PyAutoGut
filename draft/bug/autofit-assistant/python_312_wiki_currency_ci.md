# Python 3.12 floor — AutoFit assistant wiki CI

Type: bug
Target: autofit_assistant
Difficulty: small
Autonomy: human-required
Priority: high

Parent: `python-312-floor`

## Scope

Raise `.github/workflows/wiki-currency.yml` from Python 3.11 to Python 3.12.
The live `2026.7.29.2` release correctly requires Python 3.12, so the release
wiki check currently fails before auditing any documentation.

Run only workflow syntax and residual-selector checks; do not rerun the full
ecosystem release or workspace suite.

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

> I approve

No Claude delegation is authorized for this follow-up.
