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
