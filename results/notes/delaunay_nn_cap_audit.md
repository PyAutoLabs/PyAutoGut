# DelaunayNN fixed-shape cap audit

## Decision

Keep both `DelaunayNN` static limits at **32**. Caps 16 and 24 are too low for
the tested lensing geometries; 64 roughly doubles the cap-32 geometry cost
without being required by the audit.

## Correctness audit

The workspace assertion
`scripts/misc/jax_assertions/delaunay_nn_caps.py` constructs a 1,200-vertex
Hilbert image mesh from an arc-like adapt image and ray-traces both that mesh
and 4,421 image pixels through 101 Isothermal + external-shear mass models.
The ensemble contains a 25-step local mass-model trajectory, 75 broad prior
draws, and a fixed stress geometry. It audits ordinary mapper queries and all
4,800 split-cross points used by split regularization.

The untruncated cap-64 reference observed:

| Quantity | Maximum | Rows above 16 |
|---|---:|---:|
| Main natural neighbours | 27 | 198 |
| Main cavity triangles | 25 | 107 |
| Split natural neighbours | 21 | 28 |
| Split cavity triangles | 19 | 12 |

The main-neighbour 99th, 99.9th and 99.99th percentiles were 9, 14 and 22;
the corresponding split-neighbour percentiles were 9, 11 and 15. Thus 16 is
usually sufficient but fails in the tail—the precise failure mode that would
otherwise create rare NaN likelihood samples as the mass model changes.

The worst geometry was rerun explicitly at caps 16, 24 and 32. Both 16 and 24
reported fixed-shape overflow; 32 completed without main or split overflow.

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

These are local CPU measurements, not A100 results. The cap-32 choice is the
smallest tested static shape that covers the broad mass-model audit. The A100
profile should be rerun before drawing sampler-throughput conclusions.
