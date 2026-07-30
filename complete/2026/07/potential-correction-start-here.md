Moved the potential-correction technique overview out of `guides/advanced/` and into the feature folder its other material already occupied, and gave `autolens_assistant` its first knowledge of the technique.

## What shipped

| Repo | PR | Merge commit |
|---|---|---|
| autolens_workspace | [#393](https://github.com/PyAutoLabs/autolens_workspace/pull/393) | `c25dfca7` |
| autolens_assistant | [#99](https://github.com/PyAutoLabs/autolens_assistant/pull/99) | `8c6877b1` |

`scripts/guides/advanced/potential_correction.py` → `scripts/imaging/features/advanced/potential_correction/start_here.py`, completing the `start_here.py` + `likelihood_function.py` pair the interferometer sibling already had. Retitled to the `X: Start Here` convention, added a `__Related Examples__` block, re-pointed three cross-references, regenerated notebooks + `llms-full.txt` + `workspace_index.json`. **Zero code lines changed** — the diff is three docstring hunks.

New `autolens_assistant/skills/al_potential_correction.md` (full skill, not a stub): the regime gate, arc masking, one-shot `FitDpsiSrcImaging`, reading the `dkappa` map, iterative refinement with gauge constraints, evidence-sampling the regularization, and the interferometer sparse-operator route. Registered in `skills/README.md`, cross-linked both ways with `al_subhalo_detect`, citation-map row added.

## The destination was not the requested path

The request said `imaging/features/poitential_corrections/start_here.py`. The actual destination is `imaging/features/advanced/potential_correction/start_here.py` — singular, one level deeper. The requested folder did not exist; the singular one did, already held `likelihood_function.py`, was already listed in `advanced/README.md`, and matched the interferometer twin's naming. Taking the path literally would have orphaned `likelihood_function.py` and split the feature across two locations. Human-confirmed before any edit.

## Findings

**The `__Env__` rationale was factually wrong.** The script declared `ENV: full_datasets` and justified it as *"Guides load committed full-resolution FITS; SMALL_DATASETS would mismatch the pre-existing 100x100 data shape."* That is boilerplate inherited from the blanket `guides/` profile rule — the script **simulates in-memory** (`al.SimulatorImaging`, line 75) and reads no FITS. The real reason is the dpsi-mesh sparsity crash (`RegularDpsiMesh(factor=2)` too sparse → `mesh.py:get_itp_box_ctr` raises "The dpsi grid is too sparse"), already documented in `profile_release.yaml`. Declaration kept, reason rewritten.

**In-file `ENV:` declarations defeat profile patterns — by design, and it is easy to misread.** Verifying that `profile_release.yaml` needed no change first *appeared* to show a regression: `PYAUTO_SMALL_DATASETS=0` resolved at the old path but was absent at the new one, despite the destination pattern existing. It was an artifact — the old file had already been moved, so its declaration could not be read. Restoring it from `HEAD` and re-resolving gave byte-identical environments. The mechanism: `apply_profile` order is scrub → defaults → overrides → derivation → **declarations**, and each declaration token *unsets* its managed vars. So `full_datasets` releases `PYAUTO_SMALL_DATASETS` no matter which pattern matched, making the `potential_correction` patterns in `profile_release.yaml` effectively redundant for any script carrying that declaration.

**`.script_sizes.json --update` sweeps unrelated drift.** A full refresh rewrote 132/126 lines — the snapshot was already stale repo-wide. Only the moved script's single entry was re-pointed instead, keeping the PR honest.

**`pgrep -f` in a poll loop matches itself.** A waiter built as `until ! pgrep -f "run_script.py"` never exits, because the waiter's own command line contains the pattern. Wait on a captured PID with `kill -0` instead.

## Follow-up filed

[PyAutoLens#666](https://github.com/PyAutoLabs/PyAutoLens/issues/666) — **pre-existing, not caused by this change.** `IterFitDpsiSrcImaging` places its `dkappa` peak at (-0.55, 0.85) against the true subhalo at (1.41, 0.00), with log evidence 4.2e3 versus the one-shot's 9.2e3 — while the script claims it captures compact perturbers "more faithfully than a single linearization". Most likely cause: the imaging example cold-starts `solve_joint_optimization()` while the interferometer sibling warm-starts from the one-shot (`x0=fit.src_dpsi_slim`) and re-optimizes regularization each step (`reg_optimize_every=1`).

## Validation

- Moved script runs green at the new path: exit 0, 534s local against the 1800s cap (CI records 235.7s; ~2.3x is WSL). Joint fit recovers the subhalo — `dkappa` peak (1.45, 0.15) vs true (1.41, 0.00).
- Resolved CI environment proven byte-identical old-path vs new-path.
- No new `SyntaxWarning`s (5 before, 5 after — pre-existing in the science docstrings).
- CI: workspace 4/4 (navigator paths, catalogue staleness, smoke 3.12, smoke 3.13); assistant 2/2 (boundary, wiki-currency).
- `audit_skill_apis.py` 0 missing/broken across 67 files / 142 symbols — **verified non-vacuous with a positive control** (injected `al.pc.NotARealSymbolXYZ` → 143 symbols / 1 flagged, then removed).
- Every `al.*` symbol in the skill grounded by introspection against the installed stack (2026.7.23.1), not recall. The one snippet not lifted from a validated workspace script was corrected from a hand-rolled `np.sum(chi_squared_map)/grid.shape[0]` to the real `fit.reduced_chi_squared`.
- No stale `guides/advanced/potential_correction` reference anywhere in the repo post-merge.

## Process notes

- **Brain override.** Feature Agent scored `too-large` (score 12) and proposed four generic phases (design / core_api / workspace_examples / docs). Overridden to one phase — a file move plus one authored skill, zero library API change, so `core_api` was vacuous and its "public-API ripple" risk false. Same repo-count-proxy misfire recorded on `scaling-relation-bgc-anchored` as `too-large/13`.
- **Parallel claim, human-authorised.** Three other tasks already claimed `autolens_workspace` (`scaling-relation-bgc-anchored` #385, `searches-guide-nautilus-first`, `extra-galaxies-multi-galaxy-lens` #387). Footprints disjoint; the shared surface was only the regenerated catalogue/notebooks.
- **Heart YELLOW acknowledged** (score 70, `red_reasons: []`): workspace validation not passing (cloud#30516167217); manifest drift: tenant firewall (organ code) — 2 mismatches vs `repos.yaml`; release validation stale. The manifest-drift reason was **new** and not covered by the prior `searches-guide-nautilus-first` ack, so it was acknowledged explicitly rather than carried over.

## Known gap

No `wiki/core/` page for gravitational imaging. `wiki/core/concepts/substructure_and_subhalos.md` names the technique in its literature path but does not cover the `al.pc` implementation; the skill points there. Authoring a dedicated page was offered and declined for this pass — worth revisiting, since `_style.md` prefers a skill to have wiki content behind it.

## Original prompt

# Move the potential-correction guide into features/ as start_here.py, and teach the assistant

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
- autolens_assistant
Difficulty: small
Autonomy: supervised
Priority: normal
Status: draft

## Verbatim request

> make guides/advanced/potential_corrections.py instead be
> imaging/features/poitential_corrections/start_here.py, make sure assistant know about it

## Decisions taken (human-confirmed)

1. **Destination** is `scripts/imaging/features/advanced/potential_correction/start_here.py`
   — *not* a new plural `features/potential_corrections/` folder. The singular folder already
   exists one level deeper, already holds `likelihood_function.py`, is already listed in
   `imaging/features/advanced/README.md`, and its interferometer twin already carries exactly
   this `start_here.py` + `likelihood_function.py` pair. The literal path in the request would
   have orphaned `likelihood_function.py` and diverged from the interferometer naming.
2. **Assistant leg** is a new full `skills/al_potential_correction.md`, not just path pointers.
   `autolens_assistant/` has *zero* mentions of potential correction today — no skill, no wiki
   page — so "make sure assistant knows about it" is an authoring job, not a re-pointing job.
3. **Brain override — single phase, not four.** The Feature Agent scored this `too-large`
   (score 12) and proposed the four generic phases design/core_api/workspace_examples/docs.
   Overridden: this is one file move plus one authored skill, with **zero** library API change,
   so `core_api` is vacuous and `design` has nothing to decide. Its "Public-API change may
   ripple to downstream repos" risk is likewise false here. Same repo-count-proxy misfire the
   `scaling-relation-bgc-anchored` entry already records as `brain-override: too-large/13`.
4. **Parallel claim on `autolens_workspace`, human-authorised.** `scaling-relation-bgc-anchored`
   (autolens_workspace#385, status `workspace-dev`) holds a claim on the same repo, but its
   worktree is empty — zero commits, zero uncommitted changes. Script footprints are disjoint
   (`features/advanced/potential_correction/` here vs `features/scaling_relation/` +
   `multi_galaxy/features/scaling_galaxies/` there). The only real overlap is the regenerated
   `notebooks/` + `llms-full.txt` + `workspace_index.json`, which that task's own prompt already
   handles with its "whichever merges last regenerates" convention.

## Verified starting state

- Source file: `scripts/guides/advanced/potential_correction.py`, 347 lines (note: singular
  `potential_correction`, not the plural in the request). Notebook twin at
  `notebooks/guides/advanced/potential_correction.ipynb`.
- Destination folder `scripts/imaging/features/advanced/potential_correction/` exists and
  contains **only** `likelihood_function.py` — no `start_here.py`, and no `__init__.py`.
  Its interferometer twin `scripts/interferometer/features/advanced/potential_correction/`
  also has no `__init__.py`, so the missing `__init__.py` is a pre-existing convention in
  both potential-correction folders (every *other* sub-feature folder — `extra_galaxies`,
  `pixelization`, `double_einstein_ring`, `mass_stellar_dark`, `los_halos` — does have one).
- `scripts/guides/advanced/README.md` does **not** list `potential_correction` (nor
  `over_sampling_chaining`) — so the move removes no bullet from that README. The bullet in
  `scripts/imaging/features/advanced/README.md` already exists and already describes the
  feature folder, so it needs no new entry either, only a possible wording touch-up.
- **Release profile already covers the destination.** `config/build/profile_release.yaml`
  has `- pattern: "imaging/features/advanced/potential_correction/"` →
  `PYAUTO_SMALL_DATASETS: "0"`, with a comment block explaining that the 15x15 cap starves
  `al.pc.PairRegularDpsiMesh(dpsi_factor=2)` ("The dpsi grid is too sparse" from
  `mesh.py:get_itp_box_ctr`). Today the guide is instead covered by the blanket
  `- pattern: "guides/"` rule. After the move the existing pattern picks it up — **no config
  edit required**, but this must be confirmed rather than assumed.
- **The in-file `ENV:` rationale is factually wrong and must be corrected during the move.**
  The script's `__Env__ (Developer Only)` block (lines ~336-346) declares `ENV: full_datasets`
  and justifies it as *"Guides load committed full-resolution FITS; SMALL_DATASETS would
  mismatch the pre-existing 100x100 data shape."* That is boilerplate inherited from the
  `guides/` blanket: this script **simulates in memory** (`al.SimulatorImaging` at line 75)
  and never reads a committed FITS or writes a dataset path. The real reason it needs
  `full_datasets` is the dpsi-mesh sparsity crash documented in `profile_release.yaml`.
  Keep the `ENV: full_datasets` declaration (in-file declarations apply in every profile);
  rewrite the rationale prose to the true reason.
- Cross-references to the old path that will break, all pointing at
  `guides/advanced/potential_correction`:
  - `scripts/imaging/features/advanced/potential_correction/likelihood_function.py` — two hits
    (line 58 "the user-facing overview of the technique", line 407 "see ...").
  - `scripts/interferometer/features/advanced/potential_correction/start_here.py` — one hit
    (line 32 "the technique overview (imaging)").
  - the three matching `notebooks/**` twins of the above.
  - `llms-full.txt` line 485 — generated, refreshed by the `generate_and_merge` skill.
- `autolens_assistant/`: **no** file mentions potential correction. Closest existing skill is
  `skills/al_subhalo_detect.md` (stub) — same science goal (find substructure), different
  method (evidence-ratio grid search vs. pixelized potential reconstruction).

## Work

### Leg 1 — autolens_workspace: move the script

1. `git mv scripts/guides/advanced/potential_correction.py
   scripts/imaging/features/advanced/potential_correction/start_here.py`, and the notebook
   twin `notebooks/guides/advanced/potential_correction.ipynb` →
   `notebooks/imaging/features/advanced/potential_correction/start_here.ipynb`.
   (Regenerating the notebook is also acceptable; do not leave both.)
2. Rewrite the `__Env__` rationale to the dpsi-mesh reason (see verified state above). Keep
   `ENV: full_datasets`.
3. Re-point the five script/notebook cross-references listed above from
   `guides/advanced/potential_correction.{py,ipynb}` to the new
   `imaging/features/advanced/potential_correction/start_here.{py,ipynb}`, adjusting the
   surrounding wording where "the guide" no longer reads correctly. Note the interferometer
   sibling's line 32 says "the technique overview (imaging)" — that phrasing still works, only
   the path changes.
4. Adjust the script's own opening prose where it presents itself as a *guide* rather than the
   feature's entry point, and align its `__Contents__`/intro with how the interferometer
   `start_here.py` frames itself. Do **not** rewrite the science.
5. Add the `imaging/features/advanced/README.md` `potential_correction` bullet a pointer to
   `start_here.py` if the sibling folders' bullets do so; otherwise leave the bullet as is.
6. Confirm `config/build/profile_release.yaml` needs no change (the destination pattern already
   exists), and that the guide is not separately named in any other build/smoke config.
7. Regenerate `llms-full.txt` / `workspace_index.json` via the `generate_and_merge` path rather
   than hand-editing line 485. Stage generated artifacts **by name**, never `git add .`.

### Leg 2 — autolens_assistant: author the skill

8. New `skills/al_potential_correction.md` following `_style.md` and the frontmatter shape of
   the sibling skills: gravitational imaging via `al.pc`, when to reach for it vs.
   `al_subhalo_detect`, the `FitDpsiSrcImaging` / `IterFitDpsiSrcImaging` / `DpsiSrcInvAnalysis`
   entry points, the dpsi mesh and its sparsity constraint, evidence-maximised regularization,
   and the `dkappa` map as the science output. Point at
   `autolens_workspace:scripts/imaging/features/advanced/potential_correction/start_here.py`
   and its `likelihood_function.py` sibling, and at the interferometer twin.
9. Cite Cao et al. 2025 (implementation origin,
   https://github.com/caoxiaoyue/potential_correction_paper) and the B1938+666 result
   (Powell et al. 2025 Nature Astronomy 9, 1714; Vegetti et al. 2026), matching how the
   workspace script cites them.
10. Register it in `skills/README.md` and cross-link from `skills/al_subhalo_detect.md`.
11. Ground every API symbol against the installed stack and run the repo's
    `audit_skill_apis.py` gate (assistant repos have no smoke tests — that audit is the gate).

## Out of scope

- Adding the missing `__init__.py` to either potential-correction folder (pre-existing, in both,
  and touching it risks the notebook/CI collection path — file separately if wanted).
- Filling in the `al_subhalo_detect.md` stub's own TODO recipe.
- A `wiki/core/` gravitational-imaging page (offered and declined for this pass).
- Any change to `al.pc` library source, or to the interferometer `start_here.py` beyond its
  one broken cross-reference.
- The missing `potential_correction` / `over_sampling_chaining` bullets in
  `scripts/guides/advanced/README.md` (pre-existing gap; the move makes the first one moot).
