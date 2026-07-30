# Fix Optional[None] default-value typos in PyAutoLens

Type: bug
Target: autolens
Repos:
- PyAutoLens
Difficulty: small
Autonomy: supervised
Priority: normal
Parent: active/multi_plane_guide_distill_units.md

## Original request (verbatim)

> merge and then fix drift

(User instruction following the multi-plane-guide-units ship report, which
flagged this drift; the group/start_here.ipynb notebook drift is explicitly
EXCLUDED — the user confirmed it will be picked up by the next notebook
generation pass.)

## Context

Three sites in PyAutoLens use the typing construct `Optional[None]` as a
*default value* (it evaluates to `NoneType`, a truthy class object), found by
sweeping all four libraries for siblings of the site flagged in
autolens_workspace#411:

- `autolens/lens/tracer.py:250` — `plane_index_limit: int = Optional[None]`
- `autolens/lens/tracer_util.py:178` — `plane_index_limit: int = Optional[None]`
- `autolens/point/max_separation.py:27` — `plane_redshift: float = Optional[None]`

Consequences today (verified by reading the callees):

- `tracer_util.traced_grid_2d_list_from` guards `if plane_index_limit is not
  None:` — NoneType passes it, so the early-exit block runs on every default
  call and compares `plane_index == NoneType` (always False). Accidentally
  harmless, genuinely wrong.
- `SourceMaxSeparation` feeds the default into
  `tracer.plane_index_via_redshift_from`, where `np.isclose(NoneType, z)`
  raises `TypeError`, caught to fall back to `plane_index = -1`. A real `None`
  raises the same `TypeError`, so the fix preserves behavior exactly.

## Scope

Replace all three with proper annotations and defaults:

- `plane_index_limit: Optional[int] = None` (both tracer sites)
- `plane_redshift: Optional[float] = None` (max_separation)

No behavioral change; no other repos affected (sweep of PyAutoGalaxy,
PyAutoArray, PyAutoFit found zero further sites).

## Acceptance

- `python -m pytest test_autolens/lens/ test_autolens/point/` green.
- Default-call behavior identical (tracer traced grids unchanged; point-source
  max-separation fallback path unchanged).
