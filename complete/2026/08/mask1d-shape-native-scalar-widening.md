Two sites the PyAutoArray#464 `pixel_scales` scalar-widening sweep did not reach, both
reproduced on `main` before being touched, both fixed together so the 1D and 2D siblings
cannot drift apart again.

**Shipped:** PyAutoArray#485, merge commit `9e475052`, 2026-08-23. Issue #484 closed.

## The two sites

| Site | Symptom on `main` | Fix |
|---|---|---|
| `Mask1D.__init__` (`mask_1d.py:71`) | `pixel_scales=1` stored the bare `1`; `.geometry.scaled_maxima` → `TypeError: 'int' object is not subscriptable` | route through `geometry_util.convert_pixel_scales_1d`, the call `Mask2D.__init__` already made |
| `convert_shape_native_1d` (`geometry_util.py:27`) | `Array1D.full(shape_native=np.int32(5))` → `IndexError: invalid index to scalar variable` | test `validate.is_concrete_integer`, cast to a Python `int` |

Site 1 was #464's *exact reported symptom*, still live on a public constructor after that
PR shipped, because `Mask1D` hand-rolled its own `type(x) is float` check rather than
calling the chokepoint. `Mask2D` already routed through `convert_pixel_scales_2d`, and
`Grid1D.uniform` reaches it too — so this was a 1D/2D divergence, not a design choice.

## The decision this task owned

**A second predicate, not a reuse of `is_concrete_scalar`.** `shape_native` counts pixels
rather than measuring them, so accepting a `float` there would silently widen a mistake
worth surfacing. `validate.is_concrete_integer` is therefore integer-only (`int`,
`np.integer`), inheriting the `bool` exclusion and tracer-safety of its sibling. Reusing
`is_concrete_scalar` would have been the smaller diff and the wrong contract.

**A deliberate contract change on `Mask1D`.** Routing through the chokepoint brings
`validate.validate_pixel_scales` with it, so `Mask1D` now rejects `0`, negative and `nan`
pixel scales — which `Mask2D` already did. Stated in the PR rather than suppressed; no test
constructed a `Mask1D` that way and all 12 library call sites pass real scales, so nothing
was adjusted to suit it.

## Verified, not assumed

- **Both defects reproduced first**, on `main`, before any edit — the prompt's own fix had
  already shipped, so the filed work was re-derived from a live repro rather than trusted.
- **The originating prompt was already complete.** Its fix shipped as #464 / `8298d74e` on
  2026-08-22 while the prompt sat in `draft/` unrecorded. Backfilled to
  `complete/2026/08/autoarray-pixel-scales-scalar-widening.md` rather than re-filed.
- **`test_autoarray`: 1201 passed / 0 failed.** The 3 pynufft failures `8298d74e` baselined
  no longer occur, so there was nothing to baseline against.
- **A `git stash` that proved nothing.** The first attempt to show the one `test_autocti`
  failure was pre-existing stashed an already-committed tree — a silent no-op, so the run
  was *with* the change. Redone by pointing `PYTHONPATH` at the canonical `main` checkout,
  where `test_serial_eper.py::test__region_list_from__array_2d_list_from` fails identically.
- **Real-JAX, not a stand-in.** `jax.jit` compiled and ran with a traced `pixel_scales`
  passing through untouched, on top of the tracer-stand-in unit tests.
- **Blast radius measured, not assumed.** PyAutoGalaxy and PyAutoLens only re-export
  `Mask1D` and construct none. `autocti_workspace` uses `ac.Mask1D`, which subclasses
  `aa.Mask1D` and *inherits* the fix — its full suite (270 passed / 1 pre-existing) and the
  dataset_1d simulator + modeling smoke both pass.

## The test bug found on the way

#464's own widening tests asserted value only. `np.float64(1.0) == (1.0,)` NumPy-broadcasts
to `array([True])`, which is truthy — so **four of six parametrisations passed on an
unwidened NumPy scalar and tested nothing**. The tests written for this task hit the same
trap first and were caught by the fail-without-the-fix check; #464's were then tightened the
same way, proven by reverting to the pre-#464 source and watching them fail. A widening test
must assert tuple-ness *before* value.

## Merged under a human override

`pyauto-heart readiness` was red at both ship and merge time on `release validation FAILED`
— an incomplete report (`failures: []`, 262 passed / 0 failed, only the `integrate` stage,
pre-dating the task, against an older sha). Unrelated to this change and not repaired by it,
so the `AUTONOMY.md` corrective-PR exception did not apply; both the PR-open and the merge
were explicit human overrides. The other reason, `PyAutoFit: 2 commit(s) behind origin`, was
cleared by a fast-forward pull.

## Left open

- **Tuple entries returned unnormalised** — `convert_pixel_scales_2d((1, 1))` → `(1, 1)`,
  contradicting the `Tuple[float, float]` annotation. Deliberately unfixed and unfiled: it
  alters return values on paths that work today.
- **`release validation FAILED`** still red — a Heart-side artifact question
  (`validate --ingest` replacing rather than merging stages), not a library defect.
- **API-gate false positive** — the gate blocked `autocti_workspace`'s
  `scripts/dataset_1d/modeling/start_here.py` on `aplt.subplot_dataset_1d`, which the script
  then used successfully at runtime once bypassed.

## Original prompt

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
