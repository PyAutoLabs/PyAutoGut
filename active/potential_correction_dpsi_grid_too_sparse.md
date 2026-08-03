# Potential-correction interferometer examples fail smoke: dpsi grid too sparse

Type: bug
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

## Original request (verbatim)

> 5 — potential_correction: dpsi grid too sparse (claims autolens_workspace — conflict group)
> Four workspace-smoke failures, all the same exception:
>   ValueError: The dpsi grid is too sparse. Try decreasing the dpsi_factor to
>   smaller values.
>
> Affected (script + notebook of each):
>   autolens scripts|notebooks/interferometer/features/advanced/potential_correction*
>
> Evidence: PyAutoHeart workspace-smoke run 30790463134. The potential-correction
> port and its validation campaign (PyAutoLens#672) completed recently with three
> PRs merged, so this is likely drift from that work rather than a long-standing
> break.
>
> Reproduce locally, then decide whether the fix is the example's dpsi_factor, the
> smoke/test-mode grid resolution, or the library's sparsity check being too
> strict at test-mode resolutions.

## Verdict

Neither the example's `dpsi_factor` nor the library's sparsity check is at fault,
and this is **not** drift from PyAutoLens#672. The two interferometer scripts are
simply missing the `ENV: full_datasets` declaration that every other
potential-correction script in the organism already carries.

## Reproduced on clean local main

Run under the exact CI smoke profile (`autolens_workspace/config/build/profile_smoke.yaml`
resolved through `autohands.env_config.build_env_for_script`), from the workspace root:

| Script | smoke profile | `PYAUTO_SMALL_DATASETS` released |
|---|---|---|
| `scripts/interferometer/features/advanced/potential_correction/start_here.py` | FAIL — `ValueError: The dpsi grid is too sparse` | PASS, 83s |
| `scripts/interferometer/features/advanced/potential_correction/likelihood_function.py` | FAIL — same | PASS, 44s |

Identical traceback to CI, terminating at
`PyAutoLens/autolens/potential_correction/mesh.py:132` (`get_itp_box_ctr`). Both
timings sit well under the 300s smoke cap (`BUILD_SCRIPT_TIMEOUT`), so lifting the
cap costs nothing meaningful.

CI failure attribution confirmed against the run's job logs — exactly four
failures, all in this folder:

- job 91612773963 (`run_scripts` autolens/interferometer): `start_here.py` FAIL (14.4s),
  `likelihood_function.py` FAIL (5.8s)
- job 91612954327 (`run_notebooks` autolens/interferometer): both `.ipynb` FAIL

## Root cause

The smoke profile sets `PYAUTO_SMALL_DATASETS=1`. That shrinks `Mask2D.circular`
to 16x16 at `pixel_scales=0.6` (`PyAutoArray/autoarray/mask/mask_2d.py:363`). With
`dpsi_factor=2` the dpsi mesh drops to 8x8; after the arc restriction and
`cleaned_mask_from`, **zero** valid 2x2 interpolation boxes survive, so
`get_itp_box_ctr` raises. The check is correct — at that resolution there is
genuinely no mesh to build.

The escape hatch already exists and is used everywhere else:

- `scripts/imaging/features/advanced/potential_correction/start_here.py:343-357`
  carries an `__Env__ (Developer Only)` section with `ENV: full_datasets`, whose
  comment names **this exact error** and states that
  "config/build/profile_release.yaml carries the same reasoning for this folder
  and its interferometer sibling".
- `config/build/profile_release.yaml:58-61` lifts the cap for **both** folders by
  directory pattern, so the release profile has always covered all four scripts.
- All 5 potential-correction scripts in `autolens_workspace_test` declare
  `ENV: full_datasets` (two of them `ENV: jax full_datasets`).

The smoke path relies on the in-file declaration (post-#187 Stage 2, which
migrated profile `unset:` lists to `__Env__` sections). The interferometer pair
never received one. This is a gap from the port, not a regression: the
declaration was added to the imaging guide in `5c1ce1d9` when it moved into
`features/`, and the interferometer siblings were never given the equivalent.

## Rejected fixes

- **Lower the example's `dpsi_factor`** — no. `factor=2` is the configuration
  certified by the PyAutoLens#672 validation campaign (dkappa correlation ~0.83,
  peak ~0.15" from truth, ~6 sigma), documented in the script header. And at a
  16x16 capped grid even `factor=1` would be scientifically meaningless.
- **Loosen the library sparsity check** — no. It is correct at that resolution;
  relaxing it would silently build a degenerate mesh instead of raising, and the
  message is already actionable. Also violates the workspace's no-silent-guards
  convention.

## Scope (human decision, 2026-08-03)

Add an `__Env__ (Developer Only)` section carrying `ENV: full_datasets` to the
**three** scripts missing it:

- `scripts/interferometer/features/advanced/potential_correction/start_here.py` (failing)
- `scripts/interferometer/features/advanced/potential_correction/likelihood_function.py` (failing)
- `scripts/imaging/features/advanced/potential_correction/likelihood_function.py`
  (**not** currently failing — passes in 4.5s under the cap because its
  `Grid2D.uniform`-derived arc mask happens to retain a valid interpolation box.
  That is incidental, and it contradicts `profile_release.yaml`, which lifts its
  cap. Close the inconsistency rather than wait for it to break.)

Mirror the wording and placement of the existing imaging `start_here.py` section
(appended inside the final docstring, header at column 0, one bare `ENV:` line).

## Verification

1. Re-run all four scripts under the smoke profile from the workspace root;
   all four must pass, each under the 300s cap.
2. Regenerate the notebooks. `__Env__` sections are stripped from generated
   notebooks (`grep -c "__Env__" notebooks/…/start_here.ipynb` returns 0 for the
   imaging file that already has one, and no `full_datasets` appears anywhere
   under `notebooks/`), so the regenerated `.ipynb` files must come out
   **byte-identical** — prove the zero diff rather than assume it.
3. Re-run the four notebooks under the smoke profile. Env resolution maps
   `.ipynb` back to its `.py` source (`env_config.py:228-253`), so the
   declaration must cover the notebook runs.

## Out of scope (flagged, not bundled)

All four potential-correction scripts emit `SyntaxWarning: invalid escape
sequence` from LaTeX in non-raw docstrings (`\odot`, `\chi`, `\delta`, `\,`).
Unrelated to this failure; worth a separate hygiene pass across the workspace
rather than a partial fix here.

## Claim note

`worktree_check_conflict` fired twice with two different holders during this
task's setup:

1. `group-data-preparation-readme` (#454) held `autolens_workspace` at first
   survey. Its branch touched the repo-wide generated indices
   (`workspace_index.json`, `llms-full.txt`, `.script_sizes.json`,
   `notebooks/README.md`) as well as `group/data_preparation/`. **#454 closed
   2026-08-03T17:33Z**, discharging that claim.
2. `missing-auto-simulate-guards` (#455 — triage item 4, sibling of this one)
   claimed the repo in the interval, and is LIVE (16 guards applied across 18
   files, uncommitted, mid-verification).

Proceeded as a **documented concurrent claim**, matching the precedent #455's own
claim-note sets for the same repo. File scopes are strictly disjoint:

- this task: `scripts/{imaging,interferometer}/features/advanced/potential_correction/`
  + the four notebook mirrors
- #455: `config/build/no_run.yaml`, `scripts/guides/results/*`,
  `scripts/imaging/data_preparation/*`, `scripts/cluster/*`,
  `scripts/multi_dataset/*`, `scripts/interferometer/features/pixelization/*`

Shared surface is the generated index files only. Mitigation: scope notebook
regeneration to the four potential_correction files (`--only`) and leave the
repo-wide indices untouched, so whichever PR merges second regenerates them.
Pre-merge `origin/main` before opening the PR.
