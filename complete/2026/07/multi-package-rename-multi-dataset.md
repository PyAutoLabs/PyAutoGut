Renamed the `multi` example package to `multi_dataset` across **eleven repos**, covering scripts, notebooks, markdown, dataset paths, output `path_prefix` values, docs URLs, assistant wiki citations and JOSS benchmark pointers.

`multi` was ambiguous: it collided conceptually with the sibling `multi_galaxy` package, with the `multi_gaussian_expansion` feature folders, and with the general adjective "multi-" throughout the prose. `multi_dataset` names what the package actually is — the examples for fitting **multiple datasets** simultaneously via a factor graph.

## PRs (11 repos, 10 PRs, all merged 2026-07-30)

| Phase | PR |
|-------|-----|
| 1 — user workspaces | autolens_workspace#414, autogalaxy_workspace#194 |
| 2a | autogalaxy_workspace_test#101 |
| 2b | autolens_workspace_test#239, autolens_profiling#97, autolens_workspace_developer#122 |
| 3 — downstream consumers | PyAutoLens#673, PyAutoGalaxy#542, autolens_assistant#105, autolens_jax_joss#2 |

HowToLens needed no change (see below).

## The trap that would have shipped silently: `bound="multi"`

**Nine sites** across the organism use `multi` as a **Dynesty sampler value**, not a package name: `scripts/guides/modeling/searches.py` in both workspaces (×2 each), `PyAutoLens/autolens/config/non_linear.yaml` (×2), `PyAutoLens/test_autolens/config/non_linear.yaml`, `PyAutoGalaxy/test_autogalaxy/config/non_linear.yaml` (×2). A blanket `s/multi/multi_dataset/` corrupts all nine **with green CI** — nothing validates a sampler bound string.

This is why the whole rename was done pattern-by-pattern with an explicit exclude list, never as a blanket substitution. See [[feedback_delete_the_trap_dont_document_it]] for the general shape.

## Path-keyed sidecars fail OPEN on a `git mv`

No error, no CI failure — just silent loss of coverage. Every one swept by hand and proved by entry **count**, not content:

- `smoke_tests.txt` (4 repos) — including **commented-out** entries, which a naive sweep skips
- `config/build/no_run.yaml` — SLOW and BOOTSTRAP-TARGET entries, plus trailing **comments** naming the dataset path the entry produces (invisible to a sweep of the entry alone)
- `config/build/profile_release.yaml` — `- pattern: "multi/start_here"`, a **pattern** match that would have quietly stopped matching rather than erroring
- `.script_sizes.json` — 28/401 keys (al), 22/174 (ag); hand-edited, **not** `check_sizes.sh --update` (which sweeps in unrelated repo-wide drift, cf. [[project_dspl_terminology_rename]])
- `.url_check_allowlist.txt` — keyed by a trailing `# scripts/multi/...` path comment
- `gallery/gallery_run.sh`, `.gitignore` (×2), `workspace_index.json`, `llms-full.txt`, `llms.txt`

## Records vs pointers — the distinction that drove several calls

**Pointers were updated; records were not.**

- JOSS `paired_example` fields → updated (a pointer to the corresponding script; no timing, iteration count or likelihood value touched).
- A captured execution log line in `markdown/multi_dataset/modeling.md` showing `output/multi/...` from a 2026-07-10 run → **left**, since rewriting it would misrepresent what that run produced.
- `HowToLens/config/build/profile_smoke.yaml` — a dated 2026-07-23 comment recording which override patterns were *removed*. Those patterns literally said `multi/start_here`; rewriting it would falsify the record. **HowToLens therefore needed no change at all.**
- `simulators/multi.py` + `multi_summary_v*.json` + `"type": "multi"` in autolens_profiling and autolens_workspace_developer → **left as a triple**. Nothing reads the field (verified write-only), the filename is a separate literal, and renaming part of the triple would orphan the historical series or leave it inconsistent.
- `hard_group_multi.md`'s `id:` and filename → **left** (benchmark identifiers; renaming breaks comparison against historical results). Only its `workspace_packages:` entry moved.
- `autolens_jax_joss` `fetch_url(..., "multi/sdp81")` → **left** (that repo's own dataset cache key, not a workspace path; renaming forces large FITS re-downloads for no gain).

## Release notes: a breaking change silently filed as `Internal`

`generate_release_notes.py::classify_pr` matches on a `## API Changes` section containing `### Removed`/`### Renamed`/`### Changed Signature`/`### Changed Behaviour` — **not** on prose. All three workspace PRs carried a prominent `### ⚠️ Breaking for existing users` block and still classified as `internal`, so the `output/multi/` break would never have reached users. Verified by running the real `classify_pr` against the live PR bodies, then fixed. Durable lesson in [[feedback_release_notes_breaking_needs_api_changes_heading]].

## Assistant CI: `--check-provenance`, not the citation gate

`autolens_assistant` `wiki-currency` failed — but **not** on `--check-citations`, which passed with **0 missing paths** even while the workspace PR renaming those paths was still open (it resolves against pinned `sources/` clones). The failure was `--check-provenance`: every `wiki/core` page carries a `content_sha256` stamp that any body edit invalidates. Fixed with `audit_skill_apis.py --write-provenance --page <each>`; 3 errors → 0. Recorded in [[reference_docs_ci_gotchas_workspace_assistant]].

## Nine pre-existing bugs fixed as drive-bys

A faithful rename keeps a wrong path wrong in a new costume, so **every** `multi_dataset/...` reference was checked for existence rather than trusted:

- Four `"can be viewed in the folder"` docstrings had `dataset_type` and `dataset_label` **swapped** (`dataset/imaging/multi/x` for what the code builds as `dataset/multi/imaging/x`); two of those also named the **wrong `dataset_name`**.
- Two `jax_grad` scripts printed `jax_grad/multi/<name>.py` — components **reversed**.
- A run command omitted its `jax_likelihood/` component.
- Two references named a `jax_likelihood_functions/` directory **that does not exist**.
- Two had `likelihood_runtime/multi/` components reversed.
- Two stale markdown sentences referenced `advanced/multi/modeling`, a path in neither the old nor the new layout.

## Verification

- **Zero** unintended survivors organism-wide; the 13 remaining `multi` tokens are all documented exclusions.
- Simulators run green in four repos, writing to the renamed paths; consumers read those paths back and pass (`jax_grad/lp.py` gradient checks, `jax_likelihood/mge.py`) — verified across the **producer/consumer boundary**, not just at the producer.
- Regeneration counts matched exactly: al **308** scripts, ag **132**.
- Merge-order gate **verified, not assumed**: after phase 1 merged and before any phase-3 PR, all 7 target paths returned 200 on `main`; afterwards the live doc URLs return 200 and the old paths 404.
- No collateral damage to the five concurrent `autolens_workspace` branches.

## Process notes

- **Brain phase split overridden.** `pyauto-brain feature` scored `too-large (28)` and proposed the generic `design → core_api → workspace_examples → docs` split — the repo-count heuristic ([[feedback_brain_repo_count_difficulty_proxy]]). There is no design step and no API here; replaced with a per-repo split ordered by merge dependency.
- **`worktree_check_conflict` overridden twice on human authorisation**, both times after hand-checking that the holding claim was empty or file-disjoint ([[feedback_worktree_conflict_guard_never_fires]]). Up to **eight** concurrent tasks were claiming `autolens_workspace`.
- **Heart YELLOW acknowledged** by the human for exactly three pre-existing reasons (manifest drift + two stale), re-checked before each ship and never extended to new reasons.
- `markdown/` was updated **in place** rather than via `generate_markdown.py`, which executes every curated script for real (no test mode, at-release cadence) — hours of sampling to reproduce byte-identical figures for a rename. `markdown/` is stale against `scripts/` independently of this work and wants a real regeneration at release.

## Breaking for users

Results under `output/multi/` are **not migrated** — a re-run writes to `output/multi_dataset/` and will not resume from the old directory. A local `dataset/multi/` is likewise not moved (simulators simply re-create it).

## Original prompt

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
- `config/build/profile_release.yaml` — autolens_workspace has
  `- pattern: "multi/start_here"` (a **pattern match**, so it silently stops
  matching after the move rather than erroring)

**Generated indexes keyed by path** (regenerate, do not hand-edit):
- `workspace_index.json` — both workspaces (dozens of `multi/...` entries)
- `llms-full.txt` — autolens_workspace

**Package-listing prose that names the folder:**
- `autolens_workspace/README.md`, `scripts/README.md`, `AGENTS.md`
- `autolens_workspace/start_here.ipynb` (root) — `*/multi` package pointer
- the moved packages' own `README.md` / `features/README.md` bodies
- `guides/results/aggregator/` (both workspaces) — "The `multi` package of the
  workspace illustrates…"

**Output `path_prefix` values (in-scope per the confirmed scope):**
- `path_prefix=Path("multi", "modeling")`, `Path("multi") / "features"`
- `path_prefix=Path("slam", "multi", "simultaneous")` — note the **nested**
  form under `output/slam/`, which a naive leading-`multi/` sweep misses
- `dataset_main_path = Path("dataset", "multi", "imaging", dataset_name)` and
  `dataset_path = Path("dataset") / "multi" / "rxj1131"`

## Ambiguity trap — do NOT blind-sed

`multi` appears as an English word adjacent to a slash in prose that is **not**
a path. In `scripts/point_source/features/multiple_sources/` and its notebooks,
"the multi/factor-graph API" means *multi-dataset / factor-graph*, not
`multi/`. Those must stay (or be reworded to "multi-dataset/factor-graph"),
not rewritten to `multi_dataset/factor-graph`. Every replacement needs eyes on
it; the sweep is grep-assisted, not sed-automated.

Conversely, prose that names the folder — "Unlike other `multi` simulators",
"The `multi` package extends…", "Checkout the `autolens_workspace/*/multi`
package" — **does** need rewriting, and a path-shaped regex will not catch it.

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

## Phasing (Brain override — recorded)

`pyauto-brain feature` scored this `too-large (28)` and proposed the generic
`design → core_api → workspace_examples → docs` split. That is the repo-count
heuristic ([[feedback_brain_repo_count_difficulty_proxy]]) and is wrong here —
there is no design step and no API to change. **Overridden** in favour of a
per-repo split ordered by merge dependency:

- **Phase 1 — user workspaces** (`autolens_workspace`, `autogalaxy_workspace`).
  The bulk of the work; everything downstream points at these.
- **Phase 2 — test / profiling / dev** (`autolens_workspace_test`,
  `autogalaxy_workspace_test`, `autolens_profiling`,
  `autolens_workspace_developer`, `HowToLens` comment).
- **Phase 3 — downstream reference consumers** (`PyAutoLens/docs`,
  `PyAutoGalaxy/docs`, `autolens_assistant`, `autolens_jax_joss`).
  **Gated on phase 1 merging** — these are GitHub `blob/main` URLs and
  `paired_example` pointers that 404 / dangle until the workspace move lands.

**Phase 2 is BLOCKED** at time of writing: `autolens_workspace_test`,
`autolens_profiling` and `autolens_workspace_developer` are real worktrees held
by the in-flight `point-source-chi-squared-variants` phase 3
(`feature/point-source-chi-squared-variants`). `autogalaxy_workspace_test` is
free. Phase 2 starts once that task releases its claim.

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
