# multi_galaxy pixelization source-pixel over-count + missing auto-sim headers

- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/438
- pr: https://github.com/PyAutoLabs/autolens_workspace/pull/440 (MERGED 2026-07-31)
- repos: autolens_workspace

## What shipped

**1 — source-pixel count was off by 2.** `scripts/multi_galaxy/features/pixelization/fit.py` printed
`fit.inversion.reconstruction.shape[0]` as "Number of source pixels reconstructed". That vector spans **every
linear object the inversion solves**, not just the mapper. Both deflectors in that script use
`al.lp_linear.Sersic` bulges, whose intensities are solved by the same linear algebra as the source pixels — so
for a `(30, 30)` mesh it read **902**. Now:

```python
mapper = fit.inversion.cls_list_from(cls=al.Mapper)[0]
print(f"... = {fit.inversion.reconstruction_dict[mapper].shape[0]}")
```

The `__Inversion__` prose now explains the distinction rather than silently correcting it, and notes that the
galaxy-scale walkthrough (`imaging/features/pixelization/fit.py`) cannot show it — its source is the only linear
object there.

**2 — five `slam.py` files missed the auto-sim header.** `extra_galaxies`, `linear_light_profiles`,
`multi_gaussian_expansion`, `no_lens_light` and `scaling_relation` ran the auto-simulation block without the
`__Dataset Auto-Simulation__` section, so their notebooks showed a bare `subprocess.run` cell. **The code was
already present and correct in all five — prose only, no behaviour change.** All eight
`multi_galaxy/features/**/slam.py` now carry the header.

## Lessons

**`inversion.reconstruction` is not the source reconstruction when linear light profiles are in the model.** It is
the full solution vector across all linear objects. `len(reconstruction)` is only a valid source-pixel count when
the mapper is the sole linear object. `cls_list_from(cls=al.Mapper)[0]` + `reconstruction_dict[mapper]` is the
correct read, and is already the established idiom in the sibling scripts.

**`lp_linear` in the script is the tell.** Of the four `multi_galaxy/features/pixelization/*.py` scripts, only
`fit.py` uses `lp_linear` — `grep -c lp_linear` returned 2/0/0/0. `delaunay.py`, `plot.py` and
`source_science.py` read `len(reconstruction)` and are **correct as written**, because they have no linear light
profiles. A blanket sweep replacing that idiom everywhere would have been wrong. Check for `lp_linear` (or any
linear object) before flagging a `reconstruction` length read.

**Control-tested the arithmetic rather than reasoning about it.** Ran the unmodified script on `main` (902) and
the fixed one (900) — the 2-pixel delta is exactly the two `lp_linear` bulges, confirmed empirically, not
inferred. Note the two runs reported different log likelihoods (11591 vs 11564): the worktree had no dataset, so
auto-simulation generated a fresh noise realisation there. That is expected for a gitignored dataset and does not
affect the pixel count.

**"Missing section" can mean missing prose, not missing code.** The reported gap read as functionality; the
`should_simulate` block was present and correct in all five files. Checked before planning the fix, which turned
a behaviour change into a header insert.

## Verification

- `features/pixelization/fit.py` prints `900`, down from `902` on unmodified `main`.
- `grep -c '__Dataset Auto-Simulation__'` returns `1` for all eight `multi_galaxy/features/**/slam.py`.
- `check_sizes.sh` clean; notebooks regenerated via PyAutoHands `generate.py autolens`.

## Original prompt

# multi_galaxy: pixelization fit over-counts source pixels; 5 slam.py miss the auto-sim header

Type: bug
Target: autolens_workspace
Repos:
- @autolens_workspace
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

## Original request (verbatim)

> `features/pixelization/fit.py` over-counts its source pixels by 2, and
> `__Dataset Auto-Simulation__` is still missing on the five pre-2c
> `multi_galaxy/features/*/slam.py` files.

## Problem 1 — source-pixel count is off by 2

`scripts/multi_galaxy/features/pixelization/fit.py:203`:

```python
print(f"Number of source pixels reconstructed = {fit.inversion.reconstruction.shape[0]}")
```

`inversion.reconstruction` is the solution vector over **all** linear objects in the
inversion, not just the mapper. This script's two deflectors use
`al.lp_linear.Sersic` bulges (lines 147, 162), so the inversion solves 2 linear light
profile intensities alongside the 900 (`mesh_shape = (30, 30)`) source pixels. The line
therefore prints **902**, labelled as a source-pixel count.

This is the only one of the four `multi_galaxy/features/pixelization/*.py` scripts that
uses `lp_linear` — `delaunay.py`, `plot.py` and `source_science.py` have no linear light
profiles, so their `len(reconstruction)` reads are correct as written. Those siblings
already extract the mapper explicitly:

```python
mapper = inversion.cls_list_from(cls=al.Mapper)[0]   # delaunay.py:252, plot.py:206, source_science.py:194
```

**Fix:** take the mapper's own reconstruction, e.g.

```python
mapper = fit.inversion.cls_list_from(cls=al.Mapper)[0]
print(f"Number of source pixels reconstructed = {fit.inversion.reconstruction_dict[mapper].shape[0]}")
```

and add a sentence to the `__Inversion__` prose explaining that the full `reconstruction`
vector also carries the linear light profile intensities — this is a teachable distinction
that the galaxy-scale walkthrough does not surface, because it has no linear light
profiles.

## Problem 2 — missing `__Dataset Auto-Simulation__` header on five slam.py

Five of the eight `scripts/multi_galaxy/features/**/slam.py` files run the auto-simulation
block but never introduce it with the standard `__Dataset Auto-Simulation__` section, so
the generated notebooks show a bare `subprocess.run` cell with no explanation:

| file | `should_simulate` line | header present? |
|------|------------------------|-----------------|
| `extra_galaxies/slam.py` | 531 | ✗ |
| `linear_light_profiles/slam.py` | 460 | ✗ |
| `multi_gaussian_expansion/slam.py` | 446 | ✗ |
| `no_lens_light/slam.py` | 389 | ✗ |
| `scaling_relation/slam.py` | 810 | ✗ |
| `pixelization/slam.py` | 488 | ✓ (line 480) |
| `advanced/double_source_plane_lens/slam.py` | — | ✓ |
| `advanced/mass_stellar_dark/slam.py` | — | ✓ |

The **code** is already present and correct in all five; only the prose header is missing.
This is a header-insert, not a behaviour change.

**Fix:** insert the canonical block immediately before each `if al.util.dataset.should_simulate(...)`,
matching `multi_galaxy/features/pixelization/fit.py:44–49`:

```
"""
__Dataset Auto-Simulation__

If the dataset does not already exist on your system, it will be created by running the corresponding
simulator script.
"""
```

Split the existing `__Dataset__` docstring so `dataset_name` / `dataset_path` stay under
`__Dataset__` and the `should_simulate` call sits under the new header — the shape used by
`pixelization/slam.py` and `pixelization/fit.py`.

## Verification

- `grep -c '__Dataset Auto-Simulation__'` returns 1 for all eight `multi_galaxy/features/**/slam.py`.
- Run `scripts/multi_galaxy/features/pixelization/fit.py` and confirm the printed count is
  900, not 902.
- `scripts/check_sizes.sh` clean (prose inserts only grow files).
- Regenerate notebooks.
