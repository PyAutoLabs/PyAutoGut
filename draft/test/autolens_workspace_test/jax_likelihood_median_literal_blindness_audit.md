# Audit jax_likelihood median literals for source-plane-mass blindness

Type: test
Target: autolens_workspace_test
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: formalised

## Original request (verbatim)

> ok do this Also banked as memory: the underlying finding that literals
> generated at the default prior medians are bit-blind to source-plane mass
> (the solver zeroes the source there) — the existing median-anchored
> jax_likelihood scripts share that blindness and are a candidate for a future
> audit prompt.

## Background

Found during autolens_workspace_test#252 (`imaging/jax_likelihood/smbh.py`):
at the workspace's default prior medians (source `effective_radius=15.0`,
Isothermal `einstein_radius=4.0`) the positive-only linear solver zeroes the
source's solved intensity, making the imaging likelihood bit-identical for any
source-plane mass structure. A vmap literal generated at that point pins JIT
compilation and the light pipeline but CANNOT detect a mass-pipeline
regression.

## Plan

Phase 1 — audit (read-only): for every `jax_likelihood` / `datacube` script in
`imaging/`, `interferometer/`, `multi_dataset/` (point_source exempt by
mechanism — positional chi² is deflection-driven with no solver), build the
script's own model + fitness via its source up to the literal assertion,
evaluate the likelihood at the median vector, then re-evaluate with the lens
mass parameters perturbed (+5%). |ΔLL| ≈ 0 → BLIND literal. Report a
classification table.

Phase 2 — fix (pending phase-1 results + human sign-off on the pattern):
either truth-anchor blind scripts' fixed components (the `smbh.py` pattern,
regenerating literals) or add a mass-perturbation sensitivity assertion
alongside the existing literal. Decision deliberately deferred — regenerating
many pinned regression literals is a scope call.
