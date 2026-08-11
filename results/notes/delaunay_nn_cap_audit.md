# DelaunayNN fixed-shape cap audit

## Decision

Keep both `DelaunayNN` static limits at **32**. Cap 16 is demonstrably too low.
Cap 24 overflowed in the local audit but sat exactly on the platform-sensitive
boundary in GitHub CI, so it does not provide a robust safety margin. Cap 64
roughly doubles the cap-32 geometry cost without being required by the audit.

## Correctness audit

The workspace assertion
`scripts/misc/jax_assertions/delaunay_nn_caps.py` constructs a 1,200-vertex
Hilbert image mesh from an arc-like adapt image and ray-traces both that mesh
and 4,421 image pixels through 101 Isothermal + external-shear mass models.
The ensemble contains a 25-step local mass-model trajectory, 75 broad prior
draws, and a fixed stress geometry. It audits ordinary mapper queries and all
4,800 split-cross points used by split regularization.

The untruncated cap-64 reference observed:

| Quantity | Local maximum | Rows above 16 | Rows above 24 |
|---|---:|---:|---:|
| Main natural neighbours | 27 | 198 | 8 |
| Main cavity triangles | 25 | 107 | 2 |
| Split natural neighbours | 21 | 28 | 0 |
| Split cavity triangles | 19 | 12 | 0 |

The main-neighbour 99th, 99.9th and 99.99th percentiles were 9, 14 and 22;
the corresponding split-neighbour percentiles were 9, 11 and 15. Thus 16 is
usually sufficient but fails in the tail—the precise failure mode that would
otherwise create rare NaN likelihood samples as the mass model changes.

The worst geometry was rerun explicitly at caps 16, 24 and 32. Locally, caps
16 and 24 reported 94 and 4 overflow rows respectively; 32 completed without
main or split overflow. On the GitHub Actions runners the cap-24 rerun produced
zero overflow rows, while cap 16 still overflowed. This small qhull/platform
difference makes 24 a boundary result rather than a dependable production cap;
32 covered both environments.

## Runtime trade-off

The versioned local CPU benchmark uses 1,200 vertices, 15,000 data queries and
the full mapper path, including split regularization:

| Mapper | Warm median | Relative to Delaunay |
|---|---:|---:|
| Barycentric Delaunay | 0.0667 s | 1.00× |
| DelaunayNN cap 16 | 0.1923 s | 2.88× |
| DelaunayNN cap 24 | 0.2400 s | 3.59× |
| DelaunayNN cap 32 | 0.3177 s | 4.76× |
| DelaunayNN cap 64 | 0.5624 s | 8.43× |

The corresponding laptop-GPU run used the same 1,200 vertices, 15,000 queries
and query chunk of 256 on an NVIDIA GeForce RTX 2060 Max-Q. It recorded ten
warm calls to span the device's dynamic clock states:

| Mapper | CPU warm median | GPU warm median | GPU speed-up | Relative to GPU Delaunay |
|---|---:|---:|---:|---:|
| Barycentric Delaunay | 0.0667 s | 0.0440 s | 1.52× | 1.00× |
| DelaunayNN cap 16 | 0.1923 s | 0.1194 s | 1.61× | 2.71× |
| DelaunayNN cap 24 | 0.2400 s | 0.1966 s | 1.22× | 4.46× |
| DelaunayNN cap 32 | 0.3177 s | 0.2396 s | 1.33× | 5.44× |
| DelaunayNN cap 64 | 0.5624 s | 0.4422 s | 1.27× | 10.04× |

Thus the production cap-32 mapper is faster in absolute terms on the laptop GPU
(0.2396 s rather than 0.3177 s), but ordinary Delaunay benefits more: the
DelaunayNN overhead grows from 4.76× on CPU to 5.44× on GPU. Clean five-repeat
GPU sweeps put cap 32 at 0.243--0.255 s; their ratio moved from 4.93× to 5.92×
because the much shorter Delaunay baseline was more sensitive to device clock
state. The ten-repeat result is the canonical comparison.

Compilation is not accelerated: compile plus first call was 0.788 s for
Delaunay and 3.900 s for cap-32 DelaunayNN on the GPU, versus 0.351 s and
1.242 s on CPU. This is a one-off cost; the warm timings above are the relevant
per-likelihood geometry cost.

The cap-32 choice remains the smallest tested static shape with a robust margin
across the local and CI audits. These GPU measurements are for the RTX 2060,
not an A100; the A100 profile should still be run before drawing HPC
sampler-throughput conclusions.
