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

For the laptop GPU, activate the CUDA environment first:

```bash
PyAutoGPU
JAX_PLATFORMS=cuda,cpu python scripts/misc/delaunay_nn/benchmark.py --repeats 10
```

The CPU backend remains registered because the Delaunay connectivity callback
runs qhull on the host even when the mapped JAX work targets CUDA. Ten warm
repeats give a more representative median across the laptop GPU's dynamic clock
states than the five-repeat CPU default.

Useful overrides:

```bash
python scripts/misc/delaunay_nn/benchmark.py \
  --mesh-points 1500 --queries 20000 --caps 16 24 32 64 --repeats 10
```

The script writes a versioned JSON and PNG pair under
`results/delaunay_nn/`. GPU filenames include the JAX device identity so a
laptop result cannot overwrite a later A100 run; the JSON also records the
same hardware key. The cap sweep exposes the speed/headroom trade-off;
the separate workspace assertion
`scripts/misc/jax_assertions/delaunay_nn_caps.py` decides correctness using
actual Hilbert meshes ray-traced through a mass-model ensemble.

The current cap decision and measured tail distributions are recorded in
[`results/notes/delaunay_nn_cap_audit.md`](../../../results/notes/delaunay_nn_cap_audit.md).
