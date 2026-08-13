# Imaging likelihood hazards — phase 2 boundary

This directory is reserved for imaging-specific fixtures and cells that wrap
the reusable detectors in [`scripts/misc/hazards/`](../../misc/hazards/README.md)
around a complete likelihood.

Phase 1 deliberately contains no imaging cell. Active-set kinks, scientific
relevance of conditioning floors, structural degeneracies, and solver-backend
divergence are scoped by the follow-up task
`hazard_profiling_likelihood_tier.md`, after the phase-one record/check API has
merged. Reusable detector logic must not be duplicated here.
