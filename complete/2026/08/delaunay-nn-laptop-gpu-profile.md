## delaunay-nn-laptop-gpu-profile
- issue: https://github.com/PyAutoLabs/autolens_profiling/issues/105
- completed: 2026-08-13
- workspace-pr: https://github.com/PyAutoLabs/autolens_profiling/pull/106
- summary: Added the CPU, RTX 2060, and A100 DelaunayNN profiling sweep and result artifacts at matched PyAuto source revisions. The A100 evidence corrected the interim laptop conclusion: production cap-32 overhead is 4.30x on A100 rather than the RTX 2060's noisy 5.44x, with zero overflow or degeneracy. The merged submit script also records all five source revisions in future job logs.

## Original prompt

# Profile DelaunayNN against Delaunay on the laptop GPU

Type: feature
Target: autolens_profiling
Repos:
- @autolens_profiling
Difficulty: small
Autonomy: human-required
Priority: high
Status: formalised

Run the existing full-mapper DelaunayNN benchmark on the laptop's NVIDIA RTX
2060 Max-Q through the `PyAutoGPU` environment. Match the existing CPU profile
(1,200 mesh points, 15,000 queries, query chunk 256, caps 16/24/32/64, five warm
repeats) so the cap-32 production configuration can be compared directly with
ordinary barycentric Delaunay.

Persist a hardware-identified JSON/PNG result that cannot be overwritten by a
future A100 profile. Update the profiling documentation with absolute warm and
compile timings, the DelaunayNN-to-Delaunay ratio on GPU, and CPU-to-GPU
speedups. Preserve all unrelated local datasets and result artifacts.

## Original request

> OK then let's do work and profiling on this laptops gpu for now which is
> available via PyAutoGPU vent. We implemented DelaunayNN yesterday can you use
> autolens_profiling to compare its run times on gpu to thr cpu run to normal
> delaunay as for cou it was 4.6x or something slower

Follow-up approval/context:

> OK go, we did some recent pulls on main locally but I dont think updarea
> should effect the work here.
