**Question asked:** does `af.MultiStartProdigy` still have long JAX jit compile
times on MGE and the pixelized meshes (rectangular kernel-CDF / knn / delaunay),
and can they all be made fast?

**Answer: compile time is a non-problem on every endorsed model type — nothing
needed making fast.** Census of {mge, pixelization, knn, delaunay_matern} ×
{jit, vag, vmap_vag(16), pyloop_vag(4), laxmap_vag(4)}, cold/warm, at production
knobs (16 starts, batch_size 4): worst ~3.5 min cold on a 1-core 15 GB laptop
(the deliberate worst-case tier — XLA compiles on host cores), and ≤75 s cold /
≤2 s warm on a RAL 32-core node.

**Phase B was cancelled on the evidence.** The plan was to hoist MultiStart's
`jax.lax.map(value_and_grad, batch_size=)` batching out of XLA into a Python
loop ("pyloop"), which an earlier multi-band experiment had shown was
compile-intractable / OOM-killed. That blow-up **does not reproduce
single-band** — the scan explodes only with a multi-band FactorGraphModel fusion
as its body; single-band `laxmap_vag` compiles in 28–120 s everywhere. No
PyAutoFit branch was ever created; the pyloop lever stays reserved for the
multi-band case. The #71→#77 "settings suffice" verdict now extends to the full
production multi-start transform.

**PRs:** autolens_profiling#94 (MERGED `1088f41`, results + docs). Issue #93 closed.

## Findings worth keeping

1. **The Delaunay family never hits the persistent compilation cache** — warm
   compile ≡ cold (16–33 s) in *every* process, reproduced to the decimal on two
   independent hosts (n=8 process pairs), while knn / rect / mge warm to 0.2–4 s.
   knn (pure JAX, no host callback) is the control, so the suspect is the qhull
   `pure_callback` embedding a process-specific descriptor in the serialized HLO.
   Follow-up filed: `draft/research/autoarray/delaunay_callback_persistent_cache_miss.md`.
2. **Rect kernel-CDF batched gradients are memory-bound, not compile-bound:
   ~9.2 GB per start in the jvp** (fp64, 15361 px). Width 4 = ~37 GB (OOM on a
   15 GB laptop; RAL job MaxRSS confirmed 39.4 GB; fits A100 80 GB), width 16 =
   ~147 GB (fits nowhere). **`batch_size=4` is load-bearing for memory, not a
   tuning nicety** — the quantitative basis for the campaign's config.
3. **Rect's real cost axis is throughput, not compile** — ~310 s per 16-start
   step on 32 CPU cores, matching the campaign's ~5.7 min/step.

## Traps

- **A `--partition=gpu --gres=gpu:1` job that gets no usable device does not
  fail — it silently runs on CPU.** Job 331380 hit `cuInit(0) →
  CUDA_ERROR_NO_DEVICE` (A100s saturated by an external multi-day array), JAX
  warned and fell back, and produced plausible-looking "A100" rows that were
  actually 8-core CPU rows. The tell: a "GPU" row *slower* than a many-core CPU
  row (knn laxmap 160 s vs the 32-core CPU's 107 s). Verify the backend from the
  results path (`local_gpu_*` vs `local_cpu`), never from the partition. Rows
  discarded, not committed; the A100 tier remains unmeasured (confirmatory only).
- **`results/local_gpu_*/mge.json` had been corrupt since 270e5cc** (stray
  trailing `]`). `probe.py` `json.loads()` the file before appending, so the next
  A100 mge probe run would have crashed. Repaired; verified 1 row, no data lost.
- `gh api .../labels -X POST -f "labels[]=x"` is rejected (422, "not an array");
  use `echo '{"labels":["x"]}' | gh api ... --input -`.
- The RAL `/mnt/ral/jnightin/autolens_profiling` checkout is an rsync mirror with
  a broken `.git` pointer (git commands there try to resolve a laptop worktree
  path). Rsync a fresh `_census` copy for new work; read files directly.
- Brain's feature agent scored this too-large (score 12) off repo **count** and
  proposed a generic 4-phase split; overridden to the natural measure→fix shape
  and recorded in the issue.

## Documentation

`results/notes/multistart_prodigy_compile_census.md` is the durable findings
note (repo's established notes pattern). The main `README.md` now carries
`jax_compile/` in its section index — it was previously unreachable from the
front door — and its stale "JAX gradients — currently out of scope" section was
replaced with current gradient + compile-time standing conclusions. Instrument
detail and full tables stay in `scripts/misc/jax_compile/README.md`.

## Open / follow-ups

- A100 tier unmeasured — `sbatch /mnt/ral/jnightin/pixgrad_logs/census_gpu.sbatch`
  when a GPU node is genuinely free. Confirmatory only.
- `draft/research/autoarray/delaunay_callback_persistent_cache_miss.md` — the one
  actionable defect this census found, not yet started.
- `draft/feature/autolens_profiling/jax_compile_time_profiling.md` — marked
  superseded; only the recurring cell-grid compile dashboard remains of it.

## Original prompt

# Profile MultiStartProdigy JAX compile times (MGE + pix meshes) and make them all compile fast

Type: research
Target: autolens_profiling
Repos:
- @autolens_profiling
- @PyAutoFit
Difficulty: medium
Autonomy: supervised
Priority: high
Status: formalised

## Original request (verbatim)

> We have concluded that MultiStartProdigy is good to use on both sources with
> an MGE and rectangular / knn / delaunay mesh (see recent notes in
> autolens_workspace and autolens_workspace_developer and autolens_profiling).
> However, I think MultiStartProdigy can still have long jax jit compile times,
> and if it doesnt we have shown this for meshes. Can you do profiling of this
> (building on any previous work) and aim to make them all compile fast. Use
> the search pyautobrain conductor, make sure results are stored in
> autolens_profiling.

## Prior work to build on (do not re-derive)

- The compile-time arc #71→#74→#77 (autolens_profiling
  `scripts/misc/jax_compile/README.md`) is CLOSED for single-start transforms:
  persistent cache (PyAutoNerves#128) + autotune-off (#132) give worst cold
  ~35 s / warm 5–9 s on the A100 census cells. Verdict stands: settings first,
  no likelihood restructuring.
- The multi-band follow-up (same README, final section) measured the
  **MultiStartProdigy production transform** — `jax.lax.map(value_and_grad,
  batch_size=)` (PyAutoFit `multi_start_gradient/search.py`) — and found the
  in-XLA scan is the compile killer: cold-compile intractable / OOM-killed on
  a 1-core CPU host, while `pyloop_vag` (Python loop over `vmap` chunks, same
  vmap width) compiles at single-fit cost (166 s). Named "the leading source
  lever"; validated on the homogeneous 4-band MGE graph only.
- `probe.py` already has the transform axis (`vag`, `vmap_vag`, `laxmap_vag`,
  `pyloop_vag`) and `scripts/misc/searches/_setup.py` has all four model
  types: `mge`, `pixelization` (rect kernel-CDF), `knn`, `delaunay` /
  `delaunay_matern` (added in autolens_profiling PR#91).
- Prodigy campaign context (wsdev#117 / profiling PR#91): production knobs are
  16 starts / batch_size 4; rect throughput anomaly (~17× knn per step vs
  4.5× forward-eval — jvp disproportion) is an open A100 follow-up item.
- The stale broad draft `draft/feature/autolens_profiling/jax_compile_time_profiling.md`
  predates the arc close (its autotune section was overturned); this prompt
  supersedes its measurement scope for the search transform. Fold or retire
  it when this ships.

## Scope

1. **Measure** (autolens_profiling, results committed under the repo's
   dashboard conventions): cold + warm compile of the MultiStartProdigy
   transform matrix — {mge, pixelization, knn, delaunay(_matern)} ×
   {vag, vmap_vag(n=16), laxmap_vag(bs=4), pyloop_vag(bs=4)} — local CPU
   first; A100 rows via the hpc/ submit path where the CPU numbers say they
   matter.
2. **Fix** (PyAutoFit, only if the measurements confirm the lever): make
   MultiStartProdigy/MultiStartAdam batching compile fast — leading candidate
   is hoisting the batch loop out of XLA (`pyloop` pattern: Python loop over
   `vmap(batch_size)` chunks), keeping `batch_size` semantics and results
   identical. Settings-first discipline applies: confirm cache + autotune-off
   are already doing their part per cell before touching source.
3. **Record**: results + verdict live in autolens_profiling (jax_compile
   results or searches results tier as fits the repo layout); library change
   ships through the normal PyAutoFit PR flow.

<!-- filed 2026-07-28 from a direct user request in the CLI session -->
