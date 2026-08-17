Phase 1 (compatibility) and phase 2 (characterisation) of the pixelized
`MultiStartProdigy` laptop-GPU validation, across all four meshes. All 13 cells
landed. Bookkeeping only was outstanding: the work shipped 2026-08-13 but the
`active.md` entry was never retired, and it went on claiming
`PR #126 (OPEN, mergeable)` / `ready for review` for four days.

## Shipped

- **PR** `autolens_workspace_developer#126` — MERGED 2026-08-13T18:44:33Z as
  `c5cccb89` (3 commits, 29 files, +6181/-53).
- **Issue** `autolens_workspace_developer#125` — closed 2026-08-13T18:45:29Z.
- Remote branch `feature/pix-prodigy-gpu-compat` already deleted at origin.
- Results write-up on main: `searches_minimal/pix_prodigy_laptop_gpu_findings.md`
  (§1–6).

## Results

- Phase-1 item 2 (the 16-start claim) CONFIRMED on GPU.
- Phase 2 delivered the DelaunayNN starts curve, the VRAM ceiling (batch 8 OOMs
  family-wide), the batch-size comparison, free-vs-fixed regularization, and
  revised four-mesh recommendations.
- **Headline:** batch size decides whether plain Delaunay finds truth —
  b2 `+30203.3` @ `r_E 1.6001` vs b4 `+24581.8` @ `1.6314`. The local maximum was
  batch-caused, not mesh-caused. DelaunayNN is batch-INSENSITIVE (0.5 nats
  apart), consistent with its continuous Sibson interpolation through
  triangulation flips. So "batch 4 wins" is a DelaunayNN result and does **not**
  generalise.

## Corrections this task made to earlier claims

- "4 starts is too few" was over-attributed — that cell moved starts AND batch
  AND steps together. At batch 4 / 300 steps, 4 starts does reach truth.
- KNN needs ~300 steps with fixed regularization, not the >=1500 extrapolated
  from free AdaptSplit.

## Not covered (documented, not blocking)

- DelaunayNN free-AdaptSplit beyond 300 steps — still climbing at the cap, 109
  resurrections.
- Whether those lane deaths are NaN or an over-regularized floor needs a
  DelaunayNN truth-bar scan at high coefficients.

## Bookkeeping trap worth carrying

The stale entry was invisible to every routine check: `lifecycle check` reported
OK, and the worktree shell at `~/Code/PyAutoLabs-wt/pix-prodigy-gpu-compat`
survived as a directory of symlinks with **no registered git worktree left in
it**, so a `git worktree list` sweep did not name it either. The signal that
caught it was cross-checking `active.md`'s PR claim against `gh` — a merged PR
under an entry that says OPEN.

## Original prompt

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
