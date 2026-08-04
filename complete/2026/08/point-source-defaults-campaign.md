- issue: https://github.com/PyAutoLabs/PyAutoLens/issues/678
- completed: 2026-08-04 (phases A–D merged 2026-07-31 → 2026-08-03; evidence tail merged and issue closed 2026-08-04)
- library-prs: https://github.com/PyAutoLabs/PyAutoLens/pull/679 (phase A, MERGED 2026-07-31T14:11:06Z as 86dea4107) + https://github.com/PyAutoLabs/PyAutoLens/pull/686 (phase C default swap, MERGED 2026-08-03T18:31:35Z as 4927738e)
- workspace-prs: https://github.com/PyAutoLabs/autolens_workspace/pull/453 (phase D, MERGED 2026-08-03T18:35:08Z) + https://github.com/PyAutoLabs/autolens_workspace/pull/468 (evidence tail, 2026-08-04)
- evidence-prs: https://github.com/PyAutoLabs/autolens_profiling/pull/100 (phase B harness + 23 result cells + notes, 2026-08-04)
- bugfix-prs: https://github.com/PyAutoLabs/PyAutoFit/pull/1441 + https://github.com/PyAutoLabs/PyAutoLens/pull/685 + https://github.com/PyAutoLabs/autofit_workspace_test/pull/81 (all MERGED 2026-08-01)
- summary: took the point-source likelihood options from "several undocumented
  conventions" to "one evidenced default per axis, with the alternatives
  documented and their use-cases named". Four defaults moved: tensor
  (`"jacobian"`) source-plane weighting, solved centres on both chi-squared
  flavours, solved-centre demonstrated defaults across the workspace examples,
  and — the breaking one — `AnalysisPoint` image-plane pairing from
  `FitPositionsImagePairRepeat` to `FitPositionsImagePairAllSolved`, shipped
  with a `## API Changes` heading. Phase A added the two library prerequisites
  the evidence needed (max-shifted log-sum-exp in `FitPositionsImagePairAll`,
  finite at ≳38σ where it previously underflowed to `-inf`; a `weighting` class
  attribute giving free-centre `FitPositionsSource` the tensor option).
- evidence: the defaults rest on a truth-anchored A100 campaign in
  autolens_profiling — 23 result cells across galaxy-scale (quad) and
  cluster-scale (multi-plane, two sources) tiers, each evaluating its likelihood
  flavour AT the simulator-truth model and scoring the search by
  `delta = max_log_likelihood − truth_log_likelihood`. That anchoring is what
  makes the campaign conclusive rather than anecdotal: a large positive delta
  means the LIKELIHOOD mis-ranks models (a wrong model beats truth), a negative
  delta means only the SEARCH failed. The two failure classes are the reason the
  cluster gradient result below does not disturb any default.
- discriminator: the default swap rests on ONE arm — `simple_missing` (one true
  image removed). `PairRepeatSolved` mis-ranks truth by +1.8e5 (truth logL
  −183389) because nearest-image pairing cannot leave a model-predicted image
  unmatched; `PairAllSolved` recovers truth at +1.3. On clean data the two are
  statistically equivalent (+2.85 vs +2.88, 147 s vs 163 s), so robustness and
  not performance decides it.
- non-result-that-is-a-result: the complementary `simple_extra` arm (one
  spurious observed position) NEVER COMPLETED for either pairing — 331885 and
  331886 both TIMEOUT at 8h walls after a 2h-wall first attempt, the all-to-all
  arm ending f_live=0.92, N_eff=12, logZ=−14238. A spurious position cannot be
  explained by any model, so it imposes an honest ~−1.4e4 floor on EVERY sample
  alike, the live set never compresses, and Nautilus cannot converge. The DNF is
  SYMMETRIC, so this arm does not discriminate between the two candidate
  defaults and the default never rested on it. Recorded in the pairing guide as
  the stronger user-facing warning it actually is: contamination destroys
  convergence outright rather than quietly biasing the fit, so a fit that will
  not converge is itself a reason to re-examine the position catalogue.
- gate-reconciliation: #686's body said "hold merge until 331885/331886 land and
  the exp-3 verdict is confirmed on the issue". Both jobs had in fact landed
  2026-08-01/02, two days BEFORE the 08-03 merge, so the evidence existed at
  merge time and only the issue write-up was skipped; the verdict was posted
  2026-08-04 (issuecomment-5177795748). The outstanding debt was documentation,
  not science — the discriminating missing-image arm was in hand when the PR
  opened.
- discovery-1 (library defects the campaign flushed out): the first cluster
  MCR-halo gradient search crashed with `UnexpectedTracerError` and then
  produced all-NaN gradients. PyAutoFit#1441 — attributes derived inside
  `__init__` from prior parameters (`NFWMCRLudlowSph.scale_radius` from free
  `mass_at_200`) were classified as pytree AUX data, so under a trace they are
  tracers and the PointSolver `custom_jvp` rule's inner `jax.jvp` got them
  stale; flatten now promotes JAX-valued attributes to child leaves.
  PyAutoLens#685 — padded solver rows were zeroed to (0,0), which IS the cluster
  profile centres, where the NFW deflection Jacobian is NaN; reverse mode
  row-sums cotangents, so one padded row poisoned every parameter. Both were
  invisible to every non-gradient path, which is why they survived until this
  campaign.
- discovery-2 (`PointSolver.solve` plane_redshift): `solve` defaults to the
  tracer's FINAL plane, and both cluster simulators omitted `plane_redshift`, so
  the z=1.0 source's positions were generated as if it sat at z=2.0 — truth logL
  −4.2e6, becoming +26.1 once fixed. Fixed in the profiling simulator and in
  `autolens_workspace/scripts/cluster/simulator.py` (which had tainted
  autolens_workspace#436's convergence run).
- discovery-3 (the evidence tail, 2026-08-04): job 331887 re-ran the cluster
  gradient cell after both library fixes. It now COMPLETES end-to-end — 832 s on
  the A100, finite value, no NaN — validating the merged fixes through a full
  search rather than only the 8-draw gradient probe, with a truth anchor
  (+14.658) identical to its Nautilus twin's. **But the search still misses the
  basin: delta −1723.6, against Nautilus's +16.9 on the same objective.** That
  KILLS a recommendation both the notes and the pairing guide had been holding
  open — that the solved image-plane likelihood was "the gradient-search story
  at cluster scale". It fails alongside the source-plane cells (−14.8, −11062),
  so cluster scale is Nautilus's across every objective tested, and the guide now
  says so unconditionally while explicitly preserving the galaxy-scale
  solved-centre gradient case. Making the gradients finite was a CORRECTNESS
  fix; it did not buy convergence. Because a negative delta is an optimizer
  defect and not a likelihood one, no shipped default is affected.
- silent-resume trap: two free `simple` Nautilus cells had been silent PyAutoFit
  resumes — sub-second sampler wall, because an identifier ignores the DATASET,
  so a same-path re-run returns the old posterior instantly. Re-run clean as
  331888/331889 (~141–162 s sampler wall, ~14.4k posterior samples). Both
  reproduced their prior conclusions within scatter (image-plane delta
  +2.27→+2.38; source-plane +33476.5→+33474.5 on an identical truth anchor), so
  the resumes had not misled — but the shipped numbers now rest on searches that
  actually ran. exp-4's free `einstein_radius` std moved 0.0273→0.0293, i.e.
  solved error bars are ~28% wider rather than ~40%; the direction (solved is
  NOT overconfident) is what the docs claim and it holds.
- harness-quirks-recorded: `likelihood_evals` is 65 for EVERY MultiStartProdigy
  cluster cell (it counts vmapped batch calls, not per-start steps) and
  `model_summary.best_fit` is `AttributeError('ModelInstance' object has no
  attribute 'galaxies')` on EVERY cluster cell INCLUDING the Nautilus ones. Both
  are pre-existing reporting quirks of the cluster harness. Written into the
  notes because each looks exactly like a defect of whichever run you happen to
  be reading.
- lint-fix: the phase-B plane_redshift fix moved `jitted_solve` from a
  module-level function into a per-iteration assignment, making it a loop
  variable captured by reference in the `jit_profile` lambda (ruff B023). Not a
  live bug — the lambda is consumed inside the same iteration — but it turned
  lint red on the branch. Diagnosed by CONTROL TEST rather than assumption: main
  has the same-looking line and its lint is green, which pointed at a ruff
  version change; running ruff locally on main's unchanged file (passes) vs the
  branch's (fails) proved the branch introduced it.
- codex-cross-review (2026-08-04, before merge): 7 findings, ALL 7 verified real
  (contrast the PR#659 precedent where 1 of 9 was refuted — verify anyway). The
  one that mattered: BOTH docs, plus a third file, explained the missing-image
  discriminator with a WRONG MECHANISM — "nearest-image pairing has no way to
  leave an unobserved model image unmatched". It does: `pair_repeat.py` builds
  an `unmatched_model_mask` and penalizes via `unmatched_model_policy`. The real
  mechanism is that the model image which would have paired to the missing
  observation becomes the nearest neighbour of no observed position, so the
  default `magnification_filter` policy classes it a BRIGHT extra image (the
  exemption is for demagnified ones) and charges its full distance to the
  nearest other observed position — truth punished for correctly predicting an
  image the data lacks. The +1.8e5 number and the choice of default are
  untouched; only the taught explanation was wrong, and it was PRE-EXISTING
  phase-D text, already merged, not introduced by the tail. Other findings: a
  "+0.6 galaxy delta" that was actually the solved-scalar TRUTH likelihood
  (tensor is truth +12.75 / delta +2.54); a self-contradiction where the notes
  called a +5.8 delta "prefers wrong models" while their own reading key calls
  that ordinary basin recovery; an unattributed 8/8 gradient probe; 12.6 vs
  12.4 min; "hundreds to thousands" for deltas spanning -15 to -11062; and a
  SECOND stale "still being validated" sentence in `cluster/modeling.py`.
- sweep-lesson (this task, three times): grepping for the stale STRING missed
  what grepping for the stale CLAIM found. The pairing-guide fix left the same
  falsified recommendation standing in `cluster/modeling.py` (different words);
  fixing that file's first instance left a SECOND one lower down; and fixing the
  guide's wrong mechanism left a third copy in `point_source/fit.py` that the
  cross-review never saw because it was pointed at only two files. Reviewer
  scope is not repo scope — re-sweep the whole workspace for the claim after
  every fix.
- F3-OPEN-GAP (accepted, human decision 2026-08-04 "we can't do much with F3"):
  the DNF arms' convergence diagnostics — `f_live`=0.92, N_eff=12,
  logZ=-14238 — are NOT reproducible from any surviving artifact. Checked RAL
  directly: the output trees hold only `metadata`, `model.info`, `.identifier`
  and a 12-line `search.log` with no sampler statistics, no Nautilus checkpoint,
  and no SLURM stdout anywhere under `/mnt/ral/jnightin`. They were read from
  live stdout by an earlier session and that stdout is gone. Both docs now
  separate the reproducible part (sacct TIMEOUTs, the 147.2 s / 162.7 s
  comparison walls) from recorded interpretation, and concede that a timeout
  proves non-completion within the cap and not destroyed convergence. If anyone
  ever needs the mechanism rather than the outcome, re-run one arm with stdout
  captured — that is the only way to close it.
- sizing-override: Brain sized this too-large (score 11) and proposed a
  design/core-API/examples/docs split. Not taken — the score is prose-driven and
  the API had already shipped in #549. The human-scoped A–D phasing was kept
  (potential-correction precedent). Same false positive later seen on
  simulator-util-to-af-ex (score 13).
- coordination: SUPERSEDED the 2026-07-31 morning galaxy-free/cluster-solved
  split (the human widened it to solved everywhere); COORDINATED with
  cluster-point-solved-default (autolens_workspace#436) so phase D touched
  cluster/ only to reconcile; ABSORBED the ideas.md PairAll-logsumexp entry and
  draft/research/autolens_profiling/cluster_gradient_search_benchmark.md.
- deferred: the time-delay + solved-fluxes free-H0 search arm was explicitly
  deferred at scoping and remains un-run.
- stale-claim-log: this entry's `repos:` line went stale FOUR times during the
  task, each time firing `worktree_check_conflict` against an unrelated task
  while the entry's OWN status line already said the PR was merged
  (autofit_workspace_test#81, PyAutoFit#1441, PyAutoLens #679/#685/#686, and the
  merged autolens_workspace phase-D branch). The evidence-tail work also found
  that merged branch still checked out and 21 commits behind main, with main
  having since touched the very file being edited — committing there would have
  reverted a `pre build` formatting commit. Release a claim when its PR merges,
  and re-derive the branch base before editing rather than trusting the worktree.

## Original prompt

# Point-source defaults campaign: tensor/solved defaults, pairing decision, full docs + performance evidence

Human-scoped 2026-07-31 (#657 wrap-up chat; run in a fresh session). **End goal: a full
workspace docs update** — the point_source guides and modeling scripts present ALL
likelihood options with performance/robustness information — **with the complete evidence
base built in autolens_profiling** (truth-anchored result JSONs + a results/notes summary
doc; "full information building", not one-off runs).

**Target defaults to demonstrate and then adopt:**
1. **Source-plane chi-squared: tensor weighting with SOLVED centres**
   (`FitPositionsSourceSolved`, `weighting="jacobian"`), while also demonstrating the
   tensor works with FREE centres (requires phase A below — no free-centre tensor exists
   in the API yet).
2. **Image-plane chi-squared: SOLVED centres** (free centres demonstrably need sampler
   muscle: 2026-07-31 benchmark — free-centre Prodigy needed 256 starts vs solved
   converging at 64; Nautilus handles both).
3. Workspace demonstrated defaults move to **solved centres everywhere**, with the free
   option CLEARLY documented (modeling.py scripts + point_source guides), including WHEN
   free is required: informative centre priors, linked centres across bands/epochs,
   centre-as-science, and the standard-candle flux caveat (`PointSolved` forces
   `FitFluxesSolved`, whose flat-prior F* discards standardizable-candle priors — glSNe).
4. Image-plane pairing: expected outcome is **all-to-all** (`FitPositionsImagePairAll*`)
   as default — smooth in the pairings (gradient-friendly), principled Occam mixture —
   pending the phase-B robustness discriminator. This is an `AnalysisPoint` DEFAULT
   CHANGE (currently `FitPositionsImagePairRepeat`) → release notes `## API Changes`.

**SUPERSEDES** the 2026-07-31 morning split decision (galaxy-scale free / cluster solved)
— the human widened it to solved demonstrated defaults everywhere. **COORDINATE, don't
duplicate**: the cluster swap is ALREADY IN FLIGHT as its own task
(`active/cluster_default_point_solved.md`, issue autolens_workspace#436, routed to
start_workspace 2026-07-31) — phase D here covers the galaxy-scale point_source scripts
and the guides; touch cluster scripts only to reconcile with whatever #436 lands (it may
merge first). This prompt also **ABSORBS** the ideas.md PairAll-logsumexp entry (phase A).
**EXPLICITLY DEFERRED**: the time-delay + solved-fluxes free-H0 search arm (revisit after
this campaign).

## Phase A — library prerequisites (PyAutoLens; small PR, do FIRST)

1. **PairAll log-sum-exp stabilization**: `FitPositionsImagePairAll.chi_squared`
   exponentiates before logging → underflows to `-inf` at ≳38σ worst-image mismatch
   (measured 2026-07-31), strangling gradient flow (the `-inf` plateau is the prime
   suspect for the 64-start image-plane failure). Rework in log-space: values identical
   wherever currently finite, finite where currently `-inf`; re-run the wst
   `jax_likelihood` literals (unchanged at truth) as the invariance gate. Prerequisite —
   every phase-B result changes if run against the unfixed objective.
2. **Free-centre tensor option**: `weighting` class attribute on `FitPositionsSource`
   (default `"magnification"` — back-compat, Lenstool comparisons and literals untouched;
   `"jacobian"` opts into the tensor + matching normalization, reusing
   `precision_tensor_components_from` from `solved.py`). Numpy unit tests per house rule.

## Phase B — evidence campaign (autolens_profiling; truth-anchored; A100s on RAL)

Methodology from the 2026-07-31 runs (`results/searches/**`, PR#99): evaluate each
likelihood flavour AT THE SIMULATOR TRUTH as the anchor; compare Nautilus + Prodigy
best-logL/recovery/wall against it. Write every run's JSON + a
`results/notes/point_source_defaults_campaign.md` synthesis.

**Two dataset tiers — run the full matrix on BOTH:**
- **Galaxy-scale**: the existing profiling `simple` quad (anchors + 2026-07-31 results
  already in `results/searches/`).
- **Cluster-scale**: port the `autolens_workspace/cluster` test case (the family-CSV
  multi-plane system — 2 sources at different redshifts, dPIE members + host halo,
  `point_datasets.csv` conventions; the good test case per the human). Expect MUCH
  slower (image-plane forward solve ~0.3 s/call at cluster scale; multi-plane tracer).
  This is where the solved-centre dimensionality win compounds (−2 params/source) and
  where the defaults matter most. Constraint: pin cosmology in every solver-chained
  gradient cell (free cosmology cannot cross the custom_jvp boundary — Tracer aux).
  This tier ABSORBS `draft/research/autolens_profiling/cluster_gradient_search_benchmark.md`.

**Execution environment — A100s on RAL (the human's call: the profiling runs that guide
all of this run on GPU):**
- Drive with the project's `hpc/sync` CLI: `hpc/sync push-submit gpu <script>` (SLURM
  `gpu`-partition array, JAX auto-uses the A100), then `hpc/sync jobs` / `tail gpu` /
  `pull`. Venv: `/mnt/ral/jnightin/PyAuto` via its `activate.sh` (`PYAUTO_HPC_BASE`).
- **Phase A must be MERGED and synced to RAL first** — refresh the mirrored library
  mains with `HPCPullPyAuto` before submitting anything.
- **GOTCHA (recorded)**: sbatch does NOT inherit `JAX_ENABLE_X64` — set x64 explicitly
  inside the scripts/sbatch or everything runs float32 silently, poisoning the truth
  anchors and FD checks. `/mnt/ral` is NFS-slow — submit detached, don't babysit.
- `hpc/sync pull` the result JSONs back into `results/searches/**` so the
  information-building convention (committed JSONs + notes synthesis) holds; record
  device blocks (the JSONs carry `device.backend`) so CPU-laptop vs A100 rows are
  distinguishable. CPU spot-checks on the laptop are fine for smoke, not for the
  committed evidence.

1. Source-plane tensor-solved cells (Nautilus + Prodigy `source_plane_solved` — fit
   dispatch already exists) vs the free-centre TENSOR variant (new, phase A.2) vs the
   scalar flavours (already run: scalar truth −33788 vs wrong models −110/−313 — the
   bias showcase to reproduce in the notes).
2. Image-plane solved vs free (extend the existing 2026-07-31 results: solved 64×300
   converges +2.37/truth+7.74; free needs 256 starts, plateaus at −47.7/truth+7.20).
   Re-run the free-centre arm AFTER phase A.1 to test the plateau hypothesis.
3. **Pairing discriminator** (the open decision): simulate a quad with (a) one image
   REMOVED from the dataset and (b) one spurious EXTRA position; compare posterior bias
   of `PairAllSolved` vs `PairRepeatSolved` (Nautilus). This decides all-to-all vs
   repeat as default; document whichever caveats fall out.
4. **Posterior WIDTH comparison** (profile-vs-marginal honesty): same dataset, Nautilus
   free-centre vs solved image-plane — compare mass-parameter error bars. The image-plane
   solved variants are plug-in profiles (no marginalization term); if solved posteriors
   are materially overconfident, the docs' free-centre section must say so.
5. **Near-caustic stress test** (tensor domain of validity): source hugging the caustic
   so the linearization `A` at observed positions degrades; establish where tensor
   source-plane itself breaks and image-plane must take over → domain-of-validity prose
   for the pairing guide.

## Phase C — defaults decision + library change (PyAutoLens)

Informed by phase B: `AnalysisPoint` `fit_positions_cls` default →
`FitPositionsImagePairAllSolved` (expected); decide `FitPointDataset` default
consistently (currently `FitPositionsImagePair` — the Hungarian, already superseded).
Release notes with `## API Changes` heading (classify_pr matches headings).

## Phase D — workspace docs update (autolens_workspace; the END GOAL)

- All point_source + cluster modeling.py scripts demonstrate solved-centre defaults;
  free-centre composition shown as the clearly-documented alternative WITH its
  use-cases (see 3 above).
- `guides/point_source_pairing.py` becomes the full option matrix WITH performance and
  robustness numbers from phase B (per-option: params, wall/eval cost, gradient
  behaviour, robustness to missing/extra images, when to prefer).
- `point_source/fit.py`, cluster guides, lenstool mapping updated consistently
  (lenstool script stays free-centre scalar deliberately — its table already notes the
  solved/tensor siblings).
- Notebooks regenerated; ship_workspace behind the library-first gate.

## Context literals (2026-07-31, all in autolens_profiling results/searches + #657)

- Truth anchors (galaxy-scale `simple` quad, |mu| at obs = [8.2, 45.9, 366.6, 28.3]):
  image_plane free +7.20 / solved +7.74; source_plane scalar −33788.4 (the mu=367 image's
  radial noise mis-mapped), tensor-solved **+0.6**.
- Tensor-vs-solved isolation: solved+scalar still prefers wrong models (truth −2338 vs
  −848/−610); solved+tensor ranks truth first by >1500 logL → **the weighting is the
  fix; the solved centre is the orthogonal dimensionality/marginalization win.**
- Benchmark: nautilus image_plane +9.56 (740s) at truth; prodigy solved +2.37 (982s,
  64×300) truth recovered THROUGH the solver; prodigy free −47.7 (3516s, 256×300)
  basin found but plateaued.
- Constraint: free cosmology cannot cross the solver custom_jvp boundary (Tracer aux) —
  pin cosmology in solver-chained cells (follow-up filed separately).

## Exit criteria

Phase-A PR merged (literals invariant); phase-B notes doc + JSONs committed; phase-C
default change merged with release notes; phase-D workspace PR merged: guides/scripts
present all options with evidence-backed defaults (solved centres, tensor source-plane,
all-to-all image-plane if phase B confirms) and a clear, use-case-driven free-centre
section.
