<!-- toc:start -->

**Contents**

- [isothermal-ell-sph-oversampling-at-the-cusp](#isothermal-ell-sph-oversampling-at-the-cusp)
- [remote-mcp-deployment-tiers](#remote-mcp-deployment-tiers)
- [samples-parameter-paths](#samples-parameter-paths)
- [jax-point-source-point-smoke-sentinel](#jax-point-source-point-smoke-sentinel)
- [piemass-potential](#piemass-potential)
- [latent-nan-guard-honest-run](#latent-nan-guard-honest-run)
- [latex-raw-string-docstrings](#latex-raw-string-docstrings)

<!-- toc:end -->

## isothermal-ell-sph-oversampling-at-the-cusp
- status: planned — NOT yet a prompt file; file one via `/intake` before starting
- found: 2026-08-09, while pinning B10 of the @rhayes777 audit (`complete/2026/08/autogalaxy-profile-validation-guards.md`)
- classification: library (PyAutoGalaxy) — accuracy / numerical, NOT part of the audit
- summary: `mp.Isothermal(ell_comps=(0,0))` and `mp.IsothermalSph` are the same profile analytically. Under the DEFAULT `over_sample_size=4` their **potential** disagrees by up to **7% at the central pixel** (`0.0707` vs `0.0761`). With `over_sample_size=1` the disagreement collapses to `3.2e-06` — the same order as the deflections (`2.4e-06`). So this is an **over-sampling artefact at the profile's singular centre**, not a broken potential: over-sampling averages sub-pixel values across the `r -> 0` cusp and the two forms diverge there.
- benign baseline (explained, no action): the elliptical form clips `axis_ratio` to `0.99999` for numerical stability while `IsothermalSph` hardcodes `1.0`; that propagates into `einstein_radius_rescaled` (`0.5000025` vs `0.5`) and accounts for the ~1e-6 floor. This is what @rhayes777 reported as B10 and it is correctly pinned.
- why it still matters: the `1e-2` tolerance pinned in `test_autogalaxy/profiles/test_validate.py::test__b10__potential_agrees_between_elliptical_and_spherical_isothermal` papers over that 7% local disagreement, and the same over-sampling-at-a-singularity behaviour may affect other singular profiles.
- CORRECTION on the record: PyAutoGalaxy#566's PR body and the comment on PyAutoGalaxy#440 describe this as the potential agreeing "three orders of magnitude worse" at `1.9e-03` relative, framed as an accuracy defect. That normalised by the GLOBAL MAX potential and mis-attributed the cause. Superseded by the analysis above.
- RETRACTED: the guess that this shares a root cause with `draft/bug/autogalaxy/nfw_truncated_potential_accuracy.md` (MGE decomposition). It does not — MGE is not involved.
- affected-repos:
  - PyAutoGalaxy

## remote-mcp-deployment-tiers
- issue: https://github.com/PyAutoLabs/autofit_assistant/issues/20 (design/scope shipped 2026-07-21; build gated)
- status: DESIGN-COMPLETE, build BLOCKED-ON-DEMAND — issue #20 holds the full auth/transport/hosting design + Richard/PyAutoMCP coordination. No code, no network surface built. Per prompt "if it earns it": build tiers 2/3 only once demonstrated demand for REMOTE access exists.
- filed: 2026-07-21
- prompt: draft/feature/autofit_assistant/remote_mcp_deployment_tiers.md
- classification: feature (autofit_assistant + autolens_assistant) — transport/deployment/auth, NOT new tools
- suggested-branch: feature/remote-mcp-deployment-tiers
- blocked-by: (1) demonstrated demand for remote access; (2) MANDATORY security-review skill pass before any PR — never auto-ship (network-facing arbitrary-file-read surface; intake mis-sized it small/safe)
- summary: tier2 = opt-in `mcp.run(streamable-http)` + bearer-token ASGI middleware + `PYAUTO_MCP_ALLOWED_ROOTS` path confinement behind cloudflared/ngrok (default stays stdio); tier3 = hosted OAuth/OIDC + per-user scoping (Euclid sample triage; rhayes777/aggregator-agent consumer). Coordinate with Richard FIRST (rhayes777/PyAutoMCP = broader compute/optimise MCP, no transport/auth layer yet) — converge on profiles sharing one auth/transport layer, or share only the tunnel recipe.
- affected-repos:
  - autofit_assistant
  - autolens_assistant

## samples-parameter-paths
- prompt: draft/bug/health_fixes/samples_parameter_paths.md
- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1327 (open, parked)
- status: parked
- filed: 2026-07-08
- classification: library (PyAutoFit) — bug, health_fixes cluster
- suggested-branch: feature/samples-parameter-paths
- blocked-by: clean-output CI re-validation (does NOT reproduce on current main)
- summary: |
    Investigated the PyAutoHeart #27 release KeyError in
    parameter_lists_for_paths. Does NOT reproduce on current main: two legs
    (shapelets 125-prior Basis; multi-analysis 22-prior) pass in-memory AND via
    true from-disk reload (model.json + samples.csv), plus all synthetic
    round-trips. The 745117bd7 fix (May 2026) was already in main at the
    2026-07-06 run; failure most consistent with STALE cached output/ in the
    release run. No library fix warranted — parked pending a clean-output CI
    re-run. Sibling health_fixes/ prompts from the same run are suspect too.
    Full trail: PyAutoFit#1327 comments.
- affected-repos:

## jax-point-source-point-smoke-sentinel
- prompt: draft/bug/autolens/jax_point_source_point_smoke_sentinel.md
- status: planned
- filed: 2026-05-21
- classification: library (triage; routing TBD by bisect)
- suggested-branch: feature/jax-point-source-point-smoke-sentinel
- summary: |
    Pre-existing regression surfaced during fast-viz-zero-contour-perf smoke.
    `autolens_workspace_test/scripts/jax_likelihood_functions/point_source/point.py`
    fails its hardcoded `-83.38049778` literal — `fitness._vmap` returns the
    `-1e99` non-finite-likelihood sentinel from `FitPositionsImagePairAll` on
    canonical main of all three libraries. Last known good: 2026-05-08
    (autolens_workspace_test@362cfa8 rebaseline). Sibling JAX point-source
    profiling drift already tracked as PyAutoLens#514; this is a more severe
    symptom on a different file — held as two hypotheses (same root cause /
    independent regression) for triage.

    Affected repos (when resumed):
      - PyAutoLens (likely primary — PointSolver / FitPositionsImagePairAll)
      - PyAutoGalaxy or PyAutoArray (possible — bisect will say)
      - autolens_workspace_test (literal rebaseline OR no change, depending on outcome)

    Sibling smoke scripts to check while triaging: image_plane.py,
    source_plane.py in the same dir — they share the seed dataset.

## piemass-potential
- prompt: draft/feature/autogalaxy/piemass_potential.md
- status: planned
- filed: 2026-06-05
- classification: library (missing feature)
- suggested-branch: feature/piemass-potential
- summary: |
    PIEMass (Lenstool-ported PIE) has no potential_2d_from, so it now raises a
    clean NotImplementedError (post dark-matter-potentials) and crashes tracer
    visualization (potential FITS extension) — same class as the original NFW
    bug, different profile. No MGE/CSE decomposition hook exists; needs an
    analytic port (Kassiola & Kovner 1993, or the dPIEMass r_s->inf limit) or a
    new convergence-MGE hook. Validate via grad(psi)=alpha self-consistency.
- affected-repos:
  - PyAutoGalaxy

## latent-nan-guard-honest-run
- issue: NEEDS A FRESH ISSUE — #1413 was auto-closed when PyAutoFit#1415 merged (its `Closes` line). Library half is DONE+MERGED; file a new issue for this workspace half at /start_dev time.
- planned: 2026-07-22
- classification: workspace
- suggested-branch: feature/latent-nan-guard-honest-run
- blocked-by: slow-skip-timeout-cap-doc (using autolens_workspace_test; PR #194 OPEN/MERGEABLE)
- affected-repos:
  - autolens_workspace_test
- note: latent/latent_nan_robustness.py PASSES but VACUOUSLY under the smoke profile — TEST_MODE=2 yields only 4 bypass samples, and DISABLE_JAX=1 silently flips its deliberate AnalysisImaging(use_jax=True) to False (PyAutoLens analysis/analysis/dataset.py:89), so the JAX column-masking branch the guard exists to catch is never taken. MultiStartAdam/BlackJAXNUTS precedent. Work = (1) config/build/env_vars.yaml override for `latent/latent_nan_robustness` with unset: [PYAUTO_TEST_MODE, PYAUTO_DISABLE_JAX]; (2) trim the script under the 300s cap. MEASURED: honest run = 412s; PYAUTO_TEST_MODE=1 does NOT help (455s) — Nautilus is NOT the bottleneck (~136s post-fit results update + ~56s latent compute on 100 samples), so the lever is sample count. Script is in the curated smoke_tests.txt, which DOES read env_vars.yaml, so this lands in the per-PR gate. Adjacent to the blocker's own follow-up ("re-time the SLOW siblings"). NOT bugs, verified passing from clean output, no change needed: imaging/model_fit.py and latent/latent_variables_smoke.py.

## latex-raw-string-docstrings
- prompt: draft/maintenance/workspaces/latex_raw_string_docstrings.md
- issue: NOT YET FILED — file at `/start_dev` time, after hands-raw-string-docstring-prefix merges
- planned: 2026-08-20
- classification: workspace (6 repos) — maintenance, prose-only
- suggested-branch: feature/latex-raw-string-docstrings
- blocked-by: hands-raw-string-docstring-prefix — now IN FLIGHT as PyAutoHands#250,
  branch claude/latex-raw-string-docstrings-9h4ine, fix + 6 regression tests pushed and
  awaiting merge. Unblocks the moment that merges; nothing else gates this task.
- blocker-recheck: 2026-08-20 (resumed /start_dev) — STILL BLOCKED. PyAutoHands main @ cdea28c
  still carries both defects, reproduced on a probe pair differing only by an `r`:
  `_narrative_docstring_ranges` [(0,2),(6,10)] -> [(6,10)] (raw block dropped), and
  `read_env_declaration` ['jax'] -> None. Both silent. No fix branch on the remote;
  its own blocker `feature/hands-hygiene-leftovers` is still open. No issue filed, no
  workspace repo touched. Also folded into the prompt this pass: the Python 3.11-vs-3.12
  warning-class trap (a `SyntaxWarning`-only sweep returns a VACUOUS zero on 3.11 and
  would falsely clear the verification gate — verified on 3.11.15), and the supersession
  of draft/maintenance/autolens_workspace/latex_docstrings_invalid_escape_warnings.md
  (same task, autolens_workspace-only, now marked SUPERSEDED).
- summary: |
    Prefix `r` on every module-level narrative docstring containing LaTeX, in
    41 files across 6 workspace repos. The 2026-08-06 prompt named 4 lines in 2
    repos; the 2026-08-20 survey found the real surface.

    TWO sweeps are required, not one. `SyntaxWarning` fires only for escapes
    Python does NOT recognise (171 hits). The ones it DOES recognise fire
    silently and corrupt the string with no diagnostic — `\t` in `\theta`, `\f`
    in `\frac`, `\r` in `\rm`, `\b` in `\beta`, `\a` in `\alpha`, `\v` in
    `\vec` (132 hits). HowToLens chapter_4 tutorial_5_cluster_scale.py has ONLY
    silent hits and zero warnings, so a warning-only sweep skips it. Drive the
    edit off the UNION.

    Per-repo file counts: HowToFit 4, HowToGalaxy 4, HowToLens 8,
    autofit_workspace 2, autogalaxy_workspace 6, autolens_workspace 17. Full
    per-file list with counts is in the prompt.

    Notebooks are NOT currently corrupt — the generator reads source text, not
    runtime values — so this is warning noise plus latent breakage, not a
    shipped-artefact bug.

    VERIFICATION GATE: after regenerating each repo
    (`PYTHONPATH=../PyAutoHands/autohands python3
    ../PyAutoHands/autohands/generate.py <project>`), `git diff notebooks/
    markdown/ llms-full.txt workspace_index.json` MUST be empty — the generator
    swaps the delimiter for `'''` either way, so a non-empty diff means the
    Hands prerequisite is incomplete.

    EXCLUDED: `autolens_workspace/dataset/cluster/a2744/prep.py:38` is a genuine
    TSV tab, not LaTeX. Also excluded, and worth a separate library prompt:
    PyAutoGalaxy (4 warnings) and PyAutoCTI (19) carry the same defect in
    source, but need ship_library + a pending-release gate. autocti_workspace,
    every *_workspace_test / *_workspace_developer, and PyAutoFit / PyAutoArray
    / PyAutoLens source were swept and are clean.
- affected-repos:
  - HowToFit
  - HowToGalaxy
  - HowToLens
  - autofit_workspace
  - autogalaxy_workspace
  - autolens_workspace
