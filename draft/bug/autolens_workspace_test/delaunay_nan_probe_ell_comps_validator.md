# The delaunay.py NaN-poisoning probe dies in ell_comps validation before it can probe anything

Type: bug
Target: autolens_workspace_test
Repos:
- @autolens_workspace_test
- @PyAutoGalaxy
Difficulty: medium
Autonomy: supervised
Priority: normal
Status: fix shipped 2026-08-24 (autolens_workspace_test fix/delaunay-nan-probe; validation + PR in flight)
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
