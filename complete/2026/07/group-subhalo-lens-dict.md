# group subhalo detect pipeline drops every deflector after lens_0

- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/437
- pr: https://github.com/PyAutoLabs/autolens_workspace/pull/439 (MERGED 2026-07-31)
- repos: autolens_workspace

## What shipped

`scripts/group/features/advanced/subhalo/detect/start_here.py` composed its lens plane correctly only in
`source_lp`, which loops over `main_lens_centres`. All **seven** downstream stages rebuilt it as
`lens_dict = {"lens_0": lens_0}`, dropping every main lens galaxy after the first from `source_pix_1` onward:
`source_pix_1`, `source_pix_2`, `light_lp`, `mass_total`, `subhalo_no_subhalo`, `subhalo_grid_search`,
`subhalo_refine`.

All seven now loop over the prior result's `lens_*` galaxies via a module-level `n_main_from(result)` helper
mirroring the one in `multi_galaxy/slam.py`:

```python
return sum(1 for key in vars(result.instance.galaxies) if key.startswith("lens_"))
```

Each stage keeps its own chaining semantics, applied per deflector: `mass_from(..., unfix_mass_centre=True)` in
`source_pix_1`; fixed instances in `source_pix_2`; a **fresh** `mge_model_from` bulge per galaxy in `light_lp`; a
**fresh** `af.Model(al.mp.PowerLaw)` per galaxy in `mass_total`. `shear` stays on `lens_0` only, matching how
`source_lp` composes it (`if i == 0`). The now-dead `mass = af.Model(al.mp.PowerLaw)` at the top of `mass_total`
was removed (it was reassigned before use).

## Lessons

**The reported scope was half the defect.** The user reported "all three subhalo stages". The collapse in fact
began four stages earlier at `source_pix_1`. Fixing only the subhalo stages would have left the evidence
comparison differencing against a `mass_total` result that had already dropped the other deflectors — a fix that
looks complete and changes nothing. Reading the whole file rather than only the named stages is what caught it.

**The severity claim was wrong, and the wrong dataset caused it.** The issue body asserted the shipped dataset has
2 main lens centres and results are biased today. That came from
`dataset/group/102021990_NEG650312660474055399/main_lens_centres.json` — a **different** group example. This
script loads `dataset/group/dark_matter_subhalo`, whose simulator hard-codes `main_lens_centres = [(0.0, 0.0)]`
(`scripts/group/features/advanced/subhalo/simulator.py:70`). Its other two galaxies are **extra galaxies**, which
the script carries through every stage correctly and which were never dropped. **The defect was latent, not
active** — no committed result was affected. Corrected on the issue before merge
(comment 5143347492) and in the PR body + commit message.

Generalisable: a group/multi-galaxy script's deflector count comes from **its own** dataset's
`main_lens_centres.json`, and sibling datasets in `dataset/group/` differ. Read the `dataset_name` the script
actually sets before making any claim about how many deflectors are in play. "Extra galaxies" are a separate
model collection from "main lens galaxies" and are chained independently — a script can be correct about one and
broken about the other.

**Forcing the centres in the probe beat editing the dataset.** First attempt at a 2-deflector test hand-edited
`main_lens_centres.json`; the run silently reverted it to 1 centre (the auto-simulation rewrites the centres
JSON). Overriding `main_lens_centres` inside the throwaway probe copy, immediately after the `al.from_json` line,
was the reliable lever — it tests model composition, which is all the fix changes.

## Verification method (reusable)

Injected `print("PROBE_STAGE_n_KEYS", list(lens_dict.keys()))` before every `model = af.Collection(` into a
throwaway `_probe_tmp.py` copy, with `main_lens_centres` forced to 2 entries. Built the control from
`git show main:<path>` so the comparison was against unmodified `main`, not a remembered shape:

| stage | before | after |
|-------|--------|-------|
| 1 `source_lp` | `['lens_0','lens_1']` | `['lens_0','lens_1']` |
| 2-6 | `['lens_0']` | `['lens_0','lens_1']` |
| 7-8 (+subhalo) | `['lens_0','subhalo']` | `['lens_0','lens_1','subhalo']` |

Script ran end-to-end under `PYAUTO_TEST_MODE=2` (exit 0) on both the shipped 1-centre dataset and with 2 centres
forced. Probe files deleted before commit; `check_sizes.sh` clean.

## Follow-up

Filed in `ideas.md`: check `multi_galaxy/features/advanced/subhalo/detect/start_here.py` for the same collapse.
The `imaging/` and `interferometer/` variants are single-deflector by construction and are not at risk.

## Original prompt

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
