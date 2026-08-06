The Python 3.12 ecosystem-floor migration, complete across every phase: the
five core libraries, build/health machinery, a live release, the independent
downstream repos, and the long-tail selector census — the whole stack now
declares and enforces `Requires-Python >=3.12`.

- parent issue: https://github.com/PyAutoLabs/PyAutoNerves/issues/142
  (companion parents PyAutoCTI#100, PyAutoReduce#59, PyAutoHeart#113)
- phase 1 (core library floors, all merged unchanged after per-head Claude
  Opus 5 CLEAN reviews): PyAutoNerves#143 (`a9bf4561`), PyAutoArray#419
  (`41c55a44`), PyAutoFit#1429 (`241f2d69c`), PyAutoGalaxy#535 (`b9d9927f`),
  PyAutoLens#664 (`b40fb0ba`)
- phase 2 (build + health machinery): PyAutoHands#207 (`1e9ac6d5`),
  PyAutoHeart#115 (`eda92a6b`); hosted matrix 22/22 green (run 30453073189)
- phase 3 (live release): `2026.7.29.2` published to PyPI for
  autonerves/autofit/autoarray/autogalaxy/autolens, two artifacts each,
  `Requires-Python >=3.12`; release run 30487799523 (31 success / 5 classified
  failures / 1 skipped); corrective PyAutoHeart#117 merged; final validation
  run 30472573498 (588 passed, 0 failed, 91 skipped, install A–F PASS);
  human authorization + outcome on PyAutoHands#208
- phase 4 (independent repos, merged unchanged): PyAutoCTI#101 (`3ba4f7a3`),
  PyAutoReduce#60 (`d7bd916a`), PyAutoHeart#114 (`8fb1171f`),
  euclid_assistant#11 (`51143df2`, issue auto-closed)
- phase 5A (selector long tail): PyAutoHands#210, autofit_assistant#25,
  autolens_assistant#95, autocti_assistant#15, PyAutoMemory#31 merged (plus
  assistant baseline fixes #97/#98, #26/#27, #16/#17)
- phase 5B (workspace deployment runtimes): six `runtime.txt` PRs merged
  unchanged — record complete/2026/07/python-312-workspace-runtime-pins.md;
  the tracked selector census is fully at 3.12+
- known follow-ups already routed elsewhere: JAX 0.11 and Python 3.14 support
  are separate tasks; the AutoGalaxy interferometer smoke failure sits in the
  acknowledged workspace-validation class (now the nightly Stage 3 blocker,
  tracked separately)
- closure: parent issues PyAutoNerves#142, PyAutoCTI#100, PyAutoReduce#59 and
  PyAutoHeart#113 closed 2026-07-30 on explicit human cleanup authorization;
  the `python-312-floor` worktree removed post-merge

## Original prompt

# Python 3.12 floor — Phase 1A: PyAutoNerves

Type: feature
Target: PyAutoNerves
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

Parent: `python_312_floor_phase_1_core.md`

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

## Scope

In @PyAutoNerves on `feature/python-312-floor`:

- Set `requires-python = ">=3.12"` and keep only 3.12/3.13 classifiers.
- Remove the now-tautological Python markers from jax, jaxlib, and jaxnnls;
  preserve the JAX `<0.11` cap and all other behavior-driven constraints.
- Keep the import-time version warning and `version.python_version_check`
  bypass, but simplify it for the new floor and make Python 3.14's unsupported,
  experimental status explicit. Remove the unreachable pre-3.11 JAX note.
- Preserve the containing `version:` block and `minimum_library_version`.
- Update warning tests and the `AGENTS.md` floor contract.

## Gates

- Required PyAutoNerves suite passes on Python 3.12 and 3.13.
- Built metadata reports `Requires-Python: >=3.12` and the expected unmarked JAX
  requirements without loosening caps.
- Simulated/current 3.12 and 3.13 emit no warning; simulated/current 3.14 emits
  the experimental warning and remains bypassable.

## Out of scope

JAX 0.11, Python 3.14 support, downstream package manifests, Hands/Heart
matrices, workspaces, release execution, and archival documentation.

## Original series prompt (series umbrella)

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

## Original series prompt (phase 1 core)

# Python 3.12 floor — Phase 1: core library contract

Type: feature
Target: PyAutoNerves
Difficulty: large
Autonomy: supervised
Priority: high
Status: formalised

Parent: `python_312_ecosystem_floor.md`
Research: `../../research/libraries/python_312_minimum.md`

## Original request

> Ok, lets remove support for anything below python3.12, do a census to make sure we simplify requriements, build server, testing, etc. Also make sure all docs are updated.

## Scope

Implement the core contract in dependency order across @PyAutoNerves,
@PyAutoArray, @PyAutoFit, @PyAutoGalaxy, and @PyAutoLens on the unified
`feature/python-312-floor` branch.

- Set `requires-python = ">=3.12"`; advertise only 3.12 and 3.13.
- Remove the eight dependency markers made tautological by the floor while
  retaining all independently justified caps.
- Remove the PyAutoArray pre-3.12 nufftax branch and its mocked 3.11 test
  atomically; keep missing-dependency behavior with version-neutral wording.
- Remove the two PyAutoFit Python-3.7 `Protocol = ABC` shims.
- Retarget, rather than delete, the PyAutoNerves warning/bypass for unsupported
  3.14; preserve the shared `version:` config block.
- Update the five agent-facing `requires-python >=3.9` contracts.

## Gates

- Each repository's required suite passes on Python 3.12 and 3.13.
- Clean isolated install of the dependency-ordered branch chain resolves.
- No behavior-driven JAX, nufftax, SciPy, Astropy, TensorFlow Probability, or
  sampler cap is loosened.
- API-change summary explicitly states metadata/compatibility changes and that
  Python 3.14 remains experimental.

## Out of scope

JAX 0.11 migration, the Python 3.14 factor-graph fix, scheduled build/Heart
matrices, workspaces, generated docs, release execution, and archival papers.

## Feature Agent split

The Feature Agent scored this five-repository phase `too-large` (20). Execute as
five directly shippable library tasks in dependency order:

1. `python_312_floor_phase_1a_nerves.md`
2. `python_312_floor_phase_1b_array.md`
3. `python_312_floor_phase_1c_fit.md`
4. `python_312_floor_phase_1d_galaxy.md`
5. `python_312_floor_phase_1e_lens.md`

## Original series prompt (phase 4 independent)

# Python 3.12 floor — Phase 4: independent packages

Type: feature
Target: PyAutoCTI
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

Parent: `python_312_ecosystem_floor.md`

## Scope

Raise and test the metadata/living-doc floor in @PyAutoCTI, @PyAutoReduce,
@PyAutoHeart, and @euclid_assistant. AutoCTI and AutoReduce keep independent
release histories; do not release either until its own readiness gates pass.
Published paper text remains archival unless a paper is confirmed still draft.

## Original series prompt (phase 5 workspaces)

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

## Original series prompt (phase 6 docs)

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

## Original series prompt (phase 7 close-out)

# Python 3.12 floor — Phase 7: close-out

Type: feature
Target: PyAutoMind
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

Parent: `python_312_ecosystem_floor.md`
Depends on: phases 1-6

## Scope

Record final release boundaries, validation evidence, and the superseded April
policy in @PyAutoMind. Retain separate tasks for Python 3.14 promotion and the
JAX 0.11 dependency migration; do not silently absorb them into this campaign.
