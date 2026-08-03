The workspace smoke run failed on `group/data_preparation/start_here` with a
`FileNotFoundError` for `dataset/group/simple/data.fits`. The script loaded a
group dataset it never simulated — `scripts/group/simulator.py` is what writes
that dataset, and the tutorial never invoked it, so the failure reproduced on
any fresh checkout.

Rather than wire a simulate step in, the script was deleted and the folder
reduced to a README pointing at `imaging/data_preparation`. Roughly 190 of its
366 lines duplicated `imaging/data_preparation` verbatim (pixel scale, image,
noise-map, PSF, mask, positions, info), and every tool it linked to already
lived under `imaging/data_preparation/gui/`. This matched the existing
`scripts/interferometer/data_preparation` README-only precedent and what
`scripts/group/README.md` already claimed.

## Shipped

- PR: https://github.com/PyAutoLabs/autolens_workspace/pull/456 (MERGED
  2026-08-03T17:33:02Z as `047af5a0`)
- Issue: https://github.com/PyAutoLabs/autolens_workspace/issues/454 (closed)
- CI: all five checks green — navigator catalogue-staleness, navigator paths +
  banner lint, smoke/changes, smoke 3.12 (9m08s), smoke 3.13 (7m22s)

## Findings worth keeping

- **README-only folders are a supported shape.** `generate.py:169` copies
  `scripts/**/README.md` into `notebooks/`, which is why the interferometer
  pair is byte-identical. Authoring only the `scripts/` side is correct; the
  notebooks copy is generated. `generate.py` does **not** remove a stale
  `.ipynb` when its source script is deleted — that needs an explicit `git rm`.
- **`check_sizes.sh --update` is not a targeted tool.** It rewrites the entire
  `.script_sizes.json` snapshot. Run here it would have swept ~110 unrelated
  files that had drifted on `main` into a doc PR, silently re-baselining them
  and blunting the shrinkage guard for everyone. The single stale entry was
  removed by hand instead. Reserve `--update` for deliberate whole-snapshot
  refreshes, not for a one-file deletion.
- **Stale doc claim corrected.** The deleted script told readers scaling-tier
  centres live in `scaling_galaxies_centres.json`. Every live loader
  (`group/start_here.py:168`, `features/scaling_relation/{fit,modeling,
  likelihood_function}.py`) reads `scaling_galaxies.csv` via
  `al.galaxy_table_from_csv`. The simulator writes both; only the CSV is
  consumed on the modeling path. The new README states the CSV.
- **`notebooks/README.md` carried pre-existing drift.** Regenerating synced an
  "inculding" typo fix and a missing `weak` folder line that had never
  propagated from `scripts/README.md`. Generator output, flagged in both the
  commit message and the PR body rather than passed off as part of the change.
- **The conflict guard's claim was stale.** `worktree_check_conflict` blocked
  on `interferometer-start-here-integrate-oom` holding `autolens_workspace`,
  but that task's workspace PR (#450) had merged 2026-07-31 and only its
  PyAutoHeart release-validation leg remained. Verified by hand (merged PR,
  deleted local branch, clean `main`) and the claim released. Consistent with
  the standing note that the guard is unreliable in both directions — the
  manual scope check is the load-bearing one.

## Heart RED

Heart was RED throughout on two release-pipeline reasons unrelated to this
change: `install verification FAILED (testpypi; checks D)` and `release
validation FAILED (stage integrate)` (the latter already chased by
`nautilus-1core-serial-pool`). The change instead sat under Heart's separate
YELLOW reason, `workspace validation not passing (19 failed, 1 timeout,
cloud#30790463134)`, and removes one of those failures.

PR-open ran under the corrective-PR exception with the RED strings surfaced
verbatim first. Because the fix was not scoped to either RED reason, that
stretch was stated plainly on the issue rather than papered over. The merge was
separately and explicitly authorized by the human after CI went green. No
release was performed.

## Coordination

One of 4 missing-dataset smoke failures. The other 3 are handled by #455
(`missing-auto-simulate-guards`), which explicitly excludes this one. The only
surface shared between them is `workspace_index.json` — whichever lands second
must regenerate it against the new `main`.

## Original prompt

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
