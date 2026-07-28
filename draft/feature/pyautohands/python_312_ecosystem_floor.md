# Adopt Python 3.12 as the PyAuto ecosystem minimum

Type: feature
Target: PyAutoHands
Difficulty: too-large
Autonomy: supervised
Priority: high
Status: formalised

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

## Approved direction

Implement the accepted findings and phases in
`../../research/libraries/python_312_minimum.md`.

- Set maintained PyAuto package metadata to `requires-python >=3.12`.
- Declare and require-test Python 3.12 and 3.13.
- Keep Python 3.14 experimental and non-required until the existing PyAutoFit
  factor-graph regression is fixed in a separate task.
- Remove only Python-version markers and compatibility code made obsolete by
  the floor; retain independently justified dependency caps.
- Coordinate the five-package core stack in dependency order and ship it as one
  coherent release. Handle AutoCTI and AutoReduce on their own readiness and
  release cadences.
- Align build, release, install verification, workspaces, assistants, runtime
  declarations, contributor contracts, and living documentation. Regenerate
  derived notebooks/Markdown from their source scripts and do not rewrite
  published JOSS papers.
- Preserve historical wheels and document the actual last-compatible unyanked
  release for each package; do not yank usable releases.

## Repositories

- Core libraries: @PyAutoNerves, @PyAutoArray, @PyAutoFit, @PyAutoGalaxy, and
  @PyAutoLens.
- Build/health and independent packages: @PyAutoHands, @PyAutoHeart,
  @PyAutoCTI, @PyAutoReduce, and @euclid_assistant.
- Workspaces and tutorials: @autofit_workspace, @autogalaxy_workspace,
  @autolens_workspace, @HowToFit, @HowToGalaxy, @HowToLens, and
  @autocti_workspace.
- Assistants and supporting tooling: @autocti_assistant, @autofit_assistant,
  @autolens_assistant, @PyAutoMemory, @autolens_profiling,
  @autofit_workspace_developer, and @autolens_workspace_developer.
- Test-workspace config surfaces: @autofit_workspace_test,
  @autogalaxy_workspace_test, and @autolens_workspace_test.

## Branch and worktree decision

- Unified branch: `feature/python-312-floor`
- Isolated worktree root: `.codex-worktrees/python-312-floor/<repo>`
- Human approved the branch and overlap strategy on 2026-07-28.

## Sequencing

1. Core contract: PyAutoNerves -> PyAutoArray -> PyAutoFit -> PyAutoGalaxy ->
   PyAutoLens.
2. PyAutoHands/PyAutoHeart matrices and install verification.
3. Coordinated core release gate.
4. PyAutoCTI, PyAutoReduce, PyAutoHeart, and euclid_assistant metadata/readiness.
5. Workspaces, assistants, developer/test tooling, runtime declarations, and
   RAL/HPC prose.
6. Living docs and generated artifacts.
7. Close-out plus separate 3.14 and JAX 0.11 follow-ups.

The Feature Agent scored this campaign `too-large` (61) and recommended phased
combined library/workspace development. Its generic design/core/workspace/docs
stub split is overridden by the evidence-backed sequence above: the accepted
Opus review requires a core release gate and independent CTI/Reduce cadence.

## Acceptance criteria

- All maintained package manifests reject Python below 3.12.
- Required test/install gates are green on 3.12 and 3.13; 3.11 rejection is
  explicitly verified; 3.14 evidence is isolated and non-required.
- Obsolete markers, branches, tests, messages, and duplicated matrix work are
  removed without weakening behavior-driven dependency constraints.
- Core wheels are released coherently and verified on both sides of the floor.
- Every living user/contributor/build/runtime support claim is consistent, and
  generated docs are regenerated from their owning sources.
- Pre-existing Heart failures and unrelated dirty work remain outside scope.
