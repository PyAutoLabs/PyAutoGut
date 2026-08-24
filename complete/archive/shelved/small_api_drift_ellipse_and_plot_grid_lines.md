# HowToGalaxy small API drifts: ellipse kwargs + plot_grid_lines — RESOLVED (born stale) 2026-08-24

Status: RESOLVED — nothing actionable. Both call-sites were already fixed on `autogalaxy_workspace`
`main` **before this prompt was filed**, and the prompt's target repo was wrong. Retired to
`complete/archive/shelved/` without an issue, branch or worktree.

## Verification on clean main (2026-08-24)

| Item | State |
|------|-------|
| `guides/advanced/over_sampling` — `plot_grid() got an unexpected kwarg 'plot_grid_lines'` | **Fixed 2026-04-26**, autogalaxy_workspace `29b77e4` (#38): "Remove plot_grid_lines kwarg (4 sites) from scripts/guides/advanced/over_sampling.py to match current `aplt.plot_grid()` signature." The NEEDS_FIX entry was dropped in the same commit. No `plot_grid_lines` occurrence remains anywhere in the repo. |
| `ellipse/modeling` — `KeyError on 'ellipses.0.centre_0'` | The 2026-04-10 marker was superseded on 2026-04-24 by the blanket ellipse JAX-refactor park, then **un-parked 2026-05-15** in `0d6c22f` (#73) once PyAutoGalaxy #408/#410/#412 merged — all five `scripts/ellipse/*` examples verified passing under `PYAUTO_TEST_MODE=2`. |

`autogalaxy_workspace/config/build/no_run.yaml` on current `main` carries **no** NEEDS_FIX entries at
all (only the `imaging/features/shapelets/modeling` SLOW-skip), so there are no markers left to
remove. Both scripts are actively maintained (last touched 2026-07-30 / 2026-07-31), so they are not
quietly rotting behind a skip.

## The target repo was wrong

The prompt named `HowToGalaxy`. Neither call-site has ever lived there: HowToGalaxy holds only
`scripts/chapter_*/` and `scripts/simulators/` — no `ellipse/` tree, no `guides/` tree — and its
`config/build/no_run.yaml` now has **zero** entries (the dead copy-pasted workspace paths were purged;
see `complete/2026/07/no-run-config-purge.md`). This is the exact copy-paste artefact diagnosed in
`complete/2026/07/ell-comps-kwargs-keyerror.md` ("Two traps this task hit").

## Why it was filed anyway

It was written up from the **Follow-up** section of `complete/2026/07/ell-comps-kwargs-keyerror.md`,
which flagged these two siblings as "plausibly stale for the same reason". That follow-up was authored
in parallel with the 2026-07-21 umbrella triage, which had **already** reproduced both on clean `main`
and recorded them as stale — see `complete/archive/shelved/api_drift_callsite_fixes.md`:

> ~~**ellipse kwargs KeyError** `'ellipses.0.centre_0'`~~ — STALE. `autogalaxy_workspace/scripts/ellipse/modeling.py` (path was "HowToGalaxy" — wrong) runs exit 0, ellipse results print fine.
> ~~**plotter kwarg drift** `plot_grid_lines`~~ — STALE. `autogalaxy_workspace/scripts/guides/advanced/over_sampling.py` (path was "HowToGalaxy" — wrong) runs exit 0; the `plot_grid_lines` kwarg no longer exists in the script.

So the prompt was a duplicate of an already-closed triage line, born stale on 2026-07-22.

## Lesson (reinforces the ell-comps record)

A "Follow-up" bullet that merely *suspects* staleness must be reproduced against the target repo's
`main` **before** it is promoted to its own prompt — and against the repo the call-site actually lives
in, not the one the stale marker names. Intake inherited both the wrong repo and the wrong status here.

## Original prompt

# HowToGalaxy small API drifts: ellipse kwargs + plot_grid_lines (parked NEEDS_FIX)

Type: bug
Target: howtogalaxy
Repos:
- HowToGalaxy
- PyAutoGalaxy
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-07-22 (backfilled from git)

Two independent, small stale-API call-sites in HowToGalaxy, both parked since 2026-04-10 and still
parked after the 2026-07-21 census:
- `ellipse/modeling` — `KeyError on 'ellipses.0.centre_0'` kwargs after API drift in ellipse modeling.
- `guides/advanced/over_sampling` — `plot_grid() got an unexpected kwarg 'plot_grid_lines'` after a
  plotter API change (find the current plotter kwarg name and update the call).

Reproduce each on clean main, update the call-sites (or the library if the drift was unintended),
remove both NEEDS_FIX markers from HowToGalaxy/config/build/no_run.yaml, regenerate notebooks.
Only edit scripts/, never notebooks/.
