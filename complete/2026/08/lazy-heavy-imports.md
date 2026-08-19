## lazy-heavy-imports
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1505 (closed)
- completed: 2026-08-19
- library-pr: PyAutoFit#1506, PyAutoArray#451, PyAutoNerves#151, PyAutoGalaxy#575, PyAutoLens#705 (all merged 2026-08-19, branches deleted)
- summary: Deferred all heavy non-essential imports to first use. `import autolens` 4.07s → 1.2–1.3s
  (~3.2×; tree self-time 3.22s/3494 modules → 1.27s/1814). jax/jaxlib/blackjax/optax/nufftax/IPython/
  sqlalchemy/numba/astropy proven absent from bare import via `-X importtime`. Workspace-version
  warning deduped to once per process (was 3×, one per library init). Zero public-API change:
  `af.NSS`/`Aggregator`/`Query`/`GridSearchAggregator`/`db` are PEP 562 lazy attrs (+`__dir__`).
- mechanisms: lazy `sa` proxy in `autofit/database/sqlalchemy_.py` + TYPE_CHECKING `sa` imports with
  future-annotations in 14 autofit modules (Py3.12 evaluates `session: Optional[sa.orm.Session]` at
  def time); `_load_nufftax()` anchored in `TransformerNUFFT.__init__` AND its three methods
  (unpickled Pool-worker instances never re-run `__init__`); `numba_util.jit` queues functions and
  materializes ALL on first call, rebinding module globals so the 5 nopython cross-calls resolve;
  function-local astropy/IPython imports; 8 autogalaxy/autolens aggregator files needed
  future-annotations headers (`af.Aggregator` def-time annotations re-trigger the database import).
- traps (for the next reader):
  - `from autofit.database.sqlalchemy_ import sa` executes the PACKAGE `__init__` (star-imports the
    declarative models) — the shim being lazy is not enough; the import statement itself must go.
  - Scope grew from 3 repos to 5 mid-implementation (the downstream annotation sites); conflict
    override on PyAutoFit (claimed by stored-sample-reconstruction-guard, file-disjoint, human-approved).
  - Smoke control-test: the 4 autolens_workspace_test jax_likelihood failures are PRE-EXISTING on
    canonical main (lp.py = positions-LH penalty doubling, orphan worktree fb1aefe0b; others =
    stale-pin drift ~0.012% vs rtol 1e-4). subhalo_recovery 300s timeout = sweep load contention
    (252s uncontended, same as main).
  - Local blackjax 1.5 (no `blackjax.ns`) → `_HAS_NSS` False locally even on main; NSS tests skip.
  - `PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1` exported into a pytest run makes
    test_mismatch_via_version_txt_raises fail spuriously (it bypasses the check under test).
- follow-ups filed as drafts: jax_likelihood stale pins / positions-LH arc; Brain witness map lacks
  test_autonerves; optional matplotlib deferral for bare-library import.

## Original prompt

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
