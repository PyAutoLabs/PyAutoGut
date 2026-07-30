# extra-galaxies-multi-galaxy-lens

Phase 2b, the FINAL phase of the extra-galaxies parity arc. Added
`autolens_workspace/scripts/multi_galaxy/features/extra_galaxies/` — `README.md`,
`__init__.py`, `simulator.py`, `modeling.py` — and rewrote the extra-galaxies bullet in
`multi_galaxy/features/README.md` to point at the local example.

- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/387 (CLOSED)
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/391 (MERGED `9b274ff2`)
- parent: `draft/docs/workspaces/extra_galaxies_feature_parity.md` — ARC COMPLETE

## Arc summary

| Phase | Issue | PR |
|---|---|---|
| 1 — point_source | autolens#374 closed | autolens#376 merged `e005caca` |
| 2a — autogalaxy multi_galaxy | autogalaxy#182 closed | autogalaxy#184 merged `78568683` |
| 2b — autolens multi_galaxy | autolens#387 closed | autolens#391 merged `9b274ff2` |

`group/` and `cluster/` untouched throughout, per the user's original scoping.

## The division of labour with #370

This was the reason 2b was deliberately deferred until #370 merged, and it turned out to be
the right call. #370's `simulator.py` gives the `simple` dataset ONE faint contaminant with an
`ExponentialSph` light profile and **no mass** — explicitly "so the lensed source arcs are
unchanged and the dataset remains a clean two-deflector lens for all other examples" — and
`start_here`/`modeling`/`fit`/`likelihood_function` then teach the
`__Extra Galaxies Noise Scaling__` lever against it.

This example is the other half: perturbers with **mass as well as light**, where noise scaling
stops being sufficient. Same arrangement as the imaging package. Had 2b been written first it
would have duplicated the noise-scaling walkthrough instead of complementing it.

## The measurement

The prose claim ("noise scaling is not sufficient once an extra galaxy has mass") was
**measured, not asserted**. Taking the dataset's true tracer and removing ONLY the extra
galaxies' mass, keeping their light exactly as simulated:

- max |diff| / noise = **7.6 sigma**
- **226 pixels** above 3 sigma, 32 above 5 sigma
- total sqrt(sum chi^2) ~ **89**
- and **none of it in the pixels the extra-galaxies mask covers** — it is in the arcs

That last point is the argument: noise scaling cannot reach the affected pixels because they
are not the contaminated ones. A model without the tier absorbs the signal into the main pair's
free mass, biasing exactly the per-deflector measurement the multi-galaxy regime exists to make.

## The angle — operationalising the tier judgement

`multi_galaxy/simulator.py` already poses the question ("telling them apart is the first
judgement you make about a multi-galaxy field — if in doubt, the test is whether it contributes
significantly to the lensing"). This example makes it concrete across the three tiers and works
through what each mistake costs.

**Promoting a perturber is the subtle error.** Demoting a co-dominant deflector is the failure
the package already warns about and it shows in the residuals. Promoting — free centre,
uncapped mass — usually still converges and still looks fine, but a free-centre perturber near
a co-dominant deflector is degenerate with its mass, so the posterior widens and the per-galaxy
Einstein radii trade against each other. Identifiability is lost, not fit quality. This is why
the fixed centres and the `einstein_radius` cap (0.3" against the pair's 0.9"/0.8") are
load-bearing rather than stylistic.

## Process notes

**Merged main in BEFORE opening the PR.** Main moved twice mid-task (#388, then others). Phase
2a had hit a merge conflict at merge time from exactly this; here `git merge origin/main` +
regenerate ran before PR-open and produced no further catalogue diff. Adopt this ordering when
main is active.

**A duplicate-guard was too broad.** `assert "features/extra_galaxies" not in smoke_tests.txt`
matched phase 1's `point_source/features/extra_galaxies` entry and aborted. Anchor such guards
on the full path, not a substring.

**Heart gate handling.** YELLOW 70, the same two reasons acked for 2a with one delta
(release-validation-stale gained PyAutoArray). Rather than re-litigate a third near-identical
ack, the task was taken to PR-OPEN — reversible, and where the autonomy contract stops anyway —
and the merge held for explicit human confirmation. That is the right split: the gate's purpose
is authorising the irreversible act.

## Validation

- `run_smoke.py`: **19/19 passed** (18 before, +1 for the new entry)
- `scripts/check_sizes.sh`: clean
- Navigator check reproduced under the CI root layout: clean
- CI: 4/4 green on `b90af51a`
- Notebooks + catalogue regenerated; `group/` and `cluster/` untouched
- No full non-linear fit, deliberately — the example composes proven patterns, so bypass-mode
  smoke proves what is new, and the one quantitative claim was measured from the tracer directly

## Open follow-up (not filed)

The two workspaces now express README folder references differently: autolens uses the wildcard
`autolens_workspace/*/...` form (37 refs, what PR#376 used), autogalaxy uses repo-relative
`scripts/imaging/...` (what autogalaxy#183 landed concurrently while PR#184 was open). Both
satisfy the PyAutoHands#213 navigator gate, so nothing is broken — but if repo-relative is the
intended standard, autolens wants a sweep.

## Original prompt

# Phase 2b — extra_galaxies feature: multi_galaxy (autolens_workspace)

Type: docs
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Unblocked: autolens_workspace#370 MERGED and closed 2026-07-30
Parent: draft/docs/workspaces/extra_galaxies_feature_parity.md

Phase 2b of the extra-galaxies parity task — the autolens half of phase 2, split out
2026-07-30. Phase 1 (point_source) shipped as autolens_workspace#374 / PR#376; phase 2a is
the autogalaxy half.

## Now unblocked — what #370 actually landed

`multi-galaxy-imaging-parity` (autolens_workspace#370) merged and closed 2026-07-30. Verified on
`origin/main` @ `264d4ab9`:

- `scripts/multi_galaxy/` gained `likelihood_function.py`, `simulator_sample.py`,
  `source_science.py`; `modeling.py` is now 886 lines, `fit.py` 614, `start_here.py` 673.
- `simulator.py` (439 lines) adds **one** faint extra galaxy at `(2.2, 1.6)` — an
  `ExponentialSph` **light profile only, deliberately no mass**, so "the lensed source arcs are
  unchanged and the dataset remains a clean two-deflector lens for all other examples".
- It writes `mask_extra_galaxies.fits`, and `start_here`/`modeling`/`fit`/`likelihood_function`
  all carry an `__Extra Galaxies Noise Scaling__` section.
- `multi_galaxy/README.md` already has a `# Folders` section naming `features` — so this task
  does **not** need to add one (the earlier plan assumed it would).

**This settles the division of labour.** The core scripts teach the **noise-scaling lever** with a
massless contaminant. This task is the **modeling lever**: extra galaxies carried in the model with
light *and* mass, on top of N co-dominant deflectors. Exactly the imaging arrangement, and
complementary rather than duplicative — do not repeat the noise-scaling walkthrough, reference it.

The core `simulator.py` prose already raises the tier question ("telling them apart is the first
judgement you make about a multi-galaxy field — if in doubt, the test is whether it contributes
significantly to the lensing"). This example is where that judgement should be **operationalised**:
what actually goes wrong in each direction when you get it wrong.

## Scope

New `scripts/multi_galaxy/features/extra_galaxies/{README.md, __init__.py, simulator.py, modeling.py}`.

- Two co-dominant deflectors (the package's `lens_0`, `lens_1`, … loop) **plus** a lower tier
  of extra galaxies at fixed centres. The regime framing already written in
  `multi_galaxy/features/README.md:1-27` is the prose source: extra galaxies are perturbers
  *below* co-dominance, using the same tiered API that becomes the default at group scale.
- Follow the sibling `features/scaling_galaxies/` for structure and conventions —
  `dataset/multi_galaxy/extra_galaxies/`, `main_lens_centres.json` for the co-dominant pair,
  plus `extra_galaxies_centres.json` and `mask_extra_galaxies.fits` for the perturber tier.
- Rewrite the extra-galaxies bullet in `multi_galaxy/features/README.md` so it points at the
  new local example; keep the `imaging/features/extra_galaxies` pointer as the fuller API
  walkthrough.
- Update `multi_galaxy/README.md` `# Folders` if the list changes (coordinate with #370's
  edit to the same file).

## Constraints / known traps

- The new `modeling.py` should join `smoke_tests.txt` (multi_galaxy scripts are smoke-enabled:
  `autolens_workspace/smoke_tests.txt:11-14`).
- `should_simulate` tests directory EXISTENCE only — `rm -rf dataset/multi_galaxy/extra_galaxies`
  before any validation run ([[feedback_should_simulate_existence_only]]).
- **`PYAUTO_TEST_MODE=1` and `=2` share the `output/test_mode/` namespace**, so a bypass run
  silently resumes a reduced-iterations run. `rm -rf output/test_mode` before trusting a
  bypass result ([[feedback_autofit_cache_resume_pyauto_test_mode]]).
- Workspace bulk-edit rule: never whole-file `Write` a file not fully read; run
  `scripts/check_sizes.sh` before committing.
- **Navigator root-name trap** — `check_navigator.py` strips a leading `<root.name>/` prefix
  and CI clones the workspace as `workspace/`, so a literal `autolens_workspace/scripts/...`
  reference passes locally and fails in CI. Use the wildcard `autolens_workspace/*/...` form
  ([[reference_docs_ci_gotchas_workspace_assistant]]).

## Acceptance

- `simulator.py` writes its dataset + metadata from a clean dataset folder.
- `modeling.py` runs under `PYAUTO_TEST_MODE=2` / `PYAUTO_SMALL_DATASETS=1` and is added to
  `smoke_tests.txt`.
- `python .github/scripts/run_smoke.py` green; `scripts/check_sizes.sh` clean.
- Every new folder has a `README.md` + `__init__.py`; parent READMEs' `# Files` / `# Folders`
  lists updated (README ref-drift is CI-gated).
- Notebooks + navigator catalogue regenerated via PyAutoHands `generate.py autolens`.
- `group/` and `cluster/` untouched.
