# `pixel_scales` tuple entries are not normalised, so the scalar and tuple forms disagree

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: low
Status: draft

## Why this exists

An inconsistency **introduced by** PyAutoArray#465 (issue #464), which widened
the scalar `pixel_scales` path to accept any real scalar and cast it to Python
`float`. That PR deliberately left the tuple path alone — its own verification
required tuple input be returned unchanged — so the two forms now disagree.

Filed as the follow-up #465 names in its "Deliberately out of scope" section.

## The defect

`autoarray/geometry/geometry_util.py`, both `convert_pixel_scales_1d` and
`convert_pixel_scales_2d`:

```python
validate.validate_pixel_scales(pixel_scales=pixel_scales)

if validate.is_concrete_scalar(pixel_scales):
    pixel_scales = (float(pixel_scales), float(pixel_scales))

return pixel_scales          # <-- a tuple returns untouched
```

So after #465:

```
convert_pixel_scales_2d(1)                        ->  (1.0, 1.0)   # floats
convert_pixel_scales_2d((1, 1))                   ->  (1, 1)       # ints
convert_pixel_scales_2d((np.float64(1), 1.0))     ->  (np.float64(1), 1.0)
```

The same user intent expressed two ways produces two different stored types. The
scalar form now guarantees `Tuple[float, float]` — matching the annotation and
the docstring — while the per-axis form still guarantees nothing.

## Why it is worth fixing

The reasons #465 gave for casting the scalar apply unchanged to tuple entries:

- The return annotation on both functions is `Tuple[float, ...]`, and the tuple
  path can still violate it.
- A NumPy scalar reaching a stored `Mask2D` geometry is what
  `complete/2026/08/save-json-numpy-scalar-typeerror.md` was about
  (`TypeError: Object of type float32 is not JSON serializable`). #465 closed
  that door for the scalar form only.
- Anisotropic pixel scales — the whole reason the tuple form exists — are most
  likely to come from a FITS header (`(header["CD2_2"], header["CD1_1"])`),
  which is exactly where `np.floating` entries originate.

This is a real gap rather than a tidiness complaint, but it is **low priority**:
nothing is broken today that was working before #465, and integer tuple entries
behave correctly in arithmetic. It is the asymmetry that will eventually bite.

## Suggested fix

Normalise entrywise, gated per entry so a tracer in any position still passes
through:

```python
if isinstance(pixel_scales, (tuple, list)):
    pixel_scales = tuple(
        float(scale) if validate.is_concrete_scalar(scale) else scale
        for scale in pixel_scales
    )
```

Decide and pin:

- **Whether a `list` input should now return a `tuple`.** Today a list is
  returned as a list; the snippet above would change that. It may be the right
  fix, but it is a separate behaviour change — check callers first.
- **Identity.** #465's tests assert a tuple is returned *unchanged* via `is`.
  Entrywise normalisation breaks that identity even when every entry is already
  a `float`. Either return the original object when nothing needed casting, or
  update those tests deliberately — do not let them be edited to pass.

## Verification

- `convert_pixel_scales_2d((1, 1)) == (1.0, 1.0)` with both entries Python
  `float`; same for `(np.float64(1), np.int32(2))`.
- An already-`float` tuple is unchanged (and, if that is the decision, still the
  same object).
- A tracer in either position passes through untouched.
- The #440 guards still fire on `(0, 1)`, `(1, -1)` and `nan` entries.
- Full `test_autoarray` suite, with the 3 pre-existing pynufft failures
  baselined on a clean tree first.

Repro environment: `PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`,
`NUMBA_CACHE_DIR=/tmp/numba_cache`, `MPLCONFIGDIR=/tmp/matplotlib`,
`PYAUTO_DISABLE_JAX=1`. Note the repo requires Python >= 3.12.

## Provenance

- Introduced by: `active/pixel_scales_int_not_widened_to_tuple.md`
  (PyAutoArray issue #464 / PR #465), which names this in its out-of-scope list.
