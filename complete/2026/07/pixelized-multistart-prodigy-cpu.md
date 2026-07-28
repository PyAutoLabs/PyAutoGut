## pixelized-multistart-prodigy-cpu
- completed: 2026-07-28
- issue: autolens_workspace_developer#117 (closed)
- prs: autolens_workspace_developer#119, autolens_profiling#91, autolens_workspace#363 (all merged 2026-07-28)
- branch: `feature/pix-prodigy-cpu` (3 repos; deleted post-merge)
- verdict: SHIPPED — MultiStartProdigy recovers the exact truth on pixelized meshes; the #100/#101 "Nautilus wins pix" verdict is overturned
- summary: |
    Broad-start af.MultiStartProdigy (16 starts, resurrect, lr-free) on the
    SLaM source_pix[1] objective, RAL CPU (both A100 nodes unavailable).
    knn: exact truth (+29724, r_E 1.599, free AdaptSplit; late reg-mode
    breakout ~step 1300). Delaunay: exact truth via inherited reg (+30202,
    ~150 steps), free Matern (+29792, no wall), even free AdaptSplit after a
    ~2000-step resurrection tax. Beats matched-settings Nautilus baselines
    by 10-24k nats in a fraction of the wall. THE MECHANISM WAS THE
    REGULARIZATION AXIS, not mesh landscape: AdaptSplit's double-squared
    coefficients are escape-taxed (knn) or NaN-walled (delaunay); Matern or
    SLaM reg inheritance removes the hazard at equal fit quality. Rectangular
    left open: throughput-bound (~17x knn step cost — A100 follow-up) with
    the sharp-bandwidth (0.1) hypothesis arms still running.

    Found + fixed two library bugs mid-campaign (PyAutoFit#1423 cadence arc;
    PyAutoArray PR#411 Delaunay NaN-callback hardening — validated under
    fire). Deliverables: pix_prodigy_findings.md + harness + artifacts
    (wsdev); mature first-class Prodigy cells + knn/delaunay_matern model
    types + campaign knowledge (autolens_profiling); user-facing lessons in
    guides/modeling/searches.py (autolens_workspace). The Brain learned the
    findings maturation lane (samplers faculty AGENTS.md; SamplerSurface
    scan extension filed). 6 follow-ups in ideas.md. Ops traps recorded:
    library upgrades invalidate multi-start resume chains (FoM sanity
    check); smoke tests must exercise the production min()-branch.
