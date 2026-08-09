# DelaunayNN profiling

This profile isolates the full geometry cost of the Sibson natural-neighbour
mapper added as `mesh.DelaunayNN`. It times:

- qhull connectivity and JAX point location;
- data-grid natural-neighbour weights;
- barycentric dual areas and split-cross coordinates;
- natural-neighbour weights for all split-regularization points.

The comparison is therefore the complete mapper-table construction against
the equivalent barycentric `Delaunay` path, rather than an isolated
circumcircle kernel.

Run the production-shaped CPU/GPU benchmark from the repository root:

```bash
python scripts/misc/delaunay_nn/benchmark.py
```

Useful overrides:

```bash
python scripts/misc/delaunay_nn/benchmark.py \
  --mesh-points 1500 --queries 20000 --caps 16 24 32 64 --repeats 10
```

The script writes a versioned JSON and PNG pair under
`results/delaunay_nn/`. The cap sweep exposes the speed/headroom trade-off;
the separate workspace assertion
`scripts/misc/jax_assertions/delaunay_nn_caps.py` decides correctness using
actual Hilbert meshes ray-traced through a mass-model ensemble.

The current cap decision and measured tail distributions are recorded in
[`results/notes/delaunay_nn_cap_audit.md`](../../../results/notes/delaunay_nn_cap_audit.md).
