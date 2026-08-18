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
