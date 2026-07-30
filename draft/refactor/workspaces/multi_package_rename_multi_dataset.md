# Rename the `multi` example package to `multi_dataset`

Type: refactor
Target: workspaces
Repos:
- autolens_workspace
- autogalaxy_workspace
- autolens_workspace_test
- autogalaxy_workspace_test
- autolens_profiling
- autolens_jax_joss
- autolens_assistant
- PyAutoLens
- PyAutoGalaxy
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

## Original request

> Rename the multi package as multi_dataset, which is a huge endeavor with docs,
> URLs and everything so be thorough

## Why

`multi` is ambiguous — it collides conceptually with the sibling `multi_galaxy`
package, with `multi_gaussian_expansion` feature folders, and with the general
adjective "multi-" used throughout the prose ("multi-wavelength", "multi-plane",
"multi-band"). `multi_dataset` names what the package actually is: the examples
for fitting **multiple datasets** simultaneously via a factor graph.

## Scope (confirmed with the user)

Full rename, including dataset and output paths:

| Old | New |
|-----|-----|
| `scripts/multi/` | `scripts/multi_dataset/` |
| `notebooks/multi/` | `notebooks/multi_dataset/` |
| `markdown/multi/` | `markdown/multi_dataset/` |
| `dataset/multi/` | `dataset/multi_dataset/` |
| `dataset_type = "multi"` | `dataset_type = "multi_dataset"` |
| `output/multi/...` (`path_prefix`) | `output/multi_dataset/...` |

All nine repos above are in scope. This is a breaking change for existing users'
on-disk `output/multi/` directories — that is accepted.

## Surveyed surface (~330 path-shaped references)

**Directories to `git mv`** (scripts / notebooks / markdown / dataset):
- `autolens_workspace`: `scripts`, `notebooks`, `markdown`, `dataset` (incl.
  `dataset/multi/rxj1131` real data)
- `autogalaxy_workspace`: `scripts`, `notebooks`, `markdown`
- `autolens_workspace_test`: `scripts/multi` (jax_likelihood, visualization,
  images), `dataset/multi/lens_sersic`
- `autogalaxy_workspace_test`: `scripts/multi` (jax_grad, jax_likelihood)
- `autolens_profiling`: `scripts/multi/likelihood_runtime`,
  `dataset/multi/imaging`, `results/runtime/multi`

**Path-keyed sidecars that fail OPEN on a `git mv`** (must be swept explicitly —
see [[feedback_extension_filtered_grep_misses_dotfiles]] and
[[feedback_no_run_suffix_entries_break_on_moves]]):
- `smoke_tests.txt` — all four workspaces have `multi/...` entries (autolens has
  a commented-out `# multi/start_here.py` line too)
- `config/build/no_run.yaml` — autolens_workspace_test (SLOW + BOOTSTRAP-TARGET
  entries, incl. a comment naming `dataset/multi/lens_sersic`),
  autogalaxy_workspace_test (SLOW + BOOTSTRAP-TARGET)
- `.script_sizes.json` — autolens_workspace + autogalaxy_workspace (path keys;
  do **not** run `check_sizes.sh --update`, which sweeps in unrelated repo-wide
  drift — see [[project_dspl_terminology_rename]])
- `.navigator_check_ignore` — currently no `multi` entries, but re-check
- `autolens_workspace_developer/.gitignore` — `jax_profiling/dataset/multi/`
- `HowToLens/config/build/profile_smoke.yaml` — comment naming
  `multi/start_here`

**Docs & URLs:**
- `PyAutoLens/docs/general/model_cookbook.md` — 2 GitHub blob URLs
- `PyAutoGalaxy/docs/general/model_cookbook.md` — 2 GitHub blob URLs
- `PyAutoGalaxy/docs/overview/overview_2_new_user_guide.md` — a GitHub blob URL
  and a **version-pinned Colab URL** (`.../blob/2026.7.29.2/notebooks/multi/...`)
- `PyAutoLens/docs/overview/overview_3_features.md`,
  `PyAutoGalaxy/docs/overview/overview_3_features.md` — `*/multi` package prose
- In-notebook Binder / Colab / "download" links inside the moved notebooks
  themselves

**Cross-repo consumers:**
- `autolens_jax_joss` — `README.md`, `benchmarks/*.py` (`paired_example=`),
  `results/*.json`, `results/quick/*.json`, `results/RESULTS.md`
- `autolens_assistant` — `skills/al_multi_dataset.md` (already named
  `multi_dataset`!), `wiki/core/api/datasets.md`,
  `wiki/core/api/analysis_objects.md`, `wiki/core/concepts/multi_wavelength.md`
- Sibling workspace scripts referencing `multi/` cross-links:
  `interferometer/features/datacube`, `weak/features/strong_lensing`,
  `guides/modeling`, `imaging`, `misc/database/scrape`,
  `misc/searches`, `misc/simulators`, `gallery`

**Explicitly OUT of scope:**
- `PyAutoMind/complete/**` and `PyAutoMind/draft/**` historical records — these
  are a log of what happened, not live references. Do not rewrite history.
- Generated `.artifacts-*` directories.
- Any word containing `multi` that is not this package: `multi_galaxy`,
  `multi_gaussian_expansion`, `multipoles`, `multiplane`, `MultiStartProdigy`,
  `multiprocessing`, and all prose uses of "multi-wavelength"/"multi-band".

## Execution notes

- Library-first merge gate does **not** apply cleanly here: the library-side
  changes are docs-only (URLs). But the docs URLs point at
  `autolens_workspace@main`, so the **workspace PRs must merge first** or the
  doc links 404 in the interim.
- `README.md` bodies inside the moved packages describe "the `multi` folder" —
  rewrite the prose, not just the paths.
- The `features/` subpackage names stay unchanged.
- Prove each repo with a post-move grep for the old path shape returning zero
  live hits, and by the `.script_sizes.json` / `smoke_tests.txt` entry counts
  being preserved (not merely changed) — see
  [[feedback_smoke_entry_path_and_count]].
- Regenerate notebooks/markdown via `generate.py` from the repo root with the
  short project key (`al` = 308 scripts, `ag` = 132) — see
  [[feedback_generate_py_cwd_and_project_key]].
