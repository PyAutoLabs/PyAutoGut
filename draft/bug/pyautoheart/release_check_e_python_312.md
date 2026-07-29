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
