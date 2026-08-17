# `@to_instance` materializes stored samples with no `FitException` guard

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: high
Status: formalised

## What this is

[PyAutoFit#1466](https://github.com/PyAutoLabs/PyAutoFit/issues/1466) ("preserve
guarded sample lifecycle", merged `b499d4367` 2026-08-11) gave two result-reading
methods a recovery path for stored samples that a newer model class now rejects
with `FitException`:

- `Samples.max_log_likelihood` — falls back to the next-highest-likelihood valid
  sample (`samples.py:405-441`)
- `SamplesPDF.draw_randomly_via_pdf` — redraws up to
  `VALID_INSTANCE_MAX_ATTEMPTS = 100` times (`pdf.py:336-367`)

Both were written **by hand, at the call site**. The shared decorator that every
*other* result-reading method uses to turn a vector into an instance was not
touched:

```python
# autofit/non_linear/samples/interface.py:32-40
def wrapper(self, *args, as_instance=True, as_dict=False, **kwargs):
    vector = func(self, *args, **kwargs)
    if as_dict:
        return {".".join(path[0]): value for path, value in zip(self.paths, vector)}
    if as_instance:
        return self._instance_from_vector(vector)   # <-- no try/except
    return vector
```

So `@to_instance`-decorated methods — `from_sample_index`, `max_log_posterior`,
`median_pdf`, `values_at_upper_sigma`, `values_at_lower_sigma`,
`errors_at_*_sigma` — still raise straight through whenever the vector they
materialize is one the model now rejects. The guarantee #1466 established holds
for two entry points and silently does not hold for the rest.

Note the escape hatches already differ per path: `as_dict=True` and
`as_instance=False` never construct an object and are therefore always safe.
Only the materialization request needs the guard.

## Why it started failing on 2026-08-10

`PyAutoGalaxy` gained a geometric constructor guard on **2026-08-09**
(`a366f771`, #566): `validate_ell_comps` rejects `ell_comps` whose magnitude is
not below 1, because `q = (1 - f) / (1 + f)` is only a valid axis ratio while
`f < 1`. The very next day `be61b8d0` (#568) made that exception a
`ModelParameterException(ValueError, af.exc.FitException)` specifically so a
search would **resample** the candidate rather than die.

That closed the fit-time path. It did not close the results-reading path — and
roughly 21% of the `ell_comps` prior square lies outside the unit circle, so
invalid points are routinely present in a stored sample list, carrying near-zero
weight.

## Reproduction (confirmed on `main`, autofit/autogalaxy 2026.7.23.1)

Control test: a three-sample `SamplesPDF` where one sample has the exact
`ell_comps` from the CI failure, `(0.9781300707301511, -0.23873992910981626)`,
magnitude `1.006844`. Arm A puts it last with zero weight; arm B makes it the
maximum-posterior sample.

| call | arm A (invalid = last) | arm B (invalid = max posterior) |
|---|---|---|
| `max_log_likelihood()` | ok — recovered | ok — recovered |
| `draw_randomly_via_pdf()` ×50 | ok — recovered | ok — recovered |
| `max_log_posterior()` | ok (not hit) | **RAISED** `ModelParameterException` |
| `from_sample_index(-1)` | **RAISED** `ModelParameterException` | ok (not hit) |

The two hand-guarded methods recover under both arms. The two decorated methods
raise as soon as the invalid sample is the one they select — which is the whole
point: the decorator has no opinion about validity, so whether it raises depends
only on where the invalid sample happens to land.

Script: `scratchpad/repro_guard_gap.py` (control test only; recreate from the
table above — it constructs `af.Sample` kwargs directly and needs no search).

## The CI failure this explains

`PyAutoHeart` **Workspace Smoke**, scheduled runs 2026-08-10
(`31356506626`) and 2026-08-17 (`31992749671`), job
`run_notebooks (3.12, autogalaxy, guides)` — 1 failure out of 1332 checks:

```
autogalaxy_workspace notebooks/guides/results/aggregator/samples.ipynb
  FAIL (10.2s) ModelParameterException: ell_comps must satisfy
  ell_comps[0]**2 + ell_comps[1]**2 < 1; got
  (0.9781300707301511, -0.23873992910981626), whose magnitude is 1.0068441731558715
```

The failing call is `samples.from_sample_index(sample_index=-1)`
(`scripts/guides/results/aggregator/samples.py:319`, "create an instance of the
last accepted model"). That method is `@to_instance`-decorated and takes the
last sample **unconditionally**.

Two pieces of corroborating evidence that this is the site rather than the
`draw_randomly_via_pdf` call further down at line 482:

1. The reported exception is `ModelParameterException` itself. An exhausted
   `draw_randomly_via_pdf` raises `SamplesException ... from last_error`, a
   different type.
2. The smoke job installs **released wheels** (`autofit-2026.8.15.1`, confirmed
   from the run log). That wheel was downloaded and inspected directly: it
   **does** contain `VALID_INSTANCE_MAX_ATTEMPTS` and the retry loop. The guard
   was present and is not what failed.

## Fix locus

**PyAutoFit, in the decorator** — `to_instance` in
`autofit/non_linear/samples/interface.py`, so every decorated method inherits
one contract instead of each call site restating it. Patching only
`from_sample_index` would leave `max_log_posterior` (proven broken in arm B
above) and the sigma methods still exposed.

Open design question for the implementer, and the reason this is `supervised`
rather than autonomous — **the right recovery differs per method and the
decorator cannot know which applies**:

- `from_sample_index(i)` is a request for *one specific* sample. Silently
  substituting a different one would be a lie; raising a typed, explanatory
  error is arguably correct here, and `ignore_assertions`-style opt-in may be
  the better lever.
- `max_log_posterior` has a natural fallback identical to
  `max_log_likelihood`'s — the next-best valid sample.
- `median_pdf` / `values_at_*_sigma` synthesize a vector by marginalizing each
  parameter **independently**, so their output need not be a physically valid
  point at all. No stored sample can be substituted. The autogalaxy tutorial
  already documents this and works around it by requesting `as_dict=True`
  (`samples.py:271-274`) — evidence the class of failure was known and handled
  one call site at a time.

Do **not** resolve this by weakening `validate_ell_comps`, and do **not** edit
the tutorial to route around it — the tutorial is user documentation and the
guard is correct. A workspace edit would conceal a library contract gap that
affects every user reading results from a fit.

## Scope boundary

Unrelated to [PyAutoFit#1484](https://github.com/PyAutoLabs/PyAutoFit/issues/1484)
(UniformPrior bounds unenforced on the NumPy path) and
[#1481](https://github.com/PyAutoLabs/PyAutoFit/issues/1481) (prior-support
coverage after Prodigy), despite the family resemblance. Those concern the
objective during a search; this concerns reconstructing stored samples after one.
An initial triage guessed the prior-support family — that guess was wrong and the
reproduction above supersedes it.

## Incidental finding (do not fix here)

`Samples.from_sample_index` is annotated `-> ModelInstance` and its docstring
says "returned as a model instance", but the undecorated body returns
`self.parameter_lists[sample_index]` — a plain list. It only satisfies the
annotation because `@to_instance` converts it. Harmless today; worth a docstring
correction if the implementer is already in this file.
