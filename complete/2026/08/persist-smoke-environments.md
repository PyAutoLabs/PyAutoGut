## persist-smoke-environments
- issue: https://github.com/PyAutoLabs/PyAutoHeart/issues/141
- completed: 2026-08-10
- pr: https://github.com/PyAutoLabs/PyAutoHeart/pull/142
- summary: Made smoke dependency environments durable and isolated per library and Python version, with version-handshake invalidation to prevent stale dependency reuse. This directly addresses recurring nufftax and related environment drift rather than relying on a one-off local repair.
- validation: PyAutoHeart 351 tests passed locally; CI passed on Python 3.12 and 3.13; a real autogalaxy prepare/reuse cycle passed with dill 0.4.1, numba 0.66.0, and nufftax 0.6.1.
- merge-commit: `3e053d7`.

## Original prompt

# Persist smoke-test runtime dependencies

## Original request

> And make sure it is permanent enough to stay in future as I feel like nufftax and other issues crop up now and then? Maybe this was recent work

## Goal

Determine why the local all-workspace smoke gate lacked `dill`, `numba`, and
`nufftax`, check whether recent dependency or validation-runner changes caused
the regression, and make the smallest durable change that ensures future smoke
runs use a complete, declared runtime environment rather than relying on
ambient packages.

## Constraints

- Fix dependency ownership or environment construction, not individual science
  scripts.
- Keep local smoke and CI workspace validation aligned.
- Add regression coverage that detects missing required smoke dependencies
  before expensive scripts begin.
