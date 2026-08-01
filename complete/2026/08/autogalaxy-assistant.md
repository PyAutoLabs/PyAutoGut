- issue: https://github.com/PyAutoLabs/PyAutoBrain/issues/188 (epic; human to close)
- completed: 2026-08-01
- repo-born: https://github.com/PyAutoLabs/autogalaxy_assistant (PUBLIC at birth by user choice; bootstrap 8f9e57b direct to main)
- prs-assistant: #1 frame+tooling (157 files) · #2 wiki/core (31 pages + 3 skills) · #5 Phase-4a 9 core-loop skills (reopen of #3 — GitHub CLOSED the stacked PR when its merged base branch was deleted; retarget to main BEFORE deleting the base) · #4 dataset+front-door · #6 Phase-4b 8 feature skills · #7 literature wiki · #8 benchmarks+hpc+ledger-retirement — ALL MERGED 2026-08-01
- prs-external: autogalaxy_workspace#200+#201, PyAutoGalaxy#545+#546, HowToGalaxy#54+#55, .github#7 (signposts + science-context repoints; the llms.txt-census birth checklist fully closed)
- summary: Built autogalaxy_assistant, the galaxy-structure-modeling assistant cell, HAND-AUTHORED by direct comparison against autolens_assistant (clone tool NOT run — user judged it outdated; partition 56/89/301/0 @ b9c10a9 used as checklist only; autofit precedent). PUBLIC at birth, so every merged PR left a residue-free tree; all work executed by Opus subagents (user override) with judgment in the driving session. Final state: 27 skills (9 core loop, 8 features, 2 output surfaces, maintenance/meta/workflow/literature), 41-page complete wiki/core, a 39-file literature wiki with a 253-entry bibliography in which EVERY citation was verified against arXiv/CrossRef/ADS (~330 recorded verifications), a bundled REAL 4-band JWST dataset (COSJ100020+015344, spec-z 0.3422 zCOSMOS, reduced via PyAutoReduce from the cached COSMOS-Web program-1727 exposures, COWLS non-lens cross-match, measured-only info.json, 448-line provenance README), 4 benchmark cards (RESULTS.md honestly unrun), galaxy-tuned hpc/ validated by execution, README front door with dataset-grounded starter prompts. Newborn gate: legs 1-3 green (leg 3 = wiki-currency green on every PR); leg 4 = autogalaxy_assistant#9 (human chat-surface smoke, autofit precedent).
- dataset: COSJ100020+015344 = COSMOS2020 499609 / zCOSMOS 812167, selected from the cached exposure footprint by wide-field source detection + catalogue cross-match; F115W/F150W 419²@0.03", F277W/F444W 209²@0.06"; sky pedestal deliberately un-subtracted (documented); tier-2b STPSF kernel (tier-1 ePSF REJECTED — see upstream bugs); smoke Sersic fit reduced χ² 0.797, free sky recovers measured pedestal to 1.4%.
- upstream-bugs-found (unfiled unless noted): (1) PyAutoReduce tier-1 mosaic ePSF broken on crowded JWST fields — stars.find_stars selects 76% galaxies → kernel ~17× too broad; ALSO affects reduce_cosmos_web_ring.py's acceptance (takes no PSF arg); starred backend fails identically → fix belongs in find_stars. (2) af.LBFGS under JAX terminates at iteration ZERO returning its start point while logging "Search complete". (3) autogalaxy_workspace chaining.py's core claim is stale — result.model no longer narrows priors (narrowing = result.model_centred*); 3 assistant wiki pages had absorbed it and were fixed. (4) ellipse scripts document log-likelihood as −2.0×χ² (actual −0.5×χ²). (5) shapelets/modeling.py claims N=3 but builds N=43 (unlinked ell_comps + latent loop-variable bug leaves 24/25 components unconfigured). (6) workspace kwarg typos silently swallowed: auto_correlations_settings=, n_live= (DynestyStatic). (7) psf.py names nonexistent psf_with_odd_dimensions_from (real: ag.preprocess.kernel_with_odd_dimensions_from). (8) modeling.py claims N=11/N=21 where measured N=9. (9) autogalaxy __init__ __getattr__ RecursionError on getattr(autogalaxy, "plot") pre-import. (10) autogalaxy_workspace config lacks priors/mass/dark/gnfw_virial_mass_conc.yaml though ag.mp.gNFWVirialMassConcSph exists. (11) PyAutoGalaxy docs/index.md sample uses removed OO plotters; RTD says Py "3.12-3.13" vs classifiers through 3.14. (12) "273 visibilities" prose vs 190 rows in sma.fits; opposite transformer defaults between Interferometer.from_fits (NUFFT) and SimulatorInterferometer (DFT).
- traps: (a) STACKED-PR: GitHub closes (not retargets) a dependent PR when you delete its just-merged base branch via the API — retarget base=main FIRST, then delete (cost: #3 → reopened as #5). (b) SPARSE-CONE: wiki-currency sparse-clones autogalaxy_workspace at scripts/ only — every workspace citation (inline AND frontmatter sources: paths, which inline-pattern greps cannot see) must be scripts/... or a root FILE; three CI failures, one root cause. (c) WHEEL-VS-MAIN: agents verifying symbols against the ambient editable stack leaked two main-only APIs (subplot_fit_imaging_list, the jitted-simulation pytree helper) into wheel-tracked docs — verify against the released wheel in a clean venv, always. (d) EXECUTION BEATS INSPECTION: running each skill's primary path caught output_filename raising TypeError on most subplot functions (AGENTS.md's own "Right" example was a failing call), from_json returning plain list not ag.Galaxies, PYAUTO_TEST_MODE=2 writing no fit products, af.Model(ag.DatasetModel) = 0 free params silently. (e) The audit CANNOT see unregistered aliases — dropping "al" from ALIAS_TO_MODULE makes al.* prose invisible, not failing; residue detection is grep-only. (f) benchmark evidence: RESULTS.md regenerated from the EMPTY runs/ dir; calibration runs are the follow-up — never fake scores. (g) root .gitignore output/ swallowed hpc/batch_*/output/.gitignore keepers — sbatch would fail on fresh clones; explicit negations needed.
- citation-discipline: every literature entry API-verified pre-inclusion; the process caught 4+ wrong-from-memory arXiv IDs, a one-digit Kormendy collision (0407343 vs 0407434), a same-key different-paper bib conflict (both 1987 Dressler papers verified via CrossRef to resolve it), and one journal_ref FABRICATED by a fetch-summarising step. Independent 8-entry random spot-check: all exact.
- follow-ups-open: leg-4 chat-surface smoke (autogalaxy_assistant#9); benchmark calibration runs (RESULTS.md honestly empty); second HST/PyAutoReduce dataset + mask_extra_galaxies.fits for the bundled cutout; upstream bug filings (1)-(12); reference-side systemic de-lensing of autolens_assistant's generic tier (standing autocti finding, still unfiled — this birth re-confirmed it: $AUTOLENS_ASSISTANT env-var leak in start-new-project.md); PyAutoBrain REFERENCE_PROFILES["autogalaxy_assistant"] deferred to whoever first clones FROM it; paper/ + draft-pdf.yml deferred.

## Original prompt

# Build autogalaxy_assistant — the galaxy structure modeling assistant cell

Type: feature
Target: autogalaxy_assistant
Repos:
- @autogalaxy_assistant
- @PyAutoBrain
- @autogalaxy_workspace
- @PyAutoGalaxy
- @HowToGalaxy
Difficulty: large
Autonomy: supervised
Priority: normal
Status: formalised

Build **autogalaxy_assistant**, the science-assistant cell for galaxy structure
modeling with PyAutoGalaxy, hand-built as a mirror of the mature reference cell
`autolens_assistant` (the autofit_assistant precedent: hand-authored by direct
comparison, with the Clone Agent's template partition used as a checklist only —
the clone tool is NOT run; user judged it a bit outdated). This completes the
llms.txt-census birth checklist (`complete/2026/08/llms-txt-census-fixes.md`)
and resolves the 8 public places that already advertise the assistant and 404
today (PyAutoGalaxy README/RTD ×4, autogalaxy_workspace start_here ×3, org
profile README).

## Original request (verbatim)

> Make the autogalaxy_assistant, which is basically a mirror of the
> autolens_assistant but for galaxy structure moeling, which is of course
> PyAutoGalxy's science case. I think this is self explanatory but ask
> questions if not. and of course this will continue and build on the llms.txt
> work

## Locked human decisions (2026-08-01)

- Repo gate: **PyAutoLabs/autogalaxy_assistant, PUBLIC at birth** (autofit
  precedent) — every merged PR must leave the tree honest, zero lensing
  residue, green CI.
- **Real galaxy cutouts sourced now** (recommended: one multi-band JWST
  COSMOS-Web NIRCam cutout of a non-lens galaxy; human names/approves the
  target — never invent provenance). Second HST/PyAutoReduce dataset deferred.
- **Phased PRs under one epic** on PyAutoBrain (autocti precedent #136), 7
  phases: 0 epic/repo/registry → 1 frame+tooling+stack reference → 2 real
  dataset+README+external signposts → 3 wiki/core+tooling skills → 4a/4b ag_*
  skill set → 5 wiki/literature → 6 benchmarks+HPC+full newborn gate.
- Execution phases delegated to **Opus** subagents (user override of the usual
  Sonnet split); judgment/review stay in the driving session.

## Routing / gates

- Partition verified live: 56 generic / 89 mixed / 301 domain / **0
  unclassified** @ reference `b9c10a9` — no reference-side Phase-0 unblock
  needed (unlike autocti).
- Intake trap (hit on ic50 + autocti): the Target is the assistant cell —
  PyAutoGalaxy is a consumed dependency, never the edit target.
- Privacy seam: `PyAutoMemory/wiki/galaxies/` (thin: 2 concepts / 0 entities /
  12 sources) consulted for structure/pointers only, never copied; all
  literature content authored from public sources with WebSearch-verified
  citations.
- Publish gate: `PyAutoHeart/docs/newborn_validation.md` legs 1-4 run
  per-phase where applicable and in full at Phase 6 (public at birth means the
  gate protects honesty, not the visibility flip).
- Full approved plan: the epic issue carries the phase checklist; detailed
  design in the driving session's plan record.
