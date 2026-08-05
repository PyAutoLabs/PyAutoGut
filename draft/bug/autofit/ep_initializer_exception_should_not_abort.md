# EP: an `InitializerException` in one factor should degrade to a bad projection, not kill the fit

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: safe
Priority: high
Status: formalised
Issue: (none yet — parent report is https://github.com/PyAutoLabs/PyAutoFit/issues/1405)

## The defect

Defect 2 of the two filed on PyAutoFit#1405, split out because it is small,
self-contained, and independently valuable — it is the *most frequent* of the
three EP outcomes after a clean recovery.

In **23% of 30 identical-problem EP runs** (7/30) on a known-answer CPU toy, the
fit **hard-aborts mid-EP** with an `InitializerException` ("initial samples all
have the same figure of merit", `autofit/non_linear/initializer.py:185`). EP
drives one factor into a degenerate all-equal-likelihood state that the
per-factor `DynestyStatic` cannot initialise, and the exception propagates out
of the EP loop and kills the whole graph fit. Everything already computed —
every other factor's converged message, the whole `ep_history` — is lost.

Crash frequency is flat across `max_steps ∈ {20,25,30,50,60}`, so it is not a
long-run accumulation effect; any EP fit can hit it at any sweep.

### It is not hierarchical-specific (release-leg reproduction, 2026-08-03)

The toy that characterised this defect is a hierarchical graph, but the defect
is **not** a `HierarchicalFactor` property. The 2026-08-03 nightly release leg
reproduced the identical exception on a graph with *no* hierarchical factor at
all:

- PyAutoHeart run `30788224561`, job `91606145038`
  (`integrate / run_scripts (3.12, autofit_test, graphical)`).
- `autofit_workspace_test scripts/graphical/ep.py` — FAIL (11.4s) with the same
  `InitializerException` body. Its model is a **shared** `centre`
  (`af.GaussianPrior(mean=50.0, sigma=30.0)`) across two `AnalysisFactor`s, each
  with its own `DynestyStatic(nlive=300, maxcall=1000, maxiter=1000)`; there is
  no `HierarchicalFactor` in the script.
- **`scripts/graphical/hierarchical.py` PASSED in the same shard**, on the same
  wheels, in the same run — as did `ep_deterministic.py`, `ep_exact.py`,
  `ep_parity.py`, `shared_state.py` and `simultaneous.py`.

So the degenerate all-equal-FoM state is reachable through ordinary shared-prior
message passing. Scope the fix and its regression test to the **per-factor
update site in general**, not to hierarchical factors.

Two further properties from that run:

- **Intermittent, consistent with the ~23% rate.** The same shard passed the
  2026-08-04 night with no change to `ep.py`.
- **Release-profile-only.** The per-PR smoke gate runs `PYAUTO_TEST_MODE=2`,
  which bypasses the sampler and therefore the initializer entirely — this
  defect can only ever surface on the release leg (`PYAUTO_TEST_MODE=0`,
  `config/build/profile_release.yaml`). Do not expect a smoke run to show it.

### The `nan` in the exception text is a red herring — fix the message too

The exception body lists three possible causes, one of them
"The `log_likelihood_function` is always returning `nan` values." **That cause
is impossible for this check**, and the wording has already caused one
misdiagnosis (this failure was first filed as an all-`nan` likelihood bug).

The guard is:

```python
if total_points > 1 and np.allclose(a=figures_of_merit_list[0], b=figures_of_merit_list[1:]):
```

`np.allclose` defaults to `equal_nan=False`, so an all-`nan` figure-of-merit
list returns **False** and cannot raise this exception (verified:
`np.allclose(np.nan, [np.nan, np.nan]) is False` on numpy 2.4.6). The condition
detected is all-**equal**, finite likelihoods — exactly the degenerate state EP
drives a factor into. Reword the message accordingly as part of this fix.

## The fix

Catch the exception at the per-factor update site inside the EP loop and record
it as a **flagged bad projection / skipped update** (the mechanism EP already
has for `BAD_PROJECTION`), so the sweep continues with that factor's previous
message and the failure is visible in `ep_history.csv` rather than fatal.

Design points to settle while implementing:

- **Which exception surface.** `InitializerException` is the observed one, but
  the general condition is "this factor's optimiser could not run this sweep".
  Decide whether to catch narrowly (`InitializerException`) or introduce a
  factor-update failure category. Prefer narrow first — a blanket
  `except Exception` here would silently swallow real bugs, which
  `feedback_no_silent_guards` says not to do. **This must stay loud**: flagged
  in `ep_history.csv` and surfaced by the diagnostics, never silent.
- **Repeat failures.** If the same factor fails to initialise every sweep, EP
  will converge on a stale message and report success. Add a threshold — N
  consecutive failed updates on one factor should abort *with a clear message
  naming the factor*, which is strictly better than today's raw traceback.
- **Both raise sites.** The guard is duplicated in `initializer.py` at
  `samples_from_model` (line ~117/120) and `samples_jax` (line ~182/185). The
  release profile runs with `PYAUTO_DISABLE_JAX=0`, so the JAX path is live in
  the leg that caught this. Fix the handling *and* the message text at both, or
  factor the shared check into one helper.
- **Keep the release leg honest.** Degrading this crash to a skipped update
  turns a red release-leg script green while the underlying EP pathology is
  still there. That is acceptable only because the failure stays recorded —
  make sure whatever is written to `ep_history.csv` is something the nightly
  triage can actually see, so "ep.py passes now" never silently means "EP still
  degenerates every fourth run". This was the stated objection to fixing the
  release-leg failure via this prompt; it is answered by loudness, not by
  leaving the crash in place.
- **Test.** A regression test that drives a factor to an all-equal-FoM state
  and asserts the EP run completes with the failure recorded rather than
  raising. Cover a **non-hierarchical** shared-prior graph (the shape that
  failed on the release leg), not only a `HierarchicalFactor` one.
  `test_autofit/graphical/` is the home; numpy-only
  (`feedback_no_jax_in_unit_tests`).

## Repro

`complete/2026/07/ep_scale_collapse_assets/ep_toy_diagnostic.py` (self-contained,
numpy-only, minutes on CPU; run from the `HowToFit` repo root). Roughly 1 run in
4 crashes, so loop it:

```bash
cd HowToFit
export NUMBA_CACHE_DIR=/tmp/numba_cache MPLCONFIGDIR=/tmp/matplotlib PYAUTO_SKIP_VISUALIZATION=1
for r in $(seq 1 10); do TOY_MAX_STEPS=20 TOY_JOINT=0 TOY_TAG=rep_$r \
  python3 <path>/ep_toy_diagnostic.py 2>/dev/null | grep OUTCOME; done
```

Full forensics: `complete/2026/07/ep_scale_collapse_assets/EP_TOY_FINDINGS.md`.

Second, independent repro — the non-hierarchical release-leg shape, from the
`autofit_workspace_test` root (a smoke-profile run will **not** show it):

```bash
python3 <path>/PyAutoHands/autohands/run_python.py \
  autofit_test scripts/graphical \
  --env-config config/build/profile_release.yaml
```

Also intermittent, so loop it and count rather than reading one run.

## Relationship to the other defect

Independent of the COLLAPSE defect
(`draft/bug/autofit/ep_hierarchical_scale_collapse_moment_match.md`) and safe to
fix first — this one is a robustness fix with no statistical judgment in it,
whereas COLLAPSE needs a moment-match redesign. Fixing this one first also makes
the COLLAPSE work cheaper: 23% fewer wasted runs when gathering statistics over
repeated identical fits.

<!-- filed 2026-07-22 as the wrap-up follow-up of the ep-hierarchical-scale-collapse
task (report-only; PyAutoFit#1405). Origin: slope_hierarchy#1 goal 2.
2026-08-05: absorbed draft/bug/autofit/graphical_ep_nan_likelihood_release_leg.md
(the 2026-08-03 release-leg ep.py failure). That prompt read the exception's
"always returning nan" line as a nan diagnosis and scoped itself to finding the
nan source; the guard is np.allclose over the figures of merit, which cannot fire
on nan, so it is the same all-equal-FoM defect as this one on a non-hierarchical
graph. Folded rather than issued as a fourth EP issue. -->
