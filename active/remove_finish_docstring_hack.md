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
