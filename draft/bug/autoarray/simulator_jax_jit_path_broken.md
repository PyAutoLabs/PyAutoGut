# The documented `@jax.jit` simulator recipe does not run — un-threaded `xp` sites in autoarray

Type: bug
Target: autoarray
Repos:
- PyAutoArray
Difficulty: medium
Autonomy: supervised
Priority: normal

Both workspaces' `scripts/guides/using_jax.py` and the `__JAX Variant__` sections
of five `simulator.py` scripts document this recipe:

```python
simulator = al.SimulatorImaging(
    exposure_time=300.0, psf=psf, background_sky_level=0.1, use_jax=True
)

@jax.jit
def simulate(tracer):
    return simulator.via_tracer_from(tracer=tracer, grid=grid)
```

with the claim *"The simulator handles pytree registration internally — you write
nothing JAX-specific beyond the decorator."*

**Every part of that is false, and the recipe does not run.** Measured
2026-07-29 on the installed stack (`autolens` at `main`), 50×50 grid, Gaussian
PSF via `al.Convolver.from_gaussian`.

## Finding 1 — nothing registers pytrees, anywhere

`grep -rn register` over `autolens/imaging/simulator.py`,
`autolens/interferometer/simulator.py`, `autogalaxy/imaging/simulator.py`,
`autogalaxy/interferometer/simulator.py` and both autoarray simulator bases
(`autoarray/dataset/{imaging,interferometer}/simulator.py`): **zero hits**. No
simulator calls `register_tracer_classes` or `register_galaxies_pytree`.

Without registration the jitted call fails immediately:

```
TypeError: Error interpreting argument to <function simulate ...> as an abstract
array. The problematic value is of type <class 'autolens.lens.tracer.Tracer'>
and was passed to the function at path tracer.
```

`PointSolver.solve_triangles` already documents **why** a simulator cannot fix
this itself (`autolens/point/solver/point_solver.py:102-109`):

> NOTE: pytree registration is the user's responsibility ... Auto-registering
> inside `solve()` doesn't help because JAX flattens function arguments at trace
> time — before entering this method — so registration must run before the first
> jitted call.

That constraint applies identically to `via_tracer_from`. So the claim is not
merely unimplemented, it is **unimplementable as worded** — the user must call
`register_tracer_classes(tracer)` (autolens) / `register_galaxies_classes(galaxies)`
(autogalaxy, added in PyAutoGalaxy#537) before the first jitted call.

Note `autolens/jax/registration.py`'s own module docstring is stale on the same
point: it claims registration "is called automatically by
`PointSolver(use_jax=True).solve(tracer, ...)` on the first invocation and by
`Simulator(use_jax=True).via_tracer_from(tracer, ...)` ... once Phase 2 ships the
Simulator changes". Neither is true; nothing in autolens calls
`register_tracer_classes` at all.

## Finding 2 — even WITH correct registration, the jitted call still fails

This is the library bug. After `register_tracer_classes(tracer)`:

```
jax.errors.TracerArrayConversionError: The numpy.ndarray conversion method
__array__() was called on traced array with shape float64[3600]
```

Failing frame chain:

```
autolens/imaging/simulator.py:91            via_tracer_from  ->  via_image_from
autoarray/dataset/imaging/simulator.py:203  via_image_from
autoarray/dataset/preprocess.py:153         noise_map_via_data_eps_and_exposure_time_map_from
```

`noise_map_via_data_eps_and_exposure_time_map_from` (preprocess.py:134-155)
**takes no `xp` parameter at all** and hardcodes NumPy:

```python
return data_eps.with_new_array(
    np.abs(data_eps.array * exposure_time_map.array) ** 0.5
    / exposure_time_map.array
)
```

Its call site (`autoarray/dataset/imaging/simulator.py:202-204`) cannot pass `xp`
because the parameter does not exist. `include_poisson_noise_in_noise_map`
defaults to **`True`**, so the default path always hits it. Toggling
`add_poisson_noise_to_data` does not avoid it — that is a different flag.

**At least two independent sites.** Bypassing the first with
`include_poisson_noise_in_noise_map=False` moves the failure to the
`Array2D.full(...)` else-branch:

```
autoarray/structures/arrays/array_2d_util.py:147  convert_array_2d
autoarray/structures/arrays/array_2d_util.py:516  array_2d_native_from
autoarray/structures/arrays/array_2d_util.py:565  array_2d_via_indexes_from
```

So this is a multi-site `xp`-threading job, not a one-line fix, and the depth
beyond these two is unmeasured — expect to iterate: fix a site, re-run, find the
next.

## Finding 3 — `use_jax=True` does not put the EAGER result on JAX either

The simulator scripts also claim *"eager `simulator_jax.via_tracer_from(tracer,
grid)` (no `@jax.jit`) already runs on JAX and is sufficient for one-off
simulations."*

Measured: eager `via_tracer_from` with `use_jax=True` **succeeds** but returns
`dataset.data.array` of type **`numpy.ndarray`**, not `jax.Array` — with
`add_poisson_noise_to_data` either `True` or `False`. The `use_jax` plumbing is
present and not a no-op kwarg (`autoarray/dataset/imaging/simulator.py:115-122`
sets `self.use_jax` and `_xp` returns `jnp`; `via_tracer_from` threads `xp`
through), so the NumPy backing is presumably a symptom of the same un-threaded
sites silently falling back to `np`. Confirm whether eager output is *supposed*
to be JAX-backed before treating this as a separate defect — it may be the
correct consequence of `with_new_array` on a NumPy-produced noise map.

## Why nothing caught this

The `__JAX Variant__` sections leave the actual call commented out —
`autolens_workspace/scripts/imaging/simulator.py:381` is
`# dataset_jax = simulate(tracer)`. So the recipe is prose plus a `@jax.jit`
decorator that is never invoked. Same failure mode as the six
`likelihood_function.py` `__JAX__` blocks removed in autolens_workspace#368.

## Scope

**In scope (this prompt):** thread `xp` through the autoarray sites the simulator
`@jax.jit` path reaches, starting with the two identified, iterating until the
recipe runs and returns a `jax.Array`-backed `Imaging`. Add `xp=np` default
parameters rather than changing defaults.

**Out of scope / separate:**

- **The docs are wrong TODAY and should be corrected regardless of whether this
  bug is fixed** — see the docs follow-up below. Do not leave the false claims
  standing while this bug waits.
- Any change to `register_tracer_classes` / `register_galaxies_classes` auto-call
  behaviour. Per `PointSolver`'s note, auto-registration inside the call cannot
  work; registration stays the user's responsibility and the docs must say so.

## Validation

Unit tests are NumPy-only across the stack, so this cannot be covered by
`test_autoarray/`. Validate with a parity script in `autolens_workspace_test` /
`autogalaxy_workspace_test`:

1. `register_tracer_classes(tracer)` then `jax.jit(simulate)(tracer)` returns an
   `Imaging` whose `.data.array` is a `jax.Array`.
2. The jitted result matches the eager NumPy simulation for a fixed
   `noise_seed`.
3. Both `include_poisson_noise_in_noise_map` branches work under jit.
4. Interferometer equivalent (`via_tracer_from` → `FitInterferometer` path,
   `TransformerDFT` only — `TransformerNUFFT` is not JAX-traceable).
5. `test_autoarray/` stays green (additive `xp=np` defaults).

## Companion docs follow-up (file separately, do first)

Correct the false claims in:

- `autolens_workspace/scripts/guides/using_jax.py` — `__Writing @jax.jit Yourself__` item 1
- `autogalaxy_workspace/scripts/guides/using_jax.py` — `__Writing @jax.jit Yourself__`
- `autolens_workspace/scripts/{imaging,interferometer,point_source}/simulator.py` — `__JAX Variant (Advanced)__`
- `autogalaxy_workspace/scripts/{imaging,interferometer}/simulator.py` — `__JAX Variant__`
- also check `autolens_workspace/scripts/{group,multi_galaxy}/simulator.py` (`__JAX Variant__`) and `cluster/simulator.py` (`__JAX JIT__`, `__JAX JIT — Point Solver__`)
- `autolens/jax/registration.py` module docstring (stale auto-call claims) — library, tiny

Either state the registration requirement and mark the jit recipe as not yet
supported, or uncomment the call so CI proves whatever the docs claim. The
governing lesson from autolens_workspace#368: **a documented JAX recipe that no
script executes will be wrong.**
