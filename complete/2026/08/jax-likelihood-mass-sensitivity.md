## jax-likelihood-mass-sensitivity
- issue: https://github.com/PyAutoLabs/autolens_workspace_test/issues/253
- completed: 2026-08-06
- workspace-pr: https://github.com/PyAutoLabs/autolens_workspace_test/pull/254 (merged ca372a4)
- summary: Audit + fix for median-literal mass blindness across all jax_likelihood/datacube scripts (phase 2 of the finding from #251/#252). Audit probe: exec each script's source to its literal, evaluate the median vector, re-evaluate with every lens mass param +5%, compare ΔLL to the literal's rtol=1e-4 tolerance. Results: 1 hard-blind (imaging/mge_group, ΔLL 5e-11), 9 sub-tolerance (all 7 interferometer pixelized + both datacube — a 5% mass change passes their literal), 10 robustly sensitive (untouched). Human-approved pattern: `__Mass Sensitivity__` assert blocks (perturbed LL must move by audit-ΔLL/5 floor) with NO literal regeneration — except imaging/mge_group, which required anchoring its Isothermal near simulator truth (θ_E prior median 1.6, was config-median 4.0 → zeroed source) + one regenerated literal (−29060.215 → −28830.547).
- validated: all 10 patched scripts executed through literal + new assert in the worktree (10/10 pass); mge_group re-audited post-anchor (ΔLL → 48.9, floor 9.0).
- caveat: some "robustly sensitive" verdicts flow through the PositionsLH penalty rather than source light (lp/multipole, dLL ~4e8) — still regression-detecting.
- ship-context: merged under the standing human instruction "if it runs ok locally then merge" (Actions outage ongoing); Heart RED (same release-arc reason set, same-day ack).
- UNAUDITED follow-ups (deliberately out of scope, no prompt filed): 8 multi_dataset scripts (harness can't drive FactorGraphModel vmap — status UNKNOWN, not proven safe) and 5 non-standard-structure scripts (potential_correction ×2, shared_preloads ×2, delaunay_near_caustic).
- audit harness: truncated-exec probe (audit_one.py) — session scratchpad only, reconstruct from the completion record if needed.

## Original prompt

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
