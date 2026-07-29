## release-check-e-python-312
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/116
- completed: 2026-07-29
- library-pr: https://github.com/PyAutoLabs/PyAutoHeart/pull/117
- merged: bda57c16a16763604967a1e1e4ed11ced22d516e
- reviewed-head: 8259dcfb3fc7b401e4405473c3ddcf2b99e0610a
- summary: Check E now creates its historical 2026.2.26.4 environment explicitly with Python 3.12, fails clearly when that interpreter is unavailable, and records the interpreter in release evidence.
- review: PyAuto review CLEAN and Claude Opus 5 max-effort CLEAN on the exact merged tree; merged-tree identity verified after PR merge.
- tests: 17 focused install-script tests, 6 manifest-drift tests, and 302 full PyAutoHeart tests passed; GitHub PR CI passed on Python 3.12 and 3.13.
- release-evidence: Definitive release run 30472573498 passed install checks A-F, including current support on 3.12/3.13, 3.11 rejection, and historical Check E on 3.12. Its remaining workspace jobs continue under the parent python-312-floor release task.
- notes: No public package API or downstream workspace migration. Issue closure was deliberately not performed.

## Original prompt

# Fix release Check E interpreter selection

Type: bug
Target: PyAutoHeart
Difficulty: small
Autonomy: supervised
Priority: urgent

## Context

The Python 3.12-floor release integration passed 588 runnable workspace scripts
and install checks A/B/C/D/F, but Check E inherited Python 3.13 from the final
`actions/setup-python` step. Its historical `2026.2.26.4` dependency stack has
no compatible SciPy 1.14.0 wheel on Python 3.13, so pip attempted a source build
and failed for missing OpenBLAS. The same Check E passes on Python 3.12.

Make Check E select Python 3.12 explicitly, add regression coverage for the
interpreter selection, review and merge the corrective PyAutoHeart PR, then
rerun Stage 3 against the existing exact TestPyPI rehearsal artifacts. Do not
dispatch the live release unless the complete gate passes and Heart satisfies
the existing authorization conditions.

## Original Prompt

go
