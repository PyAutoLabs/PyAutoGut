# Isolate border-relocator backend parity

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: medium
Autonomy: supervised
Priority: high
Status: issued
Source: autolens_profiling#113 · positive-solver diagnosis

The positive-solver experiment proved both solvers agree on an identical NNLS
system. At the worst one-ULP Einstein-radius point, disabling border relocation
also restores the native NumPy/JAX path: the curvature-system difference falls
from 8.690e-3 to 1.595e-16 and reconstruction difference from 8.989e-3 to
9.696e-11.

Use the existing full `FitImaging` pixelization fixture to identify the first
border-relocator stage that diverges. Compare relocation enabled and disabled
across the same one-ULP neighbourhood and record traced source coordinates,
relocated coordinates, mesh extent, mapping matrix, curvature system,
reconstruction, support, and figure of merit.

Test whether the difference is an expected exact-boundary discontinuity or a
backend parity defect, including a scale-aware geometric tolerance
counterfactual where feasible.

Do not modify PyAutoArray or production geometry tolerances in this task. Open a
source task only if the profiling evidence identifies a reproducible defect and
a bounded remedy. Preserve the existing stable finding ID and results schema.
