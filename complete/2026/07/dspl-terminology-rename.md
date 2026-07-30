Renamed `double_einstein_ring` → `double_source_plane_lens` across `autolens_workspace`, and moved documentation prose to the **DSPL** acronym. "Double Einstein ring" describes the image-plane morphology; the standard literature term for the system is a double source-plane lens.

This finished a migration already half-started: the imaging README already opened with "double source-plane strong lenses (DSPLs)" while every sibling file still said "double Einstein ring".

## Shipped

- **autolens_workspace#394** → `726d060d` (45 files, 32 renames, +471/−469)
- **autolens_assistant#100** → `6a367cf8` (2 citation files)
- Issue autolens_workspace#390 closed.

## Scope

4 directories + the `plotters_*` file-pair moved via `git mv`; `dataset_name` in both simulators; 6 cross-refs (mass_stellar_dark ×3, point_source/simulator_sample, two index READMEs). `autolens_workspace_test` and `autolens_workspace_developer` had **zero** matches.

## Findings worth keeping

**1. The citation check is a hard cross-repo merge-order gate.** `autolens_assistant`'s `wiki-currency` job runs `--check-citations`, which resolves `autolens_workspace:` paths against a checkout of that repo. The assistant PR therefore **failed** until the workspace PR merged — my PR body's claim that the two were independent was wrong. Any future assistant PR re-pointing a workspace citation must merge *after* the workspace PR, then be re-run. Not advisory; it is a red X.

**2. Prose splits into system-class vs morphology, and only the first should be renamed.** Kept "They appear as two distinct Einstein rings in the image-plane, and can constrain Cosmological parameters in a way single Einstein ring lenses cannot" — substituting DSPL there makes the sentence false. Asserted the 21 unrelated Einstein-ring mentions elsewhere in `scripts/` stayed exactly 21 as a collateral check.

**3. Section headers were COMPOUND, so there was no blanket `__DSPL__` rule.** Four had to be hand-mapped (`__Log Likelihood Function: Group Double Einstein Ring__` → `__…: Group DSPL__`). Every title also carries an `===` underline that must be re-lengthened when the title shortens — a scripted census that only matched a bare `__Double Einstein Ring__` would have missed all of them.

**4. Control-test a notebook-rewriting helper before trusting it.** Round-tripping an unchanged notebook through `json.dumps` caught two format mismatches (`ensure_ascii` and a trailing newline) that would have reformatted every file. After fixing, 14/14 target notebooks round-tripped byte-identically. Final proof: regenerating via `build_util.py_to_notebook` + `inject_colab_setup` reproduced all 14 byte-for-byte — and that harness was itself control-tested against an untouched script first.

**5. `check_sizes.sh --update` sweeps in other people's drift.** `.script_sizes.json` on main was already stale for **116 unrelated scripts** (+3 keys pointing at deleted files). A blanket refresh would have put all of it in this PR and silently blessed unrelated shrinkage. Updated only the 18 affected entries by hand; the guard passes either way.

**6. Reproduce `navigator_check` CI faithfully by copying into a dir literally named `workspace`** and running `--root workspace` from the parent — that is what the workflow does.

## Left open (unfiled)

- `.script_sizes.json` stale for 116 scripts in autolens_workspace, plus 3 keys pointing at deleted `potential_correction` files.
- 44 pre-existing title-underline off-by-ones across `scripts/` (e.g. `scripts/multi/plot.py:2`). None introduced here.

## Heart

YELLOW 70 at ship time, `red_reasons` empty, read from `readiness --json`. Three reasons acknowledged; the manifest-drift one was **new** relative to the `searches-guide-nautilus-first` ack and was acknowledged explicitly.

## Original prompt

# Rename `double_einstein_ring` → `double_source_plane_lens` (DSPL) in @autolens_workspace

Difficulty: small
Autonomy: supervised
Priority: normal

## Original request (verbatim)

> in autolens_workspaces, can you rename all things referring to
> "double_einstein_ring" to "double_source_plane_lens", which is now the
> standard literature term

> In docs use DSPL acronym

## Why

"Double Einstein ring" describes the *image-plane morphology*; the standard
literature term for the *system* is a **double source-plane lens (DSPL)**. The
workspace already uses the new term in one place —
`scripts/imaging/features/advanced/double_einstein_ring/README.md` opens with
"double source-plane strong lenses (DSPLs)" — so this finishes a migration that
has already started, rather than introducing a new convention.

## Scope

`autolens_workspace` only. `autolens_workspace_test` and
`autolens_workspace_developer` have **zero** matches (verified by grep).

### Naming

- Directories, file names, dataset names and identifiers →
  `double_source_plane_lens`.
- Documentation prose → **DSPL**, expanded as "double source-plane lens (DSPL)"
  on first use in each file, bare `DSPL` thereafter. Section headers become
  `__DSPL__`.

### Do NOT touch

- The **21 unrelated "Einstein ring" mentions** elsewhere in `scripts/` (masks,
  arcs, `mass_stellar_dark`, interferometer, `guides/`) — they describe actual
  rings.
- Genuinely **observational** phrasing inside the renamed files. Example, in
  `simulator.py`: "They appear as two distinct Einstein rings in the image-plane,
  and can constrain Cosmological parameters in a way single Einstein ring lenses
  cannot." Substituting "DSPL" there would make the sentence wrong — it is
  describing the morphology, not the system class.

## Inventory (43 files)

| Shape | Count | Action |
|---|---|---|
| `double_einstein_ring/` directories | 4 (`scripts`+`notebooks` × `imaging`+`group`) | `git mv` |
| `plotters_double_einstein_ring.{py,ipynb}` | 2 (`guides/plot/advanced/`) | `git mv` |
| `dataset_name = "double_einstein_ring"` | 2 simulators | rename |
| Prose "double Einstein ring" / "Double Einstein Ring" | ~250 | → DSPL |
| Cross-refs from `mass_stellar_dark/{simulator,slam}.py`, `point_source/simulator_sample.py`, `imaging/features/advanced/README.md`, `guides/plot/advanced/README.md` | 6 | re-point |
| `workspace_index.json`, `llms-full.txt` | generated | **regenerate** |
| `.script_sizes.json` | generated | refresh |

## Notes / traps

- **Datasets are gitignored.** `dataset/**` is ignored except an explicit
  allowlist that does not include `double_einstein_ring`, so there are no
  committed data files to move — the simulators create them locally. Purge the
  old `dataset/{imaging,group}/double_einstein_ring/` dirs after renaming so a
  stale path cannot silently satisfy a later fit.
- **Catalogue files are generated, not hand-edited.** Regenerate with
  `python3 PyAutoHands/autohands/regenerate_navigator.py autolens` run from the
  workspace root; `.github/workflows/navigator_check.yml` gates staleness in CI.
- **`.script_sizes.json` guards against truncation.** `scripts/check_sizes.sh`
  flags any script that shrank >50% since the snapshot; moved paths will read as
  deletions. Refresh via `scripts/check_sizes.sh --update` in the same diff.
- **Notebooks are derived from scripts** (docstring → markdown cell, code → code
  cell, plus an injected Colab cell). Substitute scripts and notebooks in
  lockstep, then prove it by regeneration.
- **No smoke coverage.** `smoke_tests.txt` has no entries under these paths, so
  there is nothing to re-point — verify by running the renamed simulator/modeling
  pair directly instead.

## Sibling repos

Two path references outside the workspace would dangle and are **in scope**:

- `autolens_assistant/wiki/core/concepts/tracer.md:95`
- `autolens_assistant/skills/al_inspect_source_reconstruction.md:114`

`PyAutoLens/autolens/lens/tracer.py:206` ("e.g. double Einstein ring systems") is
prose-only with no path dependency — **out of scope**, left as-is by decision.

## Collision analysis (hand-checked 2026-07-30)

Three active tasks claim `autolens_workspace`. Source files are **fully
disjoint** — verified against each worktree's actual diff, not its scope line:

| Task | Touches | Overlap |
|---|---|---|
| `scaling-relation-bgc-anchored` | `scripts/imaging/features/scaling_relation/*` | none |
| `searches-guide-nautilus-first` | `scripts/guides/modeling/searches.py` (+ catalogue) | catalogue only |
| `extra-galaxies-multi-galaxy-lens` | `scripts/multi_galaxy/features/extra_galaxies/` | none |

The one real collision is the **generated catalogue** (`llms-full.txt`,
`workspace_index.json`): `searches-guide-nautilus-first` has already committed
regenerated copies on its open PR #388, and the other two will regenerate when
they add packages. Expected resolution: whichever PR merges later rebases and
re-runs `regenerate_navigator.py` — never hand-merge the catalogue.
