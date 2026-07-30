## python-312-autolens-wiki-currency-ci
- issue: https://github.com/PyAutoLabs/autolens_assistant/issues/94 (closed)
- completed: 2026-07-30
- workspace-pr: https://github.com/PyAutoLabs/autolens_assistant/pull/95 (merged 806f9a6d)
- summary: The autolens assistant wiki-currency workflow now runs on Python 3.12, completing the assistant CI-selector portion of the ecosystem migration.
- validation: clone-boundary and wiki-currency both passed on the final head after PyAutoBrain#182, autolens_assistant#97, and #98 landed.
- notes: The final branch differed from corrected main only in `.github/workflows/wiki-currency.yml`.

## Original prompt

# Python 3.12 floor — AutoLens assistant wiki CI

Type: bug
Target: autolens_assistant
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
