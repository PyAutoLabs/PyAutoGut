## hpc-guide-sync
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/360
- completed: 2026-07-28
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/361 (merged 301759a5), https://github.com/PyAutoLabs/autogalaxy_workspace/pull/174 (merged 6cbd5570)
- summary: |
    The autolens HPC guide had regressed to an older pattern (`srun -n 16
    --multi-prog`, `sys.argv[1]` integer indexing, hand-written `.conf`
    CPU-index files, no GPU coverage) while autogalaxy carried a modern
    array-job guide. Ported the modern guide across as
    `example_cpu_and_gpu.py` (replacing `example_cpu.py`), rewrote the README
    to the modern shape, and retired the legacy `batch/` directory in favour
    of `batch_cpu/` + `batch_gpu/`.

    THE REAL FINDING: autogalaxy's guide documented four artifacts — `sync`,
    `sync.conf.example`, `batch_cpu/submit`, `batch_gpu/submit` — that were
    committed as ZERO-BYTE files, with an 11.5 KB README explaining their
    setup, usage and per-directory rsync strategy in detail. A straight port
    would have left both workspaces pointing at empty files. All four are now
    populated in both repos, adapted from the working versions in
    `euclid_strong_lens_modeling_pipeline/hpc/` (which is evidently where the
    prose was written from — it matches line for line). Generalised for public
    use: no personal email, no Euclid sample names.

    Defects fixed rather than propagated:
    - `--dataset` was read via argparse then discarded by a reassignment ~40
      lines later, so every array task fitted the same dataset and the
      docstring's "each array job receives a different value" was false.
      Verified fixed by running `--dataset=cosmos_web_ring` (loaded 209x209 /
      2809 px, wrote `output/test_mode/hpc/cosmos_web_ring/example`).
    - `hpc_dataset_path` was built as `.../dataset/example/simple` then had the
      same two segments appended again -> `.../example/simple/example/simple`.
    - Three autogalaxy README errors: "fitting many LENSES" in the galaxy
      workspace; a documented `config/` folder in the hpc dir that does not
      exist; `slam_pipeline/` listed as a synced dir (neither workspace has one).
    - The `batch_{cpu,gpu}/{output,error}/.gitignore` stubs were also empty, so
      SLURM logs would have landed as untracked files rather than ignored.
    - The `__Env__` rationale claimed the guide loads committed full-resolution
      FITS; it actually simulates on demand and runs green under either dataset
      regime. Corrected in both repos (declaration kept, reason made accurate).

    GOTCHA (cost real time): `build_env_for_script` reads a script's in-file
    `ENV:` declaration by opening the path it is handed, so it MUST be called
    with the workspace root as cwd. Called from anywhere else it silently
    misses the declaration and falls back to the default profile — which is how
    an `ENV: full_datasets` script ends up running under
    `PYAUTO_SMALL_DATASETS=1` with no error at all. Two verification runs
    proved the wrong thing before this was spotted (16x16 data, mask padded,
    instead of the declared 100x100). Also hit the autofit resume trap: a
    second run reported "Fit Already Completed: skipping non-linear search",
    so output/ and the generated dataset must be cleared between verification
    runs or the run proves nothing.

    POST-MERGE FIX (autolens_workspace#362, 722d2537): the root .gitignore has
    `output/`, which matches any output/ directory at any depth, so `git add -A`
    silently refused
    `scripts/guides/hpc/batch_{cpu,gpu}/output/.gitignore` while the sibling
    error/ stubs went in. Git does not warn when add -A declines an ignored
    path. On a fresh clone the stdout log dir would not exist and sbatch rejects
    a job whose -o directory is missing, so the first submit would fail.
    autogalaxy was unaffected because it already tracked both files (force-added
    when its batch dirs were created). Fixed with `git add -f`. No gate could
    catch this: smoke/navigator/banner-lint all check scripts/ references, not
    whether an empty log dir is tracked.

    CI CATCH: `navigator / Navigator paths + banner lint` failed on autolens
    for `README.md -> missing path: scripts/guides/hpc/sync.conf`. autogalaxy
    passed the identical line because it already carried a
    `.navigator_check_ignore` entry, added when its sync artifacts were first
    introduced; autolens had none, never having had a sync script. Introducing
    `sync` into a repo therefore requires bringing that exception with it.

    `no_run.yaml` decided empirically, not assumed: autolens skipped
    `hpc/example_cpu` ("HPC paths dont exist locally") while autogalaxy had no
    entry. The ported script was RUN — it passes, thanks to the `try/except`
    around `conf.instance.push` plus a local-dataset fallback — so the entry
    was removed rather than renamed, bringing the repos into line.

    Brain phase-split override (recorded on the issue): `pyauto-brain feature`
    returned `too-large (score 15) -> split-into-phases` with four phases
    (design / core_api / workspace_examples / docs). Overridden to
    single-phase — the score is driven by repo count and it counted
    `euclid_strong_lens_modeling_pipeline` as affected when that repo is
    read-only reference material. A design/core-API split is meaningless for a
    docs task with no API surface.

    Heart was YELLOW at ship time on four pre-existing reasons (workspace
    validation 13 failed 2026-07-21; 33 stale parked scripts; manifest drift
    tenant firewall; stale release validation) — none touching
    `scripts/guides/hpc/`. Acknowledged by the human before shipping.

    Verification: smoke autolens 16/16, autogalaxy 12/12, zero failures; both
    guides EXIT 0 under their resolved smoke env; all 6 shell scripts `bash -n`
    clean and LF-only (CRLF breaks them on HPC); `sync` fails loudly when
    unconfigured and resolves the workspace root from any cwd; CI green on both
    PRs (smoke 3.12 + 3.13, catalogue staleness, navigator paths + banner lint).

## Original prompt

# Sync the autolens HPC guide up to the autogalaxy one, and fill both sets of empty batch/sync artifacts

Type: docs
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
Difficulty: medium
Autonomy: supervised
Priority: medium
Status: draft

## Original request (verbatim)

autogalaxy_workspace/scripts/guides/hpc/example_cpu_and_gpu.py, is a example and
the package is well documented. I think autolens_workpsace used to have this, but
its gone back to an older guide. Can you sync them up

## What the survey found

@autogalaxy_workspace has the modern guide, @autolens_workspace has an older one,
and both point at artifacts that do not exist.

**autogalaxy_workspace/scripts/guides/hpc/** — modern prose:
- `example_cpu_and_gpu.py` (13.5 KB) — SLURM **array jobs**
  (`--array=0-2`, `$SLURM_ARRAY_TASK_ID`), `argparse --dataset`,
  `number_of_cores` read from `$SLURM_CPUS_PER_TASK`, a JAX/thread-pinning
  section, and a `__GPU Jobs__` section.
- `README.md` (11.5 KB) — documents `sync`, `sync.conf.example`, `batch_cpu/`
  and `batch_gpu/` in detail (setup, usage, per-directory rsync strategy,
  SLURM directives, monitoring).
- **But `batch_cpu/submit`, `batch_gpu/submit`, `sync` and `sync.conf.example`
  are committed ZERO-BYTE files.** The prose documents artifacts that are empty.

**autolens_workspace/scripts/guides/hpc/** — older prose, real artifacts:
- `example_cpu.py` (15.5 KB) — `srun -n 16 --multi-prog`, `sys.argv[1]` integer
  indexing, hand-written `.conf` CPU-index files, `number_of_cores = int(sys.argv[1])`,
  no GPU coverage.
- `README.md` (6.7 KB) — no `sync`, no GPU, and a stale "Next Steps" pointing at
  `autolens_workspace/misc/hpc/example_cpu.py` and `autolens_workspace/hpc/batch`
  (neither path exists).
- `batch/` holds three **real** scripts (`example_cpu_many_datasets`,
  `example_cpu_many_datasets.conf`, `example_cpu_one_dataset_parallel`) using the
  old `srun --multi-prog` pattern with hard-coded `/hpc/home/hpc_username/` paths.

Neither guide ever had a GPU batch script: `git log --all -S batch_gpu` and
`--diff-filter=A -- '*example_cpu_and_gpu*'` return nothing in autolens_workspace.
The modern prose was written in autogalaxy against working scripts that live in
**@euclid_strong_lens_modeling_pipeline/hpc/** (`sync` 5.7 KB, `sync.conf.example`,
`batch_cpu/template`, `batch_cpu/submit_start_here`, `batch_gpu/submit_start_here`)
— that is the source material, and it matches the autogalaxy README line for line
(push/pull/sync/status, `HPC_HOST`/`HPC_BASE`/`PROJECT_NAME`, `--ignore-existing`
for FITS, `search_internal/` excluded on pull).

## Scope (user-confirmed)

Port the prose **and** fill the artifacts in both workspaces:

1. **autolens_workspace** — replace `example_cpu.py` with a lens-flavoured
   `example_cpu_and_gpu.py` mirroring the autogalaxy structure; bring `README.md`
   up to the modern 11.5 KB shape (sync + batch_cpu + batch_gpu + monitoring);
   retire `batch/` in favour of `batch_cpu/` + `batch_gpu/`.
2. **Both workspaces** — populate `sync`, `sync.conf.example`,
   `batch_cpu/submit` and `batch_gpu/submit` with real, workspace-generic
   content adapted from `euclid_strong_lens_modeling_pipeline/hpc/`.

Keep the science/register split: lens-flavoured prose for autolens (Isothermal +
ExternalShear lens, SersicCore source), galaxy-flavoured for autogalaxy —
mirroring each workspace's existing example.

## Decisions taken with the user

- **Fix the dead-argparse defect in both workspaces.** In autogalaxy's
  `example_cpu_and_gpu.py`, line 198 sets `dataset_name = args.dataset or
  "example_image_1"` and line 205 builds `dataset_path` from it — then line 238
  reassigns `dataset_name = "simple"` and line 240 rebuilds `dataset_path`,
  discarding `--dataset` entirely. The docstring's claim that "each array job
  receives a different value, so all datasets are fitted in parallel" is
  therefore false as written. Restructure so `--dataset` actually selects the
  fitted dataset, keeping the local-dataset fallback.
- **Delete autolens's old `batch/`** (three `srun --multi-prog` scripts with
  hard-coded `/hpc/home/hpc_username/` paths) rather than keeping it as a legacy
  reference — the array-job pattern supersedes it, autogalaxy has no `batch/`,
  and git history preserves the old scripts.
- **Branch:** `feature/hpc-guide-sync`.
- **Brain phase-split override.** `pyauto-brain feature` returned
  `too-large (score 15) → split-into-phases` with four phases
  (`design / core_api / workspace_examples / docs`). Overridden to single-phase:
  the score is driven by repo count and it counted
  `euclid_strong_lens_modeling_pipeline` as affected when that repo is read-only
  reference material. A design/core-API split has no meaning for a docs task
  with no API surface.
- **Accepted trade-off:** autogalaxy's `try/except` around `conf.instance.push`
  swallows an exception, but it is what makes the guide locally runnable; it is
  carried over to the lens version for parity rather than silently dropped.

## Constraints and traps found in the survey

- `autolens_workspace/config/build/no_run.yaml` line 37 lists
  `hpc/example_cpu # HPC paths dont exist locally.` — the entry must be renamed
  when the script is renamed, or the harness will try to run it.
  autogalaxy has **no** `no_run` entry for its HPC guide; check why before
  copying either way (autogalaxy's example wraps `conf.instance.push` in
  try/except and falls back to local dataset paths, autolens's does not).
- Both `.gitignore`s pin a stale local batch dir (`batch_cosma6` in autogalaxy,
  `batch_hpc6` in autolens); the euclid one gitignores `sync.conf`, which both
  workspaces need once a real `sync` script exists.
- The autogalaxy README (line ~203) lists a `config/` folder inside the hpc
  directory that does not exist there — fix or drop while rewriting.
- SLURM `output/` and `error/` log dirs need `.gitignore` stubs
  (autogalaxy's `batch_cpu`/`batch_gpu` already have them; autolens's `batch/`
  does not).
- CRLF breaks shell scripts on HPC — `sync` and `submit` are executable scripts,
  so they must be committed LF-only.
- The euclid source scripts carry a personal `--mail-user` address and
  euclid-specific `sample=`/dataset names; these must be generalised for a public
  user-facing workspace.
- `workspace_index.json` / `llms-full.txt` / `.script_sizes.json` reference the
  old filename in both workspaces and are regenerated, not hand-edited.
- Notebooks (`notebooks/guides/hpc/example_cpu.ipynb`) are generated — regenerate
  after the script rename, do not edit.
