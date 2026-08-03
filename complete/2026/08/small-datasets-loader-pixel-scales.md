## small-datasets-loader-pixel-scales
- completed: 2026-08-03
- issue: https://github.com/PyAutoLabs/PyAutoArray/issues/430
- library-pr: https://github.com/PyAutoLabs/PyAutoArray/pull/431 (merged 17885f38)
- repos: PyAutoArray
- notes: |
    Root cause of the group/slam PriorException in PyAutoHeart Workspace Smoke run
    30790463134. `cap_array_2d_for_small_datasets` handled one case and silently
    dropped the other: data LARGER than the 16x16 PYAUTO_SMALL_DATASETS cap was
    cropped AND rebuilt at SMALL_DATASETS_PIXEL_SCALES (0.6); data already
    at-or-below the cap early-returned, keeping the caller's uncapped pixel_scales
    (0.1). A capped simulator writes at 0.6, so the loader mislabelled the frame 6x
    (+/-0.8" instead of +/-4.8"). Off-centre galaxies fell outside it, their
    non-negative linear intensity solve correctly returned exactly 0.0, and the
    collapsed UniformPrior(0.0, 0.0) surfaced four steps downstream at
    autolens_workspace scripts/group/slam.py:321 in source_lp[1], naming neither
    the loader nor the pixel scale.

    FIX: the at-or-below-cap branch now rebuilds the Array2D at the capped scale,
    mirroring the crop branch. Shape preserved — that branch must never crop.
    Rebuilding is required rather than returning a corrected scalar: the Array2D is
    constructed by the caller before the call and carries its own geometry (a
    scalar-only prototype was recorded as failing in the originating prompt, and
    that held). 2 files, +57/-22.

    Two unit tests asserted the early return as INTENDED behaviour
    (test__env_set__shape_already_at_cap__* and test__env_set__shape_below_cap__*)
    and were rewritten to assert relabel-without-cropping. The env-unset test and
    both crop-path tests were left untouched as the scope guard.

    VALIDATED: pytest test_autoarray/ 929 passed (3.12 + 3.13 green in CI).
    group/slam.py under the capped smoke profile -> EXIT 0, 6 searches genuinely
    run, 0 cached resumes — re-confirmed post-merge against the canonical install.
    Crop path byte-identical patched vs unpatched on the 209x209 cosmos_web_ring
    dataset (both (16,16) @ 0.6). Uncapped operation unaffected (imaging/start_here,
    ENV: full_datasets, exit 0).

    TWO PROMPT CLAIMS PROVED WRONG, both worth remembering as a pattern — the
    originating prompt was written 2026-07-22 and had drifted by the time it ran:
    (1) its `Repos:` header listed autolens_workspace + HowToLens; both legs were
    already done (the group/slam no_run line was removed by autolens_workspace
    PR#312, HowToLens has no group/ scripts at all). The stale header made the Brain
    Feature Agent size the task too-large (score 12) and recommend a 4-phase split
    for a ~4-line one-function fix. (2) its headline "BEHAVIOUR CHANGE TO VALIDATE:
    four datasets have committed 15x15 files" was false. Measured: of 31 committed
    dataset FITS exactly ONE is at-or-below the cap (slacs1430+4105/psf.fits, 11x11)
    and PSFs never route through the capper (imaging/dataset.py caps data +
    noise_map only); two of the four named datasets do not exist at all. ZERO
    committed datasets changed scale, so the plan's main declared risk was not real.

    PROCESS: autolens_workspace PR#312 (a9b7ac1a, 2026-07-21) un-parked group/slam
    from no_run.yaml as "PriorException fixed" when it was not. The real root cause
    was formalised one day later and never shipped, so the next scheduled Workspace
    Smoke hit it. Un-parking on an assumed fix, without re-running the script, cost
    a full cycle.

    DOWNSTREAM: imaging/features/scaling_relation/slam now exits 0 (6 real searches)
    and can be un-parked — filed as
    draft/maintenance/workspaces/unpark_imaging_scaling_relation_slam.md.
    multi_galaxy/features/scaling_relation/slam clears the 0.0-luminosity cause but
    then hits a SEPARATE latent bug: slam.py:863 derives image_half_width from the
    script's hardcoded pixel_scale (0.1) while the mask uses
    dataset_full.pixel_scales (now correctly 0.6), giving an "enlarged" mask radius
    of 0.30 (smaller than the standard 3.0), an empty mask, and a zero-size
    reduction in ConvolverState. Control-tested: unpatched main fails EARLIER with
    the documented 0.0-luminosity error, so it is not a regression. Filed as
    draft/bug/autolens_workspace/script_local_pixel_scale_vs_dataset_pixel_scales.md
    and deliberately scoped as a SWEEP — the literal-vs-dataset divergence is a
    class, invisible in uncapped runs.

    SHIP GATE: Heart was RED (verdict red, score 0) at ship time. This PR fixed part
    of the YELLOW reason "workspace validation not passing (cloud#30790463134)" and
    none of the three RED reasons (PyAutoFit 1 commit behind origin; install
    verification FAILED testpypi checks D — that one belongs to
    intra-family-dep-floors; release validation FAILED stage integrate). Shipped to
    PR-open under an explicitly human-authorized corrective-PR exception, then
    merged on human instruction.

    CONCURRENCY: PyAutoArray was claimed by intra-family-dep-floors (PyAutoLens#687,
    PyAutoArray#432) which registered AFTER worktree_check_conflict ran here — the
    guard returned 0 at both start_dev and start_library for that timing reason, so
    the manual scope check was load-bearing. Scopes were disjoint (pyproject.toml vs
    autoarray/util/). This merged first; #432 rebases.

    GOTCHA worth keeping: the first "clean" validation run read as a pass but was
    6/6 "Fit Already Completed". Output is namespaced under output/test_mode/ in
    test mode, so clearing output/<path> alone leaves a stale tree that fakes a
    green run. Clear output/test_mode/<path> too. Separately, forcing
    PYAUTO_SMALL_DATASETS=1 on imaging/start_here.py (which declares
    ENV: full_datasets) produced a convincing false failure; the control on
    unpatched main reproduced it identically and exonerated the change.

## Original prompt

# PYAUTO_SMALL_DATASETS loader keeps uncapped pixel_scales for at-or-below-cap data

Type: bug
Target: PyAutoArray
Repos:
- PyAutoArray
Difficulty: small
Autonomy: supervised
Priority: normal
Status: issued

SCOPE CORRECTION 2026-08-03 (at issue-filing, PyAutoArray#430): the `Repos:`
header above listed autolens_workspace and HowToLens; both legs were already
done by then and are removed, leaving PyAutoArray as the only repo edited. The
`group/slam` no_run line was removed by autolens_workspace PR #312 (a9b7ac1a,
2026-07-21) — which un-parked the script as "PriorException fixed" when it was
not, which is why the failure resurfaced in PyAutoHeart Workspace Smoke run
30790463134. HowToLens has no `group/` scripts and no matching no_run entry.
Leaving the stale 3-repo header in place made the Brain Feature Agent size this
`too-large` (score 12) and recommend a 4-phase split for what is a ~4-line
one-function fix.

The root-cause analysis below was re-verified end-to-end on clean main before
filing: the loader returns pixel_scales=(0.1,0.1) for the 16x16 capped array,
whose bright clump at index (2,12) maps to (+3.3,+2.7)" only under 0.6 —
matching the declared extra-galaxy centre (3.5,2.5). Patching the at-or-below-cap
branch (monkeypatched, no source edits) took scripts/group/slam.py from
PriorException at line 321 to exit 0 with all six SLaM stages running.

PYAUTO_SMALL_DATASETS loader keeps uncapped pixel_scales for at-or-below-cap data.

Root cause of the group/slam PriorException (supersedes draft/bug/autolens/group_slam_priorexception_limits.md). The fault is in PyAutoArray, not in any workspace script.

autoarray/util/dataset_util.py cap_array_2d_for_small_datasets handles one case and silently drops the other:
- data LARGER than the 16x16 cap -> crops it AND rebuilds it at SMALL_DATASETS_PIXEL_SCALES (0.6). Correct.
- data already AT-OR-BELOW the cap (because a capped simulator just wrote it at 0.6) -> early-returns, keeping the callers uncapped pixel_scales (0.1). Wrong.

Consequence: the frame is mislabelled 6x (plus/minus 0.8 arcsec instead of plus/minus 4.8 arcsec). Off-centre galaxies fall outside it, their non-negative linear intensity solve correctly returns exactly 0.0, total_luminosity becomes 0, and min(5*0.5*0**0.6, 5.0) collapses a UniformPrior to lower==upper==0.0. The PriorException is four steps downstream of the fault.

FIX (about 4 lines): in the at-or-below-cap branch, when the cap is active, rebuild the Array2D at SMALL_DATASETS_PIXEL_SCALES and return that scale, mirroring what the crop branch already does. Returning a corrected scalar alone is NOT enough: the Array2D is constructed before the call and carries its own geometry. A first prototype that only fixed the scalar still failed. Also update the docstring, which currently documents only the crop case and calls the early return a no-op.

NO workspace script changes are needed. pixel_scales=0.1 is a TRUE statement about the dataset in normal operation and belongs in a tutorial script; the cap silently invalidates it and the loader must correct it.

PROVEN on clean main, standard capped smoke env (PYAUTO_TEST_MODE=2, PYAUTO_SMALL_DATASETS=1), fresh dataset:
- unmodified scripts/group/slam.py + patched loader -> EXIT 0, all six searches ran
- unmodified script, unpatched loader -> PriorException at slam.py:307
- script with pixel_scale hardcoded to 0.6, unpatched loader -> EXIT 0 (confirms the scale, not the science, was the problem)

Evidence the capped data really is 0.6 arcsec/px: the simulated 16x16 image has clumps at (+3.6,+2.4) and (-4.8,-4.8) arcsec under 0.6, matching the declared extra-galaxy centres (3.5,2.5) and (-4.4,-5.0). Under 0.1 they would be at (0.55,0.45) - nowhere near.

Safety of the >=cap-implies-0.6 inference: every committed and generated imaging dataset checked is either cropped-and-relabelled to 0.6 or written by a capped run at 0.6. It is still an inference; a genuinely small real-scale dataset added later would be mislabelled. See the follow-up prompt on simulators recording their own scale.

BEHAVIOUR CHANGE TO VALIDATE: four datasets have committed 15x15 files (double_einstein_ring, mass_stellar_dark, scaling_relation, extra_and_scaling_galaxies). Scripts loading them will now receive 0.6 instead of 0.1. That is a correction (the data genuinely is 0.6) but must be spot-checked.

ALSO IN SCOPE: remove the group/slam NEEDS_FIX line from autolens_workspace/config/build/no_run.yaml, and the dead one from HowToLens/config/build/no_run.yaml (HowToLens has no group/ scripts at all).

VALIDATION PLAN: pytest test_autoarray/ (add an at-or-below-cap test case); clean-dataset and clean-output run of scripts/group/slam.py under the standard capped smoke env expecting exit 0; the four committed-15x15 scripts; one crop-path script to confirm that branch is untouched.

DEAD ENDS ALREADY RULED OUT, do not redo: (1) the 132-vs-35 should_simulate split is NOT drift - commit 0f294fc70 scoped that migration to smoke-tested scripts deliberately, and since dataset/ is gitignored, exists() and should_simulate are equivalent on a clean CI checkout. (2) An FOV-preserving rewrite of the cap is NOT needed for this bug. (3) Flooring or guarding the collapsed prior is wrong - an off-frame profile solving to exactly zero intensity is the correct result of a non-negative solve.

<!-- formalised by the Intake (Conception) Agent on 2026-07-22 from user-intake -->
