# Remove pynufft + legacy TransformerNUFFTPyNUFFT (0.23s of import, one fallback class)

Type: refactor
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: low-medium
Autonomy: supervised
Priority: normal
Status: draft

## Original request (verbatim, 2026-08-19)

> do we even use pynufft? maybe we should file a follow up to remove it I think
> its purely for one function, so make that filing remove it but also include
> this check of import time.

## Import-time evidence (from the lazy-heavy-imports profiling, #1505)

After the 2026-08-19 import deferrals, `import autolens` is 1.09–1.17s and the
largest remaining third-party chunk is **scipy at 0.31s self-time** — about a
third of which enters via pynufft: `import pynufft` costs **~0.23s** (its
`pynufft.nufft` pulls `scipy.sparse` at ~0.11s), and it is imported **eagerly**
at `import autoarray` via the module-level try/except at
`autoarray/operators/transformer.py:11-14`
(`from pynufft.linalg.nufft_cpu import NUFFT_cpu`, guarded only against
absence). Removing it takes bare import toward the ~0.8-0.9s floor
(matplotlib being the other deliberate remainder).

## Current footprint (verified 2026-08-19)

- **Dependency**: `pynufft` is a BASE dep in `PyAutoArray/pyproject.toml:67`
  (plus dev pin `pynufft==2022.2.2` at line 77).
- **Sole code use**: the legacy `TransformerNUFFTPyNUFFT` class
  (`transformer.py:270`, subclasses `pynufft.NUFFT_cpu`) — the non-JAX NUFFT
  fallback superseded by the nufftax-backed `TransformerNUFFT`. Re-exported via
  `autoarray/__init__.py`, `autoarray/type.py`, and the autogalaxy/autolens
  `__init__` chains.
- **Workspace references**: prose-only mentions in autolens_workspace
  (start_here.py, using_jax.py, simulator.py, linear_light_profiles/modeling.py
  all describe it as a "non-JAX fallback"); ONE executable use —
  `autolens_workspace_test/scripts/interferometer/nufft.py:211` (transformer
  parity script). Check `PyAutoHands/autohands/config/no_run.yaml` for hidden
  risk per ship_library reference.

## Task

Remove the dependency and the legacy class:

1. Delete `TransformerNUFFTPyNUFFT`, the `NUFFT_cpu`/`NUFFTPlaceholder`
   try-import, and `pynufft_exception()` from `transformer.py`; drop the
   re-exports (`autoarray/__init__.py`, `type.py`) and the pyproject entries
   (base + dev). Sweep autogalaxy/autolens `__init__` re-exports and any
   `Transformer` type unions.
2. Migrate `autolens_workspace_test/scripts/interferometer/nufft.py` (drop or
   replace the PyNUFFT leg of the parity comparison) via /start_workspace.
3. Update the four autolens_workspace prose mentions (drop "legacy
   pynufft-backed fallback" sentences) — prose tier per WORKFLOW.md.
4. This is a REMOVAL: the PR body needs the `## API Changes` breaking entries
   (release-notes contract) — `TransformerNUFFTPyNUFFT` removed, migration =
   use `TransformerNUFFT` (nufftax; also numpy-capable via `xp=np`).
5. Re-run the import-time check afterwards: `python -X importtime -c "import
   autolens" | grep pynufft` must be empty, and record the new total
   (expect ~0.15-0.25s off scipy's share).

Decision the plan must confirm before deleting: `TransformerNUFFT` (nufftax)
covers the numpy/no-JAX path (`visibilities_from(..., xp=np)`), so no user
capability is lost — verify nufftax is a hard-enough dep on all supported
platforms (Intel-Mac marker excludes jax; does the numpy path of nufftax work
there, or does interferometer analysis on Intel Macs lose its transformer?).
If Intel Macs need a fallback, deprecate instead of delete.
