# @rhayes777's 2026-05-23 API audit — all 15 findings re-verified, still reproduce

Type: bug
Target: autoarray
Repos:
- @PyAutoArray
- @PyAutoGalaxy
- @PyAutoLens
Difficulty: medium
Autonomy: supervised
Priority: high
Status: draft

## Why this exists

Richard Hayes (@rhayes777 — a **PyAutoFit author**, not an outside user) filed five
detailed issues on 2026-05-23 while auditing released `2026.5.21.1` against the
documented public API. Each carries reproducible snippets and environment info.

**They sat for 66 days with zero comments on any of them.** Surfaced by the
2026-07-27 `/wake_up` community scan.

On 2026-07-27 every claim was **re-run against current `main` (`2026.7.23.1`)**.
**All 15 still reproduce** — nothing has been fixed by two months of intervening
work. Evidence below so this does not need re-deriving.

## The five issues

| Issue | Claims | Verified |
|---|---|---|
| [PyAutoArray#332](https://github.com/PyAutoLabs/PyAutoArray/issues/332) | Delaunay + KNNBarycentric crash in `FitImaging`; `ConstantSplit` broken on `RectangularUniform` | 3/3 reproduce |
| [PyAutoArray#333](https://github.com/PyAutoLabs/PyAutoArray/issues/333) | B6, B7, B8, B5, B13 — input validation | 5/5 reproduce |
| [PyAutoGalaxy#440](https://github.com/PyAutoLabs/PyAutoGalaxy/issues/440) | B9, B10, B11, B12 — profile validation | 4/4 reproduce |
| [PyAutoLens#531](https://github.com/PyAutoLabs/PyAutoLens/issues/531) | `PointSolver.solve` AxisError + IndexError | 2/2 reproduce |
| [PyAutoLens#532](https://github.com/PyAutoLabs/PyAutoLens/issues/532) | B4 + Bonus — `Tracer` validation | 2/2 reproduce |

## Verification output (2026-07-27, autolens/autoarray 2026.7.23.1)

```
[REPRO] B6    Array2D pixel_scales   0.0 accepted; -0.1 accepted; nan accepted
[REPRO] B7    Mask2D.circular_annular(inner=0.8, outer=0.3)   pixels_in_mask = 0
[REPRO] B8    Grid2D.uniform((0,0)) and ((0,5))               shape_slim = 0
[REPRO] B5    Imaging(data 10x10, noise_map 5x5)              built, shape_native (10,10)
[REPRO] B13   reg.Constant(coefficient=-1.0)                  accepted
[REPRO] B9    NFW(scale_radius=0.0)                           NaN count 3200 of 3200
[REPRO] B10   Isothermal(ell_comps=(0,0)) vs IsothermalSph    max|diff| = 2.357e-06
[REPRO] B11   Sersic(sersic_index=0.0)                        ZeroDivisionError
[REPRO] B12   Sersic(ell_comps=(2.0,0.0))                     finite image, sum 1296
[REPRO] B4    Tracer(galaxies="not a list")                   silently constructed
[REPRO] Bonus z_lens=1.0 > z_source=0.5  image sum 64.97;  redshift=-0.5 accepted
[REPRO] 531-1 source outside caustic, precision 0.001         numpy AxisError
[REPRO] 531-2 source inside caustic, precision 0.1            IndexError
[REPRO] 332-1 Delaunay(pixels=100) + Constant       AttributeError: 'NoneType' has no 'array'
                 autoarray/inversion/mesh/border_relocator.py:450
[REPRO] 332-2 KNNBarycentric(pixels=100) + Constant             same site
[REPRO] 332-3 RectangularUniform + ConstantSplit    AttributeError:
                 'InterpolatorRectangularUniform' has no '_mappings_sizes_weights_split'
                 autoarray/inversion/regularization/constant_split.py:67
[OK]    ctl   RectangularUniform + Constant                   log_evidence = 4779.4288
```

The control passing is load-bearing: it confirms #332 is specific to the adaptive
meshes and the `Split` regularization variant, not to inversions generally.

## The work splits in two

**1. Two real crashes (higher priority)** — #332 and #531. These make documented
public features unusable in a released wheel.

Why #332 survived CI: our pixelization smoke coverage
(`autolens_workspace/scripts/imaging/features/pixelization/delaunay.py`) builds
its Delaunay through a configured image-mesh path with a different dataset/mask
setup, so it never exercises the bare `al.mesh.Delaunay(pixels=N)` construction
the report uses. **Any fix must land with a regression test built the reporter's
way, not the examples' way** — otherwise the gap survives the fix.

**2. One coherent validation piece** — #333 + #440 + #532. All are "raise a clear
`ValueError` at construction instead of a confusing NumPy/numba traceback three
calls later". The reporter's suggested `_validate_*` helper spans all three repos,
so decide **where the shared helper lives (PyAutoArray or lower) before writing
it**, or the three repos get inconsistent messages.

Open design question inside #532: `z_lens > z_source` should probably **warn**
rather than raise (multi-plane genuinely supports many geometries), while a
negative redshift can raise. Not yet decided by a human.

## State as of 2026-07-27

- Five replies were **drafted and shown to the human, who chose NOT to post yet**.
  Nothing has been sent; all five issues still show zero comments. Re-draft rather
  than assume the old text is still wanted.
- **@rhayes777 offered to PR the validation set** ("Happy to PR if useful"). Do not
  pre-empt that offer by silently implementing it — agree the helper shape with him
  first. This is the main reason the work was not routed into `start_dev_for_user`.

## Verification recipe

Re-run any claim straight from the issue bodies; they are self-contained. Two
gotchas found while doing so:

- The PSF constructor is `al.Convolver.from_gaussian` (**not** `al.Kernel2D` — the
  PyAuto API gate correctly rejects that).
- Run from a workspace root with `PYAUTO_SKIP_WORKSPACE_VERSION_CHECK=1`,
  `NUMBA_CACHE_DIR=/tmp/numba_cache`, `MPLCONFIGDIR=/tmp/matplotlib`.
