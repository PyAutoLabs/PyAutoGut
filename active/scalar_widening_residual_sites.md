# Scalar widening: the two sites the `pixel_scales` sweep did not reach

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: medium
Status: active
Filed: 2026-08-23
Issued: 2026-08-23

## Why this exists

PyAutoArray#464 (`8298d74e`, 2026-08-22) fixed `convert_pixel_scales_1d` and
`convert_pixel_scales_2d`: `type(x) is float` became `validate.is_concrete_scalar`,
so `int`, `np.integer` and `np.floating` are all widened and cast to `float`.

Re-running that prompt's repro on 2026-08-23 found the sweep did not reach every site.
Two defects of the same class are live on `main`. Both are confirmed, not suspected.
Completion record: `complete/2026/08/autoarray-pixel-scales-scalar-widening.md`.

## Site 1 — `Mask1D.__init__` never routes through the chokepoint

`autoarray/mask/mask_1d.py:71` still carries the original exact-type check and does its
own widening rather than calling `convert_pixel_scales_1d`:

```python
if type(pixel_scales) is float:
    pixel_scales = (pixel_scales,)
```

```
aa.Mask1D(mask=np.array([False, False, True]), pixel_scales=1).pixel_scales
    ->  1                    # bare int, not (1.0,)
...that mask's .geometry.scaled_maxima
    ->  TypeError: 'int' object is not subscriptable
```

This is #464's exact reported symptom, on a public constructor. `Mask2D.__init__`
is unaffected — it calls `geometry_util.convert_pixel_scales_2d` at
`autoarray/mask/mask_2d.py:218`. So this is a 1D/2D divergence, not a design choice,
and `Grid1D.uniform` is fine because it goes through `geometry_util`.

**Fix:** replace the hand-rolled widening with the call `Mask2D` makes:

```python
pixel_scales = geometry_util.convert_pixel_scales_1d(pixel_scales=pixel_scales)
```

**Consequence to state, not suppress:** `convert_pixel_scales_1d` runs
`validate.validate_pixel_scales` first, so `Mask1D` starts rejecting `0`, negative and
`nan` pixel scales — exactly as `Mask2D` already does. No test in `test_autoarray`
constructs a `Mask1D` with such a value, and the 12 library call sites all pass real
scales, but read any failure this produces rather than adjusting the test.

## Site 2 — `convert_shape_native_1d` keeps `type(x) is int`

`autoarray/geometry/geometry_util.py:27`. `8298d74e` listed this as not-fixed-here.
Reachable through `Array1D.full` / `zeros` / `ones`, whose sole call site is
`autoarray/structures/arrays/uniform_1d.py:143` and which then does `shape_native[0]`:

```
aa.Array1D.full(fill_value=1.0, shape_native=np.int32(5))
    ->  IndexError: invalid index to scalar variable
```

**Fix:** widen to an **integer-only** test — `is_concrete_scalar` is the wrong predicate
here, since `shape_native` is a pixel count and a `float` must not be silently widened.
Use `isinstance(x, (int, np.integer)) and not isinstance(x, bool)`, cast to `int` so the
result matches the `Tuple[int]` annotation. Prefer adding this as `is_concrete_integer`
in `autoarray/validate.py` beside `is_concrete_scalar` (`validate.py:48`), so the
function delegates its predicate the way its `convert_pixel_scales_*` siblings do.

Do **not** add `validate.validate_shape_native` here — the function performs no
validation today and adding it is a separate change.

## Explicitly out of scope

Tuple entries are still returned unnormalised: `convert_pixel_scales_2d((1, 1))` → `(1, 1)`,
contradicting the `Tuple[float, float]` annotation. This changes return values on paths
that currently work, so it needs its own change and its own suite read. Unfiled.

## Verification

- `Mask1D(mask=…, pixel_scales=1).pixel_scales == (1.0,)`; same for `np.float64(1.0)`
  and `np.int32(1)`; `.geometry.scaled_maxima` no longer raises.
- A `(1.0,)` tuple is returned unchanged; a JAX tracer still passes through untouched,
  so `Mask1D` stays `jit`-safe.
- `Mask1D` raises `ValueError` on `pixel_scales` of `0`, `-1` and `nan`, matching `Mask2D`.
- `convert_shape_native_1d` widens `int` and `np.integer` to `(int,)` with a Python `int`
  entry; a `bool` is not widened; a `(5,)` tuple is unchanged.
- `Array1D.full(fill_value=1.0, shape_native=np.int32(5))` builds.
- Every new test confirmed to fail without the source change.
- Full `test_autoarray` suite, not just the touched files — site 1 changes the `Mask1D`
  contract. Baseline the known pre-existing pynufft failures in `test_transformer.py`
  against a clean tree; `8298d74e` recorded 1145 passed / 1 skipped / 3 failed.

Repro environment: `PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`,
`NUMBA_CACHE_DIR=/tmp/numba_cache`, `MPLCONFIGDIR=/tmp/matplotlib`,
`PYAUTO_DISABLE_JAX=1`.

## Provenance

- Follow-up of: `complete/2026/08/autoarray-pixel-scales-scalar-widening.md` (PyAutoArray#464)
- Grandparent: `complete/2026/08/autoarray-input-validation-guards.md` (PyAutoArray#440 / #333)
- Not part of the @rhayes777 audit campaign (`planned.md` § `rhayes-audit-validation-phases-2-4`).
