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
