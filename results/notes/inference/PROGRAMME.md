# PyAutoLens Inference Programme

Phased R&D plan for determining the fastest inference strategies that remain
scientifically correct and reliably find the right solution as PyAutoLens models
grow from ~15 to 100+ dimensions. Approved by the human 2026-08-17 (notes in
`DECISIONS.md`). This file is the canonical, maintained copy; per-phase results
land in `phase_<NN>_<slug>/RESULTS.md` beside it, gate outcomes in
`DECISIONS.md`, references in `LITERATURE.md`.

Evidence base: six reconnaissance sweeps (2026-08-17) over this repo,
PyAutoFit@d6fef747, PyAutoArray@394514c0, PyAutoLens, PyAutoMind/Brain/Memory,
and the external blackjax/literature ecosystem. Claims below were verified
against source/artifacts at that date unless marked HYPOTHESIS.

---

## 1. State of play (reconstructed 2026-08-17)

### Phase-0 checklist answers

| Question | Answer |
|---|---|
| MGE MultiStartProdigy ever profiled with PositionsLH? | NO — no positions plumbing in `scripts/misc/searches/_setup.py` |
| Mesh MultiStartProdigy with PositionsLH? | NO — pixelized analyses disable the positions guard (`_setup.py:1138-1152`) |
| Clipping / step-size variants with PositionsLH? | NO |
| NUTS initialized from previous NS/MAP results? | NO in-library (af.BlackJAXNUTS is single-chain, diagonal-mass, no injection); workspace-side `_warm_start.py` cache exists |
| SMC in PyAutoFit? | NO; working prototype parked on wsdev `feature/blackjax-smc-gradient-kernel` (wsdev#113) |
| BlackJAX NSS integration? | Removed 2026-07-11 (PyAutoFit#1357), stash at `autofit_workspace_developer/searches/nss/`; nested sampling has since MERGED INTO MAINLINE blackjax (PR #947 → release 1.6, current 1.6.2) — fork pins obsolete |

### Canonical numbers (imaging/mge/hst = 15 free params; A100 fp64 unless noted)

| Cell | Method | max logL | logZ | Wall | Evals |
|---|---|---|---|---|---|
| mge/hst | Nautilus n_live 200 | **31786.782** (truth bar) | 31690.5 | 831 s | 63,800 |
| mge/hst | NSS fork (200 live, 5 inner, del 50) | 31786.3–.5 | 31697.7/31700.4 | 657–679 s | ~390k |
| mge/hst | Prodigy 16×3000 fp64 laptop GPU, seed 0 | 31787.929 | — | — | 48k lane-steps |
| mge/hst | same, seed 1 | **−139,485.8** (θ_E=0 basin, 171k nats away) | — | — | 48k |
| mge/hst | Adam 128×, fp32 A100 warm | 31787.9 | — | 50 s | p_hit ≈ 0.18/start |
| delaunay/hst | Nautilus / NSS fork | 30623.5 / 30622.2 | 30562.2 / 30567.8 | 2,723 / **29,770 s** | 31.5k / 206k |
| pixelization/hst | Nautilus / NSS fork | 29143.3 / 29142.5 | 29066.3 / 29078.9 | 2,768 / **19,190 s** | 58k / 266k |

### Settled findings (do not re-derive)

- Basin selection, not speed, discriminates gradient MAP methods; only
  population methods recover truth from broad priors; line-search/quasi-Newton
  methods categorically fail on the NNLS-kinked objective; Adam→L-BFGS polish is
  harmful (wsdev #95/#97/phase-3 findings).
- Lane deaths are prior-support events; clipper eliminates them at zero accuracy
  cost but does not change the winning basin; per-parameter step scaling
  FALSIFIED; real failure = degenerate θ_E=0 basin ON the U(0,8) wall
  (this repo #128/#131, PR #133).
- Pixelized gradients work in production shape (adaptive meshes at os_pix=4,
  kernel-CDF bandwidth transform, Delaunay stop-gradient tables, autodiff Sibson
  DelaunayNN merged 2026-08-09). Reg log-det NaN localized (absolute 1e-8 lift
  below eigenvalue noise floor); slogdet opt-in shipped both terms
  (PyAutoArray#391); ConstantZeroth confirmed dead code.
- Compile time is a settings problem (persistent cache + autotune-off: ~70 min →
  ~35 s); never restructure for compile time; Delaunay-family cache misses
  remain.
- Warm-started gradient SMC samples correctly (full-Cholesky whitening,
  posterior-width steps, normalized-Gaussian geometric evidence bridge);
  cold-started posterior samplers are meaningless on this likelihood (~190k nats
  off). RAL job 331058 unharvested at plan time.
- MultiStartGradient auto-convergence exists (best-FOM plateau, window 50,
  rtol 1e-4, atol 1e-3, min 100; `n_steps` = ceiling; `stop_reason` persisted)
  but is DISABLED under `resurrect=True` and cannot distinguish wrong-basin
  plateau from convergence.
- Cluster-scale point-source objectives are not gradient-friendly; Nautilus is
  the cluster answer today (PyAutoLens#678 campaign).
- Hazard ledger: NNLS active-set kinks confirmed at TOY scale only (~10 source
  pixels, 5 transitions over θ_E ∈ [0.1,1.6], relative steps 0.006–0.014); TWO
  curvature-floor records incl. a real-path one (floor ≤ 4.5e-5 of touched
  diagonal scale).

### Canonical reference map (stale numbers resolved)

- "#104" reg-NaN localization = **autolens_workspace_developer#104** (not this
  repo's #104); "#117 campaign" = wsdev#117; clipper arc = this repo issues
  #128/#129/#131 + PRs #130/#132/#133; NaN counters PyAutoFit#1473; fitness
  guard PyAutoFit#1391-92; slogdet PyAutoArray#391-92; step scaling
  PyAutoFit#1483/1485; SMC prototype wsdev#113; open sampler-benchmark issues
  here: #69 (its "pixelized out of scope" note is stale), #82, #103.

## 2. Where the evidence corrected the original brief

1. **PositionsLH accumulation defect** — `AnalysisLens.log_likelihood_penalty_from`
   returned 2× the LAST penalty and discarded earlier entries. Verified, fixed:
   PyAutoLens#699 / PR#700 (CP-1).
2. **NSS is not currently the scalable candidate on pixelized cells** (7–11×
   slower at matched answers) — but it ran 5 inner steps in 15–20D where
   upstream now recommends ≥ 2·d, which also predicts the observed +7–13 nat
   logZ bias; and nested sampling is now MAINLINE blackjax (native-space
   logprior API, num_delete GPU axis, dlogz termination, ensemble logZ errors).
   Phase 2 = re-tuning against a moved ecosystem, with the bias hypothesis
   pre-registered. Human note at approval: on MGE, NSS was fastest/comparable
   and may scale better — worth rerunning.
3. **Phase 3 reframed as per-start hit probability**: p_hit(Adam) ≈ 0.18 ⇒
   P(16 lanes all miss) ≈ 4% — the seed-1 catastrophe is plausibly binomial
   luck. GIGA-Lens runs 300 starts at 1–5% hit rates. Measure p_hit(Prodigy)
   directly; reliability = 1−(1−p)^n. Blocker: per-lane BEST positions are not
   preserved (only final) — small PyAutoFit change first.
4. **PositionsLH should fence the θ_E=0 basin** (penalty = 1e8·(max_sep −
   threshold) outside, 0 inside, `lax.cond`, no PointSolver, differentiable) but
   has structural hazards: C⁰ hinge at threshold, argmax-switching kinks, zero
   gradient inside threshold (fences, never guides), 1e8 cliff vs ~3e4 logL.
   Characterize before campaigning. Workspace frames positions as an early-stage
   aid; SLaM keeps the penalty active through final MASS (auto-threshold,
   factor 3, min 0.2) — double-counting question open and empirically decidable.
5. **Half of Phases 7–8 groundwork exists**: the SMC informed-start bridge is
   derived + prototyped (resume, don't redesign); slogdet shipped; ConstantZeroth
   bugs filed. Reg coefficient priors are LogUniform(1e-6,1e6) ⇒ nested samplers
   already sample log-space via the unit cube; the λ⁴ pathology is specific to
   physical-space gradient stepping ⇒ 8B is a clean category-1 bijector change.
6. **Hardware constraints**: plain-Delaunay `batch_size` changes WHICH optimum is
   found (batch 4 lands 5,622 nats low; DelaunayNN insensitive) ⇒ mesh
   conclusions need A100 or fixed-batch discipline. Vmapped NUTS pays lockstep
   tree-depth costs ⇒ Phase 6 carries ChEES/MAMS arms.

## 3. Programme-wide experimental rules

- **Target ≠ algorithm.** Every run records a `target_id` (hash over model,
  priors, likelihood settings, positions config, dataset, mask, precision).
  Cross-target claims must name the target difference as the experiment.
- **Reliability = P(correct | fixed budget) over ≥5 seeds** at decision points.
  Success = Δ(max logL) within tolerance of the truth bar AND parameter recovery
  within per-target tolerances.
- **Per-step histories, not lifetime totals**, for every counter.
- **Per-lane/chain/particle final AND best states preserved.** No winner-only
  records.
- **Cold/warm compile split** recorded; compile timings from idle nodes only.
- **Hardware tiers never mix in one comparison row.** Laptop decides what earns
  A100 time; RAL CPU carries MGE volume; A100 carries mesh + confirmations.
  Every RAL sbatch exports `JAX_ENABLE_X64=True`.
- **Smoothing taxonomy on every change**: category 1 (target-preserving, proven)
  / 2 (equivalent within measured tolerance) / 3 (target-changing — never
  presented as a numerical fix; Gate F).
- **Tuning hierarchy**: cheap scan → operating region → seeded reliability →
  A100 confirmation. Every knob experiment answers a named question.
- **Termination is a metric**: `stop_reason`, steps-after-best (waste), plateau
  detectors tested against wrong-basin plateaus.
- **Delegation**: judgment in the main session; mechanical phases to cheaper
  agents; adversarial falsify-the-interpretation pass before every gate decision
  that commits A100 time or a source change.

## 4. Phases

Expense: S < 1 laptop/CPU-day · M = several laptop+RAL-CPU days · L = A100
session(s) · XL = multi-week A100.

### Phase 0 — Reconnaissance remainder & unblocking [S]
(a) PositionsLH fix — **DONE** (PyAutoLens#699/PR#700, pending merge);
(b) blackjax ≥1.6.2 upgrade local + RAL, `blackjax.nss` smoke, af.BlackJAXNUTS
API check; (c) harvest stranded RAL artifacts (331058 SMC arms, 335003-5 NaN
split, Nautilus pixgrad log) into this repo; (d) this ledger — **DONE** (#134);
(e) fix searches README dashboard "No data yet". Gate: (a)+(b) block everything.

### Phase 1 — Benchmark matrix & targets registry [M]
Targets v1 (HST fixtures, existing `_setup.py` builders): `mge` (15D),
`delaunay` (ConstantSplit), `knn` (free AdaptSplit — λ⁴ stressor),
`delaunay_matern`, `delaunay_nn` (Sibson autodiff), new `slam_source_pix`
(RectangularAdaptImage + reg.Adapt + AdaptImages + border relocator +
positions); × {positions off/on} × precision. Extend truth anchors to imaging
cells; long-Nautilus reference posterior + logZ per target as named baselines
(`results/baselines/InferenceRefs_v1/`). Pass/fail: Δ(max logL) ≤ 2 nats;
recovery within per-target tolerances; ≥5-seed success fraction; posterior
agreement (mean shift ≤ 0.2σ_ref, σ ratio ∈ [0.8,1.25]); |ΔlogZ| within errors;
performance per tier. Cheap first: MGE end-to-end before mesh targets.

### Phase 2 — Global MGE: Nautilus vs mainline BlackJAX NSS [M + 1 A100]
H2.1: inner steps ≥ 2d removes the +7–13 nat logZ bias. H2.2: tuned num_delete
(k/m ≈ 0.1–0.5) beats Nautilus wall on A100 at matched posterior+logZ.
Standing contrary evidence: fork NSS 7–11× slower on pixelized — judge Gate A
per model family. Arms: Nautilus (n_live 200 + one scan row); NSS scan n_live
{200,500,1000} × num_delete {0.1m,0.25m,0.5m} × inner {5, 2d, 3d} × dlogz
{−3,−10}; then ≥5-seed reliability at the operating point; wire via
`vector_from_unit_vector`/log-prior in a profiling-local runner first;
`af.NSS` re-mainlining only after Gate A. One pixelized probe decides whether
NSS is a serious mesh arm.
**GATE A**: matches posterior+evidence within tolerance AND wins GPU wall →
principal GPU nested-sampling baseline (Nautilus stays CPU reference); if the
pixelized deficit survives tuning, NSS scoped to parametric models.

### Phase 3 — Final MultiStartProdigy on MGE, broad priors, no positions [M]
Pre-req: PyAutoFit per-lane-best preservation. Best-supported config only
(clip=prior_box, no momentum reset, no scaler, auto-convergence on): n_starts
{16,64,256} × ≥5 seeds, budget-matched vs NS eval counts. One labelled
diagnostic arm: θ_E prior U(0.2,8) (target-changing mechanism probe only).
Metrics: per-lane basin classification, p̂_hit + CI, reliability curve,
convergence-detector confusion matrix (stopped-correct / stopped-wrong-basin /
ceiling), lane counters + alive curves.
**GATE B pt 1**: no n ≤ 256 gives ≥99% reliability below NS budget → Prodigy is
a LOCAL/INITIALIZED optimizer for parametric models; stop global investment.

### Phase 4 — PositionsLH on MGE, identical treatment for all engines [M]
Stage 1 (S): eager value_and_grad transects through threshold + θ_E=0 basin;
hazard record for hinge/plateau/cliff; penalty-factor (1e5/1e8) + threshold
sensitivity; simulator truth positions (note idealization). Stage 2: matched
trio Nautilus / NSS(op point) / Prodigy(best config) × ≥5 seeds × {on,off}.
H4.1: θ_E=0 basin acquires a monotone penalty slope → p_hit rises. H4.2: new
failure modes from the hinge/cliff — measured. H4.3: at the converged posterior
the penalty is exactly 0 for essentially all samples (loose-threshold design) →
no double-counting in practice; measure the active-penalty posterior fraction
and on/off posterior agreement.
**GATE B pt 2**: reliable + substantially cheaper than NS → adopt as
constraint-guided MAP engine (search stages); still basin-sensitive → Prodigy is
initialized-only. Positions recommendation follows H4.3 either way.

### Phase 5 — Mesh global searches with PositionsLH [L; A100 required]
Targets: delaunay, delaunay_nn, knn, slam_source_pix — all positions-on.
Engines: Nautilus / NSS (per Gate A) / Prodigy (resurrect ⇒ ceiling budget;
batch 2 on plain Delaunay; full NaN/clip/alive accounting; per-lane best).
≥3 seeds (5 where affordable). H5.1: positions raise mesh p_hit (project record:
positions "essentially required" for pixelized fits — demagnified-source
maxima). H5.2: plain Delaunay stays unreliable regardless (flips, sqrt(dual_area)
grad-NaN, batch steering); DelaunayNN + kernel-CDF are the gradient-viable
meshes — this is a mesh-family ranking as much as a sampler test. NaN
attribution split by axis (mesh sqrt vs reg λ⁴). Laptop = mechanics only
(VRAM + batch confound). Extends Gate B per mesh family; feeds Gate E.

### Phase 6 — Initialized posterior sampling [M → L]
Pre-req (PyAutoFit): multi-chain BlackJAXNUTS, inverse-mass-matrix injection
(diag/dense/low-rank), start points from a previous Result WITHOUT touching
priors (InitializerParamStartPoints + covariance carrier; promote wsdev
`_warm_start` pattern). Arms: init from Nautilus posterior (mean/cov) and
Prodigy MAP + Laplace; samplers NUTS (1 chain; 16 vmapped) and ChEES-HMC (16+
chains); MAMS only if a gap remains. Targets: MGE → delaunay_nn +
slam_source_pix (reverse-mode NNLS fine for MCMC). H6.1: dense/low-rank metric
essential (269× anisotropy, |r|=0.95 measured). H6.2: lockstep hurts vmapped
NUTS; fixed-work kernels match/beat it. Metrics: warmup cost, divergences
(count + location), acceptance, ESS_bulk/ESS_tail, split-R̂ < 1.01, ESS/grad,
ESS/s, posterior agreement, VRAM, compile split, tree-depth histograms.
**GATE C**: excellent ESS/s, no material divergences → default initialized
posterior engine (variant per hardware). Divergences clustering at NNLS/reg
sites → Gate E evidence.

### Phase 7 — SMC and other high-D candidates [M; A100 after gate]
Resume the parked wave (harvest 331058; port onto
`blackjax.adaptive_tempered_smc`, MALA/HMC rejuvenation, inner-kernel tuning).
The informed-start bridge exists (normalized-Gaussian geometric path, exact
evidence bookkeeping — matches the density-tempering literature); formalize as
a PyAutoFit abstraction only after it earns its keep. Test on a genuine
mode-birth transition (Phase 12 SOURCE→MASS or a multipole-degenerate target);
explicit mode-dropped-start test (a bridge cannot resurrect a missed mode).
Pathfinder/MAMS only against a named failure; JAXNS stays a literature
comparator.
**GATE D**: promote SMC only if it solves what NUTS-class engines fail
(multimodality / risky transitions / high-D exploration).

### Phase 8 — Regularization smoothness [S → L]
- **8A slogdet [S]**: re-run free-AdaptSplit stressors (knn truth-bar region;
  replay recorded rejected draws) under `log_det_method="slogdet"`.
  Pre-registered: NaNs gone, value equality on PD points (deltas only where
  Cholesky failed — category 2 quantified), gradient finiteness, runtime,
  Prodigy/NUTS delta. Expected pass → gradient-work likelihood profile;
  PyAutoArray default untouched.
- **8B log-coordinate [M]**: category 1 — gradient searches step in log λ (the
  prior's own CDF coordinate); samplers carry the standard Jacobian.
  Implementation lever: generalize the Scaler slot to a per-parameter bijector
  (deliberate, pre-registered revisit of unit-cube stepping — the arc that
  rejected it had its diagnosis falsified). Measure NaN-wall position,
  free-AdaptSplit convergence (historical 2,200 steps vs 98 fixed). Removing
  AdaptSplit's squaring = out of scope except as a labelled TARGET-CHANGING
  mechanism probe.
- **8C ConstantZeroth [S/M]**: fix the two filed bugs as an ALTERNATIVE scheme
  (target-changing vs AdaptSplit); verify λ_z²·I null-mode lift against the
  measured spectrum. A well-conditioned user alternative, never a silent
  replacement.
- **8+ analytic log-det probe [S]**: fixed-topology rectangular meshes admit
  exact Σ log(λ²μᵢ + ε) — category 1, kills the Cholesky there. One-day
  feasibility probe.
- **8D A100 comparative [L]**: justified variants only, on knn +
  slam_source_pix.
Gates E & F apply throughout.

### Phase 9 — NNLS positivity [M → L, conditional]
Stage 1 — confirm at production scale (only evidence is a ~10-pixel toy):
instrument support-set size/changes along transects on 1500-pixel meshes (numpy
fnnls exposes the active set; JAX PDIP via reconstruction sign pattern),
correlate with eager-AD gradient jumps and Phase 5/6 diagnostics (Prodigy
deflections, NUTS divergence locations). Stage 2 (past Gate E only): finite-μ
barrier forward (the JAX forward is already a PDIP interior-point solver —
stopping at μ>0 is in-family Moreau-Yosida smoothing; proximal-HMC literature
anchors it), smooth positivity reparameterizations. Each classified 1/2/3;
compare source morphology, likelihood, lens posterior before any
recommendation. No lensing-specific literature precedent exists (verified gap).

### Phase 10 — Curvature-diagonal floor [S]
Smaller than briefed (real-path hazard record already bounds the floor at
≤4.5e-5 of touched diagonal scale). One representative HST pixelized fit:
1e-3 absolute vs scale-aware counterfactual → likelihood, reconstruction,
short-Nautilus posterior, gradient smoothness, runtime. Expected: "no default
change justified" — recorded either way. Independent; schedulable any time
after Phase 1.

### Phase 11 — Freeze the "good likelihood" baseline [S]
Canonical recommended configuration for scaling work: what changed / what did
not / category 1 vs 2 proofs / residual kinks + evidence they matter or don't.
Re-baseline references if anything moved; targets registry v2 tagged. Phases
12–13 run only against frozen targets.

### Phase 12 — SLaM pipeline experiment [L]
Real SLaM structure (SOURCE LP → SOURCE PIX 1/2 → LIGHT → MASS TOTAL; baseline
n_live 200/150/75/150/150) on the benchmark dataset. Stage assignments follow
gates (SOURCE PIX / LIGHT → initialized Prodigy where Gate B passed; MASS →
Gate-C engine; positions per Phase 4). Per transition: params carried/new,
initializer construction (start points + metric, priors untouched), mode-birth
risk (SMC bridge per Gate D), whether a global stage is still required. Compare
end-to-end wall + per-stage reliability vs all-Nautilus. Note: current prior
passing (`model_centred_*`) REPLACES priors — initialized engines must use the
start-point/metric route; where SLaM's own prior passing is production
behaviour, record the distinction explicitly.

### Phase 13 — Mass-model dimensional scaling [L → XL]
Ladder: PowerLaw+shear → +m=1 → +m=3 → +m=4 multipoles (+2 free each via prior
pairing; m=1 undocumented in the workspace — validate first, incl. the
dipole-vs-centroid degeneracy), on MGE and mesh source configs; record N per
rung. Engines = gate survivors. ≥5 seeds per decision rung. Backend-parity
hazard row first: JAX PowerLaw is a 20-term series vs numpy hyp2f1. Measure
scaling vs N (likelihood + gradient cost, wall, memory, ESS, reliability,
multimodality); report the measured curve — no scaling-law fits from ≤3 points.
Output: the crossover measurement + the evidence base for Follow-up 1.

### Future follow-ups (deliberately undesigned)
1. N>30 / N~100+ (multi-band offsets, group-scale through SLaM) — design from
   Phase 13 evidence.
2. `autogalaxy_profiling` — analogous infrastructure; no SLaM transplant;
   staged morphology problems instead.
3. Graphical / hierarchical / EP scaling — from
   `autolens_workspace/scripts/guides/modeling/advanced/{graphical,hierarchical}.py`.

## 5. Benchmark & result schema (v2)

Extends the existing `results/searches/` JSON. Additions: `target` block
(target_id hash, cell, model_dim, priors provenance, likelihood settings,
positions config, target_class vs parent), `algorithm` block (name, config_id,
full settings, seed, initialization source), `diagnostics` block (stop_reason,
steps_after_best, NaN/clip/resurrection counters, per-step histories ref,
per-lane final+best+basin, MCMC ESS/R̂/divergences/tree-depth hist, NS
logZ + ensemble error), `verdict` block (success, Δ vs truth, posterior
agreement), `hardware` block (tier, VRAM, compile_s, cache_state, SHAs).
Registries: `scripts/misc/searches/_targets.py` (specs → target_id +
tolerances) and per-method configuration records (method cards). Reference
posteriors: `results/baselines/InferenceRefs_v1/` tagged by target_id.

## 6. Knowledge structure

```
results/notes/inference/
  PROGRAMME.md            # this file
  DECISIONS.md            # append-only gate log
  LITERATURE.md           # references + lessons
  methods/<method>.md     # living method cards
  phase_<NN>_<slug>/RESULTS.md
```

Method-card template: IDENTITY (global/local · gradient-required · JAX/GPU ·
multimodality) / EVIDENCE (regimes, datasets, initializations tested) /
STRENGTHS & WEAKNESSES (each line cites a result) / CONFIGURATION (tested ·
recommended-by-regime · auto-adapted · do-not-touch knobs · sensitivity) /
TERMINATION (rule · statistical meaning · multimodal reliability · required
diagnostics · waste) / HAZARDS / PERFORMANCE (per-tier only) / RECOMMENDED
(SLaM phases · confidence: anecdote/seeded/gated) / REFERENCES. The eventual
`autolens_workspace/scripts/guides/searches/` decision tree is generated from
cards + DECISIONS.md — nothing user-facing is written during the programme.

## 7. Likely source-library changes (separated from profiling)

| Repo | Change | Trigger |
|---|---|---|
| PyAutoLens | PositionsLH accumulation fix | DONE — #699/PR#700 |
| PyAutoFit | blackjax ≥1.6.2 floor; af.NSS re-mainlined on `blackjax.nss` | Gate A |
| PyAutoFit | Per-lane BEST preservation in MultiStartGradient | Phase 3 pre-req |
| PyAutoFit | Multi-chain NUTS + metric/start-point injection; warm-start abstraction; ChEES/MAMS if selected | Gate C |
| PyAutoFit | Per-parameter bijector slot (log-coordinate stepping) | 8B |
| PyAutoFit | SMC search + informed-start bridge | Gate D only |
| PyAutoFit | Seed-reproducibility completion (existing draft) | Phase 1 |
| PyAutoArray | ConstantZeroth repair (opt-in alternative) | 8C |
| PyAutoArray | Analytic fixed-topology log-det | 8+ probe |
| PyAutoArray | sqrt(dual_area) gradient guard | Phase 5 attribution |
| PyAutoArray | Finite-μ smoothed-positivity forward (opt-in) | Gates E+F only |
| PyAutoArray | Curvature-floor scale-aware default | Phase 10 surprise only |

## 8. Risk register (abridged — full table in the approved plan artifact)

Target drift (→ target_id + freeze) · positions double-counting (→ H4.3
measurement) · penalty gradient pathologies (→ Stage-1 characterization) ·
seed luck (→ ≥5 seeds, p_hit CIs) · mode loss in informed methods (→ NS
cross-checks + mode-dropped-start test) · NSS logZ bias (→ inner-steps scan) ·
NaN axis conflation (→ disjoint counters, alive curves) · plateau false
convergence (→ confusion matrix) · toy-scale over-generalization (→ Gate E) ·
λ⁴/1e-8 conditioning (→ 8A/8B) · SMC impoverishment (→ acceptance traces, never
"Converged: yes") · NUTS lockstep (→ tree-depth hists, ChEES arms) · VRAM
(→ single-eval memory profile; Delaunay batch=2) · compile artifacts (→
cache/autotune defaults, cold/warm split, idle nodes) · cross-tier rows
(structurally disallowed) · env artifacts (RAL fp32 export; control scripts) ·
knowledge stranded on RAL/branches (→ Phase 0(c), findings mirrored here).

## 9. Minimal critical path

1. **CP-1** PositionsLH fix — DONE (PR#700).
2. **CP-2** blackjax 1.6.2 upgrade + mainline NSS smoke on MGE (laptop GPU).
3. **CP-3** Prodigy MGE reliability scan ± PositionsLH: n_starts {16,64,256} ×
   5 seeds × positions {off,on} (RAL CPU + laptop) — the single
   highest-information experiment; decides Gate B's shape before A100 time.
4. **CP-4** slogdet A/B on the AdaptSplit NaN wall (hours).
5. **CP-5** NSS inner-steps/logZ scan + one pixelized probe (decides Gate A).

First A100 block only after CP-1..5: Phase 5 mesh campaign + Phase 6 warm-start
confirmation with pruned arms.

## 10. Expected decision tree — HYPOTHETICAL until measured

[E] = existing evidence, [H] = hypothesis.

- ~10–20D parametric, broad priors: CPU → Nautilus [E]; GPU → tuned NSS or
  Nautilus [H: Gate A]; positions known → +PositionsLH during search [H: Gate B];
  Prodigy(n≥64)+positions as fast MAP only if Gate B passes.
- Pixelized source: positions REQUIRED [E]; global → nested sampling [E];
  gradient work → DelaunayNN / kernel-CDF meshes only (plain Delaunay is a
  gradient hazard) [E]; slogdet-on profile for differentiation [H: 8A].
- Good previous fit, basin trusted: posterior → warm NUTS (dense/low-rank
  metric) [H: Gate C], many-chain GPU → ChEES/MAMS [H]; point estimate →
  initialized Prodigy (auto-converge, ceiling) [E-partial].
- Basin not trusted / new params may add modes: bridged SMC [H: Gate D], falling
  back to fresh nested sampling [E].
- Growing N: nested sampling competitive to N ≈ 20–30 [E]; crossover measured in
  Phase 13, not assumed; N ≳ 50 with good initializer → warm gradient sampler
  family [H].

Diagnostics gate every arrow: NaN/clip counters clean, stop_reason converged +
post-hoc check, R̂ < 1.01 + ESS floors + no divergence clusters, logZ
cross-checked when evidence matters.
