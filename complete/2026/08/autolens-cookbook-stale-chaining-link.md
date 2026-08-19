## autolens-cookbook-stale-chaining-link
- completed: 2026-08-19
- summary: Fixed the stale "Model Linking (Advanced)" chaining notebook link in PyAutoLens docs/general/model_cookbook.md (imaging/advanced/chaining/start_here.ipynb → guides/modeling/chaining.ipynb). PyAutoLens#701 merged 2026-08-19; docs CI green; all nine autolens_workspace links in the cookbook verified to resolve on main and no other docs/ file references the dead path.

## Lifecycle note

Filed 2026-08-18 during the three-regime restructure close-out link sweep
(complete/2026/07/autolens-docs-three-regime-restructure.md, PyAutoMind#238);
shipped the next day straight from draft/ as a trivial autonomous fix, so the
prompt never advanced to active/ — retired here dated by ship day.

## Original prompt (cookbook_stale_chaining_link)

# PyAutoLens model cookbook: fix stale chaining notebook link

Type: docs
Target: PyAutoLens
Repos:
- PyAutoLens
Difficulty: trivial
Autonomy: autonomous
Priority: low
Status: shipped 2026-08-19 (PyAutoLens#701 merged)

Found during the three-regime restructure close-out link sweep (2026-08-18):
the pre-existing "Model Linking (Advanced)" section of
`docs/general/model_cookbook.md` links to

`https://github.com/PyAutoLabs/autolens_workspace/blob/main/notebooks/imaging/advanced/chaining/start_here.ipynb`

which 404s — the chaining content moved in the workspace reorganisation. The
correct current path is

`https://github.com/PyAutoLabs/autolens_workspace/blob/main/notebooks/guides/modeling/chaining.ipynb`

(verified to resolve on `main`, 2026-08-18).

## Changes

- `docs/general/model_cookbook.md` (Model Linking section, one line): replace
  the dead `imaging/advanced/chaining/start_here.ipynb` link with
  `guides/modeling/chaining.ipynb`.
- While there, `grep` the docs for any other `notebooks/.../advanced/chaining`
  or otherwise-404ing workspace links and fix in the same pass (all nine links
  in the regime cookbook sections were verified good on 2026-08-18).

## Acceptance

- Every autolens_workspace notebook link in `model_cookbook.md` resolves on
  `main`; docs CI stays green.
