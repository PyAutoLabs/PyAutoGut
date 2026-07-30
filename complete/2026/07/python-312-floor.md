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
