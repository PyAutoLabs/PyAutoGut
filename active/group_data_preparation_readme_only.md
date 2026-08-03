# Replace `group/data_preparation/start_here` with a README pointing to imaging

Type: bug
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

The workspace smoke run fails on `group/data_preparation/start_here` with a
`FileNotFoundError` for `dataset/group/simple/data.fits` — the script loads a
group dataset it never simulates.

Rather than wiring a simulate step into the script, delete the group data
preparation tutorial entirely and leave the folder as a signpost: a `README.md`
that points readers at `imaging/data_preparation`, which already holds every
tool needed to prepare group-scale CCD imaging. This mirrors the existing
`interferometer/data_preparation` precedent (README-only folder, identical
README under `scripts/` and `notebooks/`), and matches what
`scripts/group/README.md` already claims: "`data_preparation`: See
`imaging/data_preparation` which has all tools for preparing group scale CCD
imaging data."

Scope:

- Delete `scripts/group/data_preparation/start_here.py` and
  `notebooks/group/data_preparation/start_here.ipynb`.
- Add `scripts/group/data_preparation/README.md` and an identical
  `notebooks/group/data_preparation/README.md`.
- Keep `scripts/group/data_preparation/__init__.py` (interferometer keeps one).
- Refresh the generated catalogue (`llms-full.txt`, `workspace_index.json`) via
  PyAutoHands `generate.py`, and refresh `.script_sizes.json` via
  `scripts/check_sizes.sh --update`.
- Confirm no `config/build/*.yaml` entry references the deleted script (none
  found at survey time).

## Original request

> 4 — Missing-dataset failures (claims autolens_workspace + HowToLens — conflict group)
> Four workspace-smoke failures, all FileNotFoundError on a dataset the script
> never simulates:
>   - autolens  notebooks/group/data_preparation/start_here.ipynb
>       -> dataset/group/simple/data.fits For this fix, dont include a group/data_prepatation/start_here.py file but just a README.md pointing to imaging
