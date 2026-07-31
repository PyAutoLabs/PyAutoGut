# multi_galaxy features parity — phase 4: advanced mass features

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: large
Autonomy: supervised
Priority: normal
Status: **COMPLETE 2026-07-31.** All three sub-phases shipped: 4a DSPL (#430, PR#431), 4b mass_stellar_dark (#432, PR#433), 4c subhalo (#434, PR#435 — also ran the arc-closing checks). Records in complete/2026/07/multi-galaxy-features-phase-4{a,b,c}.md.
Parent: draft/docs/workspaces/multi_galaxy_features_group_parity.md
Blocked-by: phase 1 (done), phase 3 (done — `advanced/` exists, PR#429)

Phase 4 of 4 — closes the arc. See the parent for the original request, scope decisions
and the authoring rules that apply to every script.

## Split into 4a / 4b / 4c (2026-07-31)

Measured at implementation time, phase 4 is ~5174 lines of Python across 15 scripts — larger
than all of phase 2 was, and phase 2 was itself split into 2a/2b/2c for that reason. DSPL and
`mass_stellar_dark` each carry a full six-script set including a `slam.py` (717 / 576 lines)
and a `chaining.py`, the two heaviest script types in the arc.

Split one folder per issue/PR, each at or below phase 2c's shipped size:

- **Phase 4a — `double_source_plane_lens`** (~2003 lines, 6 `.py` + README). Leads, because the
  prompt's regime motivation says it is the most genuinely regime-specific point in the phase.
- **Phase 4b — `mass_stellar_dark`** (~2010 lines, 6 `.py` + README).
- **Phase 4c — `subhalo`** (~1161 lines, 2 `.py` + 2 READMEs). Detection only, no sensitivity
  mapping — the same boundary group draws.

The **arc-closing checks** at the bottom of this prompt run at the end of **4c**, not each
sub-phase.

Terminology verified 2026-07-31 against `imaging/features/advanced/double_source_plane_lens`:
it says "double source-plane lens (DSPL)", keeps the morphology description "appear as two
distinct Einstein rings", and no retired names survive anywhere in either sibling.

## Deliverables

Under `scripts/multi_galaxy/features/advanced/` (created in phase 3; if phase 4 runs
first, create `advanced/README.md` here instead and phase 3 extends it).

- `advanced/double_source_plane_lens/` — `README.md`, `__init__.py`, `simulator.py`
  (dataset `double_source_plane_lens`), `modeling.py`, `fit.py`,
  `likelihood_function.py`, `chaining.py`, `slam.py`. Sibling:
  `group/features/advanced/double_source_plane_lens` (276/222/248/242/298/717) and the
  imaging equivalent.
  **Terminology:** the DSPL rename shipped — the *system class* is renamed, but keep the
  morphology description ("appear as two distinct Einstein rings"). Follow whatever
  `imaging/features/advanced/double_source_plane_lens` says today; do not reintroduce
  retired names.
- `advanced/mass_stellar_dark/` — `README.md`, `__init__.py`, `simulator.py` (dataset
  `mass_stellar_dark`), `modeling.py`, `fit.py`, `likelihood_function.py`,
  `chaining.py`, `slam.py`. Sibling: `group/features/advanced/mass_stellar_dark`
  (318/221/336/310/249/576) and the imaging equivalent.
- `advanced/subhalo/` — `README.md`, `__init__.py`, `simulator.py`,
  `detect/README.md`, `detect/__init__.py`, `detect/start_here.py`. Sibling:
  `group/features/advanced/subhalo` (261 + detect/start_here 900). Detection only, no
  sensitivity mapping — same boundary group draws.
  **Do not add `los_halos`** — it is imaging-only and outside the group-parity list.

## Regime motivation to write (phase-specific)

- **double_source_plane_lens**: two source planes give the extra constraint that
  *breaks* the multi-galaxy mass-split degeneracy — the ratio of deflections at two
  redshifts depends on the mass distribution, not just the total. This is the most
  genuinely regime-specific point in phase 4 and should lead the folder's prose.
- **mass_stellar_dark**: decomposing each co-dominant deflector into stellar + dark
  components. The regime point: with two deflectors, a shared mass-to-light ratio is a
  real modelling choice (tie it across galaxies or not), and tying it is what makes the
  decomposition identifiable when the mass split already is not.
- **subhalo**: the detection sensitivity floor is set by how well the *smooth* model is
  constrained, and here the smooth model has a degenerate mass split. So a false
  positive can be a mis-split rather than a subhalo — say this plainly, and make the
  comparison model in the detection grid the correct one.

## Acceptance

Same as phase 1: clean-slate smoke green (sequential), selective `smoke_tests.txt`
registration proven by count, notebooks + navigator regenerated (repo as CWD, key
`al`), no stray "group" framing, README inventories matching disk.

Arc-closing checks (run at the end of this phase):

- `grep -rn "potential_correction\|los_halos" scripts/multi_galaxy/` returns nothing.
- `scripts/multi_galaxy/features/` folder list equals `scripts/group/features/` minus
  `group_halo`, plus `extra_galaxies` and `scaling_relation`.
- The parent prompt's **Remaining** entry ("feature variants remain README cross-links")
  is struck and `draft/docs/autolens/multi_galaxy_package.md` updated, leaving only the
  real-data MAST swap-in open.
