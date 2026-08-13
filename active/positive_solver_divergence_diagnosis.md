# Diagnose positive-solver backend divergence

Type: research
Target: autolens_profiling
Repos:
- autolens_profiling
Difficulty: medium
Autonomy: supervised
Priority: high
Status: issued
Source: autolens_profiling#110 · finding `likelihood.imaging-pixelization.positive-solver-backend-divergence`

The tier-2 likelihood scan measures a maximum reconstruction-relative difference
of about 0.9% between NumPy's active-set FNNLS path and JAX's PDIP/Jacobi path,
concentrated near the high-Einstein-radius edge. Figure-of-merit differences are
much smaller. Before proposing any PyAutoArray solver change, determine whether
this is a stopping-control effect, an active-support boundary, or distinct
numerical optima.

Use the existing full `FitImaging` pixelization fixture. Retain the current
NumPy/JAX error curve, then add a bounded diagnostic at the divergent radii that
compares the default JAX policy with tighter/longer and relaxed settings through
the already-public `nnls_solver_tol` and `nnls_max_iter` controls.

Report:
- support masks and support changes;
- normalized NNLS objective gaps;
- scale-normalized primal, dual, and complementarity KKT residuals;
- reconstruction and figure-of-merit differences for each policy;
- whether more iterations or a tighter tolerance closes the backend gap;
- a bounded recommendation for, or against, a later PyAutoArray source task.

Do not modify PyAutoArray, solver dispatch, algorithms, tolerances, or production
defaults. Preserve the stable finding ID and results schema.
