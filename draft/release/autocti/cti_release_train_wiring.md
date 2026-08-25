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
   `aggregate_results.py` repo maps; `autohands/build_util.py` `COLAB_PROJECTS`
   += autocti (still the six autofit/autogalaxy/autolens/howto* keys as of
   2026-08-25); FIREWALL_ALLOWLIST tokens in Mind for every file gaining CTI
   names.
2. **PyAutoNerves** `autonerves/setup_colab.py`: an `autocti` `_PROJECTS` entry
   whose package list handles **arcticpy** correctly on Colab (apt
   `libgsl-dev` + `pip install numpy cython` + `arcticpy==2.6
   --no-build-isolation --no-deps` — a naive pip install downgrades numpy
   below 2.0). May need a per-project `pre_install` hook in the setup
   machinery.
3. **Notebook generation**: `generate.py autocti` (blocked today by the
   COLAB_PROJECTS registry check) → commit regenerated notebooks to
   autocti_workspace. Registering autocti (items 1-2) is one of two ways to
   unblock this; the other is a documented **no-Colab mode** in `generate.py`
   for workspaces whose notebooks are not meant to carry a Colab setup cell —
   which is what autocti_workspace's 79 notebooks look like today (see
   Context). Whichever is chosen, `autocti_workspace/AGENTS.md`'s *Notebook
   regeneration* line must be updated to match: it currently implies the
   standard path works, and it does not.
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
  (items 1-2) is untouched and still belongs here. That fix is closed with a
  regression test — `PyAutoHands/tests/test_generate_validates_project.py`
  drives `generate.py` as a subprocess against a seeded git workspace and pins
  the ordering, since the failure is invisible in a passing run — and a
  `finally` on the per-script loop now removes the intermediate `.ipynb`, so a
  mid-loop failure can no longer strand one inside `scripts/`. Note the old
  safety was accidental: the root-level `start_here*.py` loop injects Colab
  setup *before* the rmtree, so only a workspace WITHOUT a root `start_here.py`
  ever took the destructive path — which is why this surfaced on autocti and
  nowhere else.
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
- **Why this stayed invisible.** `autocti_workspace` is absent from
  `PyAutoHands/pre_build.sh`'s `WORKSPACE_SPECS` matrix entirely — the list is
  autofit/autogalaxy/autolens `_workspace` (+ `_test`), the three HowTos,
  `euclid_strong_lens_modeling_pipeline`, the two `_developer` repos and
  `autolens_assistant` (verified 2026-08-25). No release path has ever
  exercised `generate.py autocti`, so the breakage was unobservable.
  Corroborating: **0 of the repo's 79 notebooks carry a Colab setup cell**,
  dating them to before `inject_colab_setup` became strict. They do still track
  `scripts/` 1:1 (79 scripts, 79 notebooks, no orphans either way), so they were
  maintained by some path that no longer works. This is the evidence behind item
  3's either/or — these notebooks may simply not be Colab notebooks.
- **Item 1 and item 3 need reconciling.** Item 1 wires autocti_workspace into
  `pre_build.sh` with `generate=false`, while item 3 regenerates its notebooks.
  Not contradictory — item 3 can be a one-off — but with `generate=false` the
  notebooks will drift from `scripts/` again after it. Decide deliberately
  whether autocti_workspace joins the `generate=true` set.
- Epic records: `PyAutoMind/complete/2026/07/cti-resurrection-phase{0..5}.md`.
- PyAutoCTI pyproject floors are release-ready (setuptools-scm, Phase 0);
  CI green via Heart lib-tests (Phase 3); Heart polls the CTI repos (Phase 5).
- arcticpy traps + CI install recipe: `PyAutoCTI/AGENTS.md`,
  `autocti_workspace_test/.github/scripts/smoke_install.sh` and
  [[project_cti_resurrection_epic_scoped]].

## Validation

- `generate.py <unknown-project>` exits non-zero with `notebooks/` **intact**
  and no stray `.ipynb` beside any script. Already true and pinned by
  `test_generate_validates_project.py` — do not regress it while adding the
  registration or the no-Colab mode.
- `generate.py autocti` exits 0 from `autocti_workspace/`; all 79 notebooks
  regenerate; no code cell contains a literal `# %%` or `'''`; no markdown cell
  is `Finish.`.
- `autocti_workspace/AGENTS.md`'s *Notebook regeneration* line matches whatever
  path was actually chosen.
- **Do not hand-roll the regeneration to satisfy the above** — see the
  control-test note in Context. Control-test against an *unchanged* script
  before trusting any regeneration path here; that is what caught the
  `py_to_notebook` inequivalence in the first place.

## Provenance

Folded 2026-08-25 from `draft/bug/pyautohands/generate_rejects_autocti_after_deleting_notebooks.md`,
which the fix to PyAutoLabs/PyAutoHands#215 reduced to this task's items 1-3
and which named this file as their owner. That prompt was itself a 2026-07-30
consolidation of three independently-filed reports of the same defect. Its
unique content — the pre_build matrix gap, the no-Colab-mode alternative, the
AGENTS.md line, and the validation criteria above — is carried here; the draft
was deleted.
