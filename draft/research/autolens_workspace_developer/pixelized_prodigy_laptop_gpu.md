# Optimize MultiStartProdigy for pixelized meshes on the laptop GPU

Type: research
Target: autolens_workspace_developer
Repos:
- @autolens_workspace_developer
Difficulty: large
Autonomy: human-required
Priority: high
Status: draft

Continue the shipped CPU investigation of `af.MultiStartProdigy` on pixelized
source meshes using the laptop NVIDIA RTX 2060 Max-Q through the `PyAutoGPU`
environment. Produce comparable results for rectangular, KNN, Delaunay, and
the new `DelaunayNN` mesh whose natural-neighbour interpolation provides
smoother gradients across Delaunay topology flips.

First establish whether Prodigy recovers the correct maximum-likelihood mass
model for each mesh, reusing prior CPU findings where they remain valid and
running controlled laptop-GPU confirmations. Establish mesh-specific truth
likelihood bars and record failures precisely (non-finite wall, overflow,
VRAM limit, stalled basin, or insufficient tested budget).

Then determine settings that reach the highest likelihood in the fewest
optimizer steps and shortest wall time. Compare useful values of `n_starts`
and `batch_size`, and the fixed/inherited, free Matérn, and free AdaptSplit
regularization cases where relevant. Preserve broad start bounds unless new
evidence overturns the prior result that narrowing hurts. Persist full
figure-of-merit histories, recovered mass parameters, resurrection counts,
step throughput, steps-to-bar, hardware/library identity, and a concise
four-mesh recommendation table.

Keep the existing `autolens_profiling` DelaunayNN runtime task and its dirty
worktree separate. Mature winning configurations into profiling only after
the experiment-tier evidence is settled.

## Original request

> Using thr GPU on this laptop via PyAutoGPU continue work investigating
> MultiStartProdigy for the pixelized mesh use cases including the new
> DelaunayNN which has improved gradients. First confirm prodigy works for
> these meshes or document when it doesn't, then work out what settings infer
> the max Lh modle I fewest steps e.g. perform best

Follow-up:

> All sounds good but make aure we have results for rectangular and knn too
> which partly have already run?
