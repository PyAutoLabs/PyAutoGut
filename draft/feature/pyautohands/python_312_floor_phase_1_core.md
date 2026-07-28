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
