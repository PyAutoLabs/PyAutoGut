# PyAutoCTI main is red: serial-EPER test builds a zero-width (3, 0) region

Type: bug
Target: autocti
Repos:
- @PyAutoCTI
Difficulty: low
Autonomy: supervised
Priority: high
Status: draft
Filed: 2026-08-23

## Provenance

Found 2026-08-23 by the phase-3 pynufft-removal PR (@PyAutoCTI#107), whose diff
is a single deleted line in `docs/installation/source.rst` — the failure is
pre-existing and belongs to `main`, not to that PR. Reported there as a comment,
deliberately not fixed inside a docs PR.

## The failure

All three legs of `unittest` (3.12, 3.13, `unittest-nojax`) fail on the same
single test; 270 of 271 pass:

```
FAILED test_autocti/extract/two_d/serial/test_serial_eper.py::test__region_list_from__array_2d_list_from
  autoarray.exc.MaskException: shape_native[1] must be a positive number of
  pixels; got 0. The full shape_native input was (3, 0)
  ../PyAutoArray/autoarray/validate.py:108
```

## Why it started now

`PyAutoHeart/.github/workflows/lib-tests.yml` clones PyAutoArray **`main`** at
run time, so this repo's suite tracks autoarray source, not a released wheel.
@PyAutoArray#440 (merged `f2f7a4f`, 2026-08-09 — the #333/B8 input-validation
guards; record `complete/2026/08/autoarray-input-validation-guards.md`) added
the zero-length `shape_native` guard to `Mask2D.__init__`.

PyAutoCTI's last `main` run was **2026-08-07** (run 31134701968, green), so the
break has been dormant: nothing has pushed to this repo since the guard landed.
It will block every future PyAutoCTI PR until fixed.

## What the guard exposed — a vacuous assertion

```python
extract = ac.Extract2DSerialEPER(region_list=[(0, 3, 1, 4), (0, 3, 5, 8)])
array_2d_list = extract.array_2d_list_from(
    array=serial_array, settings=ac.SettingsExtract(pixels=(2, 3))
)
assert (array_2d_list[1] == np.array([[10.0], [10.0], [10.0]])).all()
```

`serial_array` (test_autocti/conftest.py) is 3x10 — columns 0-9, values 0-9. For
region `(0, 3, 5, 8)`, `serial_trailing_region_from(pixels=(2, 3))` returns
`(0, 3, 10, 11)`: a window entirely past the right edge. The slice was `(3, 0)`,
and `(empty == [[10.0], ...]).all()` is vacuously `True` on an empty comparison.
The tell is that `10.0` does not exist anywhere in the fixture. So this
assertion has never checked anything; autoarray now refuses to build the
degenerate structure and raises instead.

**The guard is correct.** Do not weaken or work around it in autoarray.

## The decision this task owns

1. **Fix the test** — use an in-range window for the second region, assert the
   real values, and delete the `== [[10.0], ...]` line; or
2. **Clip in the extractor** — if extracting past the array edge is meant to be
   supported, clip in `serial_trailing_region_from` / `array_2d_list_from` and
   have the test assert the clipped shape explicitly.

(2) is a behaviour decision about what an out-of-range `pixels` window means —
silently empty, clipped, or an error — so it needs a human call, not a guess.
Whichever is chosen, an out-of-range window should stop being silently empty.

## Also check

- The **parallel** EPER/FPR siblings and the other `extract/two_d/` tests for
  the same vacuous `(empty == expected).all()` pattern — an empty-array
  comparison passes for *any* expected value, so a grep for assertions whose
  expected values are outside the fixture's value range is worth one pass.
- Whether any non-test caller can produce a zero-width region the same way.

## Acceptance

- `pytest` green on PyAutoCTI `main` across all three legs (3.12, 3.13, no-jax).
- The replaced assertion checks a real extracted value, or a real clipped shape
  — not an empty comparison.
- The chosen out-of-range semantics are written down in the extractor docstring.
