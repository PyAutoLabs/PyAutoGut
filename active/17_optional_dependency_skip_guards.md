# `@PyAutoFit` `[optional]`-dependency tests have no skip guards

Type: test
Target: autofit
Difficulty: small
Autonomy: autonomous
Priority: normal
Status: issued 2026-08-22 as PyAutoFit#1511; PR #1512 open, awaiting CI

Not a defect on `main` — a test-hygiene gap that has been *repeatedly
misdiagnosed* as one. That misdiagnosis is the actual cost.

## The finding

`test_autofit/non_linear/search/nest/test_nautilus.py::test__single_core_builds_no_pool`
runs a real `search.fit`, which reaches `from nautilus import Sampler`
(`autofit/non_linear/search/nest/nautilus/search.py:238`).
`nautilus-sampler==1.0.5` ships **only** in the `[optional]` extra
(`pyproject.toml:85`), and the test carries **no skip guard**.

CI installs `[optional]` — PyAutoHeart's `lib-tests.yml` does
`pip install "./$r[optional]"` — so CI never sees it. Every env installed
without those extras (cloud sandboxes, local venvs) gets a hard
`ModuleNotFoundError`.

It is the only optional-sampler test in the suite without a guard. Precedent
is everywhere else: `test_blackjax_nuts.py:14`, `nest/nss/test_search.py:20`,
`test_arithmetic_jax_trace.py:6`, `test_fork_context.py:31`.

`astropy` is the same class of noise: two modules fail *collection* on its
top-level import, and nine aggregator tests error on it at runtime
(`autofit/aggregator/file_output.py:101`,
`autofit/aggregator/summary/aggregate_fits.py:105,165`).

## Why this was worth a task

The single nautilus failure has been reported as "pre-existing on clean
`main`" in at least six completion records since 2026-08-16 — see the
correction trail below. Each session spent a control run re-disproving it,
and the wrong gloss propagated into PR bodies #1479 and #1480. Main is **not**
red: latest main CI (run 32546158666) is 2024 passed, 3 skipped, 0 failed on
3.12, 3.13 and the no-jax leg.

## Evidence (untouched main @ `a639226`, py3.12)

| env | result |
|---|---|
| no `nautilus-sampler` | `1 failed, 3 passed` — `ModuleNotFoundError` at `search.py:242` |
| `pip install nautilus-sampler==1.0.5`, same tree, no other change | `4 passed` |
| full suite, no optional extras | 2 collection errors → then 4 failed / 9 errors, **all** missing-`astropy` |

## The fix

Skip-if-missing guards in the house pattern — an `importlib.util.find_spec`
`skipif` marker, or `pytest.importorskip` where the import is module-level.
Tests only; no `autofit/` source touched.

Verified three ways on the branch:

- no extras at all — nautilus test skips with its reason: `3 passed, 1 skipped`
- no `astropy` — `1985 passed, 33 skipped, 0 failed, 0 errors`
- full `[optional]` extras (the CI env) — `2024 passed, 3 skipped`, **identical
  to CI on main**, so the guards are inert where the deps exist and no
  coverage is lost

## Correction trail

The claim "fails identically on the untouched tree — pre-existing, not this
change" is right about causation and wrong about `main`. Records carrying the
loose gloss:

- `complete/2026/08/prior-support-clipper.md:152,218` — already issued the
  correction ("read it as environment-specific"); the correct reading
- `complete/2026/08/covariance-interpolator-rng-seed.md:14` — the only record
  that names the real `ModuleNotFoundError`; correct
- `complete/2026/08/uniform-prior-bounds-numpy-path.md:31,50` — follow-up 4
  proposed exactly this fix but it was never filed as a prompt, so nothing
  acted on it; this task is that follow-up
- `complete/2026/08/multistart-gradient-resume-fom-sanity-check.md:14` —
  "confirmed pre-existing on unmodified `main`"; wrong gloss
- `complete/2026/08/clipper-usage-in-search-summary.md:89` — "**pre-existing**";
  wrong gloss

Once this merges, no env reproduces the failure and the gloss stops
recurring.

## Prior art

`complete/2026/08/nautilus-1core-serial-pool.md` — the task that *added*
`test__single_core_builds_no_pool` (PyAutoFit#1442 → #1443). The test itself is
sound and still guards the real fork-pool deadlock; only its environment
assumption was missing.
