`convert_pixel_scales_1d` and `convert_pixel_scales_2d` tested
`type(pixel_scales) is float` — an exact-type check — so only a literal Python
`float` was widened to the tuple form both functions promise. `int`,
`np.floating` and `np.integer` fell through unconverted.

**Shipped:** PyAutoArray#465, merge-commit `a6b07cd` 2026-08-22. Issue #464
auto-closed. The follow-up #440 pointed at; pre-existing, not a regression.

- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/464
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/465 (merged `a6b07cd`)

## Delivered

The two converters are the single chokepoint for **16 call sites** — every
`Mask2D` factory, `Grid2D.uniform`, and the `Array2D`/`Array1D`/`Grid1D`/
`VectorYX2D` constructors — so one predicate change covered the whole public
surface. Test any concrete real scalar via `validate.is_concrete_scalar` (the
predicate #440 landed), and cast to Python `float`. 1D and 2D changed together
so they cannot drift.

| Change | Site |
|---|---|
| `type(x) is float` → `validate.is_concrete_scalar(x)`, value cast to `float` | `geometry_util.convert_pixel_scales_{1d,2d}` |
| Docstrings corrected — they said "float" where they meant "any real scalar" | same |
| `PixelScales` alias widened to `int`, `np.floating`, `np.integer` | `autoarray/type.py` |

177 insertions / 16 deletions across 4 files.

## The prompt's repro was stale — and the truth was worse

The prompt (written against `f2f7a4f`) said
`Array2D.no_mask(values=np.ones((5,5)), pixel_scales=1)` raises
`TypeError: 'int' object is not subscriptable`. On `b808a9b` **it did not raise**
— it constructed fine and stored the bare `1` on the mask. The `TypeError`
surfaced one call later, on `.pixel_scale`, `.derive_grid`, or anything touching
geometry. `Grid2D.uniform` and `Mask2D.circular` still raised outright.

So the real failure mode was **silent bad state written into a mask**, not a loud
error at the construction site — strictly worse than filed. The regression test
pins the post-construction values rather than the stale `pytest.raises` framing.
**Lesson: re-run a prompt's repro before trusting its error text; a prompt
written weeks ago describes the code of weeks ago.**

## Verified, not assumed

- **New tests were confirmed able to fail.** Stashing only `geometry_util.py` +
  `type.py` (leaving the tests) produced 12 failures across the new cases; 0 with
  the fix. A test that cannot fail proves nothing.
- **The `float` cast is asserted on `type()`, not `==`.** `1 == 1.0` in Python,
  so an equality assertion would have passed vacuously against the very bug the
  cast exists to prevent.
- **Pre-existing failures baselined, not assumed.** The 3 `test_transformer.py`
  pynufft failures were re-run with the whole change stashed — identical 3.

## Decisions pinned

- **Cast to Python `float`** (`1` → `(1.0, 1.0)`, not `(1, 1)`). Matches the
  existing `Tuple[float, ...]` annotation, keeps NumPy scalars out of stored
  geometry and out of JSON serialisation (cf.
  `complete/2026/08/save-json-numpy-scalar-typeerror.md`), and avoids int
  arithmetic and numba signature variants downstream. The prompt asked for this
  to be decided and pinned; it is now pinned by a test.
- **`bool` stays excluded.** `is_concrete_scalar` rejects it deliberately (#440's
  reasoning), so `pixel_scales=True` is still not widened — pinned by a test so
  it reads as intent, not accident.

## Validation

- Full suite **1145 passed / 1 skipped**, **+27 new tests** across
  `test_geometry_util.py` and `test_validate.py`.
- CI green on all three legs: `unittest (3.12)`, `unittest (3.13)`, and
  `unittest-nojax` — the nojax leg matters here because the change touches the
  tracer path.
- **Zero regressions.**

## What the planning got wrong (again)

- **The Bug Agent returned `too-large` (score 10) with a "too large for one PR"
  risk — for the second time on this exact family of change.**
  `complete/2026/08/autoarray-input-validation-guards.md` already recorded this
  same false positive and its cause: the heuristic keys off *prompt length*, and
  these prompts are long because they carry evidence, not because the diff is
  large. That record's warning was read and the score overridden to `small`; the
  diff came in at 177/16. **Two recorded instances now — this is a sizing-faculty
  defect, not bad luck. Worth a prompt against the faculty rather than a third
  manual override.**
- Confidence was reported `low` on a bug with a verbatim reproduction in hand.

## Environment notes (web-github session)

- The session's default Python was **3.11**, below the repo's `requires-python
  >=3.12`, so `pip install -e ".[dev]"` failed on `autonerves>=2026.7.29.2`.
  Fixed with a 3.13 venv (`uv venv --python 3.13`). Any future web session on
  this repo will hit the same wall.
- No PyAutoHeart in scope and no `pyauto-heart` on PATH, so the readiness gate
  fell back to the WORKFLOW.md substitute (the local suite). **Heart never
  returned a verdict on this change** — CI green is what actually backs it.
- `black` wanted to reformat 47 pre-existing files repo-wide; only the two test
  files touched here were formatted. Formatting is advisory and ungated.

## Follow-ups filed

- `draft/bug/autoarray/convert_shape_native_int_not_widened_to_tuple.md` —
  `convert_shape_native_1d` carries the **identical** `type(x) is int` check one
  function away in the same file, so `np.int64(5)` is never widened. Not a
  copy-paste of this fix: the cast is to `int`, and `is_concrete_scalar` would
  newly admit `5.0` for silent truncation, which needs deciding.
- `draft/bug/autoarray/pixel_scales_tuple_entries_not_normalised.md` — an
  asymmetry **this PR introduced**: the scalar form now guarantees
  `Tuple[float, ...]` while the tuple form still returns `(1, 1)` unnormalised.
  Low priority, but the FITS-header case that motivated this fix produces exactly
  the anisotropic tuples that path serves.

## Original prompt

# `pixel_scales` given as an `int` (or `np.float64`) is never widened to a tuple

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: medium
Status: issued 2026-08-22 as PyAutoArray#464

## Why this exists

Found while implementing PyAutoArray#333 (the `_validate_*` constructor guards,
shipped 2026-08-09 as PyAutoArray#440 / `f2f7a4f`). Noted in that PR's "Out of
scope" section and in `complete/2026/08/autoarray-input-validation-guards.md`;
this prompt is the follow-up it points at. **Pre-existing — not introduced by
that PR.**

## The defect

`autoarray/geometry/geometry_util.py`:

```python
def convert_pixel_scales_2d(pixel_scales):
    if type(pixel_scales) is float:          # <-- exact-type check
        pixel_scales = (pixel_scales, pixel_scales)
    return pixel_scales
```

`type(x) is float` is an exact-type test, so only a literal Python `float`
is widened. Everything else falls through **unconverted**, and the caller then
subscripts a scalar.

Verified against `main` @ `f2f7a4f` (2026-08-09):

```
convert_pixel_scales_2d(1)              ->  1              # not (1.0, 1.0)
convert_pixel_scales_2d(1.0)            ->  (1.0, 1.0)     # OK
convert_pixel_scales_2d(np.float64(1))  ->  np.float64(1)  # not widened
convert_pixel_scales_1d(1)              ->  1              # same bug, 1D sibling

Array2D.no_mask(values=np.ones((5,5)), pixel_scales=1)
    ->  TypeError: 'int' object is not subscriptable
```

`np.float64` matters as much as `int` here: it is what you get from indexing a
numpy array or reading a FITS header, so `pixel_scales=header["CD2_2"]` can hit
this on a path that looks perfectly reasonable.

## Why it is worth fixing

The docstring promises the widening — *"If this is input as a `float`, it is
converted to a `(float, float)` structure"* — and every `Mask2D` factory and
`Grid2D.uniform` funnel through this function, so the promise is repeated across
the public API. An `int` pixel scale is a natural thing for a user to type.

The resulting `TypeError: 'int' object is not subscriptable` names nothing the
caller passed — exactly the class of failure the #333 sweep was about, which is
why it is filed rather than fixed inline there (that task was scoped to the five
findings on #333).

## Suggested fix

Widen the test to any concrete real scalar rather than the exact `float` type.
`autoarray/validate.py` (landed by #440) already has the predicate this needs:

```python
from autoarray import validate

if validate.is_concrete_scalar(pixel_scales):
    pixel_scales = (pixel_scales, pixel_scales)
```

`is_concrete_scalar` accepts `int`, `float`, `np.integer`, `np.floating` and
rejects `bool`, arrays, `None` and JAX tracers — so this both fixes the bug and
keeps the function tracer-safe. Apply to `convert_pixel_scales_1d` (1-tuple) and
`convert_pixel_scales_2d` (2-tuple) together so the two do not drift.

**Check before assuming this is purely additive:** something downstream may rely
on a non-float passing through unconverted. Run the full `test_autoarray` suite
and read any failure rather than adjusting the test.

## Verification

- `Array2D.no_mask(values=..., pixel_scales=1)` builds, with
  `pixel_scales == (1.0, 1.0)`.
- Same for `np.float64(1.0)` and `np.int32(1)`.
- Tuple input is returned unchanged; a JAX tracer still passes through untouched.
- The #440 validation guards still fire on `0`, `-1` and `nan` in **both** the
  scalar and tuple forms.
- Decide and pin whether the widened value is cast to `float` or kept in its
  input type — `(1, 1)` vs `(1.0, 1.0)` — since downstream arithmetic differs.

Repro environment: `PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`,
`NUMBA_CACHE_DIR=/tmp/numba_cache`, `MPLCONFIGDIR=/tmp/matplotlib`,
`PYAUTO_DISABLE_JAX=1`.

## Provenance

- Found during: `complete/2026/08/autoarray-input-validation-guards.md`
- Sibling of, but NOT part of, the @rhayes777 audit campaign (`planned.md` §
  `rhayes-audit-validation-phases-2-4`) — this was not one of his 16 findings.
