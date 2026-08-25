## loggaussian-prior-support
- issue: PyAutoFit#1526 (closed by this work)
- completed: 2026-08-25
- library-pr: https://github.com/PyAutoLabs/PyAutoFit/pull/1527, **MERGED** 2026-08-25 as
  `34d6dff` (merge commit; branch commit `c3505d1`), +276/-34 over 6 files. CI green on
  all four legs (`unittest` 3.12, `unittest` 3.13, `unittest-nojax`, `docs / docs-build`).
- validation: full suite 2178 passed / 36 skipped (baseline on `main`: 2124 passed),
  plus a 37-probe before/after equivalence harness described below.
- release: not performed; merged PR carries `pending-release`.

Follow-up 3 owed by the prior-support `Clipper`
(`complete/2026/08/prior-support-clipper.md`, PyAutoFit#1477), which worked around this
defect rather than fixing it. That workaround is now retired.

## What shipped

`LogGaussianPrior`'s support is `(0, inf)` -- `log_prior_from_value` returns `-inf` for
`value <= 0` -- but the prior *reported* `(-inf, inf)`: `Prior.__getattr__` delegates to
a `TransformedMessage` whose limits default to `+/-inf` and were never set. The one
prior with a non-trivial support was the one prior that lied about it.

- `Prior.lower_limit_strict` / `upper_limit_strict` -- new class attributes, default
  `False`, stating whether the support *excludes* the bound. `True` for
  `LogGaussianPrior`'s lower bound.
- `LogGaussianPrior` sets `lower_limit = 0.0` / `upper_limit = inf` in `__init__`.
- `Prior.limits` now derives from `lower_limit`/`upper_limit` instead of returning a
  hardcoded `(-inf, inf)`.
- `ClipperPriorBox._limits_from_model` reads the strictness flags; the
  `isinstance(prior, LogGaussianPrior)` block, its import and the workaround docstrings
  are gone. Bounds output is bit-identical.

## The design decision worth remembering: shadow on the PRIOR, not the message

The prompt sanctioned either "pass the limits into the `TransformedMessage`, or override
`lower_limit`". The message route is contaminated and the difference is not cosmetic:

- `TransformedMessage.with_base()`, `.copy()`, `.project()` and `.__call__()` all
  reconstruct without the limits, so a message-level declaration evaporates on the first
  EP projection. Fixing that is a fourth change to a shared class.
- `MeanField.lower_limit` (`graphical/mean_field.py:259`) and `LaplaceOptimiser`
  (`check_limits=True` **by default**) read message limits and feed them to
  `OptimisationState.valid`, which does `(parameters < lower_limit).any()`. Today that
  compares against `-inf` and never fires; with `0.0` it would start rejecting states.
  Arguably more correct, but a live EP behaviour change.

Shadowing on the prior keeps the blast radius to consumers of `prior.lower_limit`, and
survives `copy`/`project` for free (`Prior.project` does `copy(self)` then swaps only
`.message`). It also matches the existing house pattern -- `UniformPrior` and
`LogUniformPrior` already shadow.

The `limits` half is the structural fix: deriving it from the declared bounds means the
two notions cannot disagree by construction, which is the root cause of this bug class
rather than this instance of it.

## The finding the prompt did not anticipate

Including `limits` fixed a **second live defect**. Prior passing
(`AbstractPriorModel.mapper_from_prior_means`, `prior_model/abstract.py:1153`) falls back
to `prior.limits` when config supplies no `Limits` entry, and builds a
`TruncatedGaussianPrior` from it:

| | before | after |
|---|---|---|
| passed prior | `TruncatedGaussian(1.0, 0.5, -inf, inf)` | `TruncatedGaussian(1.0, 0.5, 0.0, inf)` |
| `value_for(0.001)` | **`-0.545`** | `0.0089` |
| `log_prior_from_value(-1.0)` | **`-8.0`** (finite) | `-inf` |

A strictly positive parameter was being passed a prior that samples negative values and
assigns them finite density -- exactly the hazard the prompt described in the abstract,
found live. This is a correctness fix but it **changes the unit-cube mapping of the
passed prior**, so it is downstream-visible: PyAutoGalaxy / PyAutoLens inter-phase prior
passing is worth a spot-check.

## Traps measured, not argued

An adversarial pass ran the whole change as a throwaway prototype against a running
3.12 install *before* any commit, then diffed 37 behavioural probes against `main`.
34 identical; the 3 that moved were `lower_limit` under `copy`, `pickle` and `project`.

1. **The identifier worry is empirically dead.** `Identifier(prior)`, its full
   `description`, and `Identifier(LBFGS(clipper=ClipperPriorBox()))` are byte-identical.
   `__identifier_fields__ = ("mean", "sigma")` gates the hash; new instance and class
   attributes never reach it. No re-keying, no orphaned output directories -- the
   opposite outcome to the clipper-identifier decision of 2026-08-18
   (`complete/2026/08/clipper-in-search-identifier.md`), which chose to re-key and
   orphan. Worth knowing the two questions resolve differently and why: that one put the
   clipper *into* `__identifier_fields__`; this one adds attributes *outside* it.
2. **A test encoded the bug as expected behaviour.** `test_clipper.py` asserted
   `prior.lower_limit == -np.inf` with a docstring explaining why. The initial plan
   claimed the clipper tests would pass unchanged -- false, and it was the single
   failure in the prototype run. Rewritten with its own history in the docstring so the
   workaround is not re-added. Lesson: when retiring a workaround, grep the tests for
   assertions that *pin* the defect, not just ones that exercise the fix.
3. **`_support` was already right all along.** `TransformedMessage.__init__` computes
   `self._support` by mapping the base message's support through the inverse transform,
   giving `(0.0, inf)` correctly. So the class held the right answer in one attribute
   and the wrong answer in two others. Three notions of "bounds" (`_support`,
   `lower_limit`/`upper_limit`, `limits`) is the underlying smell; this task collapsed
   two of them, not all three.
4. **The property test had to be checked for vacuity.** "Reported support matches actual
   support" catches this bug only via the *finite-strictly-inside* clause -- with a
   reported `(-inf, inf)` there is no "outside" to test, so the outside-is-`-inf` clause
   would have passed vacuously. Verified by running the new tests against the parent
   commit: it fails for `LogGaussianPrior` alone and passes for the other five families.

## Follow-ups owed (filed, not fixed)

1. Declare the limits on `TransformedMessage` and preserve them through `with_base` /
   `copy` / `project` / `__call__`. Changes EP/Laplace behaviour (trap above) -- needs
   its own task and its own measurement.
2. The three now-redundant `limits` overrides on `UniformPrior`, `LogUniformPrior` and
   `TruncatedGaussianPrior` are exact duplicates of the new base implementation. Left in
   place to keep this PR minimal; deleting them is a trivial tidy-up.
3. `line_search.OptimisationState.valid` uses `if self.lower_limit and ...`, which is
   falsy at `0.0`. Pre-existing and untouched, but it means a `0.0` lower limit would
   silently skip that guard if the limits ever do move onto the message (follow-up 1).

## Process note

The task ran `web-github`: no local worktree, no `~/Code/PyAutoLabs` checkout, and
PyAutoHeart absent, so the readiness gate fell back to the documented per-repo
`pytest` gate (WORKFLOW.md) rather than an authoritative Heart GREEN. A Python 3.12
venv was built in-session to get a runnable install (`autofit` needs `>=3.12`; the
session default was 3.11), which is what made the 37-probe before/after harness
possible at all. Remote branch deletion was out of scope -- the egress proxy refuses
ref deletions in a proxied web session -- so `feature/loggaussian-prior-support`
remains on origin for `/repo_cleanup`.

## Original prompt

# `LogGaussianPrior` misreports its own support as `(-inf, inf)`

Type: bug
Target: autofit
Repos:
- PyAutoFit
Difficulty: small
Autonomy: supervised
Priority: normal
Status: formalised
Filed: 2026-08-16 (backfilled from git)
Issued: 2026-08-25

Filed 2026-08-16. Follow-up 3 owed by the prior-support `Clipper`
(`complete/2026/08/prior-support-clipper.md`, PyAutoFit#1477), which worked
around it rather than fixing it.

## The defect

`LogGaussianPrior`'s support is `(0, inf)` — `log_prior_from_value` returns
`-inf` for `value <= 0`. But its `TransformedMessage` defaults its limits to
`±inf` and is never passed any, so the prior **reports** `(-inf, inf)`.

Every other prior answers `lower_limit` / `upper_limit` truthfully via
`Prior.__getattr__` delegating to the message, which is why the `Clipper` needs
no type switch anywhere else. This one prior is the exception, and it is the
kind of exception that is invisible until something trusts the answer.

## Why it matters now

`ClipperPriorBox` **declares the real support in the clipper** rather than on
the prior — deliberately, to avoid touching a shared class late in that task,
and recorded as a follow-up rather than left silent. That special case is
correct but misplaced: any future consumer of `lower_limit` gets the wrong
answer unless it also knows to special-case this prior.

The general hazard: a bound of `-inf` on a strictly positive parameter means a
consumer will not guard `0`, and `log(0)` / a division by it is the failure that
follows.

## The fix

Declare the support on `LogGaussianPrior` itself — pass the limits into the
`TransformedMessage`, or override `lower_limit` — then retire the clipper's
special case and its accompanying comment.

## The care needed — why this is `supervised` and not `safe`

Changing what a prior reports as its support is not local:

- **The nested samplers work in unit-cube coordinates** and map through the
  prior. Confirm a limits change does not alter that mapping, or every stored
  nested-sampling result shifts.
- **`log_prior_from_value` must not change behaviour.** It is already correct;
  only the *reported* limits are wrong. If the fix changes the density anywhere,
  it has gone too far.
- **Check the identifier.** If `lower_limit` feeds the search identifier, a
  change re-keys existing output directories and orphans stored results — the
  same class of concern as the clipper identifier decision, which chose to
  re-key and orphan rather than special-case (2026-08-18; record
  `complete/2026/08/clipper-in-search-identifier.md`).

## Verify

- `LogGaussianPrior(...).lower_limit == 0.0` (or whatever exclusive convention
  is chosen — state it).
- `log_prior_from_value` is unchanged across a range of values either side of
  zero, asserted against the pre-change values.
- `ClipperPriorBox.bounds_from_model` returns the same bounds for a model
  containing a `LogGaussianPrior` **after** the clipper's special case is
  removed as it did before — that equivalence is the whole point of the change.
- A nested-sampler unit-cube round-trip through the prior is unchanged.

<!-- Grounding: recorded as trap 3 and follow-up 3 in
     complete/2026/08/prior-support-clipper.md, measured against a running
     install during PyAutoFit#1477. -->
