# Pixelized Prodigy laptop-GPU compatibility across four meshes

Type: research
Target: autolens_workspace_developer
Repos:
- @autolens_workspace_developer
Difficulty: medium
Autonomy: human-required
Priority: high
Status: draft
Parent: `pixelized_prodigy_laptop_gpu.md`

Extend the existing `searches_minimal/pix_prodigy.py` experiment to the new
`al.mesh.DelaunayNN` and run the production pixelized likelihood on the laptop
RTX 2060 Max-Q through `PyAutoGPU`. Preserve and summarize the existing CPU
evidence for rectangular, KNN, and Delaunay, then obtain comparable GPU
compatibility evidence for all four meshes.

For each mesh, establish or validate a truth-point likelihood reference and
run a matched broad-start `af.MultiStartProdigy` compatibility arm. Use
fixed/inherited regularization first so the test isolates the mesh gradient
from the known AdaptSplit regularization wall. Begin with memory-safe batching
on the 6 GB GPU and record compile time, per-step throughput, maximum
likelihood, recovered mass/shear, full FoM history, resurrections, non-finite
events, and any DelaunayNN overflow/degeneracy diagnostics.

The phase succeeds when each mesh has either reached the correct mass basin
against its own likelihood bar or has a documented, reproducible failure mode
and tested step budget. Persist hardware and exact source revisions with the
results. Do not modify the separate `autolens_profiling` issue #105 worktree.

## Original request

> Using thr GPU on this laptop via PyAutoGPU continue work investigating
> MultiStartProdigy for the pixelized mesh use cases including the new
> DelaunayNN which has improved gradients. First confirm prodigy works for
> these meshes or document when it doesn't.

> Make sure we have results for rectangular and knn too which partly have
> already run.
