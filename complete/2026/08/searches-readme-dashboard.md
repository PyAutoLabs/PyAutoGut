Fixed the permanently-empty searches README dashboard in autolens_profiling —
Phase 0(e) of the inference programme
(`results/notes/inference/PROGRAMME.md`). Documentation-tooling only; no
runs, no source-library changes. Done entirely from a mobile/cloud session
(no local worktree).

- **PR:** autolens_profiling#139 (merged `e43e1f1`, closes #138).
- **Root cause:** two decoupled stalenesses in
  `scripts/misc/tooling/build_readme.py`. The scanner only matched flat
  versioned filenames (`<script>_summary_v<version>.json`) or
  script-prefixed config tags, while the searches framework writes
  `results/searches/<sampler>/<class>/<model>/<instrument>/<config>.json`
  with bare-tier names — nothing matched, so the `searches-nautilus` region
  always rendered the no-data block. The renderer additionally read a payload
  schema that never shipped (`performance.wall_time_s`,
  `convergence.evals_to_ml`, top-level `backend`) instead of the real one
  (`performance.total_wall_s`/`likelihood_evals`/`time_per_eval_ms`,
  `results.max_log_likelihood`/`log_evidence`).
- **Fix:** payload-driven `SearchArtifact` scanner (identity from the
  self-describing JSON, no path parsing; skips the list-shaped
  `multi_start_nan_accounting` overhead study), one all-samplers table
  (latest version per sampler × cell × config), region renamed
  `searches-nautilus` → `searches`. 34 rows render.
- **Verification:** nautilus `imaging/mge/hst` row matches the
  inference-programme truth bar exactly (max logL 31,786.8, logZ 31,690.5,
  831 s, 63,800 evals); NSS row matches (679 s, 394,321 evals, logZ
  31,697.7). `build_readme.py --check` (CI gate) and ruff both green.
- **Trap for the record:** the `--check` CI gate means any renderer change
  must regenerate all target READMEs in the same PR, or main goes red.
- **Follow-up:** PROGRAMME.md's phase-state table still lists 0(e) as
  outstanding — updated in the next inference-notes PR rather than a
  one-line PR of its own.

## Original prompt

# searches README dashboard renders "No data yet" despite existing artifacts

Type: bug
Target: autolens_profiling
Repos:
- @autolens_profiling
Difficulty: small
Autonomy: supervised
Priority: medium

Phase 0(e) of the inference programme
(`autolens_profiling/results/notes/inference/PROGRAMME.md`): the
`searches-nautilus` auto-table in `scripts/misc/searches/README.md` renders
"_No data yet — run `searches/nautilus/{simple,jax}.py` to populate._" even
though `results/searches/nautilus/**` holds many committed artifacts
(imaging mge/delaunay/pixelization, point_source, cluster, group cells).

Root cause (verified 2026-08-18 by reading
`scripts/misc/tooling/build_readme.py`): the artifact scanner only matches
flat versioned filenames (`<script>_summary_v<version>.json`, ARTIFACT_RE) or
config-tagged filenames with a script prefix (`<script>_<config>.json`,
CONFIG_TAGGED_RE) directly under `results/searches/<sampler>/`. The searches
framework instead writes a nested cell layout:

```
results/searches/<sampler>/<dataset_class>/<model>/<instrument>/<tier>.json
e.g. results/searches/nautilus/imaging/mge/hst/hpc_a100_fp64.json
     results/searches/nautilus/point_source/image_plane/simple/default.json
     results/searches/multi_start_adam/group/mge/hst/local_local_gpu_fp64.json
```

Neither regex matches bare `<tier>.json` names, so `_render_nautilus_table`
receives zero artifacts and emits the no-data block.

Task: teach `build_readme.py` to scan the nested searches layout (cell path →
sampler/dataset_class/model/instrument, filename → hardware tier; note the
`hpc_hpc_a100_fp64.json` / `local_local_gpu_fp64.json` double-prefix and
`default.json` variants in the existing data), render the searches table from
the real artifacts (all samplers present, not just nautilus), and regenerate
the affected READMEs. Keep the sentinel-block mechanism and hand-written
prose untouched; keep `ruff check` / `ruff format --check` green. Verify by
running the generator and eyeballing the produced table against known rows
(e.g. nautilus imaging/mge/hst A100 fp64).
