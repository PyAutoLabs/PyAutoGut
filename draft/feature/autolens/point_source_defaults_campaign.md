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
