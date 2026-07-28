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
