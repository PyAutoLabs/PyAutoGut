# group subhalo detect pipeline drops every deflector after lens_0

Type: bug
Target: autolens_workspace
Repos:
- @autolens_workspace
Difficulty: small
Autonomy: safe
Priority: normal
Status: formalised

## Original request (verbatim)

> A real bug in the group package. `group/features/advanced/subhalo/detect/start_here.py`
> uses `lens_dict = {"lens_0": lens_0}` in all three subhalo stages, dropping every
> deflector after the first from the comparison model — exactly the mis-split failure
> that folder's prose warns about. Needs its own issue against group/.

## Problem

`scripts/group/features/advanced/subhalo/detect/start_here.py` composes its lens plane
correctly in the first pipeline only. `source_lp` (line 86–105) builds

```python
lens_dict = {}
for i, centre in enumerate(main_lens_centres):
    ...
    lens_dict[f"lens_{i}"] = lens
```

so every main lens galaxy in `main_lens_centres` enters the model. Every **downstream**
pipeline then hard-codes a single deflector:

| line | function | statement |
|------|----------|-----------|
| 206 | `source_pix_1` | `lens_dict = {"lens_0": lens_0}` |
| 273 | `source_pix_2` | `lens_dict = {"lens_0": lens_0}` |
| 349 | `light_lp` | `lens_dict = {"lens_0": lens_0}` |
| 420 | `mass_total` | `lens_dict = {"lens_0": lens_0}` |
| 470 | `subhalo_no_subhalo` | `lens_dict = {"lens_0": lens_0}` |
| 545 | `subhalo_grid_search` | `lens_dict = {"lens_0": lens_0, "subhalo": subhalo}` |
| 628 | `subhalo_refine` | `{"lens_0": ..., "subhalo": ...}` |

The user reported the three subhalo stages; the collapse in fact starts four stages
earlier, at `source_pix_1`. The subhalo stages are where it does the most damage — the
no-subhalo/grid-search/refine comparison is a Bayesian evidence difference, so an
under-specified lens plane biases every `log_evidence` in the detection grid, not just
one fit.

**This is not a degenerate case for the shipped dataset.** `dataset/group/102021990_.../main_lens_centres.json`
holds **two** centres, so `lens_1` is silently discarded from `source_pix_1` onward. Its
mass is simply absent from the deflection field the subhalo search is differenced against.

The script's own docstring (line 38) states:

> - The lens model includes all main lens galaxies and extra galaxies with their mass profiles.

which the code contradicts. Sibling group scripts do it correctly and say so —
`group/features/advanced/mass_stellar_dark/fit.py:335` ("The `lens_dict` API scales
naturally to any number of main lens galaxies") and
`group/features/advanced/double_source_plane_lens/fit.py:240`.

## Fix

Carry the full lens plane through every pipeline: rebuild `lens_dict` by looping over the
prior result's `galaxies` entries named `lens_*` (rather than naming `lens_0`), applying
the same per-stage chaining (free mass / fixed light / etc.) to each deflector. Keep the
`shear` on `lens_0` only, matching how `source_lp` composes it (`if i == 0`).

The `subhalo` entry stays a separate key in the two subhalo stages.

## Verification

- `main_lens_centres` has 2 entries, so `len(model.galaxies)` must grow by 1 in every
  stage from `source_pix_1` onward; assert the composed model names before/after.
- Smoke-run the script (`PYAUTO_TEST_MODE=2`) and confirm it still composes and runs
  end-to-end.
- Regenerate notebooks.

## Notes

- Check whether `imaging/`, `interferometer/` and `multi_galaxy/` variants of
  `features/advanced/subhalo/detect/start_here.py` share the defect — the imaging and
  interferometer ones are single-deflector by construction, but `multi_galaxy/` is not.
