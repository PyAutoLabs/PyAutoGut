Removed the `Finished.` / `Finish.` trailing-docstring crutch from every workspace, and fixed the two generator defects behind it. **169 occurrences removed across 11 repos; 12 PRs, all merged; CI 56/56 green.**

## The premise was half wrong

The crutch existed because notebook generation supposedly "cut off weird" when a script's last cell was not a docstring. **That shape is already safe.** Deleting the trailing block and running the real `add_notebook_quotes` → `ipynb-py-convert` chain gives a complete, unmangled final code cell (`imaging/features/no_lens_light/slam.py` 23→22 cells; `imaging/features/pixelization/source_science.py` 41→40), as does every other tail shape (no trailing newline / trailing blanks / trailing comment). So that half needed only a regression test.

## Two other generator defects were real and shipping

**1. The docstring-opener emitted its marker after a single newline.** `py2nb` splits the intermediate `.py` on the literal `"\n\n# %%\n"` — the marker must be preceded by a *blank* line. The opener branch of `add_notebook_quotes` emitted `"# %%\n"` after one newline, so a column-0 docstring opened on the line *immediately after code* never split; the marker and both `'''` delimiters landed inside the preceding code cell as literal text. The *closing* path was always fine (it emits `"'''", "\n\n"` first).

**2. Two scripts carried hand-written `# %%` markers in their source.** `guides/hpc/example_cpu_and_gpu.py` in `autolens_workspace` and `autogalaxy_workspace`, lines 1 and 36. An authored marker collides with the generated one and mangles the file *regardless of fix 1* — which is why 4 of the 13 broken cells survived the first regeneration pass. `add_notebook_quotes` now **raises** on a column-0 `# %%` in source.

**13 committed notebook code cells were `SyntaxError`** before this: `autolens_workspace` 4, `autogalaxy_workspace` 3, `autocti_workspace` 4, `HowToLens` 2.

## The two constraints that make the fix safe

Both load-bearing, both verified empirically rather than argued:

1. **Only when `out` is non-empty.** `py2nb` strips a *leading* `# %%\n` header; a leading blank line defeats that strip and yields a spurious empty first code cell.
2. **Only when not already blank-terminated.** Unconditional emission appends a trailing blank line to *every* code cell in *every* generated notebook.

Proof pair: regenerating `autofit_workspace` (33 notebooks, none with the target shape) with the fix and **no** sweep gives a **zero-byte diff**; regenerating `HowToLens` (41 notebooks, 2 with the shape) changes **exactly those 2 files**, with `llms-full.txt` / `workspace_index.json` byte-identical. Use that pattern for any future generator change — a repo without the shape must produce zero diff, a repo with only the shape must produce exactly it.

## Traps hit

**CRLF nearly shipped ~6000 lines of churn.** The first sweep pass used `pathlib.Path.read_text()` / `write_text()`, which normalises line endings. CRLF `.py` counts: `autocti_workspace_test` 61, `autocti_workspace` 43, `autofit_workspace_test` 14, `euclid_strong_lens_modeling_pipeline` 11 — and `autolens_workspace` **0**, so a canary check on the biggest repo proves nothing. Result was `35 files changed, 5971 insertions(+), 6109 deletions(-)` where `138 deletions(-)` was intended. The tell is *insertions appearing at all* in a delete-only change. Reverted and redone with `newline=""`. Note `Path.read_text(newline="")` needs Python 3.13; on 3.12 use `with f.open(newline="")`. And `$`-anchored regexes stop matching once `\r` is preserved — match against `line.rstrip("\r\n")` but keep the original line for output.

**The census was short by two, and the gap hid a whole shape.** `re.search(r"\bFinish", …)` does **not** match `__Finish__` — the preceding `_` is a word character. Two empty `__Finish__` section headers were invisible to the count *and* to the file-level prefilter, so no downstream logic could have found them. They needed different handling (delete the header plus its preceding blank line). Real total 168, not 166. Reconcile per-shape counts against a raw `grep -c` and treat any gap as an unclassified shape.

**A line scanner cannot tokenize this corpus.** Files carrying the crutch also contain function docstrings that open with text on the delimiter line (`"""Load a centres JSON file, …`), so sequential `"""`-toggling inverts every boundary after one. The sweep used `tokenize.generate_tokens` and matched each occurrence to its exact `STRING` token span. Five shapes resulted: 130 sole-content blocks, 32 in-block lines, 2 sentence-leading, 2 `__Finish__` headers, 1 commented-out.

**`__Env__` blocks change form, and that needed proving.** Removing the word above an `__Env__` header turns the canonical merged form into the standalone-fallback form. Both are supported, but rather than assume it, `env_config.read_env_declaration` was run against the old and new content of all 169 changed files: **169 identical, 0 changed, 0 errors.**

**A green-on-main CI check failed on the branch, purely from base drift.** `navigator / Navigator paths + banner lint` failed on `autolens_workspace` with 5 missing refs in READMEs the task never touched. `main` had moved 13 commits and `3dc5058e docs: fix 5 README refs newly gated by PyAutoHands #213` had already fixed exactly those. Rebased PyAutoHands / autolens / autogalaxy; green. The rebase also released the `multi_galaxy/simulator.py` carve-out (#378 merged mid-task) and surfaced one new occurrence that had arrived on main (`autogalaxy_workspace/scripts/multi_galaxy/features/extra_galaxies/simulator.py`).

**The last merge conflicted on line endings, not content.** `autocti_workspace` #16 hit whole-file conflicts starting at line 1 because the concurrently-merged `script-prose-ref-drift` #15 normalised `scripts/dataset_1d/advanced/database/examples/data_fitting.py` and `scripts/plot/plotters/ImagingCIPlotter.py` from CRLF to LF — the same trap, shipped. Resolved by resetting to `main` and re-sweeping so the commit follows main's endings, rather than rebasing and reintroducing CRLF.

## `markdown/` — edited in place, deliberately

Five curated pages carried a real occurrence. Human-approved decision: delete the paragraph in place rather than re-running `generate_markdown.py`, which re-executes real model fits and re-quantizes every figure PNG — large binary churn for a one-paragraph deletion. **No PNG is touched in any PR.** Two of the five (`autogalaxy_workspace/markdown/interferometer/fit.md`, `autofit_workspace/markdown/overview/overview_1_the_basics.md`) also carried a trailing **empty** ` ```python ` fence, the old generator's empty final code cell, removed with the paragraph. Most `Finish` hits under `markdown/` are Nautilus status tables (`Finished | 18 | 1 | …`) and must be left alone.

## Not done — `autocti_workspace` notebooks

`generate.py autocti` **raises**: `autocti` is absent from `COLAB_PROJECTS` (`build_util.py`) and from `_PROJECTS` (PyAutoNerves `setup_colab.py`), so `inject_colab_setup` refuses the project — after `generate.py` has already `rmtree`'d `notebooks/`. That repo's `scripts/` are swept, but its notebooks retain **34 `Finish.` cells and 4 mangled cells**. Registering `autocti` is a feature (Colab support, and `arcticpy` downgrades numpy), deliberately not bundled.

Why it stayed invisible: `autocti_workspace` is absent from `pre_build.sh`'s `run_workspace` matrix entirely, and **0 of its 79 notebooks carry a Colab setup cell**, dating them to before that check became strict.

## PRs (all merged)

PyAutoHands#214 (the fix, merged first as the gate) · autolens_workspace#384 (61) · autocti_workspace#16 (35) · autocti_workspace_test#12 (27) · autogalaxy_workspace#187 (22) · autofit_workspace#127 (11) · autofit_workspace_test#79 (5) · euclid_strong_lens_modeling_pipeline#38 (3) · autolens_workspace_test#233 (1) · autolens_workspace_developer#120 (1) · HowToFit#39 (1) · HowToLens#62 (0 — mangled-cell repair only).

Verified after merge: residual on `main` is **0** in all 12 repos; PyAutoHands full suite **255 passed**.

## Follow-ups filed

- `draft/bug/pyautohands/generate_rejects_autocti_after_deleting_notebooks.md` — the autocti blocker. It had been filed **three times independently** (dataset-bulk leg 6, `script-prose-ref-drift`, and this task); consolidated into one and the two duplicates deleted. It gates three separate merged sweeps from reaching that repo's notebooks, not just this one.
- `draft/bug/hands/notebook_quotes_string_literal_closing_delimiter.md` — a code string literal's column-0 *closing* delimiter is read as a docstring, inverting every boundary after it. Latent: one occurrence, `autolens_workspace_test/gallery/gallery_build.py:42`, outside `scripts/` so never converted. Needs real tokenization, shared with `navigator.py`.

## Brain override

The Feature Agent returned too-large (score 29) and a generic `design / core_api / workspace_examples / docs` split off its repo-count proxy. `design` and `core_api` were vacuous (no library API touched; design settled up front) and `docs` was empty — the convention was documented nowhere (`AGENTS.md`, `CONTRIBUTING.md`, `PyAutoHands/docs/` and the Brain skills all checked). Overridden to one PR per repo behind a single PyAutoHands-first gate.

## Original prompt

# Remove the `Finished.` / `Finish.` trailing-docstring hack from every workspace

Type: maintenance
Target: workspaces
Repos:
- PyAutoHands
- autolens_workspace
- autogalaxy_workspace
- autofit_workspace
- autocti_workspace
- autolens_workspace_test
- autofit_workspace_test
- autocti_workspace_test
- autolens_workspace_developer
- HowToFit
- euclid_strong_lens_modeling_pipeline
Difficulty: medium
Autonomy: supervised
Priority: medium

## Original request (verbatim)

> Lots of workspace examples end with a cell `Finished.`, or have the word near
> the end. This was a hack becuase notebook generation would cut off weird if
> the last bit wasnt a docstring in the Python cell. can you make sure generate
> does not do this anymore, than remove all of these `Finished.` statements
> thoruhgout all workspaces.

## Investigation — what generation actually does today

Notebook generation is `build_util.py_to_notebook` →
`autohands/add_notebook_quotes.py` → `ipynb-py-convert`'s `py2nb`. `py2nb`
splits the intermediate `.py` on the literal `'\n\n# %%\n'` and treats a chunk
starting with `'''` / `"""` as a markdown cell.

**Finding 1 — the crutch is already obsolete.** A script ending in a *code*
cell converts correctly. Verified end-to-end on two real scripts by deleting
their trailing `"""\nFinish.\n"""` block and re-running the real
`add_notebook_quotes` + `ipynb-py-convert` chain:

| script | with block | without block |
|---|---|---|
| `autolens_workspace/scripts/imaging/features/no_lens_light/slam.py` | 23 cells, last = markdown `Finish.` | 22 cells, last = code, complete and unmangled |
| `autolens_workspace/scripts/imaging/features/pixelization/source_science.py` | 41 cells, last = markdown `Finish.` | 40 cells, last = code, complete and unmangled |

Also verified against every plausible tail shape (trailing newline / no trailing
newline / trailing blank lines / trailing comment): all four produce an
identical, complete final code cell. So there is nothing to fix for the shape
the hack was written for — but it must be **pinned by a regression test** so the
crutch can never be re-justified.

**Finding 2 — there IS a live "cuts off weird" bug, in the same family.** A
column-0 docstring opened on the line *immediately after* a non-blank code line
(no blank line between) is never split into a markdown cell. On a docstring
*opener* `add_notebook_quotes` emits (`add_notebook_quotes.py:133`):

```python
out.extend(["# %%", "\n", "'''\n"])
```

which yields `...code\n# %%\n'''\n` — a **single** newline before the marker,
where `py2nb` needs `\n\n# %%\n`. The split never happens, so the marker and
both `'''` delimiters land inside the preceding code cell as literal text.
(The *closing* path is fine: it emits `"'''", "\n\n"` first, so the following
code boundary is always correctly separated.)

Reproduced minimally, and shipped in a committed notebook today —
`autolens_workspace/notebooks/interferometer/features/pixelization/many_visibilities_preparation.ipynb`
has a code cell ending:

```python
np.save(
    file=dataset_path / f"nufft_precision_operator_{mask_radius}.npy",
    arr=nufft_precision_operator,
    allow_pickle=False,
)
# %%
'''
To load the `nufft_precision_operator` matrix from hard-disk in your model-fit, you can use the code:
'''
```

That cell is a `SyntaxError` if a user runs it. Source is
`scripts/interferometer/features/pixelization/many_visibilities_preparation.py:209`
— a `"""` with no blank line above it.

A scan of the converted-script surface found this shape at 49 sites; after
excluding non-converted paths (`.github/scripts/`, `gallery/`, module docstrings
after a shebang) the live converted-script sites are:

- `autolens_workspace/scripts/interferometer/features/pixelization/many_visibilities_preparation.py:209`
- `autolens_workspace/scripts/interferometer/features/subhalo/simulator.py:117`
- `autogalaxy_workspace/scripts/interferometer/features/pixelization/many_visibilities_preparation.py:193`
- `autocti_workspace/scripts/imaging_ci/modeling/features/{cosmic_rays,serial_cti,visualize_full,non_uniform}.py`
- `HowToLens/scripts/chapter_2_lens_modeling/tutorial_4_dealing_with_failure.py:429`,
  `HowToLens/scripts/simulator/source_complex.py:71`
- plus `autocti_workspace_test/legacy/**` (not converted; ignore)

### Fix (PyAutoHands)

In the opener branch of `add_notebook_quotes`, emit the separating blank line
`py2nb` requires when it is missing:

```python
if pending_code_boundary:
    out.extend(pending_lines)
    pending_lines = []
    pending_code_boundary = False
if out and not "".join(out[-3:]).endswith("\n\n"):
    out.append("\n")
out.extend(["# %%", "\n", "'''\n"])
```

Two constraints the implementation must respect:

1. **Only when `out` is non-empty.** `py2nb` strips a *leading* `# %%\n`
   header; a leading `\n` would defeat that strip and produce a spurious empty
   first code cell.
2. **Only when not already blank-terminated.** Emitting the newline
   unconditionally appends a trailing blank line to *every* code cell, churning
   every generated notebook in every workspace for no reason. The adjacent-
   docstring path already ends with `\n\n` and must stay untouched (its
   regression test `test_adjacent_docstrings_generate_separate_markdown_cells`
   must keep passing).

### Tests to add

- a script whose docstring follows code with no blank line yields a separate
  markdown cell, and no cell source contains `# %%` or `'''`;
- a script ending in a code cell yields a complete final code cell (pins
  Finding 1 — the reason the `Finish.` hack is unnecessary);
- a script starting with a docstring still yields exactly one leading markdown
  cell and no empty first code cell.

### Out of scope (file separately)

A column-0 **closing** `"""` of a triple-quoted *string literal* in code toggles
docstring state and mangles the cell the same way. One occurrence workspace-wide
— `autolens_workspace_test/gallery/gallery_build.py:42` — which sits outside
`scripts/` and is therefore never converted. Fixing it needs real tokenization,
not a line-prefix test.

## Removal census — 166 occurrences, 166 files, 10 repos

| repo | occurrences |
|---|---|
| autolens_workspace | 61 |
| autocti_workspace | 35 |
| autocti_workspace_test | 27 |
| autogalaxy_workspace | 21 |
| autofit_workspace | 11 |
| autofit_workspace_test | 5 |
| euclid_strong_lens_modeling_pipeline | 3 |
| autolens_workspace_test | 1 |
| autolens_workspace_developer | 1 |
| HowToFit | 1 |

Five shapes, each needing different handling — a blanket regex over all of them
is wrong:

1. **126 × sole-content trailing block at EOF** —
   `"""\nFinish.\n"""` / `"""\nFinished.\n"""` as the entire final docstring.
   Delete the block and the blank line before it, leaving the file ending on
   real content with a single trailing newline.
2. **33 × a line inside a block that continues** — the block goes on with
   `__Env__` (developer-only, stripped from artifacts anyway), `__JAX Variant__`,
   or similar. Delete the `Finish.` line and the blank line after it. Note that
   for the `__Env__` cases the artifact-visible markdown cell today is *exactly*
   `Finish.` and nothing else, because `strip_env_declarations` removes the
   `__Env__` section; after removal the block holds only `__Env__` and the
   existing standalone-fallback path drops the whole block — which is correct.
3. **2 × `Finished.` leading a real sentence** — drop only the word:
   - `autolens_workspace/scripts/cluster/lenstool/modeling.py:503`
     ("Finished. The README in this folder is the narrative companion…")
   - `autolens_workspace/scripts/guides/point_source_pairing.py:182`
     ("Finished. For the production-scale picture — real solver, …")
4. **2 × `__Finish__`** — an empty trailing section header (no content follows
   it) in `{autolens,autogalaxy}_workspace/scripts/imaging/features/multi_gaussian_expansion/modeling.py`.
   Delete the header line.
5. **5 × indented or commented variants** — the same block indented inside a
   function body, or inside a fully commented-out block. Not converted to
   markdown cells (only column-0 delimiters are), so pure dead cruft:
   `autolens_workspace/scripts/interferometer/features/subhalo/sensitivity/start_here.py:305`,
   `autocti_workspace_test/imaging_ci/profiling/pruning/{parallel_x1,parallel_x3,serial_x1}.py`,
   `autolens_workspace_developer/slam_pipeline/dspl.py:304`.

The convention is documented nowhere (`AGENTS.md`, `CONTRIBUTING.md`,
`PyAutoHands/docs/`, the Brain skills were all checked) — so no doc updates are
needed and nothing is authorising new ones.

## Generated artifacts

- **`notebooks/`, `llms-full.txt`, `workspace_index.json`** — regenerate with
  `generate.py` in `autolens_workspace`, `autogalaxy_workspace`,
  `autofit_workspace`, `autocti_workspace` and `HowToFit`. Conversion only, no
  script execution — cheap. (`llms-full.txt` / `workspace_index.json` contain no
  `Finish` today; they still get rewritten and must be committed from the same
  run so the catalogue cannot drift.) The `_test` / `_developer` repos and
  `euclid_strong_lens_modeling_pipeline` have no generated artifacts at all.
- **`markdown/`** — do **not** re-run `generate_markdown.py`. Most `Finish`
  hits in `markdown/` are Nautilus sampler status tables (`Finished | 18 | 1 |
  …`), not the hack. Only five pages carry a real one:
  `autolens_workspace/markdown/{point_source/simulator,group/simulator,interferometer/simulator}.md`,
  `autogalaxy_workspace/markdown/interferometer/fit.md`,
  `autofit_workspace/markdown/overview/overview_1_the_basics.md`.
  A re-render executes real model fits and re-encodes every figure PNG, so it
  would churn large binaries for a one-paragraph deletion
  ([[feedback_ship_workspace_binary_leak]]). Delete the paragraph in place and
  say so in the PR.

## Validation

- `pytest PyAutoHands/tests/test_add_notebook_quotes.py` green, including the
  pre-existing adjacent-docstring tests.
- `generate.py` runs clean in each of the five artifact-bearing repos.
- No generated notebook contains a code cell with a literal `# %%` or `'''`
  (this currently *fails* on `many_visibilities_preparation.ipynb` and must pass
  after the fix) — assert it across the whole `notebooks/` tree.
- `grep -rn "Finish" scripts/ *.py` returns nothing but genuine prose in each
  swept repo.
- Every notebook whose script lost a trailing block has exactly one fewer cell
  than before, with the final cell a complete code cell.
- Curated smoke tests pass for the repos that have them
  ([[feedback_smoke_tests_small_subset]], [[feedback_two_env_profiles_smoke_vs_release]]).

## Claim contention (hand-read — `worktree_check_conflict` never fires,
[[feedback_worktree_conflict_guard_never_fires]])

- **`autolens_workspace` — claimed by THREE active tasks**:
  `extra-galaxies-point-source`, `likelihood-function-jax-pointer`,
  `multi-galaxy-imaging-parity`. This task edits 61 files across the whole repo
  and regenerates every notebook, so unlike the previous parallel decisions
  there *is* real overlap risk with all three.
- **`autogalaxy_workspace`** — claimed by `likelihood-function-jax-pointer`.
- **`autolens_workspace_test`** — claimed by `vacuous-jax-assertions`.
- **`PyAutoHands`** — claimed by `python-312-release-surfaces`, live with
  uncommitted work in `.gitignore`, `bin/autohands`, `docs/internals.md`,
  `pre_build.sh` and the `run_logs/` + `=3.12` cleanup. **Zero overlap** with
  `autohands/add_notebook_quotes.py` / `tests/test_add_notebook_quotes.py`, so
  parallel is safe here on the same precedent as prior decisions.
- Uncontended: `autofit_workspace`, `autocti_workspace`,
  `autocti_workspace_test`, `autofit_workspace_test`,
  `autolens_workspace_developer`, `HowToFit`,
  `euclid_strong_lens_modeling_pipeline`.

Suggested phasing follows from that, not from repo count
([[feedback_brain_repo_count_difficulty_proxy]]): PyAutoHands fix first, then
the uncontended sweep, then the contended repos once their branches land.
