## multistart-nan-step-diagnostics

- issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1472 (closed)
- completed: 2026-08-14
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1473 (MERGED fbfcece3)
- profiling-pr: https://github.com/PyAutoLabs/autolens_profiling/pull/127 (MERGED a34d6191)

`MultiStartGradient` detected a dead lane only via the VALUE. A lane whose
likelihood was finite but whose gradient was non-finite counted as alive, had
its update zeroed by `optax.apply_if_finite`, and froze in place — a
differentiability failure that looks exactly like convergence in the FoM trace.
Now counted per step, disjointly (gradient-NaN only for lanes still alive by
value), persisted into `search_internal` + `samples_info`, and surfaced in
`search.summary` with rates normalised by `n_starts * total_steps`.

Measurement only: `resurrect` still triggers on value-NaN alone, so the
wsdev #117/#125 benchmark numbers stay comparable. The resurrection policy is
deliberately deferred until the counters show how often frozen lanes occur.

### The finding that changed the design

Reducing gradient finiteness on device but OUTSIDE the jit is the WORST of three
options, not the best — it buys a kernel dispatch plus a host round-trip to
avoid a transfer that was never the cost. Measured ~+3%/step against a ~1.5%
noise floor, worse than pulling the whole `(n_starts, ndim)` gradient to host.
Fused into the jitted call it is +0.05%. On a real MGE lens likelihood the
shipped variant costs **4.1us on a 1.03s step = 0.0004% of run time**.
See [[feedback_eager_jnp_reduction_outside_jit_costs_more]].

### Traps hit

- **A benchmark can be too coarse to see its own subject.** The first profiling
  harness diffed two end-to-end loops: a ~4us effect against a ~1s step, with
  ~10-35ms jitter. Variants came out NEGATIVE (faster than a baseline doing
  strictly less work) and the verdict would have passed a 9ms regression as
  "below the noise floor". The duplicate-baseline CONTROL is what exposed it —
  without a measured noise floor the script could only make an unfalsifiable
  claim. Fixed by measuring numerator and denominator where each is resolvable.
- **`_broad_starts` already filters draws on gradient finiteness.** A forced
  NaN-gradient fixture covering the start range gets every start rejected
  outright (`could not draw any finite-gradient starting points`). Lanes must
  BEGIN differentiable and cross the cliff mid-descent — which is precisely why
  mid-search freezing was the invisible gap.
- **`| tail -N` on a long background run destroys the results.** Cost a 25-minute
  six-workspace smoke re-run. Redirect to a file.
- **Verifying the source on disk is not verifying the source that got imported.**
  Probing the smoke env's interpreter directly resolved `autofit` to the
  canonical checkout, which looked like the run had graded `main`. It hadn't —
  `heart/smoke.py` replaces `PYTHONPATH` from `--root` and preflights module
  ownership. Check the log, not a probe outside the runner's environment.
- A completed search DELETES its `search_internal`, and re-running a completed
  named search returns the cached result via `.completed` rather than resuming.
  The only real resume scenario is a search killed mid-run with
  `iterations_per_full_update` small enough to have checkpointed.

### Verification beyond the suite

Device reduction cross-checked against host recomputation on real gradients
(exact agreement); gradient-NaN counter proven to FIRE via the `jnp.where` AD
trap (14/80 lane-steps, `n_resurrections` unchanged); `search.summary` verified
ON DISK with rates recomputed from the file; both guards mutation-tested.
Full suite 1747 passed / 2 skipped. Smoke: all six workspaces, the only three
failures reproduced byte-identically against `main`.

### Spun off, not absorbed

- `draft/bug/autofit/multistart_gradient_resume_fom_sanity_check.md` —
  MultiStartGradient cannot resume a killed mid-run search on `main`; the FoM
  sanity check compares a stored log-likelihood against the multi-start
  chi-squared convention (clean -2x). This BLOCKS end-to-end verification of the
  counters' resume accumulation, which therefore ships unit-test-only.
- `draft/bug/workspaces/jax_likelihood_pins_stale_by_1e4.md` — three
  `jax_likelihood` pins stale by 1.24e-4 against rtol 1e-4, failing on `main`.

### Still owed

GPU row for the profiling artifact (unchecked box in autolens_profiling#127):
laptop GPU first, then A100 with `jax_enable_x64` set EXPLICITLY — it is not
inherited under `sbatch`, and float32 would halve the gradient array and
understate the exact quantity under test. CPU cannot see the `host` variant's
real cost at all (same-address-space memcpy).

Shipped on Heart YELLOW (score 70, `red_reasons: []`), human-acknowledged; both
reasons pre-existing and unrelated.

## Original prompt

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
