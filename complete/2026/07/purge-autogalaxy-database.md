## purge-autogalaxy-database
- issue: https://github.com/PyAutoLabs/autogalaxy_workspace/issues/169
- completed: 2026-07-27
- workspace-pr: https://github.com/PyAutoLabs/autogalaxy_workspace/pull/170
- summary: Leg 2 of the dataset-bulk series. Purged the orphaned dataset/database/simple__{0,1,2} (512 KB, 90% of the repo's committed dataset bytes) AND deleted their three light_sersic_exp__{0,1,2}.py simulators + empty __init__.py. Opus git archaeology proved no commit in history ever read dataset/database/ — the database guide reads dataset/imaging/* by design ("database" is its output path_prefix), matching the autolens sibling guide which never had a simulators/ dir; the 2026-07-13 allowlist call ("committed-by-design aggregator data", #126 Group B) rested solely on a stale prose line in start_here.py wrong since the root commit, fixed in the PR so the orphan cannot return. The simulators' absence from no_run.yaml made every pre_build re-run them — the source of the dataset byte-churn commits (34ddb66d/10a1ee64/e942d360); post-smoke clean tree confirmed the churn source gone. Also: sma.fits non-regenerable marker in .gitignore; navigator catalogue + .script_sizes.json regenerated in-diff. Verification: check_dataset_allowlist OK (1 file, 2 patterns), smoke 10/10 (16.6 s parallel). Shipped under the 2026-07-27 heart-ack. Condemned entry release-datasets/autogalaxy-database-orphans (recover e942d360, sweep-after 2026-08-27). Merged 2026-07-27, merge commit b44afb6a7.

## Original prompt

# Purge autogalaxy_workspace dataset/database/simple__{0,1,2}

Type: maintenance
Target: autogalaxy_workspace
Repos:
- autogalaxy_workspace
Difficulty: easy
Autonomy: supervised
Priority: normal
Status: formalised

Leg 2 of the dataset-bulk series (leg 1:
`draft/maintenance/workspaces/purge_committed_simulated_datasets.md`, autolens_workspace).
autogalaxy_workspace is already nearly clean — the #129 purge leg worked: only **568 KB**
of committed data remains under `dataset/`. This leg removes the last 512 KB, which is
both regenerable **and** unconsumed.

## Verified facts (2026-07-27 survey)

- Committed under `dataset/`: 568 KB across 17 files.
- `dataset/database/simple__{0,1,2}` — 3 × 170.8 KB = **512 KB** (90% of committed bytes):
  - **Regenerable.** Each is written exactly (`data.fits`, `psf.fits`, `noise_map.fits`,
    `galaxies.json`, `info.json`) by
    `scripts/guides/results/database/simulators/light_sersic_exp__{0,1,2}.py`
    (`dataset_type = "database"`, `dataset_name = "simple__N"`).
  - **Unconsumed.** No script reads `dataset/database/...`. The apparent consumer,
    `scripts/guides/results/database/start_here.py`, reads
    `dataset/imaging/{simple, simple__sersic, sersic_x2}`; its
    `path_prefix=Path("database")` is an *output* prefix — matching on the bare string
    "database" is a false positive.
- `.gitignore` allowlist entries to drop: `!dataset/database/simple__{0,1,2}/**`
  (lines 6–8).

## The task

1. **Establish intent first.** Check the git history of `scripts/guides/results/database/`
   — were `simple__{0,1,2}` orphaned by a refactor of the database/aggregator guides? If a
   guide *should* consume them, rewire it with an auto-simulate guard instead of purging.
2. If genuinely orphaned: `git rm -r --cached dataset/database/simple__{0,1,2}`, drop the
   three `!` re-includes, and decide whether the three `light_sersic_exp__N.py`
   simulators go too (nothing reads their output).
3. **Keep `dataset/interferometer/uv_wavelengths/sma.fits`** (8.4 KB) permanently — real
   SMA uv baseline coverage, no writer exists anywhere, pure *input* to 4 simulators. Add
   a comment above its `!` re-include in `.gitignore` marking it non-regenerable so no
   future purge leg misclassifies it. (Cosmetic aside: those simulators' comments mention
   an `alma.fits` companion that does not exist in the repo.)
4. Verify `python -m autohands.check_dataset_allowlist` (or the pre_build leg calling it)
   still passes; if the simulators stay, prove regeneration from a clean tree.
5. Bytes stay recoverable via the pre-purge SHA; condemn via PyAutoGut
   (`PyAutoMind/condemned.md`) as prior legs did.

## Local-only note (no PR needed)

Untracked cruft on disk (`dataset/imaging/simulated_galaxy` 772 KB,
`dataset/interferometer/simulated_galaxy` 40 KB, empty `dataset/multi/`) is written by
`start_here.py` scripts and is the clean_slate widening leg's problem
(`draft/maintenance/pyautobrain/clean_slate_write_site_provenance.md`), not this one's.
