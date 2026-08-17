# Reconstructing a stored sample raises through `ignore_assertions=True`

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised
Issue: https://github.com/PyAutoLabs/PyAutoFit/issues/1486
Blocked-by: PyAutoFit claimed by `version-stamp-sync-guards` (PyAutoHands#235) — claimed under
  `stored-sample-reconstruction-guard` in `active.md`. Re-run `worktree_check_conflict` before starting.

## What this is

Two PyAutoFit entry points materialize a **stored search sample** into a model
instance without any `FitException` recovery, so a sample the model no longer
accepts raises straight through to the user:

1. `Sample.instance_for_model(model, ignore_assertions=True)`
   (`autofit/non_linear/samples/sample.py:178-212`) — **the CI failure site.**
   `ignore_assertions` reaches only `af.Model`'s own assertion mechanism; it
   cannot stop a downstream profile constructor from raising, despite the
   parameter's docstring reading *"If True, do not check that the instance is
   valid"*.
2. The shared `to_instance` decorator (`interface.py:32-40`), used by
   `from_sample_index`, `max_log_posterior`, `median_pdf`,
   `values_at_*_sigma`, `errors_at_*_sigma`:

```python
if as_instance:
    return self._instance_from_vector(vector)   # <-- no try/except
```

[PyAutoFit#1466](https://github.com/PyAutoLabs/PyAutoFit/issues/1466)
(`b499d4367`, 2026-08-11) established the recovery contract but wrote it **by
hand at two call sites only** — `max_log_likelihood` (`samples.py:405-441`) and
`draw_randomly_via_pdf` (`pdf.py:336-367`). Everything else was left exposed.

`as_dict=True` and `as_instance=False` never construct an object and are always
safe; only the materialization request needs the guard.

## Why invalid samples are in storage at all

This is the part that makes the bug real rather than cosmetic — **the stored
sample list legitimately contains points the model rejects.**

`PyAutoGalaxy` gained a geometric constructor guard on 2026-08-09 (`a366f771`,
#566): `validate_ell_comps` rejects `ell_comps` whose magnitude is not below 1,
since `q = (1 - f) / (1 + f)` is a valid axis ratio only while `f < 1`. The next
day `be61b8d0` (#568) made it a
`ModelParameterException(ValueError, af.exc.FitException)` so a search would
*resample* rather than die.

**"Resample" is a misnomer.** `fitness.py:252-258` on the NumPy path:

```python
except exc.FitException:
    return self.resample_figure_of_merit      # -1.0e99 for Nautilus
```

It does not redraw — it returns a sentinel figure of merit, and the sampler
**still records the point**. On the JAX path (`fitness.py:244-250`) there is no
guard at all, and none is needed: `autoarray.validate.is_concrete_scalar`
returns `False` for tracers, so `validate_ell_comps` passes tracers through
unvalidated, while `convert.py:86-92` clamps the magnitude to
`ELL_COMPS_MAGNITUDE_CLAMP = 0.999`. A JAX fit therefore explores |e| >= 1
freely and stores the raw, unclamped value.

Either way the stored parameter vector keeps a value the constructor will later
refuse. Reconstruction is where it surfaces.

## The CI failure

`PyAutoHeart` **Workspace Smoke**, scheduled runs 2026-08-10 (`31356506626`)
and 2026-08-17 (`31992749671`), job `run_notebooks (3.12, autogalaxy, guides)` —
1 failure in 1332 checks:

```
autogalaxy_workspace notebooks/guides/results/aggregator/samples.ipynb
  ModelParameterException: ell_comps must satisfy ell_comps[0]**2 + ell_comps[1]**2 < 1;
  got (0.9781300707301511, -0.23873992910981626), magnitude 1.0068441731558715
```

Reproduced locally end-to-end (see below); the traceback lands on
`scripts/guides/results/aggregator/samples.py:451`:

```python
for sample in samples.sample_list:
    instance = sample.instance_for_model(model=samples.model, ignore_assertions=True)
```

That loop walks **every** stored sample, so it fires deterministically whenever
any invalid sample exists — which is why it fails every scheduled run rather
than intermittently.

## Reproduction (local, confirmed)

Ran `_quick_fit.py` then `aggregator/samples.py` under the env PyAutoHands
resolves from `config/build/profile_smoke.yaml`, then again under a
production-like env. Script:
`scratchpad/run_smoke_repro.py`.

| | smoke env | production-like (JAX on, checks on) |
|---|---|---|
| invalid stored samples | 2/300, 2/300 | **1/300**, 0/300 |
| max \|ell_comps\| | 1.124, 1.133 | 1.115 |
| weight of every invalid sample | `0.0` | `0.0` |
| tutorial result | **fails** (exact CI error) | invalid samples present |

Invalid samples appear **with checks enabled and JAX on**, so this is not purely
a smoke-profile artifact.

A second control test (`scratchpad/repro_guard_gap.py`) isolates the
`to_instance` half against a synthetic sample list — arm A puts the invalid
sample last, arm B makes it maximum-posterior:

| call | arm A | arm B |
|---|---|---|
| `max_log_likelihood()` | ok — recovered | ok — recovered |
| `draw_randomly_via_pdf()` ×50 | ok — recovered | ok — recovered |
| `max_log_posterior()` | ok (not selected) | **RAISED** |
| `from_sample_index(-1)` | **RAISED** | ok (not selected) |

The two hand-guarded methods recover under both arms; the two decorated ones
raise as soon as they happen to select the invalid sample.

## Test mode is NOT implicated (checked explicitly)

Both scripts declare `ENV: full_datasets real_search`, and
`PyAutoHands/autohands/env_config.py:63` maps `real_search` to
`("PYAUTO_TEST_MODE",)` — a token **releases** (unsets) its var. The resolved
smoke env is:

```
PYAUTO_DISABLE_JAX=1  PYAUTO_FAST_PLOTS=1  PYAUTO_SKIP_CHECKS=1  PYAUTO_SKIP_VISUALIZATION=1
```

`PYAUTO_TEST_MODE` is absent, so no sampler bypass runs. Independently,
`_build_fake_samples` (`abstract_search.py:1111-1171`) synthesizes the prior
median ±0.1%, which cannot produce |e| = 1.007. Do not re-open this line.

## Fix locus

**PyAutoFit library source**, both entry points:

- `Sample.instance_for_model` — make `ignore_assertions=True` honour its stated
  contract, i.e. also tolerate a downstream `FitException`. The caller has
  explicitly said it accepts invalid points; today the flag silently under-
  delivers. Decide and document what "tolerate" returns (skip vs. sentinel) —
  it cannot construct the rejected object.
- `to_instance` — an explicit **per-method recovery policy**, so every decorated
  method inherits one contract instead of each call site restating it:

```python
def to_instance(func=None, *, recover="raise"):
    ...

@to_instance(recover="next_valid")
def max_log_posterior(self): ...

@to_instance(recover="raise")
def from_sample_index(self, sample_index): ...
```

- `recover="next_valid"` — fall back to the next-best valid stored sample,
  reusing what `max_log_likelihood` already implements by hand.
- `recover="raise"` — a typed `SamplesException` naming the offending
  parameter, explaining why the point is invalid, and stating that
  `as_dict=True` / `as_instance=False` return the raw values safely.

Fold #1466's two hand-written guards onto the same mechanism — one
implementation, not three.

Rejected: a uniform typed error everywhere (leaves `max_log_posterior` without
the fallback its likelihood twin has); threading an `ignore_assertions` caller
flag through `to_instance` (pushes a library contract gap onto every user).

Do **not** weaken `validate_ell_comps`, and do **not** edit the tutorial to
route around this — the tutorial is user documentation and the guard is correct.

### Behaviour change to note in release notes

`ModelParameterException` subclasses **`ValueError`**; `SamplesException`
subclasses plain `Exception` (`autofit/exc.py:57`). Callers catching `ValueError`
around these methods would stop catching it. `raise ... from e` preserves the
cause.

## Split out — do not fix here

Every invalid sample measured carried weight exactly `0.0`, and
`samples_weight_threshold: 1.0e-10` is set in both the workspace and packaged
`config/output.yaml`. The prune at `updater.py:220` should therefore have
removed all 299 zero-weight rows — but **all 300 survived in both runs**, and
the `"removed from samples.csv"` log line never fired. `PYAUTO_SKIP_CHECKS=1`
explains it under smoke (`samples.py:505-506` nulls the threshold) but **not**
the checks-on run. Suspect: the early `return` on `FitException` at
`updater.py:212-215`, which skips the prune entirely — unconfirmed.

Filed separately as
[PyAutoFit#1487](https://github.com/PyAutoLabs/PyAutoFit/issues/1487):
different blast radius (every saved `samples.csv`, not just this tutorial). If that prune is repaired, invalid zero-weight samples stop
being stored and this bug's trigger becomes much rarer — but the contract gap
above is still real, because a converged fit can carry an invalid sample at
non-zero weight.

## Context worth carrying

The reproduction fit reports `f_live=1.0000, N_eff=1` — the `n_like_max=300` cap
in `_quick_fit.py` means the sampler never converges, so those 300 rows are
near-prior exploration points with a degenerate one-hot weight vector. Any
attempt to reason about "typical" weights from this fixture will mislead.

## Superseded

An initial triage guessed this was the prior-support family
([#1484](https://github.com/PyAutoLabs/PyAutoFit/issues/1484),
[#1481](https://github.com/PyAutoLabs/PyAutoFit/issues/1481)) and attributed the
failure to `from_sample_index` at `samples.py:319`. Both were wrong; the
reproduction above supersedes them. Those issues concern the objective *during*
a search — this concerns reconstructing stored samples *after* one.
