# The delaunay NaN probe injected above the boundary the validator guards

autolens_workspace_test#277 (`995f0c9`), shipped 2026-08-24 — the first of the
two bugs the smoke-surface retime sweep (#274,
`complete/2026/08/smoke-surface-retime-sweep.md`) found hiding behind SLOW
markers. Never issued as a GitHub issue: filed as a draft bug prompt at 18:0x
and fixed the same evening.

## What shipped

`scripts/interferometer/jax_likelihood/delaunay.py`'s NaN-poisoning probe
built an instance from an all-NaN vector via `instance_from_vector`, dying at
autogalaxy `validate_ell_comps` (`ModelParameterException`) before testing the
JAX NaN-lane isolation it exists to test — deterministic exit 1 on both
Python legs, 5/5 (run 32741371308). The probe now builds the instance from
prior medians and poisons a single downstream leaf
(`mass.einstein_radius = np.nan`) by attribute assignment, below the
constructor guard — a like-for-like port of the shipped imaging sibling probe
against the identical model, assertion unchanged. `no_run.yaml`'s NEEDS_FIX
entry removed, restoring mega-run coverage.

Validated in CI before the PR: retime dispatch 32759921650 on the fix branch —
NEITHER on both legs (42.0 s / 43.6 s at 14–15 % of cap), with the
previously-unreachable tail passing ("invalid Delaunay mesh reaches the raw
interferometer likelihood as NaN", TransformerNUFFT cross-check).

## Key traps / findings

- **The validator was right.** NaN rejection in `validate_ell_comps` is a
  deliberate contract: present from the validator's birth (autogalaxy
  `a366f771`, with NaN/inf parametrized as rejected across the guard family)
  and deliberately softened to a resampling `FitException` in `be61b8d0`. The
  probe-side fix was the only correct side.
- **A probe that constructs pathological inputs through the public
  construction path inherits the public path's validation.** Poison below the
  boundary (post-construction attribute assignment) — the imaging sibling had
  already made this move; interferometer was the straggler.
- The local container could not run the stack (Python 3.11 vs the libraries'
  `>=3.12` pin), so validation ran as a retime dispatch on the branch before
  the PR — the harness this same day's work repaired.

## Follow-ups

None of its own. The sibling bug found by the same sweep —
`gradient_eager_jit_divergence_py313.md`, root-caused to an NNLS
`while_loop` branch flip — remains in `draft/` with its fix direction
recorded (pin `nnls_solver_tol`/`max_iter`).

## Lifecycle note

The shipping session closed the prompt out in place (Mind commit `9f5e6972`,
`Status: shipped 2026-08-24`) but never advanced it out of `draft/`, so it kept
rendering as pickable backlog on the dashboard until the 2026-08-24
completed-prompt reconciliation sweep moved it here. No further work.

## Original prompt

# The delaunay.py NaN-poisoning probe dies in ell_comps validation before it can probe anything

Type: bug
Target: autolens_workspace_test
Repos:
- @autolens_workspace_test
- @PyAutoGalaxy
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: shipped 2026-08-24 (autolens_workspace_test#277, merged 995f0c9)
Filed: 2026-08-24

## The failure

`@autolens_workspace_test/scripts/interferometer/jax_likelihood/delaunay.py:330`
ends with a deliberate NaN-poisoning probe:

```python
nan_instance = model.instance_from_vector(
    vector=np.full(model.total_free_parameters, np.nan)
)
nan_fit = fit_jit_fn(nan_instance)
assert np.isnan(float(nan_fit.log_likelihood))
print("PASS: invalid Delaunay mesh reaches the raw interferometer likelihood as NaN.")
```

`instance_from_vector` now hands the all-NaN `ell_comps` to autogalaxy's
`validate.validate_ell_comps`, which raises `ModelParameterException`. The script
exits 1 **at instance construction**, so the thing the probe exists to test —
that an invalid Delaunay mesh propagates NaN cleanly through the JAX lane to
`log_likelihood`, rather than crashing or returning a plausible-looking number —
is never exercised.

Everything above line 330 passes: the NumPy/JIT likelihood-parity work, the
`jax.Array` type assertion and the `rtol=1e-4` round-trip all succeed first. This
is the last block in the script that fails.

## Measurement

2026-08-24 retime sweep, 5 repeats per Python leg, 300 s cap
(run 32741371308; see autolens_workspace_test#274):

- **Deterministic** — exit 1 on 5/5 repeats, on **both** the 3.12 and 3.13 legs.
- Not a timeout and not performance. The script's old
  `# SLOW 2026-07-14 - flakes at the 1800s cap (PyAutoHeart#74)` marker was a
  misdiagnosis; it has been rewritten to
  `NEEDS_FIX 2026-08-24` in `@autolens_workspace_test/config/build/no_run.yaml`
  pointing here.

## The contract question (decide in task)

Two coherent fixes exist and they disagree about whose contract is wrong. Pick
one deliberately; do not split the difference.

**A. The probe changes (filed under this target).** The validator is arguably
doing exactly its job: non-finite `ell_comps` are not a physical model and
`ModelParameterException` is the established "reject this point" signal. If so,
the probe's *injection route* is what is wrong — poisoning the free-parameter
vector is an artificial path into a NaN lane that a real fit would never take,
because a sampler proposing NaN parameters is itself the bug. Rework the probe to
inject NaN below the model-construction boundary and keep testing what it was
written to test: e.g. build a valid instance and poison the array/dataset the
mesh is derived from, or drive the jitted fitness directly with a NaN parameter
array so no eager validation intervenes. Whatever route is chosen, the assertion
must stay a real assertion about NaN reaching `log_likelihood` — do not degrade
it to `pytest.raises(ModelParameterException)`, which would only re-test the
validator.

**B. The validator changes (`@PyAutoGalaxy`, `validate.validate_ell_comps`).**
If NaN parameters are meant to be *representable* and to propagate as NaN — which
is what the JAX lane is built to do, and which under `jax.jit` the validator
cannot enforce anyway, since a traced `ell_comps` has no value to test — then
raising on NaN is an eager/jit asymmetry rather than a guard. In that case give
the validator an explicit, documented NaN policy: NaN passes through, non-finite
*non-NaN* values (`±inf`) and out-of-support finite values still raise.

**Hard constraint on either path:** the fix must not weaken validation of real
invalid input. Option B in particular must not become "skip validation when any
component is non-finite" — the point is a stated NaN policy, not a hole. If the
task lands on B, re-file/re-target this prompt at `@PyAutoGalaxy` so the PR lands
in the right repo, and check whether the same NaN policy is owed to the other
`validate.*` helpers rather than to `ell_comps` alone.

Worth establishing early, because it decides the question: **when did this start
raising, and was it intended?** The probe used to pass, so either
`validate_ell_comps` gained a NaN check or it started being called on a path that
previously skipped it. Find that change before choosing A or B.

## Acceptance

- `scripts/interferometer/jax_likelihood/delaunay.py` runs green on both Python
  legs, with the NaN-lane assertion still asserting NaN reaches
  `log_likelihood`.
- Whichever contract moved (probe or validator) is documented in a sentence
  where a reader will hit it — the script's docstring, or the validator's.
- Real invalid-input validation is demonstrably unchanged.
- The `interferometer/jax_likelihood/delaunay.py` `NEEDS_FIX` entry is removed
  from `@autolens_workspace_test/config/build/no_run.yaml`, restoring mega-run
  coverage.
