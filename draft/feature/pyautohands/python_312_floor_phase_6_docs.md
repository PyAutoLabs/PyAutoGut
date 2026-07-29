# Python 3.12 floor — Phase 6: living docs and generated artifacts

Type: docs
Target: PyAutoLens
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

Parent: `python_312_ecosystem_floor.md`
Depends on: coordinated core release

## Scope

Update all living installation, migration, contributor, workspace, assistant,
Colab/conda, build, and HPC claims to the accepted wording and verified
last-compatible releases. Edit guide `.py` owners first and regenerate their
notebook/Markdown derivatives through @PyAutoHands. Do not rewrite published
JOSS papers or historical benchmark/provenance artifacts.

Reconcile every pip guide against the live PyPI release history. In particular,
PyAutoGalaxy had multiple unyanked `>=3.9` releases after its earlier 3.12-floor
release, so Python 3.9-3.11 can silently resolve backwards. If usable historical
wheels remain unyanked, document the rollback and the verified last-compatible
pin; do not promise a `no matching distribution` error.

## Gates

Documentation navigation/link checks pass and generated diffs are confined to
the expected cells/files.
