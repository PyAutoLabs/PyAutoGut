# Python 3.12 floor — Phase 5: workspaces, assistants, and tooling

Type: feature
Target: autolens_workspace
Difficulty: too-large
Autonomy: supervised
Priority: normal
Status: formalised

Parent: `python_312_ecosystem_floor.md`
Depends on: coordinated core release

## Scope

Align @autofit_workspace, @autogalaxy_workspace, @autolens_workspace,
@HowToFit, @HowToGalaxy, @HowToLens, @autocti_workspace,
@autofit_workspace_test, @autogalaxy_workspace_test,
@autolens_workspace_test, @autocti_assistant, @autofit_assistant,
@autolens_assistant, @PyAutoMemory, @autolens_profiling,
@autofit_workspace_developer, and @autolens_workspace_developer. Move all
seven below-floor runtime declarations to Python 3.12 and update only live
version assumptions, preserving historical benchmark/provenance records.

## Gates

Baseline-aware smoke tests run sequentially; every diff is checked for generated
data/output leakage and active-work overlap before shipping.
