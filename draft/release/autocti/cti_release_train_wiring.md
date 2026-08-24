# CTI release-train wiring — first modern autocti release

Type: release
Target: PyAutoHands
Repos:
- @PyAutoHands
- @PyAutoNerves
- @autocti_workspace
Difficulty: medium
Autonomy: human-required
Priority: normal
Status: formalised
Filed: 2026-07-17 (backfilled from git)

Follow-up to the CTI resurrection epic (Phases 0-5; workspace_test + Heart
polling shipped 2026-07-17). Wire autocti into the release train and produce
its first modern PyPI release. Deliberately split from the epic's Phase 5:
this touches the nightly's most dangerous machinery and must be done with a
TestPyPI rehearsal, in a fresh session.

## Scope

1. **PyAutoHands**: `tag_and_merge.sh` `LIB_PROJECTS` += PyAutoCTI;
   `pre_build.sh` `run_workspace` lines for autocti_workspace (+ _test,
   generate=false); `release.yml` / `python_matrix.yml` matrices;
   `generate_release_notes.py` + `slack_release_notes.py` +
   `aggregate_results.py` repo maps; `build_util.py` `COLAB_PROJECTS` +=
   autocti; FIREWALL_ALLOWLIST tokens in Mind for every file gaining CTI names.
2. **PyAutoNerves** `autonerves/setup_colab.py`: an `autocti` `_PROJECTS` entry
   whose package list handles **arcticpy** correctly on Colab (apt
   `libgsl-dev` + `pip install numpy cython` + `arcticpy==2.6
   --no-build-isolation --no-deps` — a naive pip install downgrades numpy
   below 2.0). May need a per-project `pre_install` hook in the setup
   machinery.
3. **Notebook generation**: `generate.py autocti` (blocked today by the
   COLAB_PROJECTS registry check) → commit regenerated notebooks to
   autocti_workspace.
4. **Rehearsal then release**: TestPyPI rehearsal of the extended train
   (`release rehearse` / `release validate` through the Release Agent), fix
   fallout, then the first modern `autocti` release rides the next nightly or
   a human-authorized release. Never hand-dispatch the nightly.

## Context

- **Item 3's blocker is now a clean refusal, not a destructive one** (PyAutoLabs/PyAutoHands#215
  / PR #216, 2026-07-30). `generate.py` used to `rmtree` the whole `notebooks/`
  tree *before* reaching the `COLAB_PROJECTS` check, so probing `generate.py
  autocti` deleted 113 tracked notebooks and then aborted. It now validates up
  front and exits with "Nothing was modified", leaving the tree untouched — so
  this task can probe the registry check freely. The registration itself
  (items 1-2) is untouched and still belongs here.
- **Backlog item 3 will clear when it runs:** `autocti_workspace/notebooks/`
  currently carries 34 `Finish.` markdown cells (from the crutch sweep,
  PyAutoLabs/autocti_workspace#16) and 4 mangled code cells containing a literal
  `# %%` and `'''` — a `SyntaxError` if run — in
  `notebooks/imaging_ci/modeling/features/{cosmic_rays,non_uniform,serial_cti,visualize_full}.ipynb`,
  plus the 5 script-reference fixes from `autocti_workspace#15`. All are already
  correct in `scripts/`; one successful `generate.py autocti` clears all of them.
- **Do not hand-roll the regeneration.** `build_util.py_to_notebook` alone is not
  equivalent to `generate.py`: control-tested against an unchanged script, the
  committed notebook carries a trailing empty code cell that `py_to_notebook`
  does not emit. That cell is the signature of the pre-2026-07-24 generator
  (before PyAutoHands `6916814` a closing docstring always emitted a `# %%`), so
  these 79 notebooks predate it — expect the regeneration to drop those empty
  cells across the board, which is correct.
- Epic records: `PyAutoMind/complete/2026/07/cti-resurrection-phase{0..5}.md`.
- PyAutoCTI pyproject floors are release-ready (setuptools-scm, Phase 0);
  CI green via Heart lib-tests (Phase 3); Heart polls the CTI repos (Phase 5).
- arcticpy traps + CI install recipe: `PyAutoCTI/AGENTS.md` and
  `autocti_workspace_test/.github/scripts/smoke_install.sh`.
- **Why the registry gap stayed invisible.** `autocti_workspace` is absent from
  `PyAutoHands/pre_build.sh`'s `run_workspace` matrix entirely (the
  `generate=true` set is `autofit_workspace`, `autogalaxy_workspace`,
  `autolens_workspace`, `HowToGalaxy`, `HowToLens`, `HowToFit`), so no release
  path has ever exercised `generate.py autocti`. Corroborating: **0 of the
  repo's 79 notebooks carry a Colab setup cell**, dating them to before
  `inject_colab_setup` became strict. They do still track `scripts/` 1:1 (79
  scripts, 79 notebooks, no orphans either way), so they were maintained by
  some path that no longer works. Item 1's `run_workspace` line is what closes
  this blind spot, not just item 3.
- **The destructive-ordering defect is closed, tests included** — verified on
  `main` 2026-08-24. `generate.py` validates against `build_util.COLAB_PROJECTS`
  before `generate_project_folders()` and the `rmtree`, and a `finally` on the
  per-script loop removes the intermediate `.ipynb` so a mid-loop failure cannot
  strand one in `scripts/`. `PyAutoHands/tests/test_generate_validates_project.py`
  pins all three properties (exit non-zero with a clean `git status` and no
  stray `.ipynb`; the message naming both registries; a known project still
  regenerating). Do not re-file it: that half was filed **three** times
  independently before being consolidated, and its prompt
  (`draft/bug/pyautohands/generate_rejects_autocti_after_deleting_notebooks.md`)
  was folded into this file and retired on 2026-08-24 once only the
  registration remained.
- `autocti_workspace/AGENTS.md` currently states plainly that regeneration is
  blocked because `autocti` is unregistered. That line is **accurate today** and
  becomes wrong the moment item 1 lands — update it as part of this task.

## Validation

- `generate.py autocti` exits 0 from `autocti_workspace/`; all 79 notebooks
  regenerate; no code cell contains a literal `# %%` or `'''`; no markdown cell
  is `Finish.` (this is the backlog above clearing in one run).
- The trailing-empty-code-cell diff is expected across all 79 notebooks — see
  the "do not hand-roll" note; control-test against an unchanged script before
  trusting any regeneration path here.
- `generate.py <unknown-project>` still exits non-zero with `notebooks/` intact
  and no stray `.ipynb` beside any script — `tests/test_generate_validates_project.py`
  must stay green once `autocti` joins `COLAB_PROJECTS` (its unknown-project
  fixture currently uses `autocti` as the unknown name and will need a
  genuinely-unregistered one instead).
- `autocti_workspace/AGENTS.md`'s *Notebook regeneration* paragraph matches
  whatever the chosen path actually is.
