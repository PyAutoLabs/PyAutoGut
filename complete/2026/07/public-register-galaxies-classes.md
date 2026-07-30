## public-register-galaxies-classes (autogalaxy gains the public register_tracer_classes counterpart — SHIPPED)
- issue: https://github.com/PyAutoLabs/PyAutoGalaxy/issues/536 (CLOSED, auto-closed by the PR)
- completed: 2026-07-29
- library-pr: https://github.com/PyAutoLabs/PyAutoGalaxy/pull/537 (MERGED 9594c00b)
- summary: Added `autogalaxy/jax/__init__.py` + `autogalaxy/jax/registration.py` exporting `register_galaxies_classes(galaxies) -> bool`, mirroring `autolens/jax/{__init__,registration}.py`. It is the public one-time pytree registration for the case a user's own `@jax.jit` receives a `Galaxies` as a traced ARGUMENT — the code path that does not go through an `Analysis`.

  **The initial diagnosis was too strong and probing corrected it.** The claim "autogalaxy has no counterpart" was wrong: `autogalaxy/analysis/jax_pytrees.py::register_galaxies_pytree` already existed. But it is private (reached only from the two `Analysis` classes via `fit_from`) and registers ONLY the `Galaxies` list subclass, so it is insufficient alone. Measured three ways on `@jax.jit def f(galaxies): return ag.FitImaging(..., galaxies=galaxies, xp=jnp).log_likelihood`: no registration → `TypeError` on `Galaxies`; `register_galaxies_pytree()` only → STILL `TypeError`, now on `Galaxy` at `galaxies[0]`; both steps → works, `-270175.0553756637`, exactly the eager value. So the public function does both: calls the existing shared registration, then walks each galaxy registering `Galaxy` and every profile class.

  Two deliberate properties recorded in the module docstring so a future reader does not "fix" them: (1) **nothing inside autogalaxy calls this** — unlike autolens, where `PointSolver` and `Simulator` invoke `register_tracer_classes` automatically, both autogalaxy `Analysis` classes already register inline from `fit_from`; it exists purely as the public entry point, so it is not dead code. (2) The ~60-line recursive walker is **copied** from `autolens/jax/registration.py`, not shared — human decision 2026-07-29, keeping the change to one repo and one reversible PR rather than coupling autolens `main` to autogalaxy `main` immediately after the `2026.7.29.2` release.

  Validation: `test_autogalaxy` 1009 passed / 0 failed; three-way probe green on the branch AND re-verified against merged `main`; idempotent (second call returns True, registers nothing); `import autogalaxy` does NOT eagerly import `autogalaxy.jax` (checked via `sys.modules`, so no import cost added); with `import jax` forced to raise, the function returns `False` without raising. CI on the exact head `debf3eb8`: Docs success, Tests success. `autogalaxy.jax` is auto-discovered by `[tool.setuptools.packages.find]`, so no packaging change was needed. Unit tests here are NumPy-only by policy, so the JAX behaviour is covered by the probe, not by `test_autogalaxy/`.

- origin: fell out of likelihood-function-jax-pointer (autolens_workspace#368) — the six deleted `__JAX__` blocks documented a recipe that did not run, and writing the correct one exposed this asymmetry.
- followups: (1) **autogalaxy_workspace guide mention** — document the jit-argument case + this call in `scripts/guides/using_jax.py`, matching how the autolens guide points at `register_tracer_classes`. NOW UNBLOCKED (#537 merged). (2) **Dedupe the walker** across `autolens/jax/registration.py` and `autogalaxy/jax/registration.py`. (3) **Verify a neighbouring doc claim** — `using_jax.py` says "the simulator handles pytree registration internally", but neither `autogalaxy/imaging/simulator.py` nor `interferometer/simulator.py` contains any pytree registration call; either an autoarray base does it or that sentence is wrong too (pre-existing text).

## Original prompt

# autogalaxy: add a public `register_galaxies_classes`, the counterpart to `autolens.jax.register_tracer_classes`

Type: feature
Target: autogalaxy
Repos:
- PyAutoGalaxy
Difficulty: small
Autonomy: supervised
Priority: normal

PyAutoLens ships `autolens.jax.register_tracer_classes(tracer)` — a public,
one-time pytree registration for code paths that do **not** go through an
`Analysis`: a user's own `@jax.jit` that receives the aggregate object as a
traced argument. PyAutoGalaxy has no equivalent public entry point.

Found 2026-07-29 while writing the `__Custom Likelihood Functions__` section of
`autogalaxy_workspace/scripts/guides/using_jax.py`
(autogalaxy_workspace#181, merged): the guide can document the
`Analysis`, hand-rolled-inside-jit, and `Fitness` paths, but cannot document
passing a `Galaxies` **as a jit argument**, because there is no public call to
make it work.

## What exists today

`autogalaxy/analysis/jax_pytrees.py` has `register_galaxies_pytree()`, which
registers **only** the `Galaxies` list subclass (it needs a custom flatten
because the generic `__dict__` flatten would drop the list contents). It is
called from `AnalysisImaging._register_fit_imaging_pytrees` and the
interferometer equivalent — both **private**, both reached only via `fit_from`.

That helper alone is **not sufficient** for the jit-argument case. Measured on
the installed stack with

```python
@jax.jit
def log_likelihood(galaxies):
    return ag.FitImaging(dataset=masked_dataset, galaxies=galaxies, xp=jnp).log_likelihood
```

| Registration | Result |
|---|---|
| none | `TypeError: ... problematic value is of type Galaxies ... at path galaxies` |
| `register_galaxies_pytree()` only | still fails — `... problematic value is of type Galaxy ... at path galaxies[0]` |
| `register_galaxies_pytree()` **+** recursive walk registering `Galaxy` and each profile class | works; matches the eager value exactly (`-270175.0553756637`) |

So the public entry point must do **both** steps, exactly as
`register_tracer_classes` does (it registers `Tracer` with
`no_flatten=("cosmology",)` and then walks `tracer.galaxies`).

## Scope

**In scope — PyAutoGalaxy only:**

- New `autogalaxy/jax/__init__.py` exporting `register_galaxies_classes`,
  mirroring `autolens/jax/__init__.py`.
- New `autogalaxy/jax/registration.py` mirroring
  `autolens/jax/registration.py`:
  - `register_galaxies_classes(galaxies) -> bool` — returns `False` (silent
    no-op) if JAX is not installed; otherwise calls the existing
    `register_galaxies_pytree()` and then walks each galaxy registering every
    non-builtin class reachable from it. Idempotent.
  - `_register_object_classes` / `_iter_attribute_values` / `_is_builtin` —
    copies of the autolens walker, including the `_is_builtin` guard that skips
    `numpy` / `jax` / `jaxlib` module classes (registering a JAX tracer type
    would break every subsequent tracer flatten, since tracers have no
    `__dict__`).

**Deliberately out of scope:**

- **Do not** refactor `autolens/jax/registration.py` to import the shared
  walker. Human decision 2026-07-29: keep this to one repo and one PR, fully
  reversible, rather than couple autolens `main` to autogalaxy `main`
  immediately after the `2026.7.29.2` release. The ~60-line walker is therefore
  duplicated across the two libraries — record a follow-up refactor prompt to
  dedupe it (autogalaxy would own it; autolens may import autogalaxy).
- **Do not** add an internal caller. Unlike autolens — where `PointSolver` and
  `Simulator` call `register_tracer_classes` automatically — nothing in
  autogalaxy needs this internally: both `Analysis` classes already register
  inline via `fit_from`. This is purely a public entry point for the
  hand-rolled path. Say so in the docstring so a future reader does not
  "clean up" an apparently unused function.
- **Do not** change `register_galaxies_pytree()` or either `Analysis`. The new
  function composes with them.
- No workspace edits in this task — the guide mention is the follow-up below.

## Validation

Unit tests in this repo are **NumPy-only** ([[feedback_no_jax_in_unit_tests]]),
so `test_autogalaxy/` cannot cover the JAX behaviour. Validate by:

1. `python -m pytest test_autogalaxy/` — must stay green (the change is additive;
   the new module is not imported at package import time).
2. Import-surface check: `ag`'s top-level import must not eagerly import JAX.
   Confirm `import autogalaxy` still works with JAX absent and that
   `autogalaxy.jax` is only imported on demand (mirror how
   `autolens/jax/__init__.py` behaves — note `autolens.jax` is a subpackage, not
   re-exported through `autolens/__init__.py`).
3. The three-way probe above, re-run against the branch: none → fails on
   `Galaxies`; `register_galaxies_pytree()` only → fails on `Galaxy`;
   `register_galaxies_classes(galaxies)` → works and matches eager.
4. `register_galaxies_classes` returns `False` and does not raise when JAX is
   uninstallable/absent.

## Follow-ups (separate prompts, do not fold in)

- **Workspace guide mention.** Add the jit-argument case + this call to the
  `__Custom Likelihood Functions__` / `__JIT-ing Library Methods__` sections of
  `autogalaxy_workspace/scripts/guides/using_jax.py`, matching how the autolens
  guide points at `register_tracer_classes`. Blocked until this PR merges
  (library-first).
- **Dedupe the walker** across `autolens/jax/registration.py` and
  `autogalaxy/jax/registration.py`.
- **Check the autogalaxy simulator claim.** `using_jax.py` states "The simulator
  handles pytree registration internally", but `autogalaxy/imaging/simulator.py`
  and `interferometer/simulator.py` contain **no** pytree registration calls —
  verify whether an autoarray base class does it, or whether that sentence is
  wrong too. (Pre-existing text, not introduced by autogalaxy_workspace#181.)
