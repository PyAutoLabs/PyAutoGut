Closed as **superseded**, not implemented — the bug was real, but its remedy
shipped under a different task.

## What the bug was

A clean Python 3.13 install using PyAutoArray's `dev` extras failed the legacy
PyNUFFT transformer test: the pinned `pynufft==2022.2.2` calls
`scipy.linalg.pinv2`, removed in SciPy 1.17.1. The prompt correctly judged this
**pre-existing dependency drift, not a regression** from the Python-floor
Phase 1B diff — it reproduced on unmodified `main`, while the official
CI-profile environment (local packages + `optional` extras) stayed green.

Confirmed 2026-08-22 on a clean 3.13 install: with `pynufft==2022.2.2` present,
`hasattr(scipy.linalg, "pinv2")` is `False`. pynufft 2022.2.2 also emits
`SyntaxWarning: "is" with 'str' literal` on 3.13 — unmaintained against the
supported interpreter range.

## How it was resolved

By `remove_pynufft_legacy_transformer.md`, which took the **third** of this
prompt's three sanctioned remedies — "retire the legacy backend and its tests"
— rather than constraining SciPy or upgrading pynufft. `pynufft` is gone from
PyAutoArray's `optional` and `dev` extras, so no dev-extra install can reach
`scipy.linalg.pinv2` any more.

Library PRs: @PyAutoArray#475, @PyAutoGalaxy#583, @PyAutoLens#709.

## Acceptance, verified independently 2026-08-23

Checked against live code rather than trusting the `Status: superseded` marker:

- PyAutoArray `main` in sync with `origin` (0 ahead / 0 behind); **zero** tracked
  `pynufft` references.
- `pyproject.toml`: `dev = ["pytest", "black", "numba", "nufftax>=0.6.1,<0.7.0"]`
  — the `pynufft==2022.2.2` pin is gone, as is the `optional` entry.
- `TransformerNUFFTPyNUFFT` absent from all three namespaces (`al`/`ag`/`aa`);
  `TransformerNUFFT` and `TransformerDFT` both present.

## Trap worth keeping

**The removal's workspace tier was scoped too narrowly, and the gap was only
found by sweeping while confirming this supersession.** That task listed
`autolens_workspace` and `autolens_workspace_test`; it never swept the siblings.
Left behind:

- One **hard break** — `autolens_workspace_developer/jax_profiling/dataset_setup/interferometer.py:140`
  still names the deleted class. The dict at `:137` is built *eagerly* inside
  `simulate()` (`:106`), so **every** instrument raises `AttributeError`, not
  only the `alma_high_res` config that selects the pynufft backend. Repro'd via
  `simulate('sma')`, a **DFT** dataset.
- Stale prose in @autogalaxy_workspace (26 hits), @autogalaxy_assistant,
  @autolens_assistant, and @PyAutoCTI's install doc.
- Stale CI installs in @PyAutoHands (x3) and @PyAutoHeart.

Filed as `draft/maintenance/workspaces/pynufft_removal_downstream_residue.md`,
split into three phases; phase 1 issued as @autolens_workspace_developer#128.

Generalisable lesson: **when a task removes a public symbol, the sweep must cover
every sibling workspace/assistant/CI surface, not the ones the prompt happens to
name.** A "shipped" marker on the parent task is not evidence the downstream is
clean — grep for the symbol across all repos and separate *executable* references
from historical prose before believing it.

## Original prompt

# PyNUFFT dev extra is incompatible with current SciPy on Python 3.13

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: normal
Status: superseded
Filed: 2026-07-29 (backfilled from git)

## Original request

> ok do phase 1b and any other tasks

## Finding

While validating the Python 3.12-floor Phase 1B change, a clean Python 3.13
environment installed with PyAutoArray's development extras failed the legacy
PyNUFFT transformer test. The pinned `pynufft==2022.2.2` calls
`scipy.linalg.pinv2`, which is absent from SciPy 1.17.1.

The identical failure reproduces on unmodified PyAutoArray `main`, while the
official CI-profile Python 3.13 environment (local packages plus `optional`
extras) passes 928 tests with one skip. This is therefore pre-existing dependency
drift, not a regression from the Python-floor diff.

## Task

Reproduce the dev-extra failure on clean `main`, census whether PyNUFFT remains a
supported optional backend, and choose one explicit remedy: constrain SciPy to a
compatible range for that extra, replace/upgrade PyNUFFT if a maintained version
exists, or retire the legacy backend and its tests. Keep this separate from the
`nufftax` dependency and from Phase 1B issue PyAutoArray#418.

## Acceptance

- A clean Python 3.13 development-extra install has a deliberate, documented
  compatibility policy.
- The PyNUFFT test either passes against the supported dependency set or is
  removed together with an explicit backend-retirement decision.
- The standard optional-profile suite remains green.

## Superseded 2026-08-22

Resolved by `draft/maintenance/libraries/remove_pynufft_legacy_transformer.md`,
which takes this prompt's third sanctioned remedy — "retire the legacy backend
and its tests". `pynufft` is gone from PyAutoArray's `optional` and `dev`
extras, so there is no longer a dev-extra install that can hit
`scipy.linalg.pinv2`.

Confirmed on a clean Python 3.13 install (2026-08-22): with
`pynufft==2022.2.2` present, `hasattr(scipy.linalg, "pinv2")` is `False` under
SciPy 1.17.1 — the drift this prompt reported is real, and pre-existing rather
than a Python-floor regression as it said. pynufft 2022.2.2 also emits
`SyntaxWarning: "is" with 'str' literal` on 3.13, i.e. it is unmaintained
against the supported interpreter range.

Close this out when the removal PRs merge.
