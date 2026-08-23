# Regenerate autogalaxy_workspace markdown/ so three curated pages drop the pynufft prose

Type: docs
Target: autogalaxy_workspace
Repos:
- @autogalaxy_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft
Filed: 2026-08-23

## Provenance

Deferred debt from `pynufft_removal_downstream_residue` phase 2
(@autogalaxy_workspace#225; record
`complete/2026/08/pynufft-removal-residue-phase-2.md`). Split out here so it
survives its parent task's completion record instead of being buried in it —
the same pattern as
`draft/docs/autolens_workspace/markdown_regeneration_sigma_min.md`.

## What is stale

Three curated `markdown/` pages still carry the pre-removal pynufft text,
describing the deleted `TransformerNUFFTPyNUFFT` as an available "non-JAX
fallback":

- `markdown/start_here`
- `markdown/interferometer/start_here`
- `markdown/interferometer/simulator`

Their `scripts/` sources were corrected by #225; `notebooks/` was regenerated
alongside. `markdown/` was **deliberately** not regenerated.

## Why it was deferred, and the trap

`markdown/` is NOT `notebooks/`. `generate.py` converts scripts to notebooks
cheaply; `markdown/` has a separate generator
(`PyAutoHands/autohands/generate_markdown.py`) that **executes curated scripts
for real**, and whose documented policy is "manual / at-release, only when a
curated script changes — never per-commit". Running it inside a docs PR is not
the intended workflow.

Check the sibling prompt
(`draft/docs/autolens_workspace/markdown_regeneration_sigma_min.md`) before
running anything: it records the generator's constraints, including that it
refuses to run under `PYAUTO_TEST_MODE`. Confirm the project key and CWD
requirements for the `autogalaxy` project too — they differ per workspace.

## Acceptance

- The three pages no longer mention `TransformerNUFFTPyNUFFT` or advertise
  pynufft, and match what their `scripts/` sources now say.
- The pages were **regenerated**, not hand-edited.
- No unrelated curated page churns in the same commit.
