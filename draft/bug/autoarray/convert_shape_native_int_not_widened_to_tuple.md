# `shape_native` given as an `np.integer` is never widened to a tuple

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: low
Status: draft

## Why this exists

The exact sibling of `pixel_scales_int_not_widened_to_tuple.md`, found while
fixing it (shipped as PyAutoArray#465 / issue #464). **Pre-existing — not
introduced by that PR.** Filed rather than fixed inline because #464 was scoped
to `pixel_scales`; widening it to a second parameter would have been scope creep
on a change already ready to merge.

## The defect

`autoarray/geometry/geometry_util.py:27`:

```python
def convert_shape_native_1d(shape_native):
    if type(shape_native) is int:          # <-- exact-type check
        shape_native = (shape_native,)
    return shape_native
```

`type(x) is int` is an exact-type test, so only a literal Python `int` is
widened. An `np.integer` — what you get from indexing a numpy array, reading a
FITS header, or `arr.shape[0]` on some numpy paths — falls through
**unconverted**, and the caller then subscripts a scalar.

This is the identical mistake #464 fixed one function away in the same file.

## Suggested fix

`autoarray/validate.py` already has the predicate:

```python
if validate.is_concrete_scalar(shape_native):
    shape_native = (int(shape_native),)
```

Mind the differences from the `pixel_scales` case, which are why this is its own
prompt rather than a copy-paste:

- **The cast is to `int`, not `float`.** A shape is a pixel count. `#464` pinned
  `float` for `pixel_scales`; the same reasoning (match the annotation, keep
  numpy scalars out of stored state) points at `int` here.
- **`is_concrete_scalar` admits floats**, so `shape_native=5.0` would start
  being accepted and silently truncated. Decide whether that is wanted — a
  narrower `isinstance(x, (int, np.integer)) and not isinstance(x, bool)` test
  may be the better fit, or route it through `validate.validate_shape_native`
  so a non-integral value is rejected with a message rather than truncated.
- There is **no `convert_shape_native_2d`** — only the 1D form exists, so unlike
  #464 there is no sibling to keep in step.

## Verification

- `Array1D.no_mask(values=..., shape_native=np.int64(5))` builds, with
  `shape_native == (5,)` and the entry a Python `int`.
- Tuple input is returned unchanged; a JAX tracer still passes through untouched
  (shapes are static under JAX, so this is a lower-stakes path than #464's, but
  keep the behaviour).
- A `bool` is not silently accepted as a shape of 1.
- Whatever is decided for `5.0`, pin it with a test — truncation and rejection
  are both defensible, silence is not.
- Run the full `test_autoarray` suite; baseline the 3 known pre-existing
  `test_transformer.py` pynufft failures on a clean tree first.

Repro environment: `PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`,
`NUMBA_CACHE_DIR=/tmp/numba_cache`, `MPLCONFIGDIR=/tmp/matplotlib`,
`PYAUTO_DISABLE_JAX=1`. Note the repo requires Python >= 3.12.

## Provenance

- Found during: `active/pixel_scales_int_not_widened_to_tuple.md`
  (PyAutoArray issue #464 / PR #465), and recorded in both.
