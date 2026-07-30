# extra-galaxies-multi-galaxy

Phase 2a of the extra-galaxies parity task. Added
`autogalaxy_workspace/scripts/multi_galaxy/features/` — the folder did not exist at all —
with `README.md`, `__init__.py`, and an `extra_galaxies/` worked example
(`README.md`, `__init__.py`, `simulator.py`, `modeling.py`). Plus a `# Folders` section on
`scripts/multi_galaxy/README.md` and a new `smoke_tests.txt` entry.

- issue: https://github.com/PyAutoLabs/autogalaxy_workspace/issues/182 (CLOSED)
- workspace-pr: https://github.com/PyAutoLabs/autogalaxy_workspace/pull/184 (MERGED `78568683`)
- parent: `draft/docs/workspaces/extra_galaxies_feature_parity.md`
- phase 1 (point_source): SHIPPED — autolens_workspace#374 / PR#376 merged `e005caca`
- phase 2b (autolens multi_galaxy): NOT started, Blocked-on autolens_workspace#370

## Phase split

Phase 2 was split BY REPO on 2026-07-30. `multi-galaxy-imaging-parity`
(autolens_workspace#370) was found actively in flight in another session, rewriting
`autolens_workspace/scripts/multi_galaxy/` wholesale — 2,959 insertions across
start_here/modeling/fit/simulator plus 3 new scripts, and notably adding a faint extra galaxy
+ `mask_extra_galaxies.fits` to `multi_galaxy/simulator.py` and an
`__Extra Galaxies Noise Scaling__` section to the core scripts. The autolens half must be
written against that merged result. Human chose "autogalaxy now, autolens after #370".

## The angle

The API is identical to the single-galaxy version. What is new is that the model has **two
tiers at once**, so the question the example answers is which tier a galaxy belongs in:

- **Co-equal galaxies** — free light model, free centre, because decomposing them is the science.
- **Extra galaxies** — restricted light model, centre fixed, because they only need to stop
  contaminating the measurement.

The tiers describe **intent, not brightness**. Two points the multi-galaxy setting forces
which the single-galaxy example does not have to make:

1. **The choice tilts towards modeling.** The deliverable is a *decomposition*, and residual
   unmodelled flux is absorbed **asymmetrically** by the two free light models — biasing the
   flux ratio between the pair, usually the quantity the analysis exists to measure.
2. **Fixed centres matter more.** A wandering extra galaxy now has more than one bright thing
   to drift onto, including a galaxy of the pair whose light it would begin absorbing.

The two centre files (`galaxy_centres.json` vs `extra_galaxies_centres.json`) are the tier
assignment made concrete, and the scripts say so.

## Validation depth — deliberately no full fit

The human challenged the need for a full non-linear fit and was right. Phase 1 warranted one:
a mass-only extra-galaxies model on point-source data was new, and at 12 data points against
10 free parameters identifiability was a real question. Phase 2a composes two already-proven
patterns (`imaging/features/extra_galaxies` + `multi_galaxy/modeling.py`), so the bypass-mode
smoke run proves the only genuinely new thing — that the two-tier model composes and the
script runs end-to-end. The tier-choice argument is modeling practice, not a numerical result
a posterior would confirm.

## Traps hit

**The capped smoke check rewrote the dataset at 16x16.** Running the script under
`PYAUTO_SMALL_DATASETS=1` to prove it was smoke-able rmtree'd and rebuilt
`dataset/multi_galaxy/extra_galaxies` at 16x16, so a subsequent real fit trained on a
16-pixel image. Caught after ~19 minutes of CPU via an
`IMAGING - Data masked, contains a total of 256 image-pixels` line in the log (256 = 16x16).
Between any capped run and any real fit: purge dataset + output, re-simulate, and verify with
`fits.getdata(...).shape`. Recorded in [[feedback_should_simulate_existence_only]].

**PID capture returned the wrapper shell.** `ps -eo pid,cmd | grep <script> | awk '{print $1}'`
matched the `bash -c ...` wrapper (0% CPU) before the python child (108%), making a healthy
run look stalled and nearly getting it killed. Match the interpreter or take the last match.
Recorded in [[feedback_pgrep_f_matches_itself]].

**A docstring edit orphaned prose outside the block**, producing a hard `SyntaxError`. Caught
by an explicit `ast.parse` check rather than by running the script — worth doing after any
edit near a `"""` boundary in these prose-heavy tutorial scripts.

**The photometry loop labelled extras as `galaxy_2`/`galaxy_3`**, contradicting the tier
framing the whole example is built around. `max_log_likelihood_galaxies` is a flat list with
extras appended, so the script now labels by tier and warns about the flat-list trap.

## Merge conflict — concurrent duplicate fix

The first merge attempt was rejected with conflicts. `docs: make README folder refs
repo-relative` (`c2b47fd`, PR #183) had landed while this PR was open and fixed **the same 5
navigator references** exposed by PyAutoHands#213, independently and concurrently.

Resolved by taking main's version: it uses the repo-relative form
(`scripts/imaging/features/shapelets`) rather than the wildcard form used here, and that is
now the house convention. The catalogue was regenerated after the merge rather than
hand-resolved, per the standing rule for generated artifacts.

**Open inconsistency:** `autolens_workspace` PR#376 fixed its equivalent refs with the
**wildcard** form and merged first. Both forms pass the gate, but the two workspaces now
express the same idea differently. Worth a follow-up sweep if repo-relative is the intended
standard.

## Validation

- `run_smoke.py`: **13/13 passed** (12 before, +1 for the new entry)
- `scripts/check_sizes.sh`: clean
- Navigator check reproduced under the CI root layout (clone into a dir named `workspace`,
  `--root workspace`) — clean both before and after the merge
- CI: 4/4 green on the merged head `8395cff4`
- Notebooks + catalogue regenerated; `cluster/` untouched

## Heart

Shipped on an acknowledged **YELLOW** (score 70), 2 reasons, both pre-existing and unrelated:
workspace validation not passing (0 failed, cloud#30516167217); release validation stale —
source moved since rehearsal (PyAutoFit, PyAutoGalaxy, PyAutoLens). Note this was a
**different reason set** from phase 1's ack (the 33-stale-parked-scripts and manifest-drift
reasons had cleared), so a fresh acknowledgement was taken rather than carrying the old one.

## Original prompt

# Phase 2a — extra_galaxies feature: multi_galaxy (autogalaxy_workspace)

Type: docs
Target: autogalaxy_workspace
Repos:
- autogalaxy_workspace
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: draft
Parent: draft/docs/workspaces/extra_galaxies_feature_parity.md

Phase 2a of the extra-galaxies parity task. Phase 1 (point_source) shipped as
autolens_workspace#374 / PR#376.

> Adopt same style and approach for documenting extra galaxies in multi_galaxy,
> do same in autogalaxy_workspace.

Human decision 2026-07-29: **full worked example** (own simulator + own simulated dataset),
not a cross-link — matching `autolens_workspace`'s sibling tier
`multi_galaxy/features/scaling_galaxies/`, which gets full-example treatment.

**Split decision 2026-07-30:** phase 2 was split by repo. `multi-galaxy-imaging-parity`
(autolens_workspace#370) is actively in flight in another session and rewrites
`autolens_workspace/scripts/multi_galaxy/` wholesale — 2,959 insertions across
`start_here`/`modeling`/`fit`/`simulator` plus 3 new scripts, including adding a faint extra
galaxy + `mask_extra_galaxies.fits` to `multi_galaxy/simulator.py` and an
`__Extra Galaxies Noise Scaling__` section to the core scripts. The autolens half of this
task must be written against that merged result, so it is deferred to **phase 2b**. The
autogalaxy half has **zero contention** (#370 does not touch autogalaxy_workspace) and runs
now.

## Scope

`autogalaxy_workspace/scripts/multi_galaxy/` has **no `features/` folder at all**. Create:

- `scripts/multi_galaxy/features/{README.md, __init__.py}`
- `scripts/multi_galaxy/features/extra_galaxies/{README.md, __init__.py, simulator.py, modeling.py}`

Plus: add a `# Folders` section to `scripts/multi_galaxy/README.md` (it currently has none —
its last line is a one-liner pointing at `imaging/features`).

## The shape of the example

**Light-only.** PyAutoGalaxy has no mass, so unlike the point-source phase (mass-only) and
like the autogalaxy imaging example, extra galaxies here are faint companions whose *light*
blends with the co-equal pair. Both levers exist and both should be shown, as
`autogalaxy_workspace/scripts/imaging/features/extra_galaxies/modeling.py` does:

1. **Noise scaling** — `mask_extra_galaxies.fits` + `dataset.apply_noise_scaling(mask=...)`,
   then fit the pair without the extras in the model.
2. **Modeling** — extras in the model as `ag.lp_linear.SersicSph` with `bulge.centre` fixed
   to the loaded centre (Option A), with the `ag.model_util.mge_model_from(centre_fixed=...)`
   MGE variant shown commented-out as Option B. Both are the established autogalaxy
   convention — keep them.

**What is new relative to the imaging example** is the base model: two co-equal blended
galaxies via the `galaxy_0`, `galaxy_1`, ... loop over `galaxy_centres.json`
(`multi_galaxy/modeling.py:109-122`, one `mge_model_from` per galaxy), *plus* a lower tier of
extra galaxies at fixed centres. That contrast — co-equal subjects and sub-dominant
perturbers in one model — is the point of the example, and the prose should say so.

## Conventions to match (autogalaxy differs from autolens)

- The main pair's centres file is **`galaxy_centres.json`**, not autolens's
  `main_lens_centres.json` (`multi_galaxy/simulator.py:143-145`).
- The main pair sits at `(0.0, -0.75)` / `(0.0, 0.75)` with `Sersic` bulges, and
  `modeling.py` uses `mask_radius=3.0`. A larger mask is needed to admit the extra galaxies —
  the imaging example uses 6.0" for exactly this reason.
- Imports are `ag.` / `aplt.`; scripts open with `from autogalaxy import jax_wrapper` then the
  commented `setup_notebook` line.
- Dataset path is `Path("dataset", "multi_galaxy", <name>)`.
- The new `features/README.md` should carry the autogalaxy-specific
  **"Scaling Relations (not applicable in autogalaxy)"** framing already written in
  `scripts/imaging/features/extra_galaxies/README.md:18-47` — do not imply the autolens
  scaling-relation tier transfers.

## Constraints / known traps

- The new `modeling.py` should join `smoke_tests.txt` — multi_galaxy scripts are smoke-enabled
  in this repo (`autogalaxy_workspace/smoke_tests.txt:6-7`).
- `should_simulate` tests directory EXISTENCE only — `rm -rf dataset/multi_galaxy/extra_galaxies`
  before any validation run ([[feedback_should_simulate_existence_only]]).
- **`PYAUTO_TEST_MODE=1` and `=2` share the `output/test_mode/` namespace**, so a bypass run
  silently resumes a reduced-iterations run. `rm -rf output/test_mode` before trusting a
  bypass result ([[feedback_autofit_cache_resume_pyauto_test_mode]]).
- Workspace bulk-edit rule: never whole-file `Write` a file not fully read; run
  `scripts/check_sizes.sh` before committing.
- **Navigator root-name trap** — `check_navigator.py` strips a leading `<root.name>/` prefix
  and CI clones the workspace as `workspace/`, so a literal `autogalaxy_workspace/scripts/...`
  reference passes locally and fails in CI. Use the wildcard `autogalaxy_workspace/*/...`
  form. Reproduce CI by cloning into a dir named `workspace` and passing `--root workspace`
  ([[reference_docs_ci_gotchas_workspace_assistant]]).

## Acceptance

- `simulator.py` writes its dataset + `galaxy_centres.json` + `extra_galaxies_centres.json` +
  `mask_extra_galaxies.fits` from a clean dataset folder.
- `modeling.py` runs under `PYAUTO_TEST_MODE=2` / `PYAUTO_SMALL_DATASETS=1` and is added to
  `smoke_tests.txt`.
- `python .github/scripts/run_smoke.py` green; `scripts/check_sizes.sh` clean.
- Every new folder has a `README.md` + `__init__.py`; `multi_galaxy/README.md` gains a
  `# Folders` section (README ref-drift is CI-gated).
- Notebooks + navigator catalogue regenerated via PyAutoHands `generate.py autogalaxy`.
- `cluster/` untouched.
