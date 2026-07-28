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
