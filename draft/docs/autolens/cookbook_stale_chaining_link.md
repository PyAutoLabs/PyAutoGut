# PyAutoLens model cookbook: fix stale chaining notebook link

Type: docs
Target: PyAutoLens
Repos:
- PyAutoLens
Difficulty: trivial
Autonomy: autonomous
Priority: low

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
