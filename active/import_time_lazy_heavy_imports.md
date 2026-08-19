# Slow imports: defer jax chain + 5 heavy eager imports (autolens 4.1s → ~1.5s)

Type: refactor
Target: libraries
Repos:
- @PyAutoFit
- @PyAutoArray
- @PyAutoNerves
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft

## Original request (verbatim, 2026-08-19)

> Can you do a profiling of how long import times on autolens_workspace
> example scripts and performance in general is, and assess if we can speed
> it up as it is important for running smoke tests and general user
> performance being fast

(Supersedes the 2026-07-25 hygiene perf-tier finding that first filed this
prompt; the profiling below replaces its guessed causes and repo list.)

## Measured profile (2026-08-19, Python 3.12, autolens 2026.8.17.1)

`import autolens` ≈ 4.0–4.1 s; full script stanza (`af`+`al`+`aplt`) ≈ 4.4 s.
457 scripts in autolens_workspace each pay this per-process — ~30 min of pure
import per full serial smoke sweep, and smoke runs with JAX *disabled*, so the
jax import there is pure waste.

**Control test (meta-path blocker): blocking nufftax + blackjax + optax drops
import to 2.31 s and jax never loads.** The jax chain (~1.75 s, 43%) enters
via two eager paths, both already inside `try/except ModuleNotFoundError`
(the Intel-Mac marker from the JAX-default arc, PyAutoLens#702, requires
jax-less import to keep working anyway):

1. `PyAutoArray/autoarray/operators/transformer.py:27` — `import nufftax` → jax
2. `PyAutoFit/autofit/__init__.py:98` — eager `NSS` import →
   `nss/search.py:20` `import blackjax` → jax + optax

Unguarded module-level imports, ~1.1 s more (self-time from `-X importtime`):

3. `PyAutoFit/autofit/non_linear/fitness.py:3` —
   `from IPython.display import clear_output` (~0.22 s incl.
   prompt_toolkit/jedi/parso)
4. sqlalchemy via `autofit/database/sqlalchemy_.py` ←
   `non_linear/paths/database.py` (~0.35 s cum)
5. matplotlib pulled by BARE `import autolens` via
   `autoarray.dataset.plot.imaging_plots` (~0.35 s self incl. PIL/pyparsing)
6. numba+llvmlite via `autoarray/inversion/mappers/mapper_numba_util`
   (~0.17 s; jit cache=True already — it is the package import that costs)
7. astropy via `autonerves.fitsable` ← `autoarray.mask.mask_2d` (~0.17 s)

Incidental: the autonerves workspace-version `UserWarning` prints three times
per interpreter (once per library init) — dedupe while in there.

## Task

Defer the heavy imports to first use without changing the public `af.*` /
`aa.*` / `al.*` surface:

- Phase 1 (measured 1.75 s, lowest risk): function-local `import nufftax` in
  `transformer.py`; make `af.NSS` a lazy attribute (PEP 562 module
  `__getattr__` in `autofit/__init__.py`). NSS/blackjax must STAY supported —
  lazy, never removed (Mind record: nss removal parked).
- Phase 2 (~0.9 s): function-local IPython import in `fitness.py`; lazy `sa`
  proxy in `autofit/database/sqlalchemy_.py` (+ `from __future__ import
  annotations` at `sa.orm.Session` signature sites) so sqlalchemy loads only
  when database paths/aggregator are used; lazy-compile wrapper in
  `autoarray/numba_util.py:jit` (defers numba to first call for all 29
  decorated functions); lazy astropy in `autonerves.fitsable`.
- Dedupe the autonerves workspace-version warning to once per process.
- SCOPED OUT: matplotlib deferral — it enters via the autolens/autogalaxy
  visualizer chain and every workspace script imports `aplt` anyway, so
  deferring it buys nothing for smoke/users. Optional follow-up for
  bare-library import (unit tests) only.

## Acceptance

- `import autolens` cold ≤ ~1.9 s on the same box (from 4.1 s; matplotlib
  intentionally retained); `python -X importtime` shows no
  jax/jaxlib/blackjax/optax/nufftax/IPython/sqlalchemy/numba/astropy modules
  on bare import.
- No public API change: `af.NSS` still resolves; jax-mode scripts and the
  `unittest-nojax` CI leg both green; full test suites green; workspace smoke
  pass over jax-mode scripts (`# ENV: jax`) green.
