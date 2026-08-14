# MultiStartGradient value-NaN and gradient-NaN step diagnostics

Type: feature
Target: PyAutoFit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised

MultiStartGradient value-NaN and gradient-NaN step diagnostics.

Add per-step non-finite accounting to MultiStartGradient and surface it. Scope is MEASUREMENT ONLY — no change to resurrection behaviour (see 'Deliberately out of scope' below).

PART 1 (the key diagnostic) — split and record value-NaN vs gradient-NaN steps.
In autofit/non_linear/search/mle/multi_start_gradient/search.py the fit loop detects a dead lane ONLY via 'alive = np.isfinite(np.asarray(foms))' (~line 627) — the VALUE. The gradient is never checked inside the loop; gradient finiteness is tested only when drawing initial starts (~line 876). So a lane whose value is finite but whose gradient is non-finite is not counted dead and not resurrected: optax.apply_if_finite zeroes its update and the lane silently freezes in place while still counted alive. That failure mode is currently invisible, and it is exactly a differentiability failure rather than an evaluation failure. Count both, per step, and record them separately:
  - value-NaN lane-steps: where the likelihood is UNDEFINED (today's resurrection trigger)
  - gradient-NaN lane-steps: where the likelihood is defined but NOT DIFFERENTIABLE (new; currently unmeasured)
'grads' is already in hand at that point in the loop. Persist both counters into search_internal alongside n_resurrections, and into samples_info in samples_via_internal_from. Measure, do not assume, the cost: pulling grads to host is a larger device-to-host transfer than foms (n_starts x n_params vs n_starts) and sits inside the stepped loop — the step already syncs on foms, so it is likely in the noise, but benchmark it.

PART 2 — surface the counters in search.summary.
autofit/text/text_util.py:115 search_summary_from_samples(samples) already receives the samples object, and samples_via_internal_from already puts n_resurrections, n_starts, n_steps, total_steps and resurrect into samples_info. Add a guarded block emitting the resurrection count, the two NaN counters, and NORMALIZED rates (divide by n_starts * total_steps — raw counts are not comparable across runs: 797 on a 16x3000 run vs 10 on an 8x300 run differ 80x raw and ~2x by rate). Follow the existing duck-typed precedent three lines above, 'if hasattr(samples, total_accepted_samples)', which adds Total Accepted Samples / Acceptance Ratio for MCMC searches — search-specific blocks are already the idiom. Guard with .get() so other searches are unaffected.

Naming constraint: emit these as neutral factual counts. Do NOT label them a smoothness metric in user-facing output — the resurrection-rate to HMC-divergence-rate correlation is unvalidated (that validation is a separate ideas.md item, wsdev#117 resurrection diagnostics).

Deliberately out of scope: making resurrect trigger on non-finite gradients. That would change search behaviour and shift every existing benchmark number, so the wsdev #117/#125 pix results would stop being comparable without re-running. Decide the resurrection policy AFTER the counters show how often frozen lanes actually occur.

Motivation: pixelized-mesh MultiStartProdigy campaigns (wsdev #117/#125) judge mesh differentiability indirectly, from final logL and raw resurrection counts. The value/gradient NaN split directly answers the open question in pix_prodigy_laptop_gpu_findings.md section 6.2 — whether DelaunayNN's 109 free-AdaptSplit lane deaths were NaN deaths like plain Delaunay or survivable over-regularized-floor deaths like knn — and would have caught frozen zombie lanes in every run to date, some of which may have been misattributed to regularization plateaus.

Sizing note: this is SMALL despite the prose length — roughly a counter plus two dict keys in search.py, and a ~5-line guarded block in text_util.py, plus a benchmark and unit tests.

<!-- formalised by the Intake (Conception) Agent on 2026-08-14 from user-intake -->
