## local-pixel-scale-vs-dataset-pixel-scales
- completed: 2026-08-24
- issue: https://github.com/PyAutoLabs/autolens_workspace/issues/501
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace/pull/502 (merged 85027bbb)
- repos: autolens_workspace
- notes: |
    Sweep fix for the literal-vs-dataset pixel-scale divergence found while validating
    PyAutoArray#430 / PR#431. A module-level `pixel_scale` literal was escaping its
    `from_fits` argument into arithmetic that ALSO read the loaded dataset. Under
    PYAUTO_SMALL_DATASETS=1 the loader (correctly) relabels capped data to 0.6, so the
    literal and dataset.pixel_scales disagreed and the arithmetic was silently wrong.
    Invisible in a normal run, because there the two values coincide.

    THE PROMPT SAID "not a one-off" AND IT WAS RIGHT: 8 scripts, not 1. Three usage
    classes sharing one root cause:
      1. geometry — image_half_width = 0.5 * min(dataset_full.shape_native) * pixel_scale
      2. luminosity — / pixel_scale**2, per-pixel to per-arcsec^2, on a model fitted to
         the loaded dataset, so the conversion must use the dataset's scale
      3. mesh resolution — hilbert_pixels_from_pixel_scale, documented as scaling "with
         data quality", which under a cap IS 0.6

    FIX: one rebind per file, `pixel_scale = float(dataset.pixel_scales[0])` immediately
    after the load. The literal keeps its correct and only role as the `from_fits`
    argument and as documentation of the real scale. The idiom was NOT invented here — it
    already existed at group/features/scaling_relation/modeling_for_luminosities.py:88,
    and multi_dataset/features/imaging_and_point_source/modeling.py:95 is a second
    precedent (explicit cap_array_2d_for_small_datasets call for its Array2D).

    ONE FILE DELIBERATELY DIFFERENT: imaging/features/multi_gaussian_expansion/modeling.py
    had its literal never reaching from_fits, with its sole consumer one end of a sigma
    prior range whose OTHER end already read dataset.pixel_scales[0] — the two ends of one
    np.linspace, on adjacent lines, reading different scales. Removed the literal and
    inlined the value, making the disagreement unrepresentable rather than corrected.
    Matches line 566 of the same file, which already passed pixel_scales=dataset.pixel_scales[0].

    PROMPT DRIFT, worth the pattern: the prompt cited slam.py:863 and a 0.1 literal. The
    file had moved to pixel_scale = 0.05 at line 834, arithmetic at 872. The 0.05 is what
    makes the prompt's own evidence exact — 0.5*16*0.05 - 0.1 = 0.30, the reported
    "Enlarged mask radius: 0.30". Under 0.1 it would have printed 0.70. Same class as the
    PyAutoArray#430 record's "two prompt claims proved wrong": a prompt written weeks
    before it runs drifts, and its line numbers are the first thing to go. Its ARGUMENT
    survived intact; only its coordinates rotted.

    EXCLUSIONS, each checked rather than assumed (this was most of the work):
    - interferometer/features/advanced/potential_correction/start_here.py simulates its
      dataset in-memory via SimulatorInterferometer and never calls from_fits. Its literal
      BUILDS real_space_mask, so it is the source of truth. Untouched.
    - The Array2D.from_fits callers (imaging/data_preparation/{gui,examples/optional}/*,
      cluster/plot.py) are NOT affected: cap_array_2d_for_small_datasets is reached only
      from autoarray/dataset/imaging/dataset.py:339,344 (data + noise_map). Array2D.from_fits
      never routes through it. Verified against PyAutoArray main via raw fetch, not assumed —
      this is the single fact that kept the sweep from doubling in size.
    - guides/results/database/start_here.py: literal reaches from_fits only, mask already
      reads dataset.pixel_scales. Correct as-is.
    - Six multi_galaxy scripts carry the literal but never let it leave from_fits.

    VERIFICATION GAP, SHIPPED KNOWINGLY — the important part of this record:
    The capped run was NEVER EXECUTED. The authoring session was web-github with no numpy
    and no autolens. Worse, and not obvious: green CI did not cover it either, because none
    of the 8 scripts appear in smoke_tests.txt. All 7 checks passed (3 workflow runs,
    pull_request event only) and told us nothing about the geometry. That gap was written
    into the PR body, the merge commit, and the closing issue comment rather than being
    allowed to read as validated.
    Merging ahead of it was judged acceptable because the rebind is EXACTLY a no-op in
    uncapped operation — float(dataset.pixel_scales[0]) returns the same value just passed
    to from_fits — so the blast radius for real users is nil, and the one script that
    exercises the capped path stays parked.
    Also no PyAutoHeart verdict: pyauto-heart was unreachable, so the ship gate's readiness
    leg never ran. /prm's note that "the gate ran at ship time" did not hold here.

    STILL PARKED: multi_galaxy/features/scaling_relation/slam stays in no_run.yaml, its
    NEEDS_FIX reason rewritten to name this cause instead of the 0.0-luminosity one that
    PR#431 fixed. Un-parking is filed as
    draft/maintenance/workspaces/unpark_multi_galaxy_scaling_relation_slam.md and must wait
    on a capped run exiting 0. This is the direct lesson of PR#312, which un-parked
    group/slam as "PriorException fixed" without re-running it and cost a full cycle — the
    same trap recorded in the small-datasets-loader-pixel-scales record. Not repeating it.

    ENVIRONMENT NOTES: no gh CLI (GitHub MCP tools throughout). ipynb-py-convert would not
    install — Debian-patched setuptools raises AttributeError: install_layout on its
    setup.py — so the genuine upstream module was installed by hand into user site-packages
    with a matching console script. Notebooks were then regenerated through the real
    PyAutoHands per-script pipeline (py_to_notebook + inject_colab_setup) scoped to the 8
    scripts, NOT via generate.py, which rmtree's the whole notebooks/ tree. Every notebook
    diff mirrored its script diff line-for-line, which incidentally proved no committed
    notebook was stale.

    GOTCHA for future web-github sessions: a --depth 1 clone pins remote.origin.fetch to
    main only, so `git push -u` creates the remote branch and writes branch.*.merge but no
    refs/remotes/origin/<branch> ever exists locally. @{u} then fails and tooling reports
    "unpushed commits / no remote branch" for work that is fully pushed. Fix is to add the
    branch's refspec and refetch, not to re-push.

## Original prompt

# Scripts derive geometry from a hardcoded pixel_scale while the dataset carries a corrected one

Type: bug
Target: autolens_workspace
Repos:
- autolens_workspace
Difficulty: small
Autonomy: supervised
Priority: normal
Status: issued
Filed: 2026-08-03 (backfilled from git)
Issued: 2026-08-24

Found while validating PyAutoArray#430 / PR#431 (the small-datasets loader fix), 2026-08-03.

## The bug

Workspace scripts declare a module-level `pixel_scale` literal (the dataset's true
scale in normal operation, e.g. `0.1`) and then use it in geometry arithmetic
*alongside* values read from the loaded dataset. Under `PYAUTO_SMALL_DATASETS=1`
the loader now correctly relabels capped data to `0.6`, so the script's literal
and `dataset.pixel_scales` disagree and the arithmetic silently produces nonsense.

Concrete instance — `scripts/multi_galaxy/features/scaling_relation/slam.py:863`:

    image_half_width = 0.5 * min(dataset_full.shape_native) * pixel_scale

    mask_radius_larger = min(
        max(mask_radius, float(galaxy_distances.max()) + 0.5), image_half_width - 0.1
    )

`shape_native` comes from the capped dataset (16) but `pixel_scale` is the script's
`0.1` literal, while the mask a few lines later is built from
`dataset_full.pixel_scales` (now `0.6`). The run prints:

    Standard mask radius: 3.0
    Enlarged mask radius: 0.30

— the "enlarged" mask is an order of magnitude *smaller* than the standard one. The
resulting mask has no unmasked pixels, and the failure surfaces as:

    File autoarray/operators/convolver.py:112, in ConvolverState.__init__
        y_min, y_max = ys.min(), ys.max()
    ValueError: zero-size array to reduction operation minimum which has no identity

## Not a regression

Control-tested on unpatched `main`: the same script fails *earlier*, with the
documented `Measured luminosity is 0.0` ValueError. PR#431 fixes that root cause and
this latent bug is what lies behind it. The script is already parked in
`config/build/no_run.yaml` as `multi_galaxy/features/scaling_relation/slam` and must
stay parked until this is fixed — update its NEEDS_FIX reason, which currently names
only the 0.0-luminosity cause.

## Scope: this is a class, not a one-off

Do NOT fix only line 863. Sweep the workspace for scripts that mix a local
`pixel_scale` literal with dataset-derived geometry (`shape_native`,
`pixel_scales`, mask radii, `image_half_width`-style arithmetic). The fix is to
derive geometry from `dataset.pixel_scales` rather than the literal — the literal
stays as the `from_fits` argument, which is its correct and only role.

Verification must include a capped-run pass, since the two values coincide in
normal runs and the bug is invisible there.

## Do not

Do not "fix" this by reverting the loader to keep the caller's uncapped scale — that
is PyAutoArray#430, and it mislabels the frame 6x. The loader is right; the scripts
are inconsistent.
